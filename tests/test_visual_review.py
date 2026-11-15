"""Synthetic, explicitly mocked VLM responses; no real provider is called."""
import hashlib
import json

import pymupdf
import pytest
from streamlit.testing.v1 import AppTest

from src import visual_review
from src.scientific_store import ScientificStore


@pytest.fixture(autouse=True)
def no_vlm_credentials(monkeypatch):
    for key in ("VLM_BASE_URL", "VLM_MODEL", "VLM_API_KEY"):
        monkeypatch.delenv(key, raising=False)


@pytest.fixture
def synthetic_pdf():
    with pymupdf.open() as pdf:
        page = pdf.new_page(width=300, height=300)
        page.insert_text((30, 40), "SYNTHETIC TEST FIXTURE - NOT NASA DATA")
        content = pdf.tobytes()
    return content, hashlib.sha256(content).hexdigest()


def payload(digest="a" * 64):
    return {
        "page": 1, "document_sha256": digest,
        "description": "A qualitative chart and caption are visible.",
        "inference": "The figure may require comparison with the original caption.",
        "needs_human_review": True,
        "regions": [{"kind": "chart", "bbox": [.1, .1, .8, .8],
                     "text_candidate": "Figure 1 - unverified candidate label",
                     "description": "A plotted curve is visible.", "needs_human_review": True}],
    }


def test_typed_candidates_stay_inference():
    review = visual_review.validate_response(payload(), "a" * 64, 1, "synthetic-model")
    assert review.page == 1 and review.needs_human_review
    assert review.evidence_kind == "inference"
    assert review.regions[0].needs_human_review
    assert not hasattr(review, "measurements")


@pytest.mark.parametrize("mutate", [
    lambda p: p.update(page=2),
    lambda p: p.update(document_sha256="b" * 64),
    lambda p: p.update(needs_human_review=False),
    lambda p: p.update(measurements=[{"value": 42}]),
    lambda p: p.update(description="The measured flame rate is 42 cm/s"),
    lambda p: p.update(inference="<script>alert('unsafe')</script>"),
    lambda p: p["regions"][0].update(bbox=[0, 0, float("nan"), 1]),
    lambda p: p["regions"][0].update(bbox=[True, 0, 1, 1]),
    lambda p: p["regions"][0].update(bbox=[.8, .8, .1, .1]),
    lambda p: p["regions"][0].update(text_candidate="<img src=x onerror=alert(1)>"),
])
def test_schema_rejects_invalid_or_measured_claims(mutate):
    data = payload()
    mutate(data)
    with pytest.raises(ValueError):
        visual_review.validate_response(data, "a" * 64, 1)


def test_local_preview_checks_hash_and_page(synthetic_pdf):
    content, digest = synthetic_pdf
    assert visual_review.render_verified_page(content, 1, digest).startswith(b"\x89PNG")
    with pytest.raises(ValueError):
        visual_review.render_verified_page(content, 1, "b" * 64)
    with pytest.raises(ValueError):
        visual_review.render_verified_page(content, 2, digest)


def test_no_network_without_consent_or_configuration(monkeypatch, synthetic_pdf):
    def forbidden(*args, **kwargs):
        pytest.fail("No provider call was authorized")
    monkeypatch.setattr(visual_review, "_request_completion", forbidden)
    content, digest = synthetic_pdf
    assert visual_review.review_pdf_page(content, 1, digest).status == "not_requested"
    assert visual_review.review_pdf_page(content, 1, digest, consent=True).status == "unavailable"
    monkeypatch.setenv("VLM_MODEL", "synthetic")
    assert visual_review.review_pdf_page(content, 1, digest, consent=True).status == "unavailable"


def test_invalid_configuration_does_not_echo_credentials(monkeypatch, synthetic_pdf):
    monkeypatch.setenv("VLM_MODEL", "synthetic")
    monkeypatch.setenv("VLM_BASE_URL", "https://user:synthetic-secret@example.invalid/v1")
    monkeypatch.setenv("VLM_API_KEY", "synthetic-secret")
    content, digest = synthetic_pdf
    result = visual_review.review_pdf_page(content, 1, digest, consent=True)
    assert result.status == "unavailable"
    assert "synthetic-secret" not in str(result)


