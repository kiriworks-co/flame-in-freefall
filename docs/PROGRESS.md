# PROGRESS — Retomada de sessões

## Estado atual
- **Repositório Git isolado**: inicializado na raiz de `PROJETO TESTE FLAME MICROGRAVITY` com branch `main` (commit baseline `880145a`) e branch de desenvolvimento `feat/spaceapps-public-release`.
- **Portabilidade e deploy público**:
  - `.python-version` (`3.11`) e `.streamlit/config.toml` ajustados para nuvem (sem `address = "127.0.0.1"`).
  - Caminho absoluto de usuário removido de `data/embedding_model.json` e `scripts/setup_embeddings.py`; `src/pipeline.py` e `src/local_jobs.py` persistem caminhos relativos POSIX via `_portable_path()`.
  - `src/retrieval.py` normaliza identificador de modelo via `_model_mode_id()` e migra entradas legadas automaticamente.
  - `src/pipeline.py` adiciona `is_public_readonly()` e `ensure_scientific_bootstrap()` para inicialização automática de `scientific.sqlite3` e `search.sqlite3` no cold start (~5.7 s sem `.env` ou banco prévio).
  - `src/extractors.py` atualizado para `import pymupdf as fitz` (eliminando `FutureWarning`).
- **Internacionalização centralizada (`src/i18n.py`)**:
  - Padrão inicial **English (`en`)** com alternador visível **`English (EN)` / `Português (PT-BR)`** na barra lateral persistido em `st.session_state`.
  - Traduções centralizadas para navegação canônica, cards dos 9 estudos PSI + guias NASA, glossário, gráficos/tabelas, comparador, ranking, assistente, revisão visual e metodologia — mantendo intactos títulos NASA, DOIs, hashes SHA-256, cabeçalhos originais e valores brutos.
- **Redesign de UX (`app.py`, `src/scientific_ui.py`, `src/views.py`)**:
  - Navegação intuitiva em 7 áreas (`Home / Overview`, `Investigations`, `Data Explorer`, `Compare`, `Scientific Assistant`, `Visual Page Review`, `Sources & Methodology`).
  - `Home / Overview` com explicação de microgravidade (*Flame in Freefall*), 3 pilares (*Prevenção / Detecção / Supressão*) e tour guiado em 4 passos.
  - `Data Explorer` com seletor direto no topo (padrão `PSI-69`), glossário colapsável de variáveis/unidades e proteção `is_public_readonly()` que desabilita uploads/mutações em ambiente público.
  - `Scientific Assistant` com 5 perguntas de exemplo clicáveis e divulgação explícita quando o LLM externo está não configurado.
  - Página estática opcional bilíngue para GitHub Pages criada em `docs/index.html`.
- **Próxima ação manual do usuário**: enviar os commits para o GitHub e conectar `app.py` no Streamlit Community Cloud conforme `docs/DEPLOYMENT.md` e `docs/ANTIGRAVITY_HANDOFF.md`.
