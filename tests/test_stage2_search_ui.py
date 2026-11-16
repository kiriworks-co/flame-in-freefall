"""Real Stage 2 NASA originals: extraction → indexing → evidence → interface.

The isolated corpus is copied from committed, checksum-verified source files.
No network/provider access and no invented scientific measurements are used.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from src import pipeline, storage, views
from src.assistant import answer, validate_claims
from src.comparison import compare_tables
from src.i18n import evidence_label, investigation_profile
from src.retrieval import RetrievalIndex

ROOT = Path(__file__).resolve().parents[1]
STUDIES = ("PSI-62", "PSI-117", "PSI-159")


@pytest.fixture(scope="module")
def stage2_corpus(tmp_path_factory):
    temp = tmp_path_factory.mktemp("nasa-stage2-search")
    project = temp / "project"
    patch = pytest.MonkeyPatch()
    patch.setenv("RAG_EMBEDDING_MODEL", " ")
    patch.setenv("PSI_READONLY_MODE", "1")
    patch.setattr(storage, "DATA_DIR", temp / "archive")

    def forbidden_network(*args, **kwargs):
        raise AssertionError("Stage 2 offline validation cannot access a provider")

    patch.setattr("urllib.request.urlopen", forbidden_network)
    manifests = {}
    expected = 0
    for sid in STUDIES:
        original_dir = ROOT / "data/psi_downloads" / sid
        manifest = json.loads((original_dir / "source_manifest.json").read_text(encoding="utf-8"))
        manifests[sid] = manifest
        dest = project / "data/psi_downloads" / sid
        dest.mkdir(parents=True)
        shutil.copyfile(original_dir / "source_manifest.json", dest / "source_manifest.json")
        for key in ("downloaded_csvs", "downloaded_pdfs", "downloaded_documents"):
            for record in manifest.get(key, []):
                source = original_dir / record["filename"]
                assert hashlib.sha256(source.read_bytes()).hexdigest() == record["sha256"]
                target = dest / record["filename"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
                expected += 1
    catalog_dir = project / "resources/manifests"
    catalog_dir.mkdir(parents=True)
    source_catalog = json.loads((ROOT / "resources/manifests/priority_investigations.json").read_text(encoding="utf-8"))
    (catalog_dir / "priority_investigations.json").write_text(json.dumps({
        "investigations": [i for i in source_catalog["investigations"] if i["id"] in STUDIES],
    }), encoding="utf-8")
    try:
        imported = pipeline.ingest_downloads(project, temp / "science.sqlite3", index_search=False)
        assert not imported["errors"], imported["errors"]
        assert imported["imported"] == expected
        experiments = storage.list_experiments()
        index = RetrievalIndex(temp / "search.sqlite3")
        indexed = index.index_experiments(experiments)
        assert not indexed["failures"]
        assert indexed["total"] > 100
        assert index.index_experiments(experiments)["indexed"] == 0
        yield experiments, index, manifests
    finally:
        views.clear_cache()
        patch.undo()


@pytest.mark.parametrize("sid,query,needle", [
    ("PSI-62", "unsteady flamelet generated manifold tomography BASS", "flamelet"),
    ("PSI-117", "Oscillatory Cool Flame", "cool"),
    ("PSI-159", "spherical cool diffusion propane", "flame"),
])
@pytest.mark.integration
def test_real_stage2_question_returns_verified_source(stage2_corpus, sid, query, needle):
    experiments, index, manifests = stage2_corpus
    result = answer(query, index, study_ids=[sid], language="en", use_llm=False)
    assert not result["insufficient"] and result["mode"] == "offline-evidence"
    assert any(needle in e["text"].casefold() for e in result["evidence"])
    experiment = next(e for e in experiments if e["psi_id"] == sid)
    hashes = {d["sha256"] for d in experiment["documents"]}
    for source in result["evidence"]:
        assert source["study_id"] == sid and source["sha256"] in hashes
        assert source["doi"] == manifests[sid]["doi"]
        assert source["source_url"] == f"https://psi.nasa.gov/physci/repo/data/investigations/{sid}"
        assert source["location"]
        if source["kind"] == "page":
            document = next(d for d in experiment["documents"] if d["sha256"] == source["sha256"])
            pages = storage.load_extraction(experiment, document)["pages"]
            assert any(source["text"] in p["text"] for p in pages if p["page"] == source["page"])
        claims, rejected = validate_claims({"claims": [{"citation": source["id"],
            "quote": source["text"], "kind": source["evidence_kind"]}]}, result["evidence"], "en")
        assert claims and not rejected
    if sid == "PSI-62":
        assert all(e["evidence_kind"] == "metadata" for e in result["evidence"])
    assert answer("quasizebraunobtainium", index, study_ids=[sid])["insufficient"]


@pytest.mark.integration
def test_simulation_filters_and_grounding_keep_evidence_nature(stage2_corpus):
    _, index, _ = stage2_corpus
    result = answer("", index, study_ids=["PSI-117"], use_llm=False, language="en", numeric_filters=[
        {"field": "temperature", "unit": "K", "min": 500, "max": 700, "evidence_kind": "simulation"},
    ])
    assert result["evidence"] and any("numerical simulations" in w for w in result["warnings"])
    for source in result["evidence"]:
        assert source["kind"] == "table_row"
        assert any(o["evidence_kind"] == "simulation" for o in source["observations"])
    source = next(e for e in result["evidence"] if e["evidence_kind"] == "simulation")
    accepted, errors = validate_claims({"claims": [{"citation": source["id"],
        "quote": source["text"], "kind": "measurement"}]}, result["evidence"], "en")
    assert not accepted and errors


@pytest.mark.integration
def test_original_series_pairing_and_comparison_guards(stage2_corpus):
    experiments, _, _ = stage2_corpus
    experiment = next(e for e in experiments if e["psi_id"] == "PSI-117")
    entries = views.collect_entries(experiment)
    paired = next(e for e in entries if "Burning_history" in e["document"]["name"] and
                  len([m for m in e["table"]["column_meta"] if m["quantity"] == "time"]) == 2)
    frame, meta = views.entry_frame(paired, entries, {})
    axes = [m["name"] for m in meta if m["quantity"] == "time"]
    first_y = views.paired_y_columns(meta, axes[0])
    second_y = views.paired_y_columns(meta, axes[1])
    assert len(first_y) == len(second_y) == 1 and first_y != second_y
    assert set(axes).isdisjoint(first_y + second_y)
    assert all(y in frame.columns for y in first_y + second_y)
    # Bare time units in this original remain undeclared: no common-axis overlay.
    prepared = [{"meta": meta, "x": x, "ys": ys} for x, ys in zip(axes, [first_y, second_y])]
    assert not views.comparable_plot_axes(prepared)
    # Missing experimental methods/units cannot turn simulations into pooled measurements.
    comparison = compare_tables([{**e, "study_id": "PSI-117"} for e in entries[:2]])
    assert not comparison["compatible"] and comparison["reasons"]


@pytest.mark.integration
def test_real_new_studies_open_from_catalog_and_render_metadata(stage2_corpus, tmp_path):
    experiments, _, _ = stage2_corpus
    script = """
