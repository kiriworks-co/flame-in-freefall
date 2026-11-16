"""Synthetic fixtures test retrieval invariants; these are NOT NASA measurements."""
import re
import sqlite3

import pytest

from src.relevance import rank_investigations
from src.retrieval import (
    RetrievalIndex,
    matches_numeric_filters,
    safe_source_url,
    structural_chunks,
)


@pytest.fixture
def corpus(monkeypatch):
    monkeypatch.delenv("RAG_EMBEDDING_MODEL", raising=False)
    experiments = [{"id": "fixture-1", "psi_id": "PSI-TEST", "source_url": "https://psi.nasa.gov/physci/repo/data/investigations/PSI-69",
                    "doi": "10.0000/test", "name": "Synthetic FLEX fixture", "documents": [
                        {"id": "doc1", "sha256": "a" * 64, "name": "synthetic.csv", "status": "processado", "extension": ".csv", "provenance": {"evidence_kind": "condition"}}]}]
    extraction = {"pages": [{"page": 1, "text": "Droplet extinction in synthetic fixture.\n" + "combustion context " * 200, "location": "página 1"}],
                  "tables": [{"columns": ["oxygen (fraction)", "pressure (psia)", "fuel"],
                              "rows": [[.21, 14.7, "heptane"], [.3, 30, "methanol"]],
                              "source_rows": [10, 15], "location": "fixture sheet", "evidence_kind": "condition"}],
                  "observations": [
                      {"table_index": 0, "row_number": 10, "field": "oxygen", "quantity": "oxygen_fraction", "value": .21,
                       "unit": "fraction", "normalized_value": .21, "normalized_unit": "fraction", "evidence_kind": "condition"},
                      {"table_index": 0, "row_number": 10, "field": "pressure", "quantity": "pressure", "value": 14.7,
                       "unit": "psia", "reference": "absolute", "evidence_kind": "condition"},
                      {"table_index": 0, "row_number": 15, "field": "oxygen", "quantity": "oxygen_fraction", "value": .3,
                       "unit": "fraction", "normalized_value": .3, "normalized_unit": "fraction", "evidence_kind": "condition"},
                      {"table_index": 0, "row_number": 15, "field": "pressure", "quantity": "pressure", "value": 30,
                       "unit": "psia", "reference": "absolute", "evidence_kind": "condition"},
                  ]}
    monkeypatch.setattr("src.storage.load_extraction", lambda experiment, document: extraction)
    return experiments, extraction


def test_structural_chunks_retain_page_and_source_row(corpus):
    exp, extraction = corpus
    chunks = structural_chunks(exp[0], exp[0]["documents"][0], extraction)
    assert all(len(c["text"]) <= 1500 for c in chunks)
    rows = [c for c in chunks if c["kind"] == "table_row"]
    assert [c["row_number"] for c in rows] == [10, 15]
    assert rows[0]["observations"][0]["value"] == .21
    assert all(c["sha256"] == "a" * 64 and c["study_id"] == "PSI-TEST" for c in chunks)


def test_structural_observations_keep_table_boundary_and_source_order(corpus):
    experiments, _ = corpus
    observations = [
        {"table_index": 0, "row_number": 7, "field": "pressure", "value": 14.7},
        {"table_index": 1, "row_number": 7, "field": "oxygen", "value": .30},
        {"table_index": 0, "row_number": 7, "field": "oxygen", "value": .21},
        {"table_index": 1, "row_number": 7, "field": "pressure", "value": 30},
        {"table_index": 0, "row_number": 8, "field": "oxygen", "value": .99},
    ]
    extraction = {"observations": observations, "tables": [
        {"columns": ["fuel"], "rows": [["heptane"]], "source_rows": [7]},
        {"columns": ["fuel"], "rows": [["methanol"]], "source_rows": [7]},
    ]}
    chunks = structural_chunks(experiments[0], experiments[0]["documents"][0], extraction)
    rows = [chunk for chunk in chunks if chunk["kind"] == "table_row"]
    assert len(rows) == 2
    assert rows[0]["observations"] == [observations[0], observations[2]]
    assert rows[1]["observations"] == [observations[1], observations[3]]
    assert observations[4] not in rows[0]["observations"]


