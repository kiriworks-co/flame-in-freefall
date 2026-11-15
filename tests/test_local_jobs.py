"""All uploaded files here are explicitly synthetic local QA fixtures."""
import json
import time

import pytest

from src import storage
from src.extractors import extract_document
from src.local_jobs import enqueue_refresh_experiment, enqueue_uploads
from src.pipeline import _IMPORT_LOCK, job_status
from src.scientific_store import ScientificStore


@pytest.fixture
def local_archive(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path / "archive")
    experiment = storage.create_experiment("Synthetic upload fixture")
    experiment.update(psi_id="PSI-999999", source_url="https://psi.nasa.gov/not-a-real-study", doi="10.0000/synthetic")
    storage.save_experiment(experiment)
    return experiment, tmp_path / "scientific.sqlite3"


def completed(job_id, db):
    for _ in range(300):
        status = job_status(job_id, db)
        if status["status"] in {"completed", "partial", "failed"}:
            return status
        time.sleep(.01)
    raise AssertionError("Background fixture job did not finish")


def current(experiment):
    return next(e for e in storage.list_experiments() if e["id"] == experiment["id"])


def test_background_upload_syncs_original_sqlite_observations_and_index(local_archive, monkeypatch):
    experiment, db = local_archive
    indexed = []
    from src import retrieval

    class FixtureIndex:
        def index_experiments(self):
            indexed.append(True)
            return {"fixture": True}

    monkeypatch.setattr(retrieval, "RetrievalIndex", FixtureIndex)
    content = b"Oxygen Mole Fraction,Flow Velocity (cm/s)\n0.21,2\n"
    status = completed(enqueue_uploads(experiment, [("synthetic.csv", content)], db), db)
    assert status["status"] == "completed", status
    assert indexed == [True]
    exp = current(experiment)
    doc = exp["documents"][0]
    assert storage.verify_original(exp, doc)
    assert doc["provenance"]["source"] == "local_upload"
    assert doc["provenance"]["source_url"] is None
    assert doc["provenance"]["doi"] is None
    assert doc["evidence_kind"] == "unclassified"
    store = ScientificStore(db)
    assert len(store.list_documents()) == 1
    assert all(o["evidence_kind"] == "unclassified" for o in store.observations())
    assert store.observations()[0]["normalized_value"] == .21
    duplicate = completed(enqueue_uploads(experiment, [("same-bytes.csv", content)], db, index_search=False), db)
    assert json.loads(duplicate["result_json"])["existing"] == 1
    assert len(current(experiment)["documents"]) == 1


def test_parser_failure_is_partial_but_original_preserved(local_archive):
    experiment, db = local_archive
    status = completed(enqueue_uploads(experiment, [("synthetic-invalid.pdf", b"invalid PDF fixture")], db, index_search=False), db)
    assert status["status"] == "partial"
    result = json.loads(status["result_json"])
    assert result["errors"][0]["stage"] == "extraction"
    exp = current(experiment)
    assert exp["documents"][0]["status"] == "erro"
    assert storage.verify_original(exp, exp["documents"][0])
    assert ScientificStore(db).list_documents()[0]["status"] == "erro"


def test_queued_snapshot_cannot_erase_later_document(local_archive):
    experiment, db = local_archive
    with _IMPORT_LOCK:
        job_id = enqueue_uploads(experiment, [("first.csv", b"A,B\n1,2\n")], db, index_search=False)
        later = current(experiment)
        content = b"C,D\n3,4\n"
        storage.save_document(later, "later.csv", content, extract_document("later.csv", content))
    assert completed(job_id, db)["status"] == "completed"
    assert len(current(experiment)["documents"]) == 2


def test_refresh_reextracts_and_preserves_official_provenance(local_archive):
    experiment, db = local_archive
    content = b"Oxygen Mole Fraction,Diameter (mm)\n0.3,2\n"
    doc, _ = storage.save_document(experiment, "synthetic-official-like.csv", content, extract_document("fixture.csv", content))
    doc["provenance"] = {"source": "SYNTHETIC TEST ONLY", "classification": "condition", "sha256": doc["sha256"]}
    doc["evidence_kind"] = "condition"
    storage.save_experiment(experiment)
    status = completed(enqueue_refresh_experiment(experiment, db, index_search=False, reextract=True), db)
    assert status["status"] == "completed"
    exp = current(experiment)
    assert storage.verify_original(exp, exp["documents"][0])
    assert exp["documents"][0]["provenance"]["source"] == "SYNTHETIC TEST ONLY"
    assert ScientificStore(db).observations()[0]["evidence_kind"] == "condition"


def test_invalid_upload_batch_is_rejected_before_queue(local_archive):
    experiment, db = local_archive
    with pytest.raises(ValueError, match="least one"):
        enqueue_uploads(experiment, [], db, index_search=False)
    with pytest.raises(ValueError, match="100 files"):
        enqueue_uploads(experiment, [("tiny.csv", b"a")]*101, db, index_search=False)
