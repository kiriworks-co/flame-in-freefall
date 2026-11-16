# Flame in Freefall — PSI Flame Microgravity (NASA Space Apps 2026)

> **Bilingual / Bilíngue:** Default interface in **English (`en`)** with a single top-bar **`EN | PT-BR`** selector.  
> Interactive scientific workbench covering **12 NASA Physical Sciences Informatics (PSI)** combustion investigations and **2 official NASA reference guides** (`NASA-CONTEXT`). The archive preserves **40 documents (82,099,713 bytes)** — 37 with scientific or documentary content and 3 explicitly flagged 56-byte ISA placeholders (`s_PSI-*.txt`) — immutable **SHA-256** provenance, conservative **Pint** normalization, **117 extracted tables** (`10,114` tabular rows, `26,803` typed cell observations), and **15,524 searchable evidence passages in the validated local semantic index** (the cloud lexical fallback has a different passage count).

---

## Why Freefall Changes Fire

On Earth (`1g`), buoyancy lifts hot combustion gases and pulls fresh oxygen inward, stretching flames into a teardrop. In orbital microgravity (`~0g` freefall), natural buoyancy nearly vanishes: diffusion-dominated flames can become **approximately spherical**, heat and soot linger near the fuel, low-temperature **cool flames** can persist after visible extinction, and smoke aerosols evolve differently along cabin airflow.

**Flame in Freefall** structures NASA's fragmented PSI files across all three spacecraft fire-safety pillars (**Prevention**, **Detection**, **Suppression**) while strictly separating **test conditions, reported experimental outcomes, numerical simulations, derived calculations, and metadata** — never equating `26,803` typed observations to `26,803` independent experiments or treating any metric as flight certification.

---

## Workspace & Key Capabilities

1. **Discovery Home & Space Apps Challenge Hub (`SUMMARIZE · RANK · INTERPRET`)**:
   - Aerospace Navy hero banner with an embedded **1g Teardrop vs. ~0g Spherical** visual schematic and live verified archive counters (`12` PSI studies, `40` NASA files, `117` tables, `15,524` passages).
   - Three equal-height starting paths: **Discover the Science** (Guided Journey 1), **Explore Fire Safety** (Guided Journey 2), and **Investigate NASA Data** (Data Explorer), plus direct links to **Investigations** and **Scientific Assistant**.
   - Interactive **Challenge Hub** tabs for **SUMMARIZE Study**, **RANK Priority** (`0–100` reading-priority index, never a fire-risk score), and **INTERPRET Safety Impact**.
2. **Guided Journeys 1 & 2 (4 Steps · 5 Scientific Questions)**:
   - Repeatable *What am I exploring · Why does it matter · What does the NASA evidence show · What can I conclude · What are the limitations?* framework with interactive Plotly plots, PDF previews, and persistent *Return to Guided Journey* state.
3. **Investigations Catalog (`investigations`)**:
   - Searchable inventory of all 12 NASA PSI studies and 2 official guides with confirmed DOIs, permanent NASA PSI links, pillar filters, caveats, and 1-click jump to Data Explorer.
4. **Data Explorer (`explorer`)**:
   - 6-tab workbench (*Overview & Variables* with chart-first *Visual First Look*, *Interactive Charts* with reversible column fixes & series analysis, *Tables & Source Rows*, *Documents & Integrity* with SHA-256 verification, *PDF Reader & Search*, and *ISA-Tab Metadata*).
5. **Compare (`compare`)**:
   - Side-by-side schema, unit, and evidence-role compatibility audit across 2–3 studies plus deterministic reading-priority ranking.
6. **Evidence-First Scientific Assistant (`assistant`)**:
   - Bilingual hybrid retrieval (**SQLite FTS5** + 384-d local embeddings or deterministic offline lexical vectors), row-aligned physical filters (`O₂`, `psia`, `cm/s`, fuel), verifiable citations, and optional **Google Gemini (`gemini-2.5-flash`)** excerpt selection & anchored 1-sentence explanations verified programmatically via `validate_claims()`.
7. **Visual Page Review (`visual_review`) & Sources (`sources`)**:
   - Offline PyMuPDF page inspector (with optional consent-gated VLM candidate review isolated as `inference`) and complete archive SHA-256 inventory.

---

## Included NASA PSI Dataset (`12` PSI Studies + `2` Context Guides)

