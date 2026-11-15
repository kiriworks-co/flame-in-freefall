"""Background uploads/reprocessing synchronized with the NASA import worker.

Local uploads retain local provenance even when filed under a PSI investigation.
Only independently verified NASA download manifests establish NASA authorship.
"""
from __future__ import annotations

import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from . import storage
from .extractors import extract_document, validate_upload
from .pipeline import _IMPORT_LOCK, _portable_path
from .scientific_store import ScientificStore, dumps
from .units import observations_from_tables

_EXECUTOR = ThreadPoolExecutor(max_workers=1, thread_name_prefix="psi-local-files")
_ACTIVE_JOBS: set[str] = set()
MAX_BATCH_FILES = 100
MAX_BATCH_BYTES = 120 * 1024 * 1024


def _latest(experiment_id: str) -> dict[str, Any]:
    current = next((item for item in storage.list_experiments() if item["id"] == experiment_id), None)
    if current is None:
        raise ValueError("Experiment no longer exists in the local archive")
    return current


def _investigation(store: ScientificStore, experiment: dict[str, Any]) -> str:
    identifier = experiment.get("psi_id") or experiment["id"]
    store.upsert_investigation({"id": identifier, "internal_id": experiment["id"],
        "name": experiment["name"], "description": experiment.get("description", ""),
        "category": experiment.get("category", "Local"), "source_url": experiment.get("source_url"),
        "doi": experiment.get("doi")})
    return identifier


def _sync_document(store: ScientificStore, experiment: dict[str, Any], document: dict[str, Any],
                   extraction: dict[str, Any]) -> None:
    provenance = document.get("provenance") or {
        "source": "local_upload", "sha256": document["sha256"],
        "retrieved_utc": document.get("uploaded_at"), "evidence_kind": "unclassified",
        "license": "User-provided local file; no license asserted", "source_url": None, "doi": None}
    kind = document.get("evidence_kind") or provenance.get("classification") or "unclassified"
    if provenance.get("source") == "local_upload":
        kind = "unclassified"
    extraction.update(provenance=provenance, evidence_kind=kind)
    for table in extraction.get("tables", []):
        table["evidence_kind"] = kind
        table["field_classification"] = provenance.get("field_classification", [])
    extraction["observations"] = observations_from_tables(extraction.get("tables", []), kind)
    roles = {item["header"].strip(): item for item in provenance.get("field_classification", [])}
    for observation in extraction["observations"]:
        role = roles.get(observation["field"].strip())
        if role:
            observation["evidence_kind"] = role.get("role", observation["evidence_kind"])
            if role.get("warning"):
                observation.update(warning=role["warning"], normalized_value=None,
                                   normalized_unit=None, status="source_unit_ambiguous")
    document.update(provenance=provenance, evidence_kind=kind)
    storage._write_json(storage.extraction_file(experiment, document), extraction)
    storage.save_experiment(experiment)
    base = storage.experiment_dir(experiment)
    store.persist_document(experiment.get("psi_id") or experiment["id"], document, extraction,
        provenance, _portable_path(base / document["original_path"]), _portable_path(base / document["extraction_path"]))


def _index(index_search: bool, result: dict[str, Any]) -> None:
    if index_search:
        try:
            from .retrieval import RetrievalIndex
            result["index"] = RetrievalIndex().index_experiments()
        except Exception as error:  # worker records optional-model/index failures without losing originals
            result["errors"].append({"stage": "search_index", "error": str(error)})


