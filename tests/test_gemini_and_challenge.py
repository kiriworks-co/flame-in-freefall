"""Tests for optional Gemini provider guards, Challenge Hub (SUMMARIZE/RANK/INTERPRET), and design system UX."""
from __future__ import annotations

import io
import json
import tomllib
import urllib.error
from pathlib import Path
from typing import Any, cast

from streamlit.testing.v1 import AppTest

from src import assistant, challenge_engine, design_system, gemini_provider, i18n

ROOT = Path(__file__).resolve().parents[1]

SAMPLE_EVIDENCE: list[dict[str, Any]] = [
    {
        "id": "psi69-chunk-1",
        "study_id": "PSI-69",
        "document_name": "PSI-69_Experimental table_FLEX.csv",
        "location": "row 4",
        "evidence_kind": "condition",
        "source_url": "https://psi.nasa.gov/physci/repo/data/investigations/PSI-69",
        "text": "Test condition in PSI-69 FLEX: O initial ambient composition; mole fraction was 0.21 with Fuel = n-heptane.",
    },
    {
        "id": "local-upload-1",
        "study_id": "LOCAL-CUSTOM",
        "document_name": "private_lab_notes.pdf",
        "location": "page 1",
        "evidence_kind": "document_context",
        "source_url": "",
        "provenance": {"source": "local_upload"},
        "text": "Private confidential draft notes containing internal laboratory details 12345.",
    },
]


class _FixtureIndex:
    def __init__(self, evidence: list[dict]) -> None:
        self._evidence = evidence
        self.warnings: list[str] = []

    def search(self, *args, **kwargs) -> list[dict]:
        return list(self._evidence)


class _FakeHTTPResponse:
    def __init__(self, payload: dict) -> None:
        self._data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    def read(self, _limit: int = -1) -> bytes:
        return self._data

    def __enter__(self) -> _FakeHTTPResponse:
        return self

    def __exit__(self, *args) -> None:
        return None


def test_gemini_unconfigured_and_privacy_filter(monkeypatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    gemini_provider.reset_gemini_runtime_state()

    assert gemini_provider.gemini_configured() is False
    status_en = gemini_provider.gemini_status_summary("en")
    status_pt = gemini_provider.gemini_status_summary("pt")
    assert status_en["status"] == "unconfigured"
    assert status_pt["status"] == "unconfigured"

    public_only = gemini_provider.filter_public_nasa_evidence(SAMPLE_EVIDENCE)
    assert len(public_only) == 1
    assert public_only[0]["id"] == "psi69-chunk-1"


def test_gemini_verified_quote_and_private_upload_never_sent(monkeypatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "AIzaSyTestFakeKeyDoNotLeak")
    gemini_provider.reset_gemini_runtime_state()
    captured_bodies: list[str] = []

    def fake_urlopen(request, timeout=0):
        body_text = request.data.decode("utf-8")
        captured_bodies.append(body_text)
        assert "local-upload-1" not in body_text
        assert "private_lab_notes.pdf" not in body_text
        assert request.get_header("X-goog-api-key") == "AIzaSyTestFakeKeyDoNotLeak"
        envelope = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": json.dumps(
                                    {
                                        "claims": [
                                            {
                                                "citation": "psi69-chunk-1",
                                                "quote": "O initial ambient composition; mole fraction was 0.21 with Fuel = n-heptane.",
                                                "kind": "condition",
                                            },
                                            {
                                                "citation": "psi69-chunk-1",
                                                "quote": "Invented hallucinated flame temperature 9999 K",
                                                "kind": "measurement",
                                            },
                                        ]
                                    }
                                )
                            }
                        ]
                    }
                }
            ]
        }
        return _FakeHTTPResponse(envelope)

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    res = assistant.answer(
        "What oxygen mole fraction was used in FLEX?",
        cast(Any, _FixtureIndex(SAMPLE_EVIDENCE)),
        language="en",
        use_llm=True,
    )
    assert captured_bodies
    assert res["mode"] == "gemini-verified-excerpts"
    assert res["provider_status"] == "gemini_verified"
    assert len(res["claims"]) == 1
    assert res["claims"][0]["citation"] == "psi69-chunk-1"
    assert any("not found verbatim" in w.lower() for w in res["warnings"])


def test_gemini_rate_limit_and_error_recovery_never_leaks_key(monkeypatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "SECRET_GEMINI_KEY_XYZ")
    gemini_provider.reset_gemini_runtime_state()

    def raise_429(request, timeout=0):
        raise urllib.error.HTTPError(
            request.full_url,
            429,
            "Too Many Requests SECRET_GEMINI_KEY_XYZ",
            hdrs={},  # type: ignore[arg-type]
            fp=io.BytesIO(b"quota exceeded SECRET_GEMINI_KEY_XYZ"),
        )

    monkeypatch.setattr("urllib.request.urlopen", raise_429)
    res = assistant.answer(
        "FLEX oxygen conditions",
        cast(Any, _FixtureIndex(SAMPLE_EVIDENCE[:1])),
        language="en",
        use_llm=True,
    )
    assert res["mode"] == "offline-evidence"
    assert res["provider_status"] == "fallback_after_error"
    assert res["evidence"] == SAMPLE_EVIDENCE[:1]
    assert "SECRET_GEMINI_KEY_XYZ" not in json.dumps(res)
    assert any("rate limit" in w.lower() for w in res["warnings"])


