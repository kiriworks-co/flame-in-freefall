"""Fixtures are synthetic unless explicitly loaded from downloaded NASA files."""
import hashlib
import io
import json
import time
import zipfile
from pathlib import Path

import pytest

from src import storage
from src.extractors import extract_document, validate_upload
from src.pipeline import enqueue_ingestion, ingest_downloads, job_status
from src.scientific_store import ScientificStore


@pytest.fixture
def fixture_project(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path / "archive")
    project = tmp_path / "project"
    directory = project / "data/psi_downloads/PSI-999999"
    directory.mkdir(parents=True)
    content = b"Fuel,Oxygen Mole Fraction,Velocity (cm/s)\nSynthetic fuel,0.21,2\n"
    (directory / "fixture.csv").write_bytes(content)
    manifest = {"investigation_id": "PSI-999999", "doi": "10.0000/synthetic-fixture",
                "downloaded_csvs": [{"filename": "fixture.csv", "sha256": hashlib.sha256(content).hexdigest(),
                                      "classification": "condition", "source_api_url": "https://psi.nasa.gov/fixture-only"}]}
    (directory / "source_manifest.json").write_text(json.dumps(manifest))
    return project, tmp_path / "registry.sqlite3"


def test_incremental_idempotency_sources_and_cells(fixture_project):
    project, db = fixture_project
    first = ingest_downloads(project, db, index_search=False)
    second = ingest_downloads(project, db, index_search=False)
    assert first["imported"] == 1 and not first["errors"]
    assert second["existing"] == 1 and second["imported"] == 0 and not second["errors"]
    store = ScientificStore(db)
    assert len(store.list_documents()) == 1
    with store.connection() as conn:
        assert conn.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM cells").fetchone()[0] == 6
        assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
    experiment = storage.list_experiments()[0]
    assert experiment["psi_id"] == "PSI-999999"
    assert storage.verify_original(experiment, experiment["documents"][0])
    assert store.observations()[1]["normalized_value"] == .21


def test_hash_mismatch_rejected(fixture_project):
    project, db = fixture_project
    (project / "data/psi_downloads/PSI-999999/fixture.csv").write_bytes(b"changed")
    result = ingest_downloads(project, db, index_search=False)
    assert result["imported"] == 0 and "SHA-256" in result["errors"][0]["error"]


def test_background_job_reaches_completed(fixture_project):
    project, db = fixture_project
    identifier = enqueue_ingestion(project, db, index_search=False)
    for _ in range(200):
        status = job_status(identifier, db)
        if status["status"] in {"completed", "failed", "partial"}:
            break
        time.sleep(.01)
    assert status["status"] == "completed", status
    assert status["progress"] == 1


def test_zip_traversal_and_expansion_rejected():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as archive:
        archive.writestr("../outside.xml", "fixture")
    with pytest.raises(ValueError, match="inseguro"):
        validate_upload("fixture.xlsx", buf.getvalue())
    bomb = io.BytesIO()
    with zipfile.ZipFile(bomb, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("word/document.xml", b"x" * (2 * 1024 * 1024))
    with pytest.raises(ValueError, match="compressão"):
        validate_upload("fixture.docx", bomb.getvalue())


def test_path_boundary_and_original_hash(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path / "archive")
    with pytest.raises(ValueError):
        storage.experiment_dir({"folder": "../escape"})
    exp = storage.create_experiment("Synthetic test")
    doc, _ = storage.save_document(exp, "../../fixture.csv", b"a,b\n1,2", extract_document("fixture.csv", b"a,b\n1,2"))
    assert storage.verify_original(exp, doc)
    original = storage.experiment_dir(exp) / doc["original_path"]
    original.write_bytes(b"tampered fixture")
    assert not storage.verify_original(exp, doc)


def test_real_nasa_csv_extraction_and_typed_evidence():
    root = Path(__file__).resolve().parents[1]
    files = list((root / "data/psi_downloads/PSI-69").glob("*.csv"))
    if not files:
        pytest.skip("Real NASA download not present; run collector")
    result = extract_document(files[0].name, files[0].read_bytes())
    assert result["status"] == "processado"
    assert "Visible flame extinction diameter; mm" in result["tables"][0]["columns"]
    assert result["tables"][0]["source_rows"][0] == 2


def test_real_nasa_pdf_layout_pages():
    root = Path(__file__).resolve().parents[1]
    files = list((root / "data/psi_downloads/PSI-69").glob("*.pdf"))
    if not files:
        pytest.skip("Real NASA PDF download not present; run collector --pdfs")
    result = extract_document(files[0].name, files[0].read_bytes())
    assert result["status"] in {"processado", "parcial"}
    assert result["pages"] and result["pages"][0]["page"] == 1
    assert any(p.get("blocks") for p in result["pages"])
