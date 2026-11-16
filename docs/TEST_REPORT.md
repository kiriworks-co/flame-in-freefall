# Test & Verification Report — Etapa 3 (`feat/spaceapps-public-release`)

## Validação Final de Engenharia, UX/UI e Gemini (Etapa 3 — 2026-11-15)

Ambiente validado: Windows, `.venv` Python **3.12.14** (portabilidade fixada em Python **3.11** via `.python-version`).

| Verificação | Resultado | Observações |
|---|---|---|
| Suíte `pytest` completa (offline) | **164 passed in 179.45s** | Inclui novos testes de cota por sessão/servidor Gemini, explicação ancorada e seletor único de idioma |
| Suíte UI/i18n/Gemini pós-ajuste visual | **39 passed in 38.60s** | Revalida `test_gemini_and_challenge.py`, `test_guided_ux.py`, `test_i18n_and_deployment.py`, `test_app.py` e `test_ui_details.py` após último ajuste CSS/Hub |
| Ruff (`app.py src scripts tests`) | **All checks passed!** | Zero avisos de estilo/lint |
| Mypy ampliado (19 arquivos) | **Success: no issues found in 19 source files** | Cobre frontend, backend científico, Gemini, scripts CLI e testes |
| `compileall` & `pip check` | **Exit 0 / No broken requirements** | Árvore de dependências limpa |
| Scripts Gemini (`setup_gemini.py`, `gemini_live_check.py`) | **Validados em modo UNCONFIGURED** | Sem chave ativa local; fallback offline confirmado |
| Auditoria de segredos / caminhos privados | **0 ocorrências** | `.env`, `.streamlit/secrets.toml` e `*.sqlite3` fora do Git |
| Navegador real (`http://127.0.0.1:8511`) | **Desktop `1440×900` & Mobile `390×844` aprovados** | Zero exceções, diagrama `1g vs ~0g` visível, 3 cartões de entrada com altura idêntica (`224.95px`), 4 métricas em linha única, zero overflow horizontal (`390px`), `EN ↔ PT-BR`, Jornada 1 + `Voltar`/`Início`, `PSI-69`/`117`/`159`/`62` e Assistente |

---

## Histórico — Etapa 2 (`feat/spaceapps-public-release`)

## Validação científica em 2026-11-15

Ambiente efetivamente usado nesta etapa: Windows, Python **3.12.14** na `.venv`.
Python 3.11 continua sendo a versão alvo de portabilidade; não foi executada
uma segunda matriz Python 3.11 nesta sessão.

| Verificação | Resultado |
|---|---|
| Suíte completa final | **161 passed in 243.83s**, sem falhas |
| Ruff | Aprovado em app.py, src, scripts e tests |
| Mypy ampliado | Aprovado em 15 arquivos, incluindo ingestão, armazenamento, unidades e recuperação |
| compileall | Exit 0 |
| pip check | No broken requirements found |
| Proveniência e replay | Originais NASA conferidos por SHA-256; replay sem alterações de conteúdo |
| Ingestão idempotente real | 0 importados, 40 existentes, errors vazio |
| SQLite | 13 registros (12 PSI + contexto), 40 documentos, foreign_key_check vazio |
| E2E novos originais | Os 24 documentos foram reextraídos e indexados em cópia isolada; RAG/DOI/hash/localizações e filtros validados |
| Embeddings reais | 15.524 chunks FTS5/384 dimensões; três estudos, filtro de simulação e insuficiência de evidência aprovados |
| Integridade no Git | 83 SHA-256 conferidos diretamente nos blobs preparados; atributos preservam bytes dos originais |
| Navegador real | Chromium desktop 1280×900 e mobile 390×844; catálogo/explorador, tipos científicos EN/PT, gráficos e ativação de tab por teclado |

