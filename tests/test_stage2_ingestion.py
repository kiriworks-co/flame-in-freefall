"""Regression tests for incremental source additions and mixed scientific evidence."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from src import pipeline, storage
from src.extractors import extract_document
from src.scientific_store import ScientificStore
from src.units import field_definition, normalize_quantity, observations_from_tables


def test_same_header_in_different_blocks_keeps_source_role() -> None:
    # Synthetic fixture mirrors NASA's separate experimental/model blocks.
    extraction = extract_document("fixture.csv", b"Experiment,Pressure,Kavg,,Model,Pressure,Kavg\n,0.5,0.31,,,0.5,0.5\n,1,0.3,,,1,0.49\n")
    provenance = {"field_classification": [
        {"column_index": 1, "role": "condition"},
        {"column_index": 2, "role": "reported_result"},
        {"column_index": 5, "role": "simulation"},
        {"column_index": 6, "role": "simulation"},
    ]}
    pipeline._classify_tables(extraction, provenance, "mixed_experiment_and_simulation")
    left, right = extraction["tables"]
    assert left["source_column_indices"] == [1, 2]
    assert right["source_column_indices"] == [5, 6]
    observations = observations_from_tables(extraction["tables"], "mixed_experiment_and_simulation")
    assert [o["evidence_kind"] for o in observations if o["table_index"] == 0] == ["condition", "condition"]
    assert [o["evidence_kind"] for o in observations if o["table_index"] == 1] == ["simulation", "simulation"]
    assert all(o["normalized_value"] is None for o in observations)


def test_manifest_warning_overrides_inferred_normalization() -> None:
    extraction = extract_document("fixture.csv", b"Burning rate; mm\n2\n3\n")
    pipeline._classify_tables(extraction, {"field_classification": [
        {"header": "Burning rate; mm", "role": "reported_result", "warning": "Length is not rate"},
    ]}, "mixed_conditions_and_reported_results")
    observations = observations_from_tables(extraction["tables"])
    assert observations and all(o["evidence_kind"] == "reported_result" for o in observations)
    assert all(o["normalized_value"] is None and o["status"] == "source_unit_ambiguous" for o in observations)


def test_catalog_refreshes_fallback_names_without_changing_custom_names(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path / "archive")
    study = {"id": "PSI-900001", "name": "Synthetic catalog title", "description": "Synthetic description"}
    fallback = storage.create_experiment("PSI-900001 · PSI-900001")
    fallback["psi_id"] = study["id"]
    original_folder = fallback["folder"]
    result = pipeline._experiment(study, [fallback])
    assert result["name"] == "PSI-900001 · Synthetic catalog title"
    assert result["description"] == study["description"] and result["folder"] == original_folder
    result["name"] = "User's research notes"
    result["description"] = "User's own description"
    assert pipeline._experiment(study, [result])["name"] == "User's research notes"
    assert result["description"] == "User's own description"


def test_scientific_abbreviations_preserve_dimensions() -> None:
    assert field_definition("T_max(K)")[:2] == ("temperature", "K")
    assert field_definition("Peak burner T (C )")[:2] == ("temperature", "C")
    assert field_definition("Peak burner Temp (C)")[:2] == ("temperature", "C")
    assert field_definition("Tad (K)")[:2] == ("temperature", "K")
    assert field_definition("Time(sec)")[:2] == ("time", "sec")
    assert field_definition("P (atm)")[:2] == ("pressure", "atm")
    assert field_definition("approx p (bar)")[:2] == ("pressure", "bar")
    assert field_definition("Dflame (mm)")[:2] == ("diameter", "mm")
    assert field_definition("K(mm^2/sec)")[:2] == ("area_rate", "mm^2/sec")
    assert normalize_quantity(.5, "mm^2/sec", "area_rate")["normalized_unit"] == "mm²/s"
    assert normalize_quantity(.5, "mm2/s", "area_rate")["normalized_value"] == .5
    assert normalize_quantity(.5, "atm", "pressure")["status"] == "reference_required"
    assert field_definition("t/(Do)2 (s/mm2)")[0] is None
    assert normalize_quantity(.5, "s/mm2")["normalized_unit"] == "s/mm2"


def _add_source(project: Path, study_id: str, value: int) -> None:
    folder = project / "data" / "psi_downloads" / study_id
    folder.mkdir(parents=True)
    content = f"Time(sec),Temperature(K)\n0,{value}\n1,{value + 1}\n".encode()
    (folder / "fixture.csv").write_bytes(content)
    (folder / "source_manifest.json").write_text(json.dumps({
        "investigation_id": study_id, "downloaded_csvs": [{
            "filename": "fixture.csv", "sha256": storage.sha256_bytes(content),
            "classification": "simulation", "source_url": "https://psi.nasa.gov/fixture-only",
        }],
    }), encoding="utf-8")


def test_warm_bootstrap_detects_added_sources_and_reindexes(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("RAG_EMBEDDING_MODEL", " ")
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path / "archive")
    project = tmp_path / "project"
    db, search = tmp_path / "science.sqlite3", tmp_path / "search.sqlite3"
    _add_source(project, "PSI-900001", 400)
    first = pipeline.ensure_scientific_bootstrap(project, db, search)
    assert first["bootstrapped"] and first["chunks"] > 0
    assert not pipeline.ensure_scientific_bootstrap(project, db, search)["bootstrapped"]
    _add_source(project, "PSI-900002", 500)
    # Simulates CLI --no-index (or a process stopping between ingest and indexing).
    imported = pipeline.ingest_downloads(project, db, index_search=False)
    assert imported["imported"] == 1 and not imported["errors"]
    second = pipeline.ensure_scientific_bootstrap(project, db, search)
    assert second["bootstrapped"] and second["index"] is not None
    assert second["chunks"] > first["chunks"]
    store = ScientificStore(db)
    assert len(store.list_documents()) == 2
    assert all(o["evidence_kind"] == "simulation" for o in store.observations())
    with store.connection() as conn:
        assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
        assert conn.execute("SELECT count(*) FROM events").fetchone()[0] == 2
    assert not pipeline.ensure_scientific_bootstrap(project, db, search)["bootstrapped"]


def test_competing_cli_imports_share_archive_lock(tmp_path: Path, monkeypatch) -> None:
    """Two real processes must not create duplicate experiment folders or temp races."""
    project = tmp_path / "project"
    archive = tmp_path / "archive"
    registry = tmp_path / "science.sqlite3"
    monkeypatch.setattr(storage, "DATA_DIR", archive)
    _add_source(project, "PSI-900001", 400)
    _add_source(project, "PSI-900002", 500)
    code = """
