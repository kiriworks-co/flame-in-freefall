"""SQLite scientific registry complementing the backward-compatible JSON archive."""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from .storage import PROJECT_DIR, utc_now

DEFAULT_DB = PROJECT_DIR / "data" / "scientific.sqlite3"
SCHEMA_VERSION = 1

SCHEMA = """
CREATE TABLE IF NOT EXISTS schema_migrations(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS investigations(id TEXT PRIMARY KEY, internal_id TEXT, name TEXT NOT NULL,
 category TEXT, description TEXT, source_url TEXT, doi TEXT, version TEXT, metadata_json TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS sources(id TEXT PRIMARY KEY, investigation_id TEXT REFERENCES investigations(id),
 url TEXT, doi TEXT, retrieved_utc TEXT, license TEXT, provenance_json TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS documents(id TEXT PRIMARY KEY, investigation_id TEXT NOT NULL REFERENCES investigations(id),
 sha256 TEXT NOT NULL, filename TEXT NOT NULL, size_bytes INTEGER NOT NULL, extension TEXT, original_path TEXT,
 extraction_path TEXT, status TEXT, source_id TEXT REFERENCES sources(id), metadata_json TEXT NOT NULL,
 UNIQUE(investigation_id,sha256));
CREATE TABLE IF NOT EXISTS document_versions(document_id TEXT REFERENCES documents(id),version TEXT,sha256 TEXT,
 metadata_json TEXT, PRIMARY KEY(document_id,version));
CREATE TABLE IF NOT EXISTS pages(document_id TEXT REFERENCES documents(id),page_number INTEGER,text TEXT,
 location TEXT,method TEXT,metadata_json TEXT,PRIMARY KEY(document_id,page_number));
CREATE TABLE IF NOT EXISTS regions(id TEXT PRIMARY KEY,document_id TEXT REFERENCES documents(id),page_number INTEGER,
 kind TEXT,bbox_json TEXT,text TEXT,metadata_json TEXT);
CREATE TABLE IF NOT EXISTS scientific_tables(id TEXT PRIMARY KEY,document_id TEXT REFERENCES documents(id),table_index INTEGER,
 name TEXT,location TEXT,evidence_kind TEXT,metadata_json TEXT,UNIQUE(document_id,table_index));
CREATE TABLE IF NOT EXISTS cells(table_id TEXT REFERENCES scientific_tables(id),row_number INTEGER,column_index INTEGER,
 header TEXT,is_header INTEGER,raw_json TEXT,PRIMARY KEY(table_id,row_number,column_index,is_header));
CREATE TABLE IF NOT EXISTS observations(id TEXT PRIMARY KEY,document_id TEXT REFERENCES documents(id),
 investigation_id TEXT REFERENCES investigations(id),table_index INTEGER,row_number INTEGER,column_index INTEGER,
 field TEXT,quantity TEXT,value REAL,unit TEXT,normalized_value REAL,normalized_unit TEXT,reference TEXT,
 evidence_kind TEXT,status TEXT,raw_json TEXT,metadata_json TEXT);
CREATE INDEX IF NOT EXISTS observations_numeric ON observations(quantity,normalized_unit,normalized_value);
CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT,investigation_id TEXT,document_id TEXT,
 kind TEXT,created_at TEXT,payload_json TEXT);
CREATE TABLE IF NOT EXISTS chunks(id TEXT PRIMARY KEY,document_id TEXT REFERENCES documents(id),
 text TEXT,location TEXT,metadata_json TEXT);
CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY,kind TEXT,status TEXT,created_at TEXT,started_at TEXT,
 finished_at TEXT,progress REAL NOT NULL DEFAULT 0,result_json TEXT,error TEXT);
CREATE TABLE IF NOT EXISTS analysis_results(id TEXT PRIMARY KEY,investigation_id TEXT,kind TEXT,
 created_at TEXT,result_json TEXT);
"""


def dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, default=str)


