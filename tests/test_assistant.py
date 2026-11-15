"""Synthetic excerpts exercise programmatic grounding and no-key behavior."""
from src.assistant import answer, sanitize_markdown, validate_claims

EVIDENCE = [{"id": "source1", "text": "Test pressure was 14.7 psia; this is a condition.",
             "evidence_kind": "condition", "study_id": "PSI-TEST", "document_name": "synthetic.csv", "location": "linha 2"}]


class FixtureIndex:
    def __init__(self, evidence):
        self.evidence = evidence
        self.warnings = []
    def search(self, *args, **kwargs):
        return self.evidence


def test_valid_excerpt_and_category():
    claims, errors = validate_claims({"claims": [{"citation": "source1", "quote": EVIDENCE[0]["text"], "kind": "condition"}]}, EVIDENCE)
    assert len(claims) == 1 and not errors


def test_unknown_source_invented_number_or_measurement_rejected():
    for claim in [
        {"citation": "outside-source", "quote": EVIDENCE[0]["text"]},
        {"citation": "source1", "quote": "Test pressure was 999 psia."},
        {"citation": "source1", "quote": EVIDENCE[0]["text"], "kind": "measurement"},
        {"citation": "source1", "quote": EVIDENCE[0]["text"], "text": "Material is safe at 14.7 psia."},
    ]:
        accepted, errors = validate_claims({"claims": [claim]}, EVIDENCE)
        assert not accepted and errors


def test_offline_insufficient_data():
    result = answer("unknown", FixtureIndex([]))
    assert result["insufficient"] and "Não encontrei dados" in result["text"]
    result = answer("unknown", FixtureIndex([]), language="en")
    assert "did not find" in result["text"]


def test_no_key_mode_preserves_sources(monkeypatch):
    monkeypatch.delenv("RAG_MODEL", raising=False)
    result = answer("pressure", FixtureIndex(EVIDENCE), use_llm=True)
    assert result["mode"] == "offline-evidence" and result["evidence"] == EVIDENCE
    assert not result["claims"]


def test_prompt_injection_rendered_as_inert_text():
    text = sanitize_markdown('<script>steal()</script> [click](javascript:alert(1))')
    assert "<script>" not in text and "[click](" not in text


def test_provider_failure_does_not_disclose_error_body(monkeypatch):
    monkeypatch.setattr("src.assistant.llm_configured", lambda: True)
    def fail(*args):
        raise ValueError("SECRET_TOKEN_DO_NOT_PRINT")
    monkeypatch.setattr("src.assistant._llm_claims", fail)
    result = answer("pressure", FixtureIndex(EVIDENCE), use_llm=True)
    assert "SECRET_TOKEN_DO_NOT_PRINT" not in str(result)
    assert result["evidence"] == EVIDENCE
