"""Smoke public navigation with the real Streamlit testing runtime."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("section", [
    "Visão geral", "Investigações NASA", "Busca e assistente",
    "Comparar estudos", "Ingestão e fontes", "Arquivos do experimento"])
def test_global_navigation(section):
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
    assert not app.exception
    app.radio(key="workspace_section").set_value(section).run()
    assert not app.exception


def test_question_returns_visible_evidence_or_insufficiency():
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
    app.radio(key="workspace_section").set_value("Busca e assistente").run()
    next(b for b in app.button if b.label == "Pesquisar evidências").click().run()
    assert not app.exception
    assert any("Resposta e evidências" == h.value for h in app.header)