import streamlit as st
from src import storage, scientific_ui, views
experiments = storage.list_experiments()
if st.session_state.get('workspace_section') == 'explorer':
    experiment = next(e for e in experiments if e['id'] == st.session_state['active_experiment_id'])
    views.show_study_overview(experiment)
    views.show_metadata(experiment)
else:
    scientific_ui.show_catalog(experiments)
"""
    script_path = tmp_path / "stage2_catalog_ui.py"
    script_path.write_text(script, encoding="utf-8")
    for sid in STUDIES:
        app = AppTest.from_file(str(script_path), default_timeout=90).run()
        assert not app.exception
        app.button(key=f"nasa-open-{sid}").click().run()
        assert not app.exception
        assert app.session_state["active_experiment_id"] == next(e["id"] for e in experiments if e["psi_id"] == sid)
        assert any(sid in heading.value or investigation_profile(sid, "en")["objective"] in heading.value
                   for heading in app.markdown) or any("UFGM" in text.value for text in app.markdown)


def test_stage2_profiles_and_nature_labels_are_bilingual():
    for sid in STUDIES:
        en, pt = investigation_profile(sid, "en"), investigation_profile(sid, "pt")
        assert set(en) == set(pt) == {"pillar", "objective", "relevance", "caveat"}
        assert en["objective"] != pt["objective"] and en["caveat"] != pt["caveat"]
    for kind in ("simulation", "metadata", "mixed_experiment_and_simulation"):
        assert evidence_label(kind, "en") != kind
        assert evidence_label(kind, "pt") != kind
