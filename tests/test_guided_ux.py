"""UX regression tests for discovery-first home, guided journeys, chart guides, and bilingual parity."""
from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

from src import i18n

ROOT = Path(__file__).resolve().parents[1]


def _run_app(timeout: int = 90) -> AppTest:
    return AppTest.from_file(str(ROOT / "app.py"), default_timeout=timeout).run()


def _btn(app: AppTest, key: str):
    return next(b for b in app.button if b.key == key)


def _radio(app: AppTest, key: str):
    return next(r for r in app.radio if r.key == key)


def _all_text(app: AppTest) -> str:
    parts = [
        *[str(x.value) for x in app.title],
        *[str(x.value) for x in app.header],
        *[str(x.value) for x in app.subheader],
        *[str(x.value) for x in app.markdown],
        *[str(x.value) for x in app.caption],
        *[str(x.value) for x in app.info],
        *[str(x.value) for x in app.warning],
    ]
    return "\n".join(parts)


def test_discovery_home_and_three_experiences() -> None:
    app = _run_app()
    assert not app.exception

    assert any(i18n.t("home.title", "en") == title.value for title in app.title)
    text = _all_text(app)
    assert i18n.t("home.subtitle", "en") in text
    assert i18n.t("home.exp_a_title", "en") in text
    assert i18n.t("home.exp_b_title", "en") in text
    assert i18n.t("home.exp_c_title", "en") in text

    for key in ("home-start-j1", "home-start-j2", "home-open-explorer", "home-open-assistant", "home-open-studies"):
        assert _btn(app, key) is not None

    assert _radio(app, "interaction_mode").value == "guided"


def test_guided_journey_1_full_progression_and_handoff() -> None:
    app = _run_app()
    app = _btn(app, "home-start-j1").click().run()
    assert not app.exception
    assert "Step 1 of 4" in _all_text(app)
    assert _btn(app, "gj_journey_1_back_1").disabled

    app = _radio(app, "gj_j1_s1_aspect").set_value("temp").run()
    assert not app.exception
    assert "cool flames" in _all_text(app).lower()

    app = _btn(app, "gj_journey_1_next_1").click().run()
    assert not app.exception
    assert "Step 2 of 4" in _all_text(app)
    assert "FLEX" in _all_text(app)

    app = _btn(app, "gj_journey_1_next_2").click().run()
    assert not app.exception
    assert "Step 3 of 4" in _all_text(app)
    assert i18n.t("chart_guide.title", "en") in _all_text(app)

    app = _radio(app, "gj_j1_s3_view").set_value("burning").run()
    assert not app.exception
    assert "Burning rate; mm" in _all_text(app)

    app = _btn(app, "gj_journey_1_next_3").click().run()
    assert not app.exception
    assert "Step 4 of 4" in _all_text(app)
    assert _btn(app, "gj_journey_1_next_4").disabled

    # Verify Back & Continue state persistence
    app = _btn(app, "gj_journey_1_back_4").click().run()
    assert "Step 3 of 4" in _all_text(app)
    app = _btn(app, "gj_journey_1_next_3").click().run()
    assert "Step 4 of 4" in _all_text(app)

    # Handoff to Data Explorer keeps Return to Journey button
    app = _btn(app, "gj_j1_to_explorer").click().run()
    assert not app.exception
    assert _radio(app, "workspace_section").value == "explorer"
    app = _btn(app, "active-return-journey").click().run()
    assert _radio(app, "workspace_section").value == "home"
    assert "Step 4 of 4" in _all_text(app)


def test_guided_journey_2_full_progression_and_pillars() -> None:
    app = _run_app()
    app = _btn(app, "home-start-j2").click().run()
    assert not app.exception
    assert "Step 1 of 4" in _all_text(app)

    app = _btn(app, "gj_journey_2_next_1").click().run()
    assert not app.exception
    assert "Step 2 of 4" in _all_text(app)
    for pillar in ("prevention", "detection", "suppression"):
        app = _radio(app, "gj_j2_s2_pillar").set_value(pillar).run()
        assert not app.exception

    app = _btn(app, "gj_journey_2_next_2").click().run()
    assert not app.exception
    assert "Step 3 of 4" in _all_text(app)
    for focus in ("bass", "same", "compare"):
        app = _radio(app, "gj_j2_s3_focus").set_value(focus).run()
        assert not app.exception
    assert "BASS-II" in _all_text(app) and "FLEX" in _all_text(app)

    app = _btn(app, "gj_journey_2_next_3").click().run()
    assert not app.exception
    assert "Step 4 of 4" in _all_text(app)

    app = _btn(app, "gj_j2_to_compare").click().run()
    assert not app.exception
    assert _radio(app, "workspace_section").value == "compare"


def test_chart_explanation_and_progressive_disclosure_in_explorer() -> None:
    app = _run_app()
    app = _radio(app, "workspace_section").set_value("explorer").run()
    assert not app.exception

    # Default explorer opens Tab 0 ("Overview"), switch interaction mode to advanced cleanly too
    assert i18n.t("chart_guide.title", "en") in _all_text(app)
    app = _radio(app, "interaction_mode").set_value("advanced").run()
    assert not app.exception
    assert i18n.t("chart_guide.title", "en") in _all_text(app)


def test_assistant_example_autorun_and_plain_summary() -> None:
    app = _run_app()
    app = _radio(app, "workspace_section").set_value("assistant").run()
    assert not app.exception

    app = _btn(app, "ast-ex1").click().run()
    assert not app.exception
    text = _all_text(app)
    assert i18n.t("ast.results_header", "en") in text
    assert i18n.t("ast_guide.summary_title", "en") in text


def test_bilingual_portuguese_guided_journey_and_no_raw_keys() -> None:
    app = _run_app()
    app = _radio(app, "lang_selector").set_value("pt").run()
    assert not app.exception
    assert any(i18n.t("home.title", "pt") == title.value for title in app.title)

    app = _btn(app, "home-start-j1").click().run()
    assert not app.exception
    text = _all_text(app)
    assert "Passo 1 de 4" in text
    for prefix in ("home.", "j1.", "j2.", "chart_guide.", "ast_guide.", "glossary."):
        assert prefix not in text