def test_gemini_local_only_records_stay_local(monkeypatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "AIzaSyTestFakeKeyDoNotLeak")
    gemini_provider.reset_gemini_runtime_state()

    def forbidden(*args, **kwargs):
        raise AssertionError("Private upload should never invoke external Gemini endpoint")

    monkeypatch.setattr("urllib.request.urlopen", forbidden)
    res = assistant.answer(
        "laboratory draft",
        cast(Any, _FixtureIndex([SAMPLE_EVIDENCE[1]])),
        language="pt",
        use_llm=True,
    )
    assert res["mode"] == "offline-evidence"
    assert any("locais privados" in w.lower() for w in res["warnings"])


def test_challenge_engine_summarize_rank_interpret() -> None:
    exp_psi69 = {
        "id": "psi-69",
        "psi_id": "PSI-69",
        "name": "Flame Extinguishment Experiment (FLEX)",
        "description": "Spherical droplet combustion study.",
        "documents": [
            {
                "name": "PSI-69_Experimental table_FLEX.csv",
                "extension": ".csv",
                "table_count": 1,
                "status": "processado",
                "evidence_kind": "mixed_conditions_and_reported_results",
                "sha256": "a" * 64,
                "source_url": "https://psi.nasa.gov/physci/repo/data/investigations/PSI-69",
            },
            {
                "name": "PSI-69_Engineering Documents_FLEX Engineering Requirements Document.pdf",
                "extension": ".pdf",
                "table_count": 0,
                "status": "parcial",
                "evidence_kind": "engineering_or_publication",
                "sha256": "b" * 64,
                "source_url": "https://psi.nasa.gov/physci/repo/data/investigations/PSI-69",
            },
        ],
    }
    summary = challenge_engine.build_study_summary(exp_psi69, "en")
    assert summary["study_id"] == "PSI-69"
    assert summary["pillar"] == "Suppression"
    assert any("FLEX-2" in c for c in summary["caveats"])

    interp = challenge_engine.build_spacecraft_interpretation(exp_psi69, "pt")
    assert interp["pillar"] == "Supressão"
    assert "certificação" in interp["scientific_boundary"].lower()

    ranked = challenge_engine.build_priority_ranking(
        [{"id": "PSI-69", "name": "FLEX", "description": "droplet extinction suppression", "files_downloaded": 2}],
        application="suppression",
        query="droplet extinction",
        language="en",
    )
    assert len(ranked) == 1
    assert ranked[0]["score"] > 50


def test_streamlit_config_and_design_tokens() -> None:
    config = tomllib.loads((ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8"))
    assert config["client"]["toolbarMode"] == "viewer"
    assert config["client"]["showErrorDetails"] == "none"
    assert design_system.DESIGN_TOKENS["accent_flame"] == "#B84A24"
    assert design_system.DESIGN_TOKENS["ink_primary"] == "#0F1D2B"


def test_app_ux_topbar_hub_and_no_dev_jargon() -> None:
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=90).run()
    assert not app.exception

    # Top bar controls present
    btn_keys = {b.key for b in app.button}
    assert "topbar-home-btn" in btn_keys
    assert "topbar-back-btn" in btn_keys
    assert "topbar-lang-toggle" in btn_keys

    # Challenge Hub tabs & clean end-user copy
    tab_labels = [tb.label for tb in app.tabs]
    assert i18n.t("hub.tab_summarize", "en") in tab_labels
    assert i18n.t("hub.tab_rank", "en") in tab_labels
    assert i18n.t("hub.tab_interpret", "en") in tab_labels

    # Primary text excludes developer tokens
    primary_text = "\n".join([
        *[str(x.value) for x in app.title],
        *[str(x.value) for x in app.header],
        *[str(x.value) for x in app.markdown],
        *[str(x.value) for x in app.info],
    ])
    for forbidden in ("SQLite + SHA-256", "lexical vectors", "lexical-vectors"):
        assert forbidden not in primary_text

    # Top bar language toggle flips cleanly EN -> PT-BR -> EN without selectbox errors
    app = next(b for b in app.button if b.key == "topbar-lang-toggle").click().run()
    assert not app.exception
    assert app.session_state["lang"] == "pt"
    assert app.radio(key="lang_selector").value == "pt"
    app = next(b for b in app.button if b.key == "topbar-lang-toggle").click().run()
    assert not app.exception
    assert app.session_state["lang"] == "en"
    assert app.radio(key="lang_selector").value == "en"
    app = next(b for b in app.button if b.key == "topbar-lang-toggle").click().run()
    assert not app.exception
    assert app.session_state["lang"] == "pt"

    # Launch Journey 1 and verify 5-question comprehension structure
    app = next(b for b in app.button if b.key == "home-start-j1").click().run()
    assert not app.exception
    j_text = "\n".join([str(x.value) for x in app.subheader] + [str(x.value) for x in app.markdown])
    assert i18n.t("journey.q_heading", "pt") in j_text
    assert i18n.t("journey.q_exploring", "pt") in j_text
    assert i18n.t("journey.q_limitations", "pt") in j_text
