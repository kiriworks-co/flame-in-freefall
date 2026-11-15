"""UI provenance and navigation checks; helper fixtures are synthetic metadata."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from src import scientific_ui

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("url", [
    "javascript:alert(1)", "https://user:password@example.org/file",
    "https://example.org/file?X-Amz-Signature=expired",
    "http://example.org/file", None,
])
def test_external_links_reject_executable_credentials_and_signed_urls(url):
    assert scientific_ui._safe_url(url) is None


def test_doi_and_permanent_source_links():
    assert scientific_ui._safe_url("https://psi.nasa.gov/physci/repo/data/investigations/PSI-69")
    assert scientific_ui._doi_url("10.60555/mbq8-0451") == "https://doi.org/10.60555/mbq8-0451"
    assert scientific_ui._doi_url("https://evil.example/unknown") is None


def test_catalog_coverage_uses_actual_archived_documents(monkeypatch):
    def fake_json(path, default):
        return {"investigations": [{"id": "TEST-1", "name": "Synthetic fixture"}]} if path.name == "priority_investigations.json" else {}

    monkeypatch.setattr(scientific_ui, "_json", fake_json)
    row = scientific_ui.catalog([{"id": "internal", "psi_id": "TEST-1", "documents": [{"name": "fictional.csv"}]}])[0]
    assert row["document_count"] == 1
    assert len(row["documents"]) == 1


def test_document_field_caveats_are_visible_data():
    document = {"name": "PSI-69_Engineering Documents_FLEX Engineering Requirements Document.pdf",
                "provenance": {"field_classification": [{"header": "Burning rate; mm", "warning": "Unresolved dimensional unit"}]}}
    warnings = scientific_ui._document_notices("PSI-69", document)
    assert any("FLEX-2" in warning for warning in warnings)
    assert any("Burning rate; mm" in warning for warning in warnings)


@pytest.mark.integration
def test_nasa_catalog_opens_existing_study():
    from src.storage import list_experiments
    experiments = list_experiments()
    flex = next((e for e in experiments if e.get("psi_id") == "PSI-69" and e.get("documents")), None)
    if not flex:
        pytest.skip("Run NASA downloads and ingestion first")
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=90).run()
    app.radio(key="workspace_section").set_value("investigations").run()
    app.button(key="nasa-open-PSI-69").click().run()
    assert not app.exception
    assert app.radio(key="workspace_section").value == "explorer"
    assert app.session_state["active_experiment_id"] == flex["id"]
