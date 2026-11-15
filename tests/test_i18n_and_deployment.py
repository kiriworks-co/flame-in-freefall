"""Tests for EN/PT-BR localization parity, language persistence, read-only public mode, and cold-start bootstrap."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from streamlit.testing.v1 import AppTest

from src import i18n, pipeline, retrieval, storage

ROOT = Path(__file__).resolve().parents[1]


def test_translation_key_parity_and_non_empty() -> None:
    en_keys = set(i18n.TRANSLATIONS["en"])
    pt_keys = set(i18n.TRANSLATIONS["pt"])
    assert en_keys == pt_keys, f"Missing keys: en-pt={en_keys - pt_keys}, pt-en={pt_keys - en_keys}"
    for lang, mapping in i18n.TRANSLATIONS.items():
        for key, value in mapping.items():
            assert isinstance(value, str) and value.strip(), f"Empty translation for {lang}.{key}"


def test_domain_label_helpers_and_navigation_normalization() -> None:
    assert i18n.normalize_section("Visão geral") == "home"
    assert i18n.normalize_section("Arquivos do experimento") == "explorer"
    assert i18n.normalize_section("investigations") == "investigations"
    assert i18n.normalize_section("unknown") == "home"

    for kind in ("condition", "sample", "measurement", "calculation", "inference", "document_context"):
        assert i18n.evidence_label(kind, "en") != i18n.evidence_label(kind, "pt")
    assert i18n.quantity_label("oxygen", "en") == "oxygen"
    assert i18n.quantity_label("oxygen", "pt") == "oxigênio"
    assert i18n.translate_comparison_reason("Selecione duas ou três tabelas.", "en") == "Select two or three tables."
    assert "Application match:" in i18n.translate_relevance_reason("Aplicação: termo +30", "en")
    assert "re-indexing recommended" in i18n.translate_retrieval_warning("Índice criado com outro modelo: reindexação necessária", "en")
    profile_en = i18n.investigation_profile("PSI-69", "en")
    profile_pt = i18n.investigation_profile("PSI-69", "pt")
    assert profile_en["pillar"] == "Suppression"
    assert profile_pt["pillar"] == "Supressão"


def test_app_defaults_to_english_and_switches_to_portuguese_consistently() -> None:
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=90).run()
    assert not app.exception
    assert app.session_state["lang"] == "en"
    assert any(i18n.t("home.title", "en") == header.value for header in app.title)

    # Navigate to Investigations in English and ensure original NASA study names stay intact
    app.radio(key="workspace_section").set_value("investigations").run()
    assert not app.exception
    assert any("PSI-69" in sub.value for sub in app.subheader)

    # Switch to Portuguese (PT-BR) and confirm persistence on the active section
    app.radio(key="lang_selector").set_value("pt").run()
    assert not app.exception
    assert app.session_state["lang"] == "pt"
    assert app.radio(key="workspace_section").value == "investigations"
    assert any(i18n.t("inv.title", "pt") == title.value for title in app.title)
    assert any("PSI-69" in sub.value for sub in app.subheader)


def test_public_readonly_mode_disables_uploads_and_mutations(monkeypatch) -> None:
    monkeypatch.setenv("PSI_READONLY_MODE", "1")
    assert pipeline.is_public_readonly() is True

    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=90).run()
    assert not app.exception

    app.radio(key="workspace_section").set_value("explorer").run()
    assert not app.exception
    assert any(i18n.t("exp.readonly_notice", "en") in info.value for info in app.info)
    assert not any(b.label == i18n.t("docs.import_btn", "en") for b in app.button)
    assert not any(b.label == i18n.t("docs.reprocess_btn", "en") for b in app.button)

    app.radio(key="workspace_section").set_value("sources").run()
    assert not app.exception
    assert any(i18n.t("src.ingestion_readonly", "en") in info.value for info in app.info)
    assert not any(b.label == i18n.t("src.ingestion_btn", "en") for b in app.button)


def test_bootstrap_initializes_from_committed_artifacts(tmp_path: Path, monkeypatch) -> None:
    project_dir = tmp_path / "clean_clone"
    manifest_dir = project_dir / "resources" / "manifests"
    dl_dir = project_dir / "data" / "psi_downloads" / "PSI-999"
    manifest_dir.mkdir(parents=True)
    dl_dir.mkdir(parents=True)

    sample_csv = b"O2;Pressure_psia;Velocity_cm_s\n0.21;14.7;10\n"
    sha = storage.sha256_bytes(sample_csv)
    (dl_dir / "sample.csv").write_bytes(sample_csv)
    (manifest_dir / "priority_investigations.json").write_text(
        json.dumps({
            "investigations": [{
                "id": "PSI-999",
                "name": "Synthetic Portability Test Study",
                "category": "Suppression",
                "description": "Verifies cold-start SQLite bootstrap.",
                "nasa_record_url": "https://psi.nasa.gov/physci/repo/data/investigations/PSI-999",
            }]
        }),
        encoding="utf-8",
    )
    (dl_dir / "source_manifest.json").write_text(
        json.dumps({
            "investigation_id": "PSI-999",
            "study_id": "PSI-999",
            "source_url": "https://psi.nasa.gov/physci/repo/data/investigations/PSI-999",
            "downloaded_csvs": [{
                "filename": "sample.csv",
                "sha256": sha,
                "size_bytes": len(sample_csv),
                "classification": "condition",
                "source_url": "https://psi.nasa.gov/physci/repo/data/investigations/PSI-999",
            }],
        }),
        encoding="utf-8",
    )

    monkeypatch.setattr(storage, "PROJECT_DIR", project_dir)
    monkeypatch.setattr(storage, "DATA_DIR", project_dir / "data" / "experimentos")

    db_path = project_dir / "data" / "scientific.sqlite3"
    search_db = project_dir / "data" / "search.sqlite3"
    summary = pipeline.ensure_scientific_bootstrap(project_dir=project_dir, db_path=db_path, search_db_path=search_db)

    assert db_path.exists()
    assert search_db.exists()
    assert summary["bootstrapped"] is True
    assert summary["chunks"] > 0

    with sqlite3.connect(db_path) as conn:
        inv_count = conn.execute("SELECT count(*) FROM investigations").fetchone()[0]
        orig_path, ext_path = conn.execute("SELECT original_path, extraction_path FROM documents").fetchone()
    assert inv_count == 1
    assert "\\" not in orig_path and "\\" not in ext_path
    assert orig_path.startswith("data/experimentos/")
    assert ext_path.startswith("data/experimentos/")

    # Second run is a quick no-op
    second = pipeline.ensure_scientific_bootstrap(project_dir=project_dir, db_path=db_path, search_db_path=search_db)
    assert second["bootstrapped"] is False


def test_no_user_specific_paths_in_committed_metadata() -> None:
    meta = json.loads((ROOT / "data" / "embedding_model.json").read_text(encoding="utf-8"))
    serialized = json.dumps(meta)
    assert "local_path" not in meta
    assert "C:\\" not in serialized
    assert "Users\\" not in serialized
    assert "/home/" not in serialized
    assert retrieval._model_mode_id("/home/runner/.cache/paraphrase-multilingual-MiniLM-L12-v2") == (
        "local-semantic:paraphrase-multilingual-MiniLM-L12-v2"
    )