No código final, o navegador mostrou dois gráficos em PSI-117, zero exceções,
tipos reportado/simulação preservados e unidade ausente explícita; não houve
overflow horizontal de página nas duas larguras observadas. PSI-62 abriu
metadados sem fabricar gráfico numérico; PSI-159 abriu suas tabelas e relatórios.
Capturas e logs locais em `tmp/`; comandos e limites detalhados em
[STAGE2_INTEGRATION.md](STAGE2_INTEGRATION.md). As figuras PDF foram inspecionadas
por amostragem, não integralmente. Não houve auditoria WCAG completa, configuração
Gemini, chamada LLM ao vivo ou publicação.

O primeiro passe de 143 testes teve um problema do diretório temporário global
de AppTest; o teste foi isolado em arquivo próprio e os passes posteriores de
158 e 161 passaram. O último inclui os três testes de relevância semântica.
Os casos de escrita concorrente, nome temporário longo no Windows, retomada do
índice e rótulos científicos incorretos foram corrigidos e cobertos por regressão.

## Histórico anterior à Etapa 2 — Product & UX/UI Overhaul

O registro abaixo foi preservado como histórico da versão anterior; as
observações e o ambiente atualizados desta sessão estão na seção acima.

All automated checks and live Chromium browser checks below were executed against the `.venv` Python 3.11 environment after the final product, responsive CSS, localization, Challenge Hub, and Gemini provider updates.

---

## 1. Automated Static, Dependency, and Offline Pytest Suite

| Check | Command | Outcome | Notes |
|---|---|---|---|
| Linter (`ruff`) | `.\.venv\Scripts\python.exe -m ruff check app.py src scripts tests` | **Passed** (`All checks passed!`) | Zero lint issues across `app.py`, `src`, `scripts`, `tests` |
| Type Check (`mypy`) | `.\.venv\Scripts\python.exe -m mypy app.py src/design_system.py src/gemini_provider.py src/challenge_engine.py src/assistant.py src/scientific_ui.py src/guided_journeys.py src/views.py src/i18n.py tests/test_gemini_and_challenge.py` | **Passed** (`Success: no issues found in 10 source files`) | Clean static typing across `app.py`, design system, Gemini provider, challenge engine, UI, guided journeys, views, i18n, and new test module |
| Bytecode Compile | `.\.venv\Scripts\python.exe -m compileall -q app.py src scripts tests` | **Passed** (exit `0`) | Zero Python syntax issues |
| Dependency Check | `.\.venv\Scripts\python.exe -m pip check` | **Passed** (`No broken requirements found.`) | Clean dependency tree |
| Full Offline Pytest | `$env:RAG_EMBEDDING_MODEL=""; .\.venv\Scripts\python.exe -m pytest -q` | **112 passed** | Includes all core scientific/retrieval/security/i18n/guided-UX suites plus [`tests/test_gemini_and_challenge.py`](../tests/test_gemini_and_challenge.py) |

### Key Verified Capabilities in `tests/`
- **Preserved Scientific & Security Tests**: Conservative Pint unit conversions and `psig`/`psia` rules (`test_units.py`), CSV/PDF/ISA ingestion (`test_ingestion.py`), SQLite `FTS5` + hybrid search & legacy migration (`test_retrieval.py`), extractive claim verification (`test_assistant.py`), table compatibility guardrails (`test_comparison.py`), background upload jobs & traversal/formula injection protections (`test_local_jobs.py`, `test_security_regressions.py`), and offline VLM review (`test_visual_review.py`).
- **Complete Bilingual Parity (`tests/test_i18n_and_deployment.py`)**: Verified **`679` EN keys == `679` PT-BR keys** with zero missing strings, English default startup, stateful language switching, and automatic `PSI_READONLY_MODE=1` upload/mutation restrictions.
- **Discovery UX, 5-Question Journeys & Visual Guide (`tests/test_guided_ux.py`)**: Verified Journey 1 and Journey 2 across 4 steps, back/forward navigation, PT-BR pillar filtering, chart explainers, and preserved `'Burning rate; mm'` / `FLEX-2` caveats.
- **Gemini Provider, Challenge Hub & Overhaul Regression Tests (`tests/test_gemini_and_challenge.py`)**:
  - Verified Google Gemini REST adapter payload/extraction with HTTP mocks, rolling rate-limit enforcement, fallback to offline mode on HTTP errors, and blocking `local_upload` excerpts from leaving the machine.
  - Verified Challenge Hub `build_study_summary`, deterministic `0–100` `build_priority_ranking`, and `build_spacecraft_interpretation` caveats.
  - Verified `.streamlit/config.toml` (`toolbarMode = "viewer"`, `showErrorDetails = "none"`), top navigation bar (`topbar-home-btn`, `topbar-back-btn`, `topbar-lang-toggle`), absence of developer tokens (`SQLite + SHA-256`, `lexical vectors`) in primary UI copy, and repeated `EN -> PT-BR -> EN -> PT-BR` top-bar toggles with zero exceptions.