import json,sys,time
from pathlib import Path
from src import pipeline,storage
storage.DATA_DIR=Path(sys.argv[2])
original=pipeline._experiment
def delayed(*args):
    time.sleep(.15)
    return original(*args)
pipeline._experiment=delayed
result=pipeline.ingest_downloads(Path(sys.argv[1]),Path(sys.argv[3]),index_search=False)
print(json.dumps({k:v for k,v in result.items() if k!='documents'}))
assert not result['errors'], result
"""
    env = dict(os.environ, RAG_EMBEDDING_MODEL=" ")
    processes = [subprocess.Popen(
        [sys.executable, "-c", code, str(project), str(archive), str(registry)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env,
    ) for _ in range(2)]
    try:
        for process in processes:
            stdout, stderr = process.communicate(timeout=60)
            assert process.returncode == 0, stdout + stderr
    finally:
        for process in processes:
            if process.poll() is None:
                process.kill()
                process.wait()
    experiments = storage.list_experiments()
    assert len(experiments) == 2
    assert {e["psi_id"] for e in experiments} == {"PSI-900001", "PSI-900002"}
    assert len(ScientificStore(registry).list_documents()) == 2


def test_real_stage2_multiblock_csv_preserves_source_rows() -> None:
    root = Path(__file__).resolve().parents[1]
    path = root / "data/psi_downloads/PSI-117/PSI-117_Analyzed Data_MST_2024_Dext.csv"
    if not path.is_file():
        # During source preparation the archive may use a subdirectory.
        matches = list((root / "data/psi_downloads/PSI-117").rglob("*MST_2024_Dext.csv"))
        assert matches, "The Stage 2 NASA source must be committed for this integration test"
        path = matches[0]
    result = extract_document(path.name, path.read_bytes())
    assert result["status"] == "processado"
    assert len(result["tables"]) == 2
    assert [t["block"]["label"] for t in result["tables"]] == ["Model", "Expt"]
    assert result["tables"][0]["rows"][0] == [.5, 1.197278912, 3.442176871]
    assert result["tables"][1]["rows"][0] == [.5, 1.947105678]
    assert all(t["source_rows"][0] == 2 for t in result["tables"])


def test_real_nasa_roles_separate_models_and_reported_experiments() -> None:
    folder = Path(__file__).resolve().parents[1] / "data/psi_downloads/PSI-117"
    manifest = json.loads((folder / "source_manifest.json").read_text(encoding="utf-8"))
    records = {r["filename"]: r for r in manifest["downloaded_csvs"]}
    record = records["PSI-117_Analyzed Data_MST_2024_Dext.csv"]
    result = extract_document(record["filename"], (folder / record["filename"]).read_bytes())
    pipeline._classify_tables(result, record, record["classification"])
    assert [t["evidence_kind"] for t in result["tables"]] == ["simulation", "reported_result"]
    assert [t["source_column_indices"] for t in result["tables"]] == [[1, 2, 3], [6, 7]]
    # Pressure has no declared unit in this file: it cannot silently become psia.
    observations = observations_from_tables(result["tables"], record["classification"])
    assert {o["evidence_kind"] for o in observations} == {"simulation", "reported_result"}
    assert all(o["normalized_value"] is None for o in observations)
    record = records["PSI-117_Analyzed Data_PROCI_2019_Stable_Cool.csv"]
    result = extract_document(record["filename"], (folder / record["filename"]).read_bytes())
    pipeline._classify_tables(result, record, record["classification"])
    observations = observations_from_tables(result["tables"], record["classification"])
    assert all(o["evidence_kind"] == "simulation" for o in observations)
    rate = next(o for o in observations if o["field"] == "K(mm^2/sec)")
    assert rate["quantity"] == "area_rate" and rate["normalized_unit"] == "mm²/s"
    assert rate["normalized_value"] == -.0325791


def test_real_nasa_readme_retains_conflicting_composition_conventions() -> None:
    path = (Path(__file__).resolve().parents[1] / "data/psi_downloads/PSI-117"
            / "PSI-117_Analyzed Data_ReadMe_List_of_Data.xlsx")
    result = extract_document(path.name, path.read_bytes())
    assert result["raw_matrices"][0]["rows"][1][4:7] == [.21, 74, "Balance"]
    observations = observations_from_tables(result["tables"], "metadata")
    assert all(o["evidence_kind"] == "metadata" for o in observations)
    assert not any(o["quantity"] == "oxygen" for o in observations)


@pytest.mark.parametrize("study_id", ["PSI-62", "PSI-117", "PSI-159"])
def test_real_isa_metadata_has_searchable_pages_not_fabricated_samples(study_id: str) -> None:
    folder = Path(__file__).resolve().parents[1] / "data/psi_downloads" / study_id / "metadata"
    investigation = folder / "i_Investigation.txt"
    extracted = extract_document(investigation.name, investigation.read_bytes())
    assert extracted["status"] == "processado" and extracted["isa"]["study"]["id"] == study_id
    assert any(page["text"] for page in extracted["pages"])
    sample = next(folder.glob("s_*.txt"))
    placeholder = extract_document(sample.name, sample.read_bytes())
    assert placeholder["metadata"]["placeholder"]
    assert placeholder["pages"] == placeholder["tables"] == []
