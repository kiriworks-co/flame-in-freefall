"""Persistent, source-addressable FTS5/vector retrieval; no external service needed.

The default vector representation is lexical feature hashing with PT/EN synonyms,
NOT a learned semantic embedding. Set RAG_EMBEDDING_MODEL to a downloaded local
SentenceTransformer directory to enable learned multilingual/scientific vectors.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sqlite3
from collections.abc import Callable
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from .search import _SYN, _tokens

PROJECT = Path(__file__).resolve().parents[1]
MAX_CHUNK_CHARS = 1500
# A lexical-free match needs substantially stronger support than an anchored
# passage. On the real local multilingual corpus, an invented out-of-domain
# token scored 0.493 against technical fragments: 0.35 admitted false evidence.
# This conservative relevance gate is not a calibrated answer-confidence score.
MIN_SEMANTIC_ONLY_COSINE = 0.60


def _model_mode_id(resolved_model: str) -> str:
    """Return a portable model identifier free of user-specific parent directories."""
    return "local-semantic:" + Path(resolved_model).name


@lru_cache(maxsize=2)
def _load_local_model(model_path: str):
    """Reuse immutable model weights across Streamlit reruns in one process."""
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(model_path, local_files_only=True, trust_remote_code=False)


def safe_source_url(value: str | None) -> str:
    """Allow permanent HTTPS references, never executable or signed URLs."""
    try:
        parts = urlsplit(str(value or ""))
        if parts.scheme != "https" or not parts.hostname or parts.username or parts.password:
            return ""
        if re.search(r"(?i)(signature|credential|token|x-amz|x-goog)", parts.query):
            return ""
        return urlunsplit(parts)
    except ValueError:
        return ""


def _vector(text: str) -> dict[str, float]:
    counts: dict[str, float] = {}
    for token in _tokens(text):
        key = min(_SYN.get(token, {token}))
        # Stable cryptographic hashing, unlike Python's randomized hash().
        key = str(int.from_bytes(hashlib.sha256(key.encode()).digest()[:4], "little") % 8192)
        counts[key] = counts.get(key, 0) + 1
    norm = math.sqrt(sum(v * v for v in counts.values())) or 1
    return {k: v / norm for k, v in counts.items()}


def _dot(left: dict[str, float], right: dict[str, float]) -> float:
    return sum(v * right.get(k, 0) for k, v in left.items())


def _parts(text: str, limit: int = MAX_CHUNK_CHARS):
    """Split within the enclosing page/section, preferentially at paragraph ends."""
    text = str(text).strip()
    offset = 0
    while text:
        end = min(limit, len(text))
        if end < len(text):
            split = max(text.rfind("\n", limit // 2, end), text.rfind(". ", limit // 2, end))
            if split > 0:
                end = split + 1
        yield text[:end].strip(), offset, offset + end
        text = text[end:]
        offset += end


def structural_chunks(experiment: dict, document: dict, extraction: dict) -> list[dict]:
    """Build chunks with immutable file identity and exact page/table row scope."""
    provenance = document.get("provenance", {}) or {}
    study_id = str(experiment.get("psi_id") or experiment.get("investigation_id") or experiment.get("study_id") or experiment["id"])
    local_upload = provenance.get("source") == "local_upload" or not provenance
    source = "" if local_upload else safe_source_url(provenance.get("landing_page") or provenance.get("source_url") or experiment.get("source_url"))
    doi = "" if local_upload else str(provenance.get("doi") or experiment.get("doi") or "")
    if doi.startswith("https://doi.org/"):
        doi = doi.removeprefix("https://doi.org/")
    if not re.fullmatch(r"10\.\d{4,9}/[^\s<>]+", doi):
        doi = ""
    common = {"study_id": study_id, "investigation_name": experiment.get("name", ""), "experiment_id": experiment["id"], "document_name": document["name"],
              "document_id": document["id"], "sha256": document["sha256"], "source_url": source, "doi": doi,
              "source_member": provenance.get("archive_member", provenance.get("source_member", "")),
              "nested_member": provenance.get("nested_member", ""),
              "parent_archive_sha256": provenance.get("parent_archive_sha256", ""),
              "classification_basis": provenance.get("classification_basis") or provenance.get("classification_note", ""),
              "evidence_kind": provenance.get("evidence_kind", extraction.get("evidence_kind", "document_context"))}
    result = []

    def add(text: str, **where):
        for part, start, end in _parts(text):
            if not part:
                continue
            identity = json.dumps([study_id, document["sha256"], where, start, part], sort_keys=True, ensure_ascii=False)
            result.append({**common, **where, "id": hashlib.sha256(identity.encode()).hexdigest(),
                           "text": part, "char_start": start, "char_end": end})

    for page in extraction.get("pages", []):
        add(page.get("text", ""), kind="page", page=page.get("page"), location=page.get("location", ""),
            section=page.get("section", ""), observations=[])
    for caption in extraction.get("captions", []):
        add(caption.get("text", ""), kind="caption", page=caption.get("page"),
            location=f"página {caption.get('page')}, {caption.get('kind')} {caption.get('number')}", observations=[])
    observations_by_row: dict[tuple, list[dict]] = {}
    for observation in extraction.get("observations", []):
        key = (observation.get("table_index"), observation.get("row_number"))
        observations_by_row.setdefault(key, []).append(observation)
    for ti, table in enumerate(extraction.get("tables", [])):
        columns = table.get("columns", [])
        row_numbers = table.get("source_rows", table.get("row_numbers", []))
        for ri, row in enumerate(table.get("rows", [])):
            rn = row_numbers[ri] if ri < len(row_numbers) else (table.get("header_row") or 1) + ri + 1
            observations = observations_by_row.get((ti, rn), [])
            add(" | ".join(f"{col}: {row[j] if j < len(row) else ''}" for j, col in enumerate(columns)),
                kind="table_row", page=table.get("page"), table_index=ti, row_number=rn,
                location=f"{table.get('location', table.get('name', 'tabela'))}; linha {rn}",
                observations=observations,
                field_classification=table.get("field_classification", []),
                source_column_indices=table.get("source_column_indices", []),
                evidence_kind=table.get("evidence_kind", common["evidence_kind"]))
    return result


def _matches_observation(obs: dict, constraint: dict) -> bool:
    field = constraint["field"]
    names = {str(obs.get("field", "")).casefold(), str(obs.get("quantity", "")).casefold()}
    aliases = {"oxygen_fraction": {"oxygen_fraction", "o2", "oxygen", "oxygen_concentration"},
               "velocity": {"velocity", "speed", "flow_velocity"}, "fuel": {"fuel", "combustivel"}}
    if not names.intersection(aliases.get(field, {field.casefold()})):
        return False
    if constraint.get("reference") and obs.get("reference") != constraint["reference"]:
        return False
    if constraint.get("evidence_kind") and obs.get("evidence_kind") != constraint["evidence_kind"]:
        return False
    if "value" in constraint:
        return str(obs.get("raw_value", obs.get("value", ""))).casefold() == str(constraint["value"]).casefold()
    # Ranges/uncertainties do not become fabricated exact numbers.
    if obs.get("status") in {"range", "qualitative", "missing", "uncertain"}:
        return False
    requested_unit = constraint.get("unit")
    if requested_unit and requested_unit == obs.get("normalized_unit"):
        value = obs.get("normalized_value")
    elif not requested_unit or requested_unit == obs.get("unit"):
        value = obs.get("value")
    else:
        return False
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
        return False
    return (constraint.get("min") is None or value >= constraint["min"]) and (constraint.get("max") is None or value <= constraint["max"])


def matches_numeric_filters(chunk: dict, filters: list[dict] | None) -> bool:
    return all(any(_matches_observation(o, c) for o in chunk.get("observations", [])) for c in (filters or []))


class RetrievalIndex:
    def __init__(self, db_path: Path | str | None = None):
        self.db_path = Path(db_path or PROJECT / "data" / "search.sqlite3")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.model = None
        self.mode = "lexical-vectors"
        self.warnings: list[str] = []
        model_path = os.getenv("RAG_EMBEDDING_MODEL", "").strip()
        if model_path:
            if Path(model_path).is_dir():
                try:
                    resolved_model = str(Path(model_path).resolve())
                    self.model = _load_local_model(resolved_model)
                    self.mode = _model_mode_id(resolved_model)
                except Exception as error:  # noqa: BLE001 - optional model backends raise heterogeneous dependency errors
                    self.warnings.append(f"Modelo local indisponível: {type(error).__name__}; busca lexical ativa.")
            else:
                self.warnings.append("RAG_EMBEDDING_MODEL deve apontar para um diretório local existente.")
        with self.connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS chunks (id TEXT PRIMARY KEY,payload TEXT NOT NULL,vector TEXT NOT NULL,model TEXT NOT NULL)")
            db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(id UNINDEXED,text, tokenize='unicode61 remove_diacritics 2')")
            if self.model is not None and self.mode.startswith("local-semantic:"):
                suffix = self.mode.split(":", 1)[1]
                db.execute(
                    "UPDATE chunks SET model=? WHERE (model LIKE ? OR model LIKE ?) AND model != ?",
                    (self.mode, f"local-semantic:%/{suffix}", f"local-semantic:%\\{suffix}", self.mode),
                )

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.db_path, timeout=30)
        try:
            db.execute("PRAGMA journal_mode=WAL")
            with db:
                yield db
        finally:
            db.close()

    def _encode(self, text: str) -> dict[str, float]:
        if self.model is not None:
            vector = self.model.encode(text, normalize_embeddings=True)
            return {str(i): float(v) for i, v in enumerate(vector)}
        return _vector(text)

    def _encode_batch(self, texts: list[str], batch_size: int = 64) -> list[dict[str, float]]:
        if self.model is None:
            return [_vector(text) for text in texts]
        vectors = self.model.encode(texts, normalize_embeddings=True, batch_size=batch_size,
                                    show_progress_bar=False, convert_to_numpy=True)
        if len(vectors) != len(texts):
            raise ValueError("Embedding batch returned an unexpected vector count")
        return [{str(i): float(value) for i, value in enumerate(vector)} for vector in vectors]

    def _model_chunks(self, chunk: dict) -> list[dict]:
        """Split on tokenizer offsets so model truncation cannot discard evidence.

        Overlap preserves boundary context; char spans still address the original
        page/row, and full text remains in FTS. No measured values are inferred.
        """
        tokenizer = getattr(self.model, "tokenizer", None)
        if tokenizer is None:
            return [chunk]
        max_tokens = int(getattr(self.model, "max_seq_length", 128))
        special_tokens = tokenizer.num_special_tokens_to_add(pair=False)
        budget = max_tokens - special_tokens
        if budget < 8:
            raise ValueError("Model token budget too small for scientific evidence")
        try:
            offsets = tokenizer(chunk["text"], add_special_tokens=False, return_offsets_mapping=True,
                                truncation=False)["offset_mapping"]
        except (NotImplementedError, KeyError) as error:
            raise ValueError("Local embedding tokenizer must expose exact token offsets") from error
        if len(offsets) <= budget:
            return [chunk]
        overlap = min(16, budget // 4)
        result = []
        first = 0
        while first < len(offsets):
            last = min(first + budget, len(offsets))
            start, end = offsets[first][0], offsets[last - 1][1]
            text = chunk["text"][start:end]
            # Slicing at a subword boundary can retokenize the leading fragment
            # into additional tokens. Validate the actual substring, not just
            # the original token count, before it reaches model.encode().
            token_count = len(tokenizer(text, add_special_tokens=True, truncation=False)["input_ids"])
            while token_count > max_tokens and last > first + 1:
                last -= 1
                end = offsets[last - 1][1]
                text = chunk["text"][start:end]
                token_count = len(tokenizer(text, add_special_tokens=True, truncation=False)["input_ids"])
            if token_count > max_tokens:
                raise ValueError("Source substring cannot fit the model token budget")
            identity = f"{chunk['id']}:{start}:{end}:token-split-v1"
            result.append({**chunk, "id": hashlib.sha256(identity.encode()).hexdigest(), "text": text,
                           "char_start": chunk.get("char_start", 0) + start,
                           "char_end": chunk.get("char_start", 0) + end,
                           "token_count": token_count - special_tokens})
            if last == len(offsets):
                break
            first = max(first + 1, last - overlap)
        return result

    def index_experiments(self, experiments: list[dict] | None = None,
                          progress: Callable[[dict], None] | None = None, batch_size: int = 64) -> dict:
        """Encode batches before one atomic commit; failures preserve the old index.

        ``progress`` receives stage, completed and total counts. No slow model
        work holds a SQLite write transaction or hides the previous evidence.
        """
        from .storage import list_experiments, load_extraction
        experiments = list_experiments() if experiments is None else experiments
        expected: set[str] = set()
        failures = []
        pending = []
        batches = 0
        with self.connect() as db:
            known = {cid: (model, payload) for cid, model, payload in db.execute("SELECT id,model,payload FROM chunks")}
            fts_ids = {row[0] for row in db.execute("SELECT id FROM chunks_fts")}
        for experiment in experiments:
            for document in experiment.get("documents", []):
                if document.get("status") == "erro":
                    continue
                try:
                    extraction = load_extraction(experiment, document)
                    for structural in structural_chunks(experiment, document, extraction):
                        for chunk in self._model_chunks(structural):
                            cid = chunk["id"]
                            expected.add(cid)
                            payload = json.dumps(chunk, ensure_ascii=False, sort_keys=True)
                            if known.get(cid) != (self.mode, payload):
                                searchable = self._searchable(chunk)
                                # Metadata remains searchable in FTS but cannot consume the
                                # model's token budget and truncate the source evidence.
                                embedding_text = chunk["text"] if self.model is not None else searchable
                                pending.append((cid, payload, searchable, embedding_text))
                except (OSError, ValueError, KeyError) as error:
                    failures.append(f"{document.get('name')}: {type(error).__name__}")
        if progress:
            progress({"stage": "encoding", "completed": 0, "total": len(pending)})
        encoded: list[tuple[str, str, str, str, str]] = []
        batch_size = max(1, min(256, int(batch_size)))
        for start in range(0, len(pending), batch_size):
            batch = pending[start:start + batch_size]
            vectors = self._encode_batch([item[3] for item in batch], batch_size)
            encoded.extend((cid, payload, json.dumps(vector), self.mode, searchable)
                           for (cid, payload, searchable, _), vector in zip(batch, vectors))
            batches += 1
            if progress:
                progress({"stage": "encoding", "completed": len(encoded), "total": len(pending)})
        with self.connect() as db:
            # BEGIN explicitly includes reconciliation even when no batch changed.
            db.execute("BEGIN IMMEDIATE")
            for cid, payload, vector, mode, searchable in encoded:
                db.execute("INSERT OR REPLACE INTO chunks VALUES (?,?,?,?)", (cid, payload, vector, mode))
                # FTS id is UNINDEXED: avoid a full scan for every new passage.
                if cid in fts_ids:
                    db.execute("DELETE FROM chunks_fts WHERE id=?", (cid,))
                db.execute("INSERT INTO chunks_fts VALUES (?,?)", (cid, searchable))
                fts_ids.add(cid)
            # Reconcile only studies explicitly supplied; failures retain old sources.
            if not failures:
                active_ids = {e["id"] for e in experiments}
                for cid, payload in db.execute("SELECT id,payload FROM chunks").fetchall():
                    if json.loads(payload).get("experiment_id") in active_ids and cid not in expected:
                        db.execute("DELETE FROM chunks WHERE id=?", (cid,))
                        db.execute("DELETE FROM chunks_fts WHERE id=?", (cid,))
            total = db.execute("SELECT count(*) FROM chunks").fetchone()[0]
        if progress:
            progress({"stage": "completed", "completed": len(encoded), "total": len(pending)})
        return {"indexed": len(encoded), "total": total, "mode": self.mode, "batches_encoded": batches,
                "failures": failures, "warnings": self.warnings}

    def search(self, query: str, study_ids: list[str] | None = None, numeric_filters: list[dict] | None = None,
               active_study: str | None = None, limit: int = 8) -> list[dict]:
        query = str(query)[:2000]
        terms = set(_tokens(query))
        expanded = {v for t in terms for v in _SYN.get(t, {t})}
        if not terms and not numeric_filters:
            return []
        qv = self._encode(query)
        lexical_qv = _vector(query)
        lexical = {}
        with self.connect() as db:
            if expanded:
                expression = " OR ".join('"' + t.replace('"', '""') + '"' for t in sorted(expanded))
                lexical = {cid: -rank for cid, rank in db.execute("SELECT id,bm25(chunks_fts) FROM chunks_fts WHERE chunks_fts MATCH ? ORDER BY bm25(chunks_fts) LIMIT 2000", (expression,))}
            rows = db.execute("SELECT id,payload,vector,model FROM chunks").fetchall()
        if any(model != self.mode for _, _, _, model in rows):
            warning = "Índice criado com outro modelo: reindexação necessária; evidências preservadas em busca lexical."
            if warning not in self.warnings:
                self.warnings.append(warning)
        results = []
        for cid, payload, vector, model in rows:
            chunk = json.loads(payload)
            if study_ids and chunk["study_id"] not in study_ids:
                continue
            if not matches_numeric_filters(chunk, numeric_filters):
                continue
            compatible_model = model == self.mode
            cosine = (_dot(qv, json.loads(vector)) if compatible_model else
                      _dot(lexical_qv, _vector(self._searchable(chunk)))) if terms else 0
            word_hits = expanded.intersection(_tokens(self._searchable(chunk)))
            if terms and not word_hits and (self.model is None or not compatible_model or cosine < MIN_SEMANTIC_ONLY_COSINE):
                continue
            coverage = len(word_hits) / max(1, len(terms))
            score = .55 * min(1, coverage) + .35 * max(0, cosine) + (.1 if cid in lexical else 0)
            if active_study == chunk["study_id"]:
                score *= 1.08
            results.append({**chunk, "score": round(score, 6), "vector_score": round(cosine, 6),
                            "retrieval_mode": self.mode if compatible_model else "lexical-fallback:reindex-required", "snippet": chunk["text"]})
        return sorted(results, key=lambda r: (-r["score"], r["id"]))[:max(1, min(100, limit))]

    @staticmethod
    def _searchable(chunk: dict) -> str:
        return "\n".join(str(chunk.get(k, "")) for k in ("study_id", "investigation_name", "document_name", "text"))


def index_experiments(experiments: list[dict] | None = None, db_path=None) -> dict:
    return RetrievalIndex(db_path).index_experiments(experiments)