def test_mock_provider_and_persistence_do_not_create_observations(monkeypatch, synthetic_pdf, tmp_path):
    monkeypatch.setenv("VLM_MODEL", "synthetic-model")
    monkeypatch.setenv("VLM_BASE_URL", "http://127.0.0.1:9999/v1")
    content, digest = synthetic_pdf
    monkeypatch.setattr(visual_review, "_request_completion", lambda *args: payload(digest))
    review = visual_review.review_pdf_page(content, 1, digest, consent=True)
    assert review.status == "candidate"
    db_path = tmp_path / "synthetic.sqlite3"
    visual_review.save_review(review, "SYNTHETIC-TEST", db_path)
    reviewed = visual_review.record_human_review(review, "Synthetic reviewer checked the original page.")
    visual_review.save_review(reviewed, "SYNTHETIC-TEST", db_path)
    assert reviewed.needs_human_review and reviewed.human_reviewed_utc
    with ScientificStore(db_path).connection() as conn:
        assert conn.execute("SELECT count(*) FROM observations").fetchone()[0] == 0
        assert conn.execute("SELECT count(*) FROM chunks").fetchone()[0] == 0
        rows = conn.execute("SELECT result_json FROM analysis_results WHERE kind='visual_review'").fetchall()
    assert len(rows) == 1
    assert json.loads(rows[0][0])["human_review_note"]


def test_provider_failure_does_not_echo_response_or_secret(monkeypatch, synthetic_pdf):
    monkeypatch.setenv("VLM_MODEL", "synthetic-model")
    monkeypatch.setenv("VLM_BASE_URL", "http://127.0.0.1:9999/v1")
    def fail(*args):
        raise RuntimeError("synthetic-secret and private provider response")
    monkeypatch.setattr(visual_review, "_request_completion", fail)
    content, digest = synthetic_pdf
    result = visual_review.review_pdf_page(content, 1, digest, consent=True)
    assert result.status == "failed"
    assert "synthetic-secret" not in str(result)
    assert "RuntimeError" in result.warnings[0]


def test_mock_transport_sends_key_only_in_header_and_limits_response(monkeypatch):
    calls = []
    response_bytes = json.dumps({"choices": [{"message": {"content": json.dumps(payload())}}]}).encode()
    class SyntheticResponse:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return None
        def read(self, maximum):
            assert maximum == visual_review.MAX_RESPONSE_BYTES + 1
            return response_bytes
    class SyntheticOpener:
        def open(self, request, timeout):
            calls.append(request)
            assert timeout == 40
            return SyntheticResponse()
    monkeypatch.setattr(visual_review.urllib.request, "build_opener", lambda *handlers: SyntheticOpener())
    config = visual_review.VisualConfig("https://synthetic.invalid/v1", "synthetic-model", "synthetic-private-key")
    result = visual_review._request_completion(config, b"SYNTHETIC PNG FIXTURE", 1, "a" * 64)
    assert result["needs_human_review"] is True
    assert calls[0].get_header("Authorization") == "Bearer synthetic-private-key"
    assert b"synthetic-private-key" not in calls[0].data
    response_bytes = b" " * (visual_review.MAX_RESPONSE_BYTES + 1)
    with pytest.raises(ValueError):
        visual_review._request_completion(config, b"SYNTHETIC PNG FIXTURE", 1, "a" * 64)


def test_visual_section_without_provider():
    from pathlib import Path

    from src.i18n import t

    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=60).run()
    app.radio(key="workspace_section").set_value("visual_review").run()
    assert not app.exception
    buttons = [b for b in app.button if b.label == t("vis.vlm_btn", "en")]
    assert buttons
    assert buttons[0].disabled
