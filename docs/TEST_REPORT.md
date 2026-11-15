# Test & Verification Report — Public Release (`feat/spaceapps-public-release`)

All checks below were executed on the release candidate in the `.venv` Python 3.11 environment after all source, UI, i18n, and test edits.

---

## 1. Automated Static, Dependency, and Unit/Integration Checks

| Check | Command | Outcome | Notes |
|---|---|---|---|
| Linter (`ruff`) | `.\.venv\Scripts\python.exe -m ruff check app.py src scripts tests` | **Passed** (`All checks passed!`) | 0 lint errors across app, src, scripts, tests |
| Type Check (`mypy`) | `.\.venv\Scripts\python.exe -m mypy src/units.py src/scientific_store.py src/comparison.py src/visual_review.py src/local_jobs.py src/pipeline.py src/retrieval.py src/assistant.py src/i18n.py` | **Passed** (`Success: no issues found in 9 source files`) | Clean static typing across core domain & i18n modules |
| Bytecode Compile | `.\.venv\Scripts\python.exe -m compileall -q app.py src scripts tests` | **Passed** (exit `0`) | Zero syntax errors |
| Package Consistency | `.\.venv\Scripts\python.exe -m pip check` | **Passed** (`No broken requirements found.`) | Dependencies cleanly resolved |
| Full Pytest Suite | `$env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1'; .\.venv\Scripts\python.exe -m pytest -q` | **99 passed in 37.87s** | 0 failed, 0 skipped, 0 warnings |

### Key Verified Capabilities in `tests/`
- **Previous validated core tests preserved**: Pint conservative unit conversions & `psig` ambient reference enforcement (`test_units.py`), CSV/PDF/ISA ingestion (`test_ingestion.py`), `RetrievalIndex` & SQLite FTS5 + legacy model migration (`test_retrieval.py`), extractive LLM refusal / unsupported claim guard (`test_assistant.py`), table compatibility guardrails (`test_comparison.py`), background upload jobs & path traversal/injection protections (`test_local_jobs.py`, `test_security_regressions.py`), offline VLM guardrails & `AppTest` navigation (`test_app.py`, `test_ui_details.py`, `test_visual_review.py`, `test_end_to_end.py`).
- **New release & localization checks (`tests/test_i18n_and_deployment.py`)**:
  - Complete `TRANSLATIONS["en"] == TRANSLATIONS["pt"]` key parity and non-empty strings.
  - Default `English (EN)` boot (`session_state["lang"] == "en"`) and stateful switching to `Português (PT-BR)` preserving active section and keeping original NASA IDs/DOIs intact.
  - `PSI_READONLY_MODE=1` disables uploads, document reprocessing, and experiment creation/editing across `Data Explorer` and `Sources & Methodology`.
  - `ensure_scientific_bootstrap()` creates SQLite stores and indexed chunks offline with portable POSIX relative paths (`data/experimentos/...`).
  - Zero user-specific paths or host prefixes in committed `data/embedding_model.json` and normalized model identifiers.

---

## 2. Clean-Clone Cold-Start Verification (No `.env`, No Pre-Built SQLite DBs)
Copied project contents into an isolated temporary directory excluding `.git`, `.venv`, `.env`, and `*.sqlite3*`, running with `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, and `PSI_READONLY_MODE=1`:
- **Result**: `Clean cold-start OK in 5.70s: invs=10, docs=16, chunks=1517`
- Both `data/scientific.sqlite3` and `data/search.sqlite3` rebuilt automatically from preserved artifacts on initial Streamlit `AppTest` boot with zero network access or API keys. Temporary directory removed immediately after check.

---

## 3. Live Headless Browser Validation (`http://127.0.0.1:8511`)
Executed interactive verification in headless browser against running `streamlit run app.py --server.port 8511 --server.headless true`:
- **Desktop (`1440x1000`) & Mobile (`375x812`)**:
  - English default landing page rendered `"Flame in Freefall: Microgravity Combustion Explorer"`, metrics (`9` NASA PSI Studies, `16` Preserved NASA Files, `31` Extracted Tables, `1517` Indexed Chunks) with full label visibility (zero ellipsis truncation after CSS + label polish), 3 Pillars, and 4-step Guided Tour.
  - Switched `English (EN)` ↔ `Português (PT-BR)` cleanly without resetting section state.
  - Exercised `Investigations`, `Data Explorer` (`PSI-69`, Plotly interactive chart rendered `.js-plotly-plot`), `Compare` (`FLEX vs BASS-II` incompatibility notice + reading priority ranking), `Scientific Assistant` (`FLEX droplet O₂ 18–25%` example query + unsupported query zero-fabrication check), and `Sources & Methodology` (16 preserved originals).
  - Mobile `375x812`: `appBox.width = 375px`, `mainBox.width = 375px`, matching `window.innerWidth = 375px` (`scrollWidth <= innerWidth`, zero horizontal overflow, clean sidebar collapse toggle).
  - Zero runtime exceptions and zero console errors.
  - Refreshed desktop screenshot saved to `docs/qa-desktop.png`.

---

## 4. Documented Scope Limitations & Remaining Manual Action
- **Embedding model in offline cloud containers**: Default cloud boot uses deterministic EN/PT `lexical-vectors` alongside SQLite FTS5 unless `requirements-models.txt` and `RAG_EMBEDDING_MODEL` are configured.
- **External LLM / VLM providers**: Intentionally unconfigured by default; live external completion calls were not run without API credentials, while local extractive fallback and mock HTTP boundary tests are fully verified.
- **Remote GitHub Push & Streamlit Community Cloud Live URL**: Not executable automatically because `gh` CLI and SSH credentials are absent locally; exact handoff commands appear in [docs/ANTIGRAVITY_HANDOFF.md](ANTIGRAVITY_HANDOFF.md) and [docs/DEPLOYMENT.md](DEPLOYMENT.md).
