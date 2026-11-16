"""Deterministic encoder fixtures test relevance gates, not scientific findings."""
from __future__ import annotations

import json
import math

from src.assistant import answer
from src.retrieval import MIN_SEMANTIC_ONLY_COSINE, RetrievalIndex


class FixtureEncoder:
    def encode(self, text, **kwargs):
        return [1.0, 0.0]


def semantic_index(tmp_path, monkeypatch, sources):
    monkeypatch.setenv("RAG_EMBEDDING_MODEL", " ")
    index = RetrievalIndex(tmp_path / "semantic-guard.sqlite3")
    index.model = FixtureEncoder()
    index.mode = "local-semantic:deterministic-fixture"
    with index.connect() as db:
        for position, (text, cosine) in enumerate(sources):
            payload = {"id": str(position), "text": text, "study_id": "FIXTURE",
                       "document_name": "Synthetic relevance fixture", "experiment_id": "fixture",
                       "evidence_kind": "document_context", "observations": []}
            vector = {"0": cosine, "1": math.sqrt(1 - cosine ** 2)}
            db.execute("INSERT INTO chunks VALUES (?,?,?,?)",
                       (str(position), json.dumps(payload), json.dumps(vector), index.mode))
            db.execute("INSERT INTO chunks_fts VALUES (?,?)", (str(position), text))
    return index


def test_weak_semantic_only_neighbor_returns_insufficient(tmp_path, monkeypatch):
    # Real unknown-token false neighbors reached ~0.493. Include a near-gate
    # neighbor too, so accidental restoration of the old 0.35 gate is detected.
    index = semantic_index(tmp_path, monkeypatch, [
        ("Technical nomenclature reference fragment.", .493),
        ("Unrelated source fragment with no shared vocabulary.", MIN_SEMANTIC_ONLY_COSINE - .01),
    ])
    result = answer("quasizebraunobtainium", index, use_llm=False)
    assert result["insufficient"] and not result["evidence"]


def test_strong_semantic_paraphrase_survives_without_literal_anchor(tmp_path, monkeypatch):
    index = semantic_index(tmp_path, monkeypatch, [
        ("Delayed oxidation persists despite reduced temperature.", .82),
        ("Disconnected nomenclature fragment.", .49),
    ])
    result = index.search("lowheat chemical longevity")
    assert len(result) == 1
    assert result[0]["text"].startswith("Delayed oxidation")
    assert result[0]["vector_score"] == .82


def test_literal_anchor_does_not_require_semantic_only_floor(tmp_path, monkeypatch):
    index = semantic_index(tmp_path, monkeypatch, [("Flamelet tomography source reference.", .1)])
    result = index.search("tomography")
    assert result and result[0]["vector_score"] < MIN_SEMANTIC_ONLY_COSINE