class ScientificStore:
    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path or DEFAULT_DB)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as conn:
            conn.executescript(SCHEMA)
            conn.execute("INSERT OR IGNORE INTO schema_migrations VALUES (?,?)", (SCHEMA_VERSION, utc_now()))

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA journal_mode=WAL")
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def list_investigations(self) -> list[dict[str, Any]]:
        with self.connection() as conn:
            return [dict(r) for r in conn.execute("SELECT i.*,COUNT(d.id) document_count FROM investigations i LEFT JOIN documents d ON d.investigation_id=i.id GROUP BY i.id ORDER BY i.id")]

    def list_documents(self, investigation_id: str | None = None) -> list[dict[str, Any]]:
        with self.connection() as conn:
            return [dict(r) for r in conn.execute("SELECT * FROM documents" + (" WHERE investigation_id=?" if investigation_id else ""), (investigation_id,) if investigation_id else ())]

    def observations(self, investigation_id: str | None = None) -> list[dict[str, Any]]:
        with self.connection() as conn:
            return [dict(r) for r in conn.execute("SELECT * FROM observations" + (" WHERE investigation_id=?" if investigation_id else ""), (investigation_id,) if investigation_id else ())]

    def jobs(self) -> list[dict[str, Any]]:
        with self.connection() as conn:
            return [dict(r) for r in conn.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT 30")]

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        with self.connection() as conn:
            row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
            return dict(row) if row else None

    def upsert_investigation(self, record: dict[str, Any]) -> None:
        with self.connection() as conn:
            conn.execute("""INSERT INTO investigations VALUES (?,?,?,?,?,?,?,?,?,?)
              ON CONFLICT(id) DO UPDATE SET internal_id=COALESCE(excluded.internal_id,investigations.internal_id),
              name=excluded.name,category=excluded.category,description=excluded.description,
              source_url=excluded.source_url,doi=excluded.doi,version=excluded.version,
              metadata_json=excluded.metadata_json,updated_at=excluded.updated_at""",
              (record["id"], record.get("internal_id"), record.get("name", record["id"]), record.get("category"),
               record.get("description", ""), record.get("source_url"), record.get("doi"), str(record.get("version", "")),
               dumps(record), utc_now()))

    def persist_document(self, investigation_id: str, document: dict[str, Any], extraction: dict[str, Any],
                         provenance: dict[str, Any], original_path: str, extraction_path: str) -> bool:
        digest = document["sha256"]
        doc_id = f"{investigation_id}:{digest}"
        with self.connection() as conn:
            existed = conn.execute("SELECT 1 FROM documents WHERE id=?", (doc_id,)).fetchone() is not None
            source_id = doc_id
            conn.execute("INSERT OR REPLACE INTO sources VALUES (?,?,?,?,?,?,?)", (source_id, investigation_id,
                provenance.get("source_api_url") or provenance.get("source_url") or provenance.get("landing_page"),
                provenance.get("doi"), provenance.get("retrieved_utc"), provenance.get("license", "Not specified; consult NASA source"), dumps(provenance)))
            conn.execute("""INSERT INTO documents VALUES (?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET
                 status=excluded.status,source_id=excluded.source_id,metadata_json=excluded.metadata_json""",
                 (doc_id, investigation_id, digest, document["name"], document["size_bytes"], document.get("extension"),
                  original_path, extraction_path, document.get("status"), source_id, dumps(extraction.get("metadata", {}))))
            version = str(provenance.get("file_version", provenance.get("study_version", "unspecified")))
            conn.execute("INSERT OR REPLACE INTO document_versions VALUES (?,?,?,?)", (doc_id, version, digest, dumps(provenance)))
            # This transaction replaces derived rows; immutable source bytes stay in storage.
            for name in ("pages", "regions", "observations", "chunks"):
                conn.execute(f"DELETE FROM {name} WHERE document_id=?", (doc_id,))
            conn.execute("DELETE FROM cells WHERE table_id IN (SELECT id FROM scientific_tables WHERE document_id=?)", (doc_id,))
            conn.execute("DELETE FROM scientific_tables WHERE document_id=?", (doc_id,))
            for index, page in enumerate(extraction.get("pages", []), 1):
                number = page.get("page", index)
                conn.execute("INSERT INTO pages VALUES (?,?,?,?,?,?)", (doc_id, number, page.get("text", ""), page.get("location", ""), page.get("method", "source text"), dumps(page)))
                for region_index, block in enumerate(page.get("blocks", [])):
                    conn.execute("INSERT INTO regions VALUES (?,?,?,?,?,?,?)", (f"{doc_id}:p{number}:b{region_index}", doc_id, number, block.get("kind", "text"), dumps(block.get("bbox")), block.get("text", ""), dumps(block)))
            for index, caption in enumerate(extraction.get("captions", [])):
                conn.execute("INSERT INTO regions VALUES (?,?,?,?,?,?,?)", (f"{doc_id}:caption{index}", doc_id, caption.get("page"), caption.get("kind", "caption"), dumps(caption.get("bbox")), caption.get("text", ""), dumps(caption)))
            for table_index, table in enumerate(extraction.get("tables", [])):
                table_id = f"{doc_id}:t{table_index}"
                conn.execute("INSERT INTO scientific_tables VALUES (?,?,?,?,?,?,?)", (table_id, doc_id, table_index, table.get("name"), table.get("location"), table.get("evidence_kind", "unclassified"), dumps({k:v for k,v in table.items() if k != "rows"})))
                for col, header in enumerate(table.get("original_headers", table.get("columns", []))):
                    conn.execute("INSERT INTO cells VALUES (?,?,?,?,?,?)", (table_id, table.get("header_row") or 0, col, str(header), 1, dumps(header)))
                for row_index, row in enumerate(table.get("rows", [])):
                    numbers = table.get("source_rows", [])
                    source_row = numbers[row_index] if row_index < len(numbers) else row_index + 2
                    for col, value in enumerate(row):
                        headers = table.get("columns", [])
                        conn.execute("INSERT INTO cells VALUES (?,?,?,?,?,?)", (table_id, source_row, col, headers[col] if col < len(headers) else "", 0, dumps(value)))
            for index, obs in enumerate(extraction.get("observations", [])):
                conn.execute("INSERT INTO observations VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
                    f"{doc_id}:o{index}", doc_id, investigation_id, obs.get("table_index"), obs.get("row_number"), obs.get("column_index"),
                    obs.get("field"), obs.get("quantity"), obs.get("value"), obs.get("unit"), obs.get("normalized_value"), obs.get("normalized_unit"), obs.get("reference"), obs.get("evidence_kind"), obs.get("status"), dumps(obs.get("raw_value")), dumps(obs),))
            if not existed:
                conn.execute("INSERT INTO events(investigation_id,document_id,kind,created_at,payload_json) VALUES (?,?,?,?,?)", (investigation_id, doc_id, "ingested", utc_now(), dumps({"sha256": digest})))
        return existed
