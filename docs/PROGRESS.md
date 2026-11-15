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
- **Redesign de UX Orientado à Descoberta (`src/guided_journeys.py`, `src/scientific_ui.py`, `src/views.py`, `app.py`)**:
  - **Home orientada à descoberta**: Título *"Explore the Science of Fire in Space"*, explicação simples de `1g` vs. `~0g`, glossário introdutório opcional e 3 experiências iniciais explícitas (**A. Discover How Fire Behaves**, **B. Investigate Spacecraft Fire Safety**, **C. Explore Scientific Data**).
  - **Duas Jornadas Guiadas em 4 passos (`src/guided_journeys.py`)**: *Journey 1* (física de queda livre, `PSI-69 · FLEX`, prévia PDF p. 36, gráfico Plotly interativo + guia de leitura e achados/limitações) e *Journey 2* (risco espacial, seletor de 3 pilares Prevenção/Detecção/Supressão, evidências `PSI-25 · BASS-II`, `PSI-102 · SAME` p. 13 e alerta metodológico), com persistência em `st.session_state`, controles `← Back` / `Continue →` e botão de retorno contínuo ao visitar seções avançadas.
  - **Divulgação progressiva (`Guided Exploration` vs. `Advanced Research`)**: seletor de nível de experiência na barra lateral ocultando controles `⚙ ...`, filtros numéricos, diagnósticos de índice e caminhos locais sob painéis recolhidos para iniciantes.
  - **Explicação de gráficos e resultados**: componente *"How to Read This Chart"* exibido abaixo dos gráficos no Data Explorer e nas jornadas (eixos, unidades, papel dos dados e ressalvas como `'Burning rate; mm'`); no Assistente Científico, perguntas de exemplo executam imediatamente com *"Plain-Language Guide to These Results"* acima das citações.
  - **Bootstrap & chunks verificados**: `src/pipeline.py` atualiza automaticamente o índice semântico local (**2,711 trechos por janela de tokens** com `paraphrase-multilingual-MiniLM-L12-v2`) quando `.env` aponta modelo local, mantendo **1,517 segmentos estruturais** determinísticos (`lexical-vectors`) em clones limpos ou nuvem sem peso de modelo.
  - **Regressão & QA**: `tests/test_guided_ux.py` (6 testes E2E de jornada/UX/PT-BR), totalizando **105 testes passando** offline e validação ao vivo no navegador desktop (`1440x1000`) e mobile (`375x812`).
  - Página estática opcional bilíngue para GitHub Pages em `docs/index.html`.
- **Próxima ação manual do usuário**: enviar os commits para o GitHub e conectar `app.py` no Streamlit Community Cloud conforme `docs/DEPLOYMENT.md` e `docs/ANTIGRAVITY_HANDOFF.md`.
