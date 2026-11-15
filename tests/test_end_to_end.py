"""Offline integration uses ORIGINAL NASA PSI bytes, not synthetic measurements.

Downloads are performed explicitly by the collector. Tests copy those verified
local originals into temporary project/archive/SQLite directories and never
write into the working scientific archive or access the network.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest

from src import storage
from src.assistant import answer, validate_claims
from src.extractors import render_pdf_page
from src.pipeline import ingest_downloads
from src.retrieval import RetrievalIndex
from src.scientific_store import ScientificStore

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def real_nasa_project(tmp_path, monkeypatch):
    source = ROOT / "data" / "psi_downloads" / "PSI-69"
    manifest_path = source / "source_manifest.json"
    if not manifest_path.is_file():
        pytest.skip("Run the NASA collector first; this integration requires real PSI-69 files")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = manifest.get("downloaded_csvs", []) + manifest.get("downloaded_pdfs", [])
    if not any(r["filename"].lower().endswith(".csv") for r in files) or not any(
        r["filename"].lower().endswith(".pdf") for r in files
    ):
        pytest.skip("Real NASA CSV and PDF are both required")
    project = tmp_path / "source"
    dest = project / "data" / "psi_downloads" / "PSI-69"
    dest.mkdir(parents=True)
    shutil.copyfile(manifest_path, dest / "source_manifest.json")
    for record in files:
        original = source / record["filename"]
        assert hashlib.sha256(original.read_bytes()).hexdigest() == record["sha256"]
        shutil.copyfile(original, dest / record["filename"])
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path / "archive")
    monkeypatch.delenv("RAG_EMBEDDING_MODEL", raising=False)
    monkeypatch.delenv("RAG_MODEL", raising=False)

    def forbidden_network(*args, **kwargs):
        raise AssertionError("Offline integration must never access a network provider")

    monkeypatch.setattr("urllib.request.urlopen", forbidden_network)
    return project, tmp_path / "scientific.sqlite3", tmp_path / "search.sqlite3", manifest


@pytest.mark.integration
def test_real_nasa_import_extract_persist_index_question_and_source(real_nasa_project):
    project, db_path, index_path, manifest = real_nasa_project
    imported = ingest_downloads(project, db_path, index_search=False)
    expected_files = manifest["downloaded_csvs"] + manifest["downloaded_pdfs"]
    assert not imported["errors"], imported
    assert imported["imported"] == len(expected_files)
    experiments = storage.list_experiments()
    assert len(experiments) == 1
    experiment = experiments[0]
    assert experiment["psi_id"] == "PSI-69"
    expected_hashes = {record["sha256"] for record in expected_files}
    assert {doc["sha256"] for doc in experiment["documents"]} == expected_hashes
    assert all(storage.verify_original(experiment, doc) for doc in experiment["documents"])

    store = ScientificStore(db_path)
    with store.connection() as db:
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []
        assert db.execute("SELECT COUNT(*) FROM documents").fetchone()[0] == len(expected_files)
        assert db.execute("SELECT COUNT(*) FROM cells").fetchone()[0] > 100
        assert db.execute("SELECT COUNT(*) FROM regions").fetchone()[0] > 10
        assert db.execute("SELECT COUNT(*) FROM sources WHERE doi=?", (manifest["doi"],)).fetchone()[0] == len(expected_files)
    index = RetrievalIndex(index_path)
    first = index.index_experiments(experiments)
    assert not first["failures"]
    assert first["total"] > 100
    assert index.index_experiments(experiments)["indexed"] == 0
    filters = [{"field": "oxygen_fraction", "unit": "fraction", "min": .21, "max": .21},
               {"field": "fuel", "value": "Methanol"}]
    response = answer("Methanol", index, study_ids=["PSI-69"], numeric_filters=filters, use_llm=False)
    assert response["mode"] == "offline-evidence"
    assert not response["insufficient"] and response["evidence"]
    for evidence in response["evidence"]:
        assert evidence["kind"] == "table_row"
        assert evidence["study_id"] == "PSI-69" and evidence["sha256"] in expected_hashes
        assert evidence["source_url"] == "https://psi.nasa.gov/physci/repo/data/investigations/PSI-69"
        assert evidence["doi"] == manifest["doi"] and evidence["row_number"] >= 2
        oxygen = [o for o in evidence["observations"] if o["quantity"] == "oxygen"]
        assert oxygen and oxygen[0]["normalized_value"] == .21
        assert any(o["evidence_kind"] == "reported_result" for o in evidence["observations"])
    # Ambiguous mmHg reference must never be silently promoted to absolute psia.
    assert not index.search("", study_ids=["PSI-69"], numeric_filters=[
        {"field": "pressure", "unit": "psia", "reference": "absolute", "min": 0, "max": 1000}
    ])
    assert not index.search("", numeric_filters=[
        {"field": "oxygen_fraction", "unit": "fraction", "min": .99, "max": 1.0},
        {"field": "fuel", "value": "Methanol"}
    ])

    pdf_response = answer("requirements", index, study_ids=["PSI-69"], language="en", use_llm=False)
    pdf_evidence = [e for e in pdf_response["evidence"] if e["document_name"].lower().endswith(".pdf")]
    assert pdf_evidence and not pdf_response["insufficient"]
    source = pdf_evidence[0]
    document = next(doc for doc in experiment["documents"] if doc["sha256"] == source["sha256"])
    extraction = storage.load_extraction(experiment, document)
    page = next(p for p in extraction["pages"] if p["page"] == source["page"])
    assert source["text"] in page["text"]
    # This PSI-69 association is a NASA catalog link; content is explicitly FLEX-2.
    assert "FLEX-2" in extraction["pages"][0]["text"]
    png = render_pdf_page(storage.read_original(experiment, document), source["page"], dpi=50)
    assert png.startswith(b"\x89PNG\r\n\x1a\n")
    claims, errors = validate_claims({"claims": [{"citation": source["id"],
        "quote": source["text"], "kind": source["evidence_kind"]}]}, pdf_evidence)
    assert claims and not errors
    missing = answer("quasizebraunobtainium", index, use_llm=False)
    assert missing["insufficient"] and not missing["evidence"]

    before = {doc["sha256"]: storage.read_original(experiment, doc) for doc in experiment["documents"]}
    second = ingest_downloads(project, db_path, index_search=False)
    assert second["existing"] == len(expected_files) and second["imported"] == 0 and not second["errors"]
    assert len(storage.list_experiments()) == 1
    assert all(storage.read_original(experiment, doc) == before[doc["sha256"]] for doc in experiment["documents"])
    with store.connection() as db:
        assert db.execute("SELECT COUNT(*) FROM documents").fetchone()[0] == len(expected_files)
        assert db.execute("SELECT COUNT(*) FROM events").fetchone()[0] == len(expected_files)


@pytest.mark.integration
def test_every_downloaded_nasa_file_matches_recorded_sha256():
    checked = []
    for path in (ROOT / "data" / "psi_downloads").glob("PSI-*/source_manifest.json"):
        manifest = json.loads(path.read_text(encoding="utf-8"))
        for record in manifest.get("downloaded_csvs", []) + manifest.get("downloaded_pdfs", []):
            original = path.parent / record["filename"]
            assert original.is_file()
            assert hashlib.sha256(original.read_bytes()).hexdigest() == record["sha256"]
            assert original.stat().st_size == record["size_bytes"]
            checked.append(original)
    for sidecar in (ROOT / "resources" / "official").glob("*.provenance.json"):
        provenance = json.loads(sidecar.read_text(encoding="utf-8"))
        original = sidecar.with_name(sidecar.name.removesuffix(".provenance.json") + ".pdf")
        assert hashlib.sha256(original.read_bytes()).hexdigest() == provenance["sha256"]
        assert original.read_bytes().startswith(b"%PDF-")
        checked.append(original)
    if not checked:
        pytest.skip("NASA download files are not present")
    assert len(checked) >= 16