def _worker(job_id: str, experiment_id: str, uploads: list[tuple[str, bytes]] | None,
            db_path: str | Path | None, index_search: bool,
            document_ids: list[str] | None = None, reextract: bool = False) -> None:
    store = ScientificStore(db_path)
    result: dict[str, Any] = {"imported": 0, "existing": 0, "synced": 0, "errors": []}
    try:
        with store.connection() as conn:
            conn.execute("UPDATE jobs SET status='running',started_at=? WHERE id=?", (storage.utc_now(), job_id))
        with _IMPORT_LOCK:
            # The queued snapshot is never written back: reload after obtaining
            # the shared lock so another worker's documents cannot be erased.
            experiment = _latest(experiment_id)
            _investigation(store, experiment)
            if uploads is not None:
                for index, (name, content) in enumerate(uploads):
                    try:
                        experiment = _latest(experiment_id)
                        validate_upload(name, content)
                        digest = storage.sha256_bytes(content)
                        document = next((d for d in experiment.get("documents", []) if d["sha256"] == digest), None)
                        if document is not None:
                            if not storage.verify_original(experiment, document):
                                raise ValueError("Existing original does not match its recorded SHA-256")
                            extraction = storage.load_extraction(experiment, document)
                            result["existing"] += 1
                        else:
                            extraction = extract_document(name, content)
                            document, _ = storage.save_document(experiment, name, content, extraction)
                            document["provenance"] = {"source": "local_upload", "sha256": digest,
                                "retrieved_utc": storage.utc_now(), "filename": document["name"],
                                "evidence_kind": "unclassified", "source_url": None, "doi": None,
                                "license": "User-provided local file; no license asserted"}
                            document["evidence_kind"] = "unclassified"
                            result["imported"] += 1
                        _sync_document(store, experiment, document, extraction)
                        result["synced"] += 1
                        if document.get("status") == "erro":
                            result["errors"].append({"filename": name, "stage": "extraction", "warnings": extraction.get("warnings", [])})
                    except Exception as error:
                        result["errors"].append({"filename": name, "error": str(error)})
                    with store.connection() as conn:
                        conn.execute("UPDATE jobs SET progress=? WHERE id=?", ((index + 1) / max(1, len(uploads)) * .85, job_id))
            else:
                documents = experiment.get("documents", [])
                targets = [d for d in documents if document_ids is None or d["id"] in document_ids]
                for document in targets:
                    try:
                        if not storage.verify_original(experiment, document):
                            raise ValueError("Original does not match its recorded SHA-256")
                        extraction = storage.reextract_document(experiment, document) if reextract else storage.load_extraction(experiment, document)
                        _sync_document(store, experiment, document, extraction)
                        result["synced"] += 1
                        if document.get("status") == "erro":
                            result["errors"].append({"filename": document["name"], "stage": "extraction", "warnings": extraction.get("warnings", [])})
                    except Exception as error:
                        result["errors"].append({"filename": document.get("name"), "error": str(error)})
            _index(index_search, result)
        with store.connection() as conn:
            conn.execute("UPDATE jobs SET status=?,finished_at=?,progress=1,result_json=? WHERE id=?",
                ("partial" if result["errors"] else "completed", storage.utc_now(), dumps(result), job_id))
    except Exception as error:
        with store.connection() as conn:
            conn.execute("UPDATE jobs SET status='failed',finished_at=?,error=? WHERE id=?", (storage.utc_now(), str(error), job_id))
    finally:
        _ACTIVE_JOBS.discard(job_id)


def _submit(experiment: dict[str, Any], uploads: list[tuple[str, bytes]] | None,
            db_path: str | Path | None, index_search: bool,
            document_ids: list[str] | None = None, reextract: bool = False) -> str:
    store = ScientificStore(db_path)
    job_id = uuid.uuid4().hex
    kind = f"{'Local upload' if uploads is not None else 'Archive refresh'}:{experiment['id']}"
    with store.connection() as conn:
        # A thread cannot survive a process restart. Only this worker's kind is
        # touched; concurrent NASA jobs retain their own state.
        for row in conn.execute("SELECT id FROM jobs WHERE kind=? AND status IN ('queued','running')", (kind,)).fetchall():
            if row["id"] not in _ACTIVE_JOBS:
                conn.execute("UPDATE jobs SET status='interrupted',finished_at=?,error='Local worker process restarted' WHERE id=?", (storage.utc_now(), row["id"]))
        conn.execute("INSERT INTO jobs(id,kind,status,created_at) VALUES (?,?,?,?)", (job_id, kind, "queued", storage.utc_now()))
    _ACTIVE_JOBS.add(job_id)
    _EXECUTOR.submit(_worker, job_id, experiment["id"], uploads, db_path, index_search, document_ids, reextract)
    return job_id


def enqueue_uploads(experiment: dict[str, Any], uploads: list[tuple[str, bytes]],
                    db_path: str | Path | None = None, index_search: bool = True) -> str:
    if not uploads:
        raise ValueError("Select at least one file")
    if len(uploads) > MAX_BATCH_FILES or sum(len(content) for _, content in uploads) > MAX_BATCH_BYTES:
        raise ValueError("Upload batch exceeds 100 files or 120 MiB")
    return _submit(experiment, list(uploads), db_path, index_search)


def enqueue_refresh_experiment(experiment: dict[str, Any], db_path: str | Path | None = None,
                               index_search: bool = True, document_ids: list[str] | None = None,
                               reextract: bool = False) -> str:
    """Synchronize existing extractions, optionally reextracting verified originals."""
    return _submit(experiment, None, db_path, index_search, document_ids, reextract)