def test_duplicate_pending_and_existing_updates_keep_one_fts_row_per_chunk(tmp_path, corpus):
    experiments, _ = corpus
    index = RetrievalIndex(tmp_path / "index.db")
    # Repeated input creates duplicate pending IDs before the first transaction.
    duplicated = experiments + experiments
    first = index.index_experiments(duplicated)
    assert first["indexed"] == first["total"] * 2
    with index.connect() as db:
        old_fts = dict(db.execute("SELECT id,text FROM chunks_fts"))
        assert len(old_fts) == first["total"]
        assert not db.execute("SELECT id FROM chunks_fts GROUP BY id HAVING COUNT(*) != 1").fetchall()

    # Metadata changes preserve chunk IDs but must replace existing FTS text.
    experiments[0]["name"] = "Updated synthetic investigation label"
    updated = index.index_experiments(duplicated)
    assert updated["total"] == first["total"]
    assert updated["indexed"] == first["total"] * 2
    with index.connect() as db:
        fts_rows = db.execute("SELECT id,text FROM chunks_fts").fetchall()
        assert len(fts_rows) == first["total"]
        assert {cid for cid, _ in fts_rows} == set(old_fts)
        assert all(text != old_fts[cid] for cid, text in fts_rows)
        assert all("Updated synthetic investigation label" in text for _, text in fts_rows)
        assert not db.execute("SELECT id FROM chunks_fts GROUP BY id HAVING COUNT(*) != 1").fetchall()
    assert index.index_experiments(experiments)["indexed"] == 0


def test_persistent_idempotent_hybrid_index(tmp_path, corpus):
    experiments, _ = corpus
    index = RetrievalIndex(tmp_path / "index.db")
    first = index.index_experiments(experiments)
    assert first["total"] >= 3
    assert index.index_experiments(experiments)["indexed"] == 0
    results = RetrievalIndex(tmp_path / "index.db").search("extinção de gotas")
    assert results and "Droplet extinction" in results[0]["text"]
    assert index.search("unrelated-zebras") == []


def test_numeric_filters_apply_to_same_source_row(tmp_path, corpus):
    index = RetrievalIndex(tmp_path / "index.db")
    index.index_experiments(corpus[0])
    oxygen = {"field": "oxygen_fraction", "min": .2, "max": .22, "unit": "fraction"}
    pressure = {"field": "pressure", "min": 25, "unit": "psia", "reference": "absolute"}
    rows = index.search("", numeric_filters=[oxygen])
    assert len(rows) == 1 and rows[0]["row_number"] == 10
    assert index.search("", numeric_filters=[oxygen, pressure]) == []
    assert index.search("oxygen", study_ids=["PSI-OTHER"]) == []


def test_pressure_reference_and_ranges_are_not_exact_measurements():
    chunk = {"observations": [{"field": "pressure", "value": 14.7, "unit": "psi", "reference": "unspecified"}]}
    assert not matches_numeric_filters(chunk, [{"field": "pressure", "unit": "psia", "reference": "absolute"}])
    chunk["observations"][0].update(unit="psia", reference="absolute", status="range")
    assert not matches_numeric_filters(chunk, [{"field": "pressure", "unit": "psia", "min": 10}])


def test_safe_reference_url():
    assert safe_source_url("javascript:alert(1)") == ""
    assert safe_source_url("https://example.org/a?X-Amz-Signature=secret") == ""
    assert safe_source_url("https://doi.org/10.0000/test").startswith("https://doi.org/")


def test_relevance_is_deterministic_and_explainable():
    inputs = [{"id": "flex", "name": "FLEX", "category": "Supressão", "files_downloaded": 1},
              {"id": "same", "name": "SAME", "category": "Detecção", "files_downloaded": 2}]
    ranked = rank_investigations(inputs, application="detection")
    assert ranked == rank_investigations(inputs, application="detection")
    assert ranked[0]["id"] == "same" and ranked[0]["reasons"]
    assert 0 <= ranked[0]["score"] <= 100


class FixtureEncoder:
    """Deterministic fake model for orchestration tests, not scientific embeddings."""
    def __init__(self):
        self.batch_calls = []

    def encode(self, texts, **kwargs):
        if isinstance(texts, str):
            return [1.0, 0.0]
        self.batch_calls.append(list(texts))
        return [[1.0, 0.0] for _ in texts]


def test_semantic_index_batches_and_commits_once(tmp_path, corpus):
    index = RetrievalIndex(tmp_path / "index.db")
    index.model = FixtureEncoder()
    index.mode = "local-semantic:synthetic-encoder-test"
    progress = []
    result = index.index_experiments(corpus[0], batch_size=2, progress=progress.append)
    assert result["indexed"] >= 3
    assert all(1 <= len(batch) <= 2 for batch in index.model.batch_calls)
    assert result["batches_encoded"] == len(index.model.batch_calls)
    assert progress[-1] == {"stage": "completed", "completed": result["indexed"], "total": result["indexed"]}
    assert index.index_experiments(corpus[0])["batches_encoded"] == 0


