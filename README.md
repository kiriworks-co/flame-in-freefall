# PSI Flame Microgravity — Flame in Freefall (NASA Space Apps 2026)

> **Bilingual / Bilíngue:** Default interface in **English (`en`)** with instant **Português (`PT-BR`)** switching in the sidebar (`Language / Idioma`).  
> Interactive scientific workbench unifying **9 NASA Physical Sciences Informatics (PSI)** microgravity combustion investigations (**16 authentic NASA files, 7,881,267 bytes**) with immutable **SHA-256** provenance, conservative **Pint** unit normalization, side-by-side compatibility checks, and an evidence-first research assistant.

---

## Why Freefall Changes Fire

On Earth, buoyancy lifts hot combustion gases and draws fresh oxygen inward, shaping a familiar teardrop flame. In orbital microgravity (freefall), natural buoyancy nearly vanishes: flames become spherical, heat and soot remain near the fuel, low-temperature **cool flames** can persist, and smoke aerosols evolve differently along cabin airflow.

NASA's PSI repository spreads these experiments across heterogeneous CSV spreadsheets, engineering requirements PDFs, and final science reports using conflicting unit conventions (`psia`, `psig`, `mmHg`, `cm/s`, mole fractions). **PSI Flame Microgravity** brings 9 high-priority investigations across all three spacecraft fire-safety pillars (**Prevention**, **Detection**, **Suppression**) into one transparent, verifiable explorer where **test conditions are never confused with measured results**.

---

## Workspace Structure (7 Sections)

1. **Home / Overview (`home`)**: Visual introduction to microgravity combustion, spacecraft fire-safety pillars, summary metrics, and a 1-click **3-Minute Guided Tour**.
2. **Investigations (`investigations`)**: Searchable catalog of 9 NASA PSI studies + 2 official NASA reference guides with permanent NASA PSI URLs, confirmed DOIs, objectives, safety relevance, caveats, and direct jump into Data Explorer.
3. **Data Explorer (`explorer`)**: Study selector (defaulting to `PSI-69 · FLEX`), collapsible **Variable & Unit Glossary**, interactive Plotly charts, descriptive statistics, reversible column fixes, source tables with original row numbers, document integrity & SHA-256 verification, in-PDF keyword reader, and ISA-Tab metadata.
4. **Compare (`compare`)**: Guided cross-study schema and methodology audit (with quick presets such as *FLEX vs BASS-II*, *SAME vs SAME-R*, *Saffire-I vs Saffire-II*) plus a deterministic **0–100 Reading Priority Ranking** (never a safety score).
5. **Scientific Assistant (`assistant`)**: Hybrid retrieval engine (SQLite **FTS5** + local multilingual embeddings when configured or deterministic EN/PT lexical vectors) with row-level physical unit filters (`O₂`, `psia`, `cm/s`, fuel), clickable example queries, and strict extractive grounding when an external LLM is configured.
6. **Visual Page Review (`visual_review`)**: Offline rendered PDF diagram inspector with optional opt-in VLM qualitative review strictly tagged as `inference` (`needs_human_review = True`).
7. **Sources & Methodology (`sources`)**: Full provenance, unit normalization policy, known scientific caveats, verification hashes, and archive synchronization controls (read-only when publicly deployed).

---

## Included NASA PSI Dataset

- **Prevention**: `PSI-25` (BASS-II), `PSI-26` (BASS), `PSI-98` (Saffire-I), `PSI-99` (Saffire-II), `PSI-100` (Saffire-III)
- **Detection**: `PSI-101` (SAME-R), `PSI-102` (SAME)
- **Suppression**: `PSI-68` (FLEX-2), `PSI-69` (FLEX)
- **Context Guides**: *A Researcher's Guide to ISS Combustion Science* and *Complete PSI Database Guide*

---

## Key Scientific Caveats (Preserved Transparently)

1. **`Burning rate; mm` in `PSI-69_Experimental table_FLEX.csv`**: Original NASA column declares length without time (`mm` instead of `mm/s` or `mm²/s`). Kept raw without automated dimensional conversion.
2. **FLEX-2 Requirements PDF under `PSI-69`**: NASA catalogs the requirements PDF under `PSI-69`, while its cover title states `FLEX-2`; an explicit warning surfaces wherever this file is displayed.
3. **SAME Ignitor Drawing (`PSI-102`)**: 1-page CAD engineering PDF contains no embedded text layer; full OCR requires external Tesseract.
4. **No Certification Claim**: Retrieved summaries, statistics, regressions, and reading rankings never replace independent scientific review or spacecraft fire-safety qualification.

---

## Quickstart (Local Development)

Requires **Python 3.11** (matching `.python-version`).

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

On cold start, `app.py` invokes `ensure_scientific_bootstrap()`, initializing `data/scientific.sqlite3` and `data/search.sqlite3` automatically from the preserved repository artifacts in under ~6 seconds with zero external API keys required.

### Optional Providers (Unconfigured by Default)
- Local multilingual embeddings (`requirements-models.txt` + `scripts/setup_embeddings.py` + `RAG_EMBEDDING_MODEL`).
- Extractive LLM / Qualitative VLM endpoints configured exclusively via `.env` locally or Streamlit Cloud Secrets (see `.env.example` and `docs/DEPLOYMENT.md`). Never commit credentials.

---

## Verification & Quality Assurance

```powershell
.\.venv\Scripts\python.exe -m ruff check app.py src scripts tests
.\.venv\Scripts\python.exe -m mypy src/units.py src/scientific_store.py src/comparison.py src/visual_review.py src/local_jobs.py src/pipeline.py src/retrieval.py src/assistant.py src/i18n.py
.\.venv\Scripts\python.exe -m compileall -q app.py src scripts tests
.\.venv\Scripts\python.exe -m pip check
$env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1'; .\.venv\Scripts\python.exe -m pytest -q
```

---

## Public Deployment Architecture

- **Primary Runtime (`Streamlit Community Cloud`)**: Runs `app.py` with `PSI_READONLY_MODE` auto-detected on cloud hosts (`STREAMLIT_SHARING_MODE` / `/mount/src`) or set explicitly. Public visitors cannot upload files or overwrite the NASA archive; ephemeral chart column overrides remain session-scoped.
- **Static Showcase (`docs/index.html` for GitHub Pages)**: GitHub Pages only serves static assets; `docs/index.html` provides a bilingual overview and links directly to the interactive Streamlit Community Cloud app.

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) and [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md) for deployment instructions.
