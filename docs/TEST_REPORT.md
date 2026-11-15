# Test & Verification Report — Public Release (`feat/spaceapps-public-release`)

All checks below were executed on the release candidate in the `.venv` Python 3.11 environment after all source, UI, i18n, and test edits.

---

## 1. Automated Static, Dependency, and Unit/Integration Checks

| Check | Command | Outcome | Notes |
|---|---|---|---|
| Linter (`ruff`) | `.\.venv\Scripts\python.exe -m ruff check app.py src scripts tests` | **Passed** (`All checks passed!`) | 0 lint errors across app, src, scripts, tests |
| Type Check (`mypy`) | `.\.venv\Scripts\python.exe -m mypy src/units.py src/scientific_store.py src/comparison.py src/visual_review.py src/local_jobs.py src/pipeline.py src/retrieval.py src/assistant.py src/i18n.py src/guided_journeys.py` | **Passed** (`Success: no issues found in 10 source files`) | Clean static typing across core domain, i18n, and guided UX modules |
| Bytecode Compile | `.\.venv\Scripts\python.exe -m compileall -q app.py src scripts tests` | **Passed** (exit `0`) | Zero syntax errors |
| Package Consistency | `.\.venv\Scripts\python.exe -m pip check` | **Passed** (`No broken requirements found.`) | Dependencies cleanly resolved |
| Full Pytest Suite | `$env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1'; .\.venv\Scripts\python.exe -m pytest -q` | **105 passed** | All 99 prior tests + 6 guided UX & progressive-disclosure tests passing |

### Key Verified Capabilities in `tests/`
- **Previous validated core tests preserved**: Pint conservative unit conversions & `psig` ambient reference enforcement (`test_units.py`), CSV/PDF/ISA ingestion (`test_ingestion.py`), `RetrievalIndex` & SQLite FTS5 + legacy model migration (`test_retrieval.py`), extractive LLM refusal / unsupported claim guard (`test_assistant.py`), table compatibility guardrails (`test_comparison.py`), background upload jobs & path traversal/injection protections (`test_local_jobs.py`, `test_security_regressions.py`), offline VLM guardrails & `AppTest` navigation (`test_app.py`, `test_ui_details.py`, `test_visual_review.py`, `test_end_to_end.py`).
- **Release & localization checks (`tests/test_i18n_and_deployment.py`)**:
  - Complete `TRANSLATIONS["en"] == TRANSLATIONS["pt"]` key parity (**608 identical keys**) and non-empty strings.
  - Default `English (EN)` boot (`session_state["lang"] == "en"`) and stateful switching to `Português (PT-BR)` preserving active section and keeping original NASA IDs/DOIs intact.
  - `PSI_READONLY_MODE=1` disables uploads, document reprocessing, and experiment creation/editing across `Data Explorer` and `Sources & Methodology`.
  - `ensure_scientific_bootstrap()` creates SQLite stores and indexed chunks offline with portable POSIX relative paths (`data/experimentos/...`).
  - Zero user-specific paths or host prefixes in committed `data/embedding_model.json` and normalized model identifiers.
- **Discovery UX, Guided Journeys & Explainability checks (`tests/test_guided_ux.py`)**:
  - Discovery-first Home verifies `"Explore the Science of Fire in Space"`, subtitle, Experiences A/B/C, and default `Guided Exploration` mode.
  - Journey 1 (*Understanding Fire in Microgravity*) and Journey 2 (*Fire Safety in Spacecraft*) verified across all 4 steps, `Back`/`Continue`, interactive physics/pillar/evidence controls, and sticky `← Return to Guided Journey` handoffs.
  - Chart explanation card (`"How to Read This Chart"`) verified in Journey 1 Step 3 (with `'Burning rate; mm'` unit caveat) and inside Data Explorer.
  - Scientific Assistant verified instant example execution on click alongside `"Plain-Language Guide to These Results"`.
  - Bilingual `Português (PT-BR)` parity verified inside Guided Journeys with zero raw key leakage.

---

## 2. Clean-Clone vs. Local Semantic Indexing Verification
- **Local Semantic Model Active (`.env` / `paraphrase-multilingual-MiniLM-L12-v2`)**: `ensure_scientific_bootstrap()` automatically upgrades local `data/search.sqlite3` to **2,711 semantic token-window chunks** (`local-semantic:...`, `128`-token windows).
- **Clean-Clone Offline / Cloud Default (`RAG_EMBEDDING_MODEL=""`)**: Tested against an isolated temporary SQLite DB (`index_experiments` with `RAG_EMBEDDING_MODEL=""`) yielding **1,517 deterministic structural chunks** (`lexical-vectors`), and previous clean-clone cold-start boot initialized cleanly in **5.70s** (`invs=10, docs=16, chunks=1517`) with zero external credentials.

---

## 3. Live Headless Browser Validation (`http://localhost:8511`)
Executed full 6-part live usability walkthrough in Chromium against `streamlit run app.py --server.port 8511 --server.headless true`:
- **Desktop (`1440x1000`) & Mobile (`375x812`)**:
  - English Discovery Home rendered `"Explore the Science of Fire in Space"`, subtitle, 3 starting experience cards, Earth vs. Microgravity contrast, and **2,711 Semantic Token Chunks** (`9` Studies, `16` Files, `31` Tables; `15 processed · 1 partial · 0 failed`).
  - Completed Guided Journey 1 Steps 1–4 (`PSI-69` PDF preview `naturalWidth > 0`, interactive Plotly chart + `"How to Read This Chart"`, `'Burning rate; mm'` caveat, retrieved evidence, `Back`/`Continue`, return to Home).
  - Completed Guided Journey 2 Steps 1–4 (`Detection`/`Suppression` pillars, `PSI-25 · BASS-II` chart, `PSI-102 · SAME` report PDF + CSV table, cross-pillar warning, Compare handoff + sticky return button + sidebar exit).
  - Verified Experience C (`Data Explorer` progressive disclosure + inline chart guide) and `Scientific Assistant` (3+2 untruncated example buttons, auto-execution on click, `"Plain-Language Guide to These Results"`).
  - Switched `English (EN)` ↔ `Português (PT-BR)` cleanly across Home & Journey 1 (`"Explore a Ciência do Fogo no Espaço"`, `"Passo 1 de 4"`).
  - Mobile `375x812`: `bodyBox.width = 375px`, matching `innerWidth = 375px` (`scrollWidth <= innerWidth`, zero horizontal overflow, clean collapsed sidebar toggle).
  - Zero `[data-testid="stException"]` elements and zero console errors across the entire walkthrough.
  - Updated verification captures saved to `docs/qa-desktop.png`, `docs/qa-search-desktop.png`, and `docs/qa-mobile.png`.

---

## 4. Documented Scope Limitations & Remaining Manual Action
- **Embedding model in offline cloud containers**: Default cloud boot uses deterministic EN/PT `lexical-vectors` alongside SQLite FTS5 unless `requirements-models.txt` and `RAG_EMBEDDING_MODEL` are configured.
- **External LLM / VLM providers**: Intentionally unconfigured by default; live external completion calls were not run without API credentials, while local extractive fallback and mock HTTP boundary tests are fully verified.
- **Remote GitHub Push & Streamlit Community Cloud Live URL**: Not executable automatically because `gh` CLI and SSH credentials are absent locally; exact handoff commands appear in [docs/ANTIGRAVITY_HANDOFF.md](ANTIGRAVITY_HANDOFF.md) and [docs/DEPLOYMENT.md](DEPLOYMENT.md).