def test_model_switch_preserves_lexical_search_before_reindex(tmp_path, corpus):
    index = RetrievalIndex(tmp_path / "index.db")
    index.index_experiments(corpus[0])
    index.model = FixtureEncoder()
    index.mode = "local-semantic:new-synthetic-encoder"
    results = index.search("extinction droplet")
    assert results and all(r["retrieval_mode"] == "lexical-fallback:reindex-required" for r in results)
    assert any("reindexação necessária" in w for w in index.warnings)
    index.index_experiments(corpus[0])
    assert index.search("extinction")[0]["retrieval_mode"] == index.mode
    # Reopening offline without the model also preserves retrieval from semantic indices.
    offline = RetrievalIndex(tmp_path / "index.db")
    assert offline.search("extinction")[0]["retrieval_mode"] == "lexical-fallback:reindex-required"


def test_failed_embedding_batch_does_not_modify_previous_index(tmp_path, corpus, monkeypatch):
    index = RetrievalIndex(tmp_path / "index.db")
    index.index_experiments(corpus[0])
    with index.connect() as db:
        old = db.execute("SELECT * FROM chunks ORDER BY id").fetchall()
        old_fts = db.execute("SELECT * FROM chunks_fts ORDER BY id").fetchall()
    index.mode = "local-semantic:failing-synthetic-encoder"
    calls = []
    def fail_after_first_batch(texts, batch_size):
        calls.append(texts)
        if len(calls) > 1:
            raise ValueError("synthetic embedding failure")
        return [{"0": 1.0} for _ in texts]
    monkeypatch.setattr(index, "_encode_batch", fail_after_first_batch)
    with pytest.raises(ValueError, match="synthetic embedding failure"):
        index.index_experiments(corpus[0], batch_size=2)
    with index.connect() as db:
        assert db.execute("SELECT * FROM chunks ORDER BY id").fetchall() == old
        assert db.execute("SELECT * FROM chunks_fts ORDER BY id").fetchall() == old_fts


def test_model_chunking_respects_token_budget_and_source_offsets(tmp_path):
    class FixtureTokenizer:
        @staticmethod
        def num_special_tokens_to_add(pair=False):
            return 2

        def __call__(self, text, **kwargs):
            offsets = [(match.start(), match.end()) for match in re.finditer(r"\S+", text)]
            count = len(offsets) + (2 if kwargs.get("add_special_tokens", True) else 0)
            return {"offset_mapping": offsets, "input_ids": [0] * count}

    index = RetrievalIndex(tmp_path / "index.db")
    index.model = FixtureEncoder()
    index.model.tokenizer = FixtureTokenizer()
    index.model.max_seq_length = 18
    text = " ".join(f"word{i}" for i in range(80))
    chunk = {"id": "synthetic", "text": text, "char_start": 100, "char_end": 100 + len(text),
             "study_id": "PSI-TEST", "page": 2, "sha256": "a" * 64}
    split = index._model_chunks(chunk)
    assert len(split) > 1 and all(c["token_count"] <= 16 for c in split)
    assert set(text.split()) == {token for c in split for token in c["text"].split()}
    assert all(c["text"] == text[c["char_start"] - 100:c["char_end"] - 100] for c in split)
    assert split == index._model_chunks(chunk)


def test_subword_retokenization_cannot_exceed_model_budget(tmp_path):
    original = " ".join(f"synthetic-token-{i}" for i in range(70))

    class SubwordTokenizer:
        @staticmethod
        def num_special_tokens_to_add(pair=False):
            return 2

        def __call__(self, text, **kwargs):
            offsets = [(match.start(), match.end()) for match in re.finditer(r"\S+", text)]
            special = 2 if kwargs.get("add_special_tokens", True) else 0
            # Simulate a leading subword becoming two tokens when sliced.
            extra = 1 if text != original and kwargs.get("add_special_tokens", True) else 0
            return {"offset_mapping": offsets, "input_ids": [0] * (len(offsets) + special + extra)}

    index = RetrievalIndex(tmp_path / "index.db")
    index.model = FixtureEncoder()
    index.model.tokenizer = SubwordTokenizer()
    index.model.max_seq_length = 18
    chunks = index._model_chunks({"id": "synthetic-subword", "text": original, "char_start": 0})
    assert len(chunks) > 1
    assert all(len(index.model.tokenizer(c["text"])["input_ids"]) <= 18 for c in chunks)
    assert set(original.split()) == {token for chunk in chunks for token in chunk["text"].split()}


def test_sqlite_connections_close_before_windows_file_cleanup(tmp_path):
    path = tmp_path / "index.db"
    index = RetrievalIndex(path)
    with index.connect() as db:
        assert db.execute("SELECT count(*) FROM chunks").fetchone()[0] == 0
    with pytest.raises(sqlite3.ProgrammingError, match="closed"):
        db.execute("SELECT 1")
    # Windows denies unlinking an SQLite database while a connection owns it.
    path.unlink()
    assert not path.exists()