- **Prevention:** `PSI-25` (BASS-II, `10.60555/4qc4-de67`), `PSI-26` (BASS, `10.60555/58h4-dy80`), `PSI-62` (UFGM modeling, `10.60555/e9xp-ex83`, *metadata only*), `PSI-98` (Saffire-I, `10.60555/0t15-1z43`), `PSI-99` (Saffire-II, `10.60555/2chp-m469`), `PSI-100` (Saffire-III, `10.60555/040q-4h36`)
- **Detection:** `PSI-101` (SAME-R, `10.60555/2np7-jv14`), `PSI-102` (SAME, `10.60555/gd4k-8h62`)
- **Suppression & Cool Flames:** `PSI-68` (FLEX-2, `10.60555/byp8-h018`), `PSI-69` (FLEX, `10.60555/mbq8-0451`), `PSI-117` (Cool Flame Dynamics CFD/FLEX, `10.60555/gz0q-b577`), `PSI-159` (ACME CFI-G, `10.60555/cyt1-kh64`)
- **Reference Guides (`NASA-CONTEXT`):** *A Researcher's Guide to ISS Combustion Science* & *Complete PSI Database Guide*

---

## Quickstart (Windows · Python 3.11+)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8511 --server.address 127.0.0.1
```

Open `http://127.0.0.1:8511`. On cold start, `ensure_scientific_bootstrap()` initializes `data/scientific.sqlite3` and `data/search.sqlite3` automatically from preserved repository artifacts with zero API keys required.

### Optional Google Gemini Configuration
The app works 100% offline in **Verified Local Evidence Mode**. To enable optional Gemini excerpt selection and anchored explanations (`gemini-2.5-flash`):

```powershell
.\.venv\Scripts\python.exe scripts/setup_gemini.py
.\.venv\Scripts\python.exe scripts/gemini_live_check.py
```

Private `local_upload` excerpts are blocked by code (`filter_public_nasa_evidence`) and rate caps (`10/min`, `250/day`, `40/session`) are enforced automatically. Never commit `.env` or `.streamlit/secrets.toml`.

---

## Verification & Quality Assurance

```powershell
.\.venv\Scripts\python.exe -m ruff check app.py src scripts tests
.\.venv\Scripts\python.exe -m mypy app.py src/design_system.py src/gemini_provider.py src/challenge_engine.py src/assistant.py src/scientific_ui.py src/guided_journeys.py src/views.py src/i18n.py src/pipeline.py src/scientific_store.py src/storage.py src/units.py src/retrieval.py src/comparison.py src/relevance.py scripts/setup_gemini.py scripts/gemini_live_check.py tests/test_gemini_and_challenge.py
.\.venv\Scripts\python.exe -m compileall -q app.py src scripts tests
.\.venv\Scripts\python.exe -m pip check
$env:PYTHONUNBUFFERED="1"; $env:RAG_EMBEDDING_MODEL=" "; $env:HF_HUB_OFFLINE="1"; $env:TRANSFORMERS_OFFLINE="1"; .\.venv\Scripts\python.exe -m pytest -q
```

---

## Final Release & Stage 3 Documentation

- **A — Project Overview (PT-BR):** [docs/PROJECT_OVERVIEW_PTBR.md](docs/PROJECT_OVERVIEW_PTBR.md)
- **B — Complete Functional Manual (PT-BR):** [docs/FEATURES_AND_WORKFLOWS_PTBR.md](docs/FEATURES_AND_WORKFLOWS_PTBR.md)
- **C — Real Folder Structure (PT-BR):** [docs/FOLDER_STRUCTURE_PTBR.md](docs/FOLDER_STRUCTURE_PTBR.md)
- **D — NASA Space Apps Submission Description (EN):** [docs/SUBMISSION_DESCRIPTION_EN.md](docs/SUBMISSION_DESCRIPTION_EN.md)
- **E — Final Release Status (PT-BR):** [docs/FINAL_RELEASE_STATUS_PTBR.md](docs/FINAL_RELEASE_STATUS_PTBR.md)
- Provenance, Testing & Deployment: [docs/DATA_PROVENANCE.md](docs/DATA_PROVENANCE.md) · [docs/TEST_REPORT.md](docs/TEST_REPORT.md) · [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) · [docs/AI_USAGE.md](docs/AI_USAGE.md)
