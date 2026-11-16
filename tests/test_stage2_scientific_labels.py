"""Scientific display contracts; small metadata fixtures are not NASA measurements."""
from __future__ import annotations

from contextlib import nullcontext

import pytest

from src import guided_journeys, storage
from src.challenge_engine import build_spacecraft_interpretation
from src.i18n import evidence_label


@pytest.mark.parametrize("kind", ["simulation", "reported_result", "derived", "metadata", "condition"])
@pytest.mark.parametrize("lang", ["en", "pt"])
def test_chart_explainer_preserves_selected_source_classification(monkeypatch, kind, lang):
    rendered = []
    monkeypatch.setattr(guided_journeys.st, "container", lambda **kwargs: nullcontext())
    monkeypatch.setattr(guided_journeys.st, "markdown", rendered.append)
    entry = {"document": {"name": "Synthetic classification fixture", "evidence_kind": "mixed_experiment_and_simulation"},
             "table": {"columns": ["t", "value"], "evidence_kind": "mixed_experiment_and_simulation",
                       "field_classification": [{"column_index": 0, "role": "condition"},
                                                {"column_index": 1, "role": kind}]}}
    roles = guided_journeys.chart_evidence_roles(entry, ["t", "value"])
    assert roles == {"t": "condition", "value": kind}
    guided_journeys.render_chart_explanation(entry, "t", ["value"], {"kind": "numeric"},
        [{"name": "value", "kind": "numeric", "quantity": "unknown"}], None, {"psi_id": "TEST-ONLY"}, lang)
    output = "\n".join(rendered)
    assert evidence_label(kind, lang) in output
    assert ("unit not declared" if lang == "en" else "unidade não declarada") in output
    assert "measured quantities" not in output and "grandezas medidas" not in output
    assert "mixed table" not in output and "tabela mista" not in output


@pytest.mark.parametrize("lang", ["en", "pt"])
def test_missing_numeric_unit_never_becomes_dimensionless(lang):
    assert guided_journeys.extract_display_unit("t", {"kind": "numeric"}, lang) == (
        "unit not declared" if lang == "en" else "unidade não declarada")
    assert guided_journeys.extract_display_unit("Time(sec)", None, lang) == "sec"
    assert guided_journeys.extract_display_unit("T_max(K)", None, lang) == "K"
    assert guided_journeys.extract_display_unit("Burning rate; mm", None, lang) == "mm"


@pytest.mark.parametrize("lang", ["en", "pt"])
def test_simulation_interpretation_is_separate_from_reported_experiments(lang):
    for kinds in (["simulation"], ["mixed_experiment_and_simulation", "engineering_or_publication"]):
        experiment = {"psi_id": "PSI-117", "documents": [{"evidence_kind": k} for k in kinds]}
        text = build_spacecraft_interpretation(experiment, lang)["observation_scope"]
        assert ("simulação numérica" if lang == "pt" else "numerical simulation") in text
        assert ("não são medições" if lang == "pt" else "not measurements") in text
        assert "combines reported experimental outcomes" not in text
    metadata = build_spacecraft_interpretation({"psi_id": "PSI-62", "documents": [{"evidence_kind": "metadata"}]}, lang)
    assert ("apenas metadados" if lang == "pt" else "metadata and bibliographic references only") in metadata["observation_scope"]


@pytest.mark.integration
def test_actual_stage2_archive_summaries_keep_scientific_nature():
    experiments = {e.get("psi_id"): e for e in storage.list_experiments()}
    # Required source artifacts make these studies available after the real import.
    assert "PSI-62" in experiments and "PSI-117" in experiments
    assert "references only" in build_spacecraft_interpretation(experiments["PSI-62"], "en")["observation_scope"]
    assert "numerical simulation" in build_spacecraft_interpretation(experiments["PSI-117"], "en")["observation_scope"]