---

## 2. Live Browser Verification (`http://127.0.0.1:8511`)

Verified directly against a live Streamlit headless server (`streamlit run app.py --server.port 8511 --server.address 127.0.0.1 --server.headless true`):

- **Desktop (`1440×1000`)**:
  - `0` `[data-testid="stException"]` errors and `0` `[data-testid="stDeployButton"]` developer chrome buttons.
  - Verified `"Explore the Science of Fire in Space"` H1 hero, top context strip (`Where you are: Home / Overview`, `← Back`, `🏠 Home`, `Language: EN → PT-BR`), 3 starting cards, Challenge Hub tabs (`1. SUMMARIZE Study`, `2. RANK Priority`, `3. INTERPRET Safety Impact`), repeated `EN ↔ PT-BR` switching on desktop and while viewing the Rank tab (zero tracebacks), and Guided Journey 1 Step 1 (`Step 1 of 4` + 5-question guide) → Step 2 → `🏠 Home` return.
  - Verified Streamlit server log (`task-920.log`) contained zero Python tracebacks and zero widget session-state warnings.
- **Tablet (`768×1024`)**:
  - `window.innerWidth = 768px`, `stApp = 768.0px`, `mainBlockContainer = 758.0px`, header height `60.0px` with zero overlap.
  - Challenge Hub tabs fit cleanly in one row (`726.0px` tablist width); toggling sidebar open yields `300.0px + 468.0px = 768.0px == clientWidth` (`0` horizontal overflow).
- **Mobile (`375×812`, fresh session)**:
  - Sidebar starts collapsed (`>>` toggle visible), leaving `"Explore the Science of Fire in Space"` immediately readable on load.
  - `window.innerWidth = 375px`, `clientWidth = 375.0px`, `main = 375.0px`, `stMainBlockContainer = 365.0px` (`0` horizontal overflow across containers).
  - Top-bar controls stack cleanly (`305.81px` full width, zero text truncation) and Challenge Hub tabs wrap neatly across two lines (`337.81px` tablist width).
- **200% Zoom Reflow (`720×500` viewport)**:
  - Sidebar auto-collapsed, zero fixed-header collision, top-bar buttons arranged in a 2×2 grid (`<= 678px`), hero width `678px` (`<= 720px`) with zero horizontal clipping.

---

## 3. Honest Limitations & Unconfigured External Services

- **Google Gemini API**: **`IMPLEMENTED BUT UNCONFIGURED`** in the local `.env`; live Gemini HTTP calls were not executed without an active key and were verified through mocked unit/integration tests alongside offline NASA evidence fallback.
- **External VLM Endpoint**: Intentionally unconfigured by default; verified with quarantined mock visual reviews (`needs_human_review = True`).
- **Public Cloud Deployment**: Verified locally (`PSI_READONLY_MODE=1` tested cleanly); remote Git push and Streamlit Cloud provisioning remain intentionally left for owner approval via [LOCAL_ACCEPTANCE.md](LOCAL_ACCEPTANCE.md) and [DEPLOYMENT.md](DEPLOYMENT.md).
