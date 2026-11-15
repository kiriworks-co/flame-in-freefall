"""Incremental import of verified NASA downloads into legacy storage and SQLite.

The worker is a real background thread. A restart retains job history; a new
submission explicitly marks abandoned running jobs interrupted.
"""
from __future__ import annotations

import json
import os
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from . import storage
from .extractors import MAX_UPLOAD_BYTES, SCHEMA_VERSION, SUPPORTED_EXTENSIONS, extract_document
from .scientific_store import ScientificStore, dumps
from .units import observations_from_tables

_EXECUTOR = ThreadPoolExecutor(max_workers=1, thread_name_prefix="psi-ingestion")
_IMPORT_LOCK = threading.Lock()
_ACTIVE_JOBS: set[str] = set()


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _portable_path(path: Path) -> str:
    """Return a repository-relative POSIX path when inside PROJECT_DIR."""
    try:
        return path.resolve().relative_to(storage.PROJECT_DIR.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _safe_local(base: Path, filename: str) -> Path:
    candidate = (base / filename).resolve()
    if not candidate.is_relative_to(base.resolve()) or not candidate.is_file():
        raise ValueError("Download path is outside its source directory or unavailable")
    return candidate


def _experiment(study: dict[str, Any], experiments: list[dict[str, Any]]) -> dict[str, Any]:
    study_id = study["id"]
    record = next((e for e in experiments if e.get("psi_id") == study_id), None)
    if record is None:
        record = storage.create_experiment(f"{study_id} · {study.get('name', study_id)}", study.get("description", ""))
        experiments.append(record)
    record.update(psi_id=study_id, investigation_id=study_id, study_id=study_id,
                  source_url=study.get("source_url") or study.get("nasa_record_url"),
                  doi=study.get("doi"), category=study.get("category", "Contexto"))
    storage.save_experiment(record)
    return record


def _import_file(store: ScientificStore, experiment: dict[str, Any], path: Path,
                 provenance: dict[str, Any], evidence_kind: str) -> tuple[bool, dict[str, Any]]:
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported source file: {path.name}")
    if path.stat().st_size > MAX_UPLOAD_BYTES:
        raise ValueError(f"Source exceeds the 30 MiB ingestion limit: {path.name}")
    content = path.read_bytes()
    digest = storage.sha256_bytes(content)
    if not provenance.get("sha256") or digest != provenance["sha256"]:
        raise ValueError(f"SHA-256 mismatch or missing source hash: {path.name}")
    existing = next((d for d in experiment.get("documents", []) if d.get("sha256") == digest), None)
    if existing and existing.get("schema_version") == SCHEMA_VERSION:
        if not storage.verify_original(experiment, existing):
            raise ValueError(f"Archived original hash mismatch: {path.name}")
        extraction = storage.load_extraction(experiment, existing)
        document = existing
        already = True
    else:
        extraction = extract_document(path.name, content)
        if existing:
            storage.reextract_document(experiment, existing)
            document = existing
            already = True
        else:
            document, already = storage.save_document(experiment, path.name, content, extraction)
    extraction["evidence_kind"] = evidence_kind
    for table in extraction.get("tables", []):
        table["evidence_kind"] = evidence_kind
        table["field_classification"] = provenance.get("field_classification", [])
    extraction["observations"] = observations_from_tables(extraction.get("tables", []), evidence_kind)
    field_roles = {item["header"].strip(): item for item in provenance.get("field_classification", [])}
    for observation in extraction["observations"]:
        role = field_roles.get(observation["field"].strip())
        if role:
            observation["evidence_kind"] = role.get("role", observation["evidence_kind"])
            if role.get("warning"):
                observation["warning"] = role["warning"]
                observation["normalized_value"] = None
                observation["normalized_unit"] = None
                observation["status"] = "source_unit_ambiguous"
    extraction["provenance"] = provenance
    document["provenance"] = provenance
    document["evidence_kind"] = evidence_kind
    # Source original stays immutable; only the extraction is refreshed.
    storage._write_json(storage.extraction_file(experiment, document), extraction)
    storage.save_experiment(experiment)
    base = storage.experiment_dir(experiment)
    store.persist_document(
        experiment["psi_id"],
        document,
        extraction,
        provenance,
        _portable_path(base / document["original_path"]),
        _portable_path(base / document["extraction_path"]),
    )
    return already, document


def ingest_downloads(project_dir: str | Path | None = None, db_path: str | Path | None = None,
                     index_search: bool = True) -> dict[str, Any]:
    """Import every local verified manifest; per-file failures do not hide successes.

    This function does no network I/O. Run fetch scripts first. Catalog DOI
    candidates are never promoted to confirmed DOI values.
    """
    project = Path(project_dir or storage.PROJECT_DIR)
    result: dict[str, Any] = {"imported": 0, "existing": 0, "errors": [], "investigations": 0, "documents": []}
    with _IMPORT_LOCK:
        store = ScientificStore(db_path)
        catalog_path = project / "resources" / "manifests" / "priority_investigations.json"
        catalog = _json(catalog_path).get("investigations", []) if catalog_path.is_file() else []
        studies = {item["id"]: dict(item) for item in catalog}
        experiments = storage.list_experiments()
        for source_manifest in sorted((project / "data" / "psi_downloads").glob("PSI-*/source_manifest.json")):
            try:
                manifest = _json(source_manifest)
                study_id = manifest.get("investigation_id") or source_manifest.parent.name
                study = studies.setdefault(study_id, {"id": study_id, "name": study_id})
                if manifest.get("doi"):
                    study["doi"] = manifest["doi"]
                study["version"] = manifest.get("study_version") or manifest.get("version")
                study["source_url"] = f"https://psi.nasa.gov/physci/repo/data/investigations/{study_id}"
                study["source_manifest"] = str(source_manifest.relative_to(project))
                files = manifest.get("downloaded_csvs", []) + manifest.get("downloaded_documents", []) + manifest.get("downloaded_pdfs", [])
                # Files can carry the confirmed DOI even when the manifest has no summary.
                doi = next((r.get("doi") for r in files if r.get("doi")), None)
                if doi:
                    study["doi"] = doi
                experiment = _experiment(study, experiments) if files else None
                store.upsert_investigation({**study, "internal_id": experiment["id"] if experiment else None})
                for record in files:
                    try:
                        assert experiment is not None
                        path = _safe_local(source_manifest.parent, record["filename"])
                        classification = record.get("classification", "condition")
                        if classification not in {"condition", "sample", "measurement", "context", "unclassified", "mixed_conditions_and_reported_results", "engineering_or_publication"}:
                            classification = "unclassified"
                        already, document = _import_file(store, experiment, path, record, classification)
                        result["existing" if already else "imported"] += 1
                        result["documents"].append({"study_id": study_id, "filename": path.name, "sha256": document["sha256"]})
                        if document.get("status") == "erro":
                            result["errors"].append({"study_id": study_id, "filename": path.name,
                                                     "error": "Original preservado; extração falhou. Consulte os avisos do documento."})
                    except Exception as exc:
                        result["errors"].append({"study_id": study_id, "filename": record.get("filename"), "error": str(exc)})
            except Exception as exc:
                result["errors"].append({"manifest": str(source_manifest), "error": str(exc)})
        # Context publications are deliberately kept separate from experimental PSI data.
        context = {"id": "NASA-CONTEXT", "name": "Guias oficiais NASA", "category": "Contexto",
                   "source_url": "https://psi.nasa.gov/", "description": "Documentação e fundamentos; não contém novas medições deste dashboard."}
        for sidecar in sorted((project / "resources" / "official").glob("*.provenance.json")):
            try:
                provenance = _json(sidecar)
                path = sidecar.with_name(sidecar.name.removesuffix(".provenance.json") + ".pdf")
                if not path.is_file():
                    continue
                experiment = _experiment(context, experiments)
                store.upsert_investigation({**context, "internal_id": experiment["id"]})
                already, document = _import_file(store, experiment, path, provenance, "context")
                result["existing" if already else "imported"] += 1
                result["documents"].append({"study_id": context["id"], "filename": path.name, "sha256": document["sha256"]})
                if document.get("status") == "erro":
                    result["errors"].append({"study_id": context["id"], "filename": path.name,
                                             "error": "Original preservado; extração falhou. Consulte os avisos do documento."})
            except Exception as exc:
                result["errors"].append({"manifest": str(sidecar), "error": str(exc)})
        for study in studies.values():
            # Keep already-imported metadata rather than dropping its internal ID.
            store.upsert_investigation(study)
        result["investigations"] = len(store.list_investigations())
        if index_search:
            try:
                from .retrieval import RetrievalIndex
                result["index"] = RetrievalIndex().index_experiments()
            except ImportError:
                result["index_warning"] = "Search adapter not yet installed; reindex from the dashboard."
            except Exception as exc:
                result["errors"].append({"stage": "search_index", "error": str(exc)})
    return result


def _worker(job_id: str, project_dir: str | Path | None, db_path: str | Path | None, index_search: bool) -> None:
    store = ScientificStore(db_path)
    try:
        with store.connection() as conn:
            conn.execute("UPDATE jobs SET status='running',started_at=?,progress=0.05 WHERE id=?", (storage.utc_now(), job_id))
        result = ingest_downloads(project_dir, db_path, index_search)
        with store.connection() as conn:
            conn.execute("UPDATE jobs SET status=?,finished_at=?,progress=1,result_json=? WHERE id=?",
                         ("partial" if result["errors"] else "completed", storage.utc_now(), dumps(result), job_id))
    except Exception as exc:
        with store.connection() as conn:
            conn.execute("UPDATE jobs SET status='failed',finished_at=?,error=? WHERE id=?", (storage.utc_now(), str(exc), job_id))
    finally:
        _ACTIVE_JOBS.discard(job_id)


def enqueue_ingestion(project_dir: str | Path | None = None, db_path: str | Path | None = None,
                      index_search: bool = True) -> str:
    store = ScientificStore(db_path)
    # Avoid submitting duplicate imports from repeated button presses.
    for job in store.jobs():
        if job["status"] in {"queued", "running"} and job["id"] in _ACTIVE_JOBS:
            return job["id"]
    with store.connection() as conn:
        conn.execute("UPDATE jobs SET status='interrupted',finished_at=?,error='Worker process restarted' WHERE kind='NASA import' AND status IN ('queued','running')", (storage.utc_now(),))
        job_id = uuid.uuid4().hex
        conn.execute("INSERT INTO jobs(id,kind,status,created_at) VALUES (?,?,?,?)", (job_id, "NASA import", "queued", storage.utc_now()))
    _ACTIVE_JOBS.add(job_id)
    _EXECUTOR.submit(_worker, job_id, project_dir, db_path, index_search)
    return job_id


def job_status(job_id: str, db_path: str | Path | None = None) -> dict[str, Any] | None:
    return ScientificStore(db_path).get_job(job_id)


def is_public_readonly() -> bool:
    """Return True when running in a public/cloud read-only deployment."""
    flag = os.getenv("PSI_READONLY_MODE", "").strip().lower()
    if flag in {"1", "true", "yes", "on"}:
        return True
    if flag in {"0", "false", "no", "off"}:
        return False
    if os.getenv("STREAMLIT_SHARING_MODE", "").strip():
        return True
    return Path("/mount/src").exists()


def ensure_scientific_bootstrap(
    project_dir: str | Path | None = None,
    db_path: str | Path | None = None,
    search_db_path: str | Path | None = None,
) -> dict[str, Any]:
    """Initialize SQLite stores and search index on cold start if missing or empty."""
    from .retrieval import RetrievalIndex

    store = ScientificStore(db_path)
    experiments = storage.list_experiments()
    docs_in_db = store.list_documents()
    ingest_result: dict[str, Any] | None = None
    bootstrapped = False

    if not experiments or not docs_in_db:
        ingest_result = ingest_downloads(project_dir, db_path, index_search=False)
        experiments = storage.list_experiments()
        bootstrapped = True

    index = RetrievalIndex(search_db_path)
    with index.connect() as db:
        chunk_count = int(db.execute("SELECT COUNT(*) FROM chunks").fetchone()[0])

    index_result: dict[str, Any] | None = None
    if chunk_count == 0 and experiments:
        index_result = index.index_experiments(experiments)
        chunk_count = int(index_result.get("total", 0))
        bootstrapped = True

    return {
        "bootstrapped": bootstrapped,
        "status": "bootstrapped" if bootstrapped else "ready",
        "chunks": chunk_count,
        "experiments": len(experiments),
        "ingest": ingest_result,
        "index": index_result,
    }
