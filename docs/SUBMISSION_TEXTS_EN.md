# Flame in Freefall — Ready-to-Paste Submission Texts (EN)

> **Editorial note — 2026-11-15, Stage 3 baseline `e8db878`.** Adapted from the existing Stage 2 submission draft and the final Stage 3 documentation. Copy the text blocks into the matching portal fields; field names and length limits have not been verified in the live submission form. Archive counts describe the locally validated release, not independent experiments. Search passage counts vary with the selected embedding/chunking mode. Public hosting status and URL must be confirmed separately; this document does not claim a completed deployment. No live Gemini/VLM API validation is claimed. No separately identified owner-authored scientific manuscript was found in the reviewed project documentation; its wording can be incorporated when supplied.

---

## 1. Project Title

**Primary Title:**
```text
Flame in Freefall
```

**Subtitle / Challenge-Aligned Variant (if field permits longer title):**
```text
Flame in Freefall: Evidence-First Workbench for NASA PSI Microgravity Combustion Data
```

---

## 2. One-Sentence Pitch

**Concise Version:**
```text
An open-source, bilingual (EN/PT-BR) workbench turning 12 NASA PSI microgravity combustion studies into auditable charts, guided journeys, and cited evidence.
```

**Expanded One-Sentence Pitch:**
```text
Flame in Freefall transforms 40 authentic NASA Physical Sciences Informatics (PSI) documents across 12 PSI combustion investigations into a bilingual, provenance-locked research and learning platform with conservative unit normalization, hybrid offline search, and extractive claim verification.
```

---

## 3. Short Project Description

```text
In orbital freefall, vanishing buoyancy transforms how flames ignite, spread, emit smoke, and extinguish—yet NASA's Physical Sciences Informatics (PSI) data are spread across complex spreadsheets, multi-page engineering PDFs, and inconsistent unit systems. Flame in Freefall is an open-source, bilingual (English / Portuguese PT-BR) scientific workbench covering 12 NASA PSI investigations and 2 official NASA guides across spacecraft fire Prevention, Detection, and Suppression. Preserving 40 original files (82.1 MB) with immutable SHA-256 verification, the application separates test conditions, reported outcomes, CFD simulations, derived calculations, and metadata. Learners explore microgravity fire physics through two 4-step Guided Journeys framed by five scientific questions, while researchers inspect chart-first Plotly visualizations, audit cross-study compatibility, compute transparent 0–100 Reading Priority scores, and run offline hybrid search (SQLite FTS5 + local multilingual embeddings or lexical vectors) backed by programmatic verbatim claim verification.
```

---

## 4. Full Project Description

```markdown
### Overview
**Flame in Freefall** is an interactive, evidence-first scientific workbench built for the **Flame in Freefall** challenge (NASA Space Apps Challenge 2026). It bridges plain-language microgravity fire education and reproducible data engineering using authentic records from NASA's **Physical Sciences Informatics (PSI)** repository and official NASA publications.

### What It Covers
The archive preserves **40 NASA documents (82,099,713 bytes)** across **12 NASA PSI investigations** and **2 official NASA reference guides** (`NASA-CONTEXT`), organized across the three pillars of spacecraft fire safety:
- **Prevention:** `PSI-25` (BASS-II), `PSI-26` (BASS), `PSI-62` (Concurrent Flame Spread Modeling / UFGM — metadata only), `PSI-98` (Saffire-I), `PSI-99` (Saffire-II), and `PSI-100` (Saffire-III).
- **Detection:** `PSI-101` (SAME-R) and `PSI-102` (SAME).
- **Suppression & Droplet Combustion:** `PSI-68` (FLEX-2), `PSI-69` (FLEX), and `PSI-117` (Cool Flame Dynamics — CFD / FLEX comparison), and `PSI-159` (ACME CFI-G — cool flames with gases).

From these verified sources, the pipeline extracts **117 tables**, **10,114 tabular rows**, **566 pages/sections**, and **26,803 typed observation records** (distinctly tagged as `simulation`, `reported_result`, `condition`, `derived`, `engineering_or_publication`, `metadata`, `context`, or `identifier_or_unclassified`), indexed into **15,524 searchable passages** using local 384-dimensional multilingual embeddings alongside SQLite **FTS5** (or **11,582 structural chunks** in offline lexical mode without an external embedding model).

### Key Capabilities
- **Discovery-First Bilingual Experience (EN / PT-BR):** Defaults to English with switching to Portuguese through a single top-bar selector, and progressive disclosure between *Guided Exploration* and *Advanced Research*.
- **Two 5-Question Guided Journeys:** Structured 4-step walkthroughs answering *What am I exploring? · Why does it matter? · What does NASA evidence show? · What can I conclude? · What are the limitations?* with live `PSI-69`, `PSI-25`, and `PSI-102` plots and embedded NASA PDF page previews.
- **Challenge Hub (`SUMMARIZE · RANK · INTERPRET`):** Produces source-anchored study summaries, explainable `0–100` **Reading Priority** rankings (explicitly distinguished from fire-risk ratings), and spacecraft engineering interpretations with preserved boundaries.
- **Chart-First Data Explorer & Conservative Analytics:** Renders 6 Plotly chart modes paired with *"How to Read This Chart"* guides, prevents plotting incompatible units or unaligned clocks together, and computes reproducible linear fits, baselines, normalizations, and derived columns without mutating originals.
- **Cross-Study Comparator:** Evaluates schema, evidence roles, methodology, and physical dimensions across 2–3 investigations before allowing quantitative pooling.
- **Hybrid Scientific Assistant & Offline Page Review:** Combines SQLite FTS5, semantic/lexical vectors, and row-aligned numeric filters (`O₂`, pressure, velocity) with an extractive verification layer (`validate_claims()`) that works 100% offline. Optional Google Gemini (`gemini-2.5-flash`) and VLM page-review adapters are implemented behind strict privacy/consent guards and remain unconfigured by default.
```

---

## 5. Problem Statement

```text
In orbital microgravity, the near-absence of natural buoyancy fundamentally alters flame shape, oxygen transport, cool-flame chemistry, soot retention, and smoke movement. While NASA's Physical Sciences Informatics (PSI) repository provides open access to landmark ISS combustion experiments, using these datasets safely and effectively remains difficult:

1. Heterogeneous Structure: Empirical conditions, reported outcomes, CFD model trajectories, engineering requirements, and bibliographic metadata are scattered across multi-block spreadsheets, mixed file encodings (UTF-8 and cp1252), and dense technical PDFs.
2. Unit and Provenance Ambiguities: Original tables mix gauge and absolute pressures (psig vs. psia), omit units on select columns, or contain source anomalies (such as FLEX's `Burning rate; mm` header lacking a time unit, or a FLEX-2 requirements PDF cataloged under PSI-69).
3. Epistemic Conflation Risk: Without column-level classification, chamber setup conditions or numerical CFD outputs can easily be misread as raw flight measurements or used to draw unwarranted spacecraft fire-safety claims.
4. High Barrier to Entry: Students, educators, and cross-disciplinary engineers lack a guided, multilingual interface that connects plain-language physical intuition directly to verifiable NASA primary sources.
```

---

## 6. Proposed Solution

```text
Flame in Freefall addresses these barriers through a dual-audience scientific workbench built on Python, Streamlit, SQLite, Pint, Plotly, and PyMuPDF:

1. Immutable Provenance & Row-Level Epistemic Tagging: Every NASA file is stored untouched and verified by SHA-256 alongside its permanent NASA PSI API/landing URL, version, and confirmed DOI. Each column and block is explicitly typed (`condition`, `reported_result`, `simulation`, `derived`, `metadata`, `engineering_or_publication`, or `context`) so simulated curves and setup parameters are never relabeled as measured flight telemetry.
2. Conservative Unit Engine: Powered by `pint`, unit normalization converts compatible units while strictly blocking ungrounded assumptions—such as converting `psig` or unspecified `psi` to `psia` without a documented reference pressure, or altering ambiguous source headers like `Burning rate; mm`.
3. Progressive Disclosure UX (Guided + Advanced): Beginners start with two 4-step Guided Journeys built around 5 Scientific Questions and an inline chart explainer, while researchers switch seamlessly into full descriptive statistics, curve fitting, cross-study schema audits, ISA-Tab inspection, and numeric-filtered search.
4. Offline-First Hybrid Retrieval with Programmatic Grounding: A persistent SQLite FTS5 + local vector index supports deterministic offline retrieval and optional local multilingual embeddings. When optional LLM synthesis (e.g., Google Gemini) is configured, programmatic validation (`validate_claims`) accepts only verbatim contiguous excerpts matching retrieved document IDs, numeric values, and evidence categories.
```

---

## 7. NASA Data Sources

All empirical data and reference manuals were acquired directly from official NASA endpoints (`psi.nasa.gov` and `nasa.gov`) with verified SHA-256 checksums, study versions, and confirmed DOIs:

| NASA ID | Investigation / Resource Name | Fire Safety Pillar | Version | Confirmed DOI | Preserved Files & Scope |
|---|---|---|---:|---|---|
| **PSI-25** | BASS-II (Burning and Suppression of Solids - II) | Prevention | v4 | `10.60555/4qc4-de67` | Experimental table CSV, Science Requirements Document PDF (16 pp.), proofsheet PDF (3 files) |
| **PSI-26** | BASS (Burning and Suppression of Solids) | Prevention | v4 | `10.60555/58h4-dy80` | Experimental table CSV (test conditions & sample catalog, 1 file) |
| **PSI-62** | Concurrent Flame Spread Modeling (UFGM) | Prevention (Modeling) | v1 | `10.60555/e9xp-ex83` | ISA-Tab investigation metadata (`i_Investigation.txt` + preserved `s_PSI-62.txt` placeholder; metadata only, no numerical series in the collected public selection) |
| **PSI-68** | FLEX-2 (Flame Extinguishment Experiment - 2) | Suppression | v6 | `10.60555/byp8-h018` | Experimental table CSV (setup conditions & ranges, 1 file) |
| **PSI-69** | FLEX (Flame Extinguishment Experiment) | Suppression | v5 | `10.60555/mbq8-0451` | Experimental table CSV (`cp1252`, conditions + reported extinction outcomes) & Engineering Requirements PDF (37 pp., cover reads FLEX-2) |
| **PSI-98** | Saffire-I | Prevention | v4 | `10.60555/0t15-1z43` | Experimental table CSV (large-scale flame spread summary, 1 file) |
| **PSI-99** | Saffire-II | Prevention | v5 | `10.60555/2chp-m469` | Experimental table CSV (multi-sample test matrix, 1 file) |
| **PSI-100** | Saffire-III | Prevention | v4 | `10.60555/040q-4h36` | Experimental table CSV (test summary, 1 file) |
| **PSI-101** | SAME-R (Smoke Aerosol Measurement Experiment - Reflight) | Detection | v4 | `10.60555/2np7-jv14` | Experimental table CSV (sample conditions, airflow, aging, mass loss rate, 1 file) |
| **PSI-102** | SAME (Smoke Aerosol Measurement Experiment) | Detection | v4 | `10.60555/gd4k-8h62` | Experimental table CSV, Final Science Report PDF (68 pp.), 1-page CAD ignitor coil PDF (no text layer; `partial`) |
| **PSI-117** | Cool Flame Dynamics (CFD / FLEX comparison) | Suppression / Droplets | v2 | `10.60555/gz0q-b577` | 9 multi-block CSVs (experimental reference & CFD series separated), 4 presentation PDFs (18–36 pp.), ReadMe XLSX, ISA-Tab (`i_Investigation.txt` + `s_PSI-117.txt`) |
| **PSI-159** | ACME CFI-G (Cool Flames Investigation with Gases) | Cool Flames / Suppression context | v1 | `10.60555/cyt1-kh64` | 2 Experimental table CSVs (Normal & Inverse Flames), Engineering Implementation PDF (102 pp.), Final Report PDF (93 pp.), ISA-Tab (`i_Investigation.txt` + `s_PSI-159.txt`) |
| **NASA-CONTEXT** | Official NASA Reference Guides | Educational Context | — | N/A | *A Researcher's Guide to ISS Combustion Science* (`researchers_guide.pdf`) and *Complete PSI Database Guide* (`psi_database_guide.pdf`) |

**Additional Challenge Context Resources Checked (`resources/manifests/official_resources.json`):** NASA Combustion Science portal, NASA ScienceCasts video link, Mir Space Station fire historical article, NASA Spinoff links (*Fireman's Air Tanks*, *Fire Detector*, *New Technology for the Fire Attire*), and Apollo 1 / Apollo 13 historical links (recorded with TLS verification error notes without bypassing certificate validation).

---

## 8. AI and Technology Stack

```markdown
- **Core Application & Visualization:** Python (`.python-version`: 3.11; Locally validated on 3.12.14 `.venv`), Streamlit (`>=1.57`), Pandas, NumPy, Plotly (`>=5.18`), Scikit-learn.
- **Document Extraction & Physical Units:** PyMuPDF (`>=1.23`) for PDF text/layout/table extraction and on-demand page rendering; `openpyxl` / `xlrd` for spreadsheets; `python-docx` and custom ISA-Tab TSV parser (`src/isa.py`); `pint` (`>=0.24,<1`) for conservative dimensional conversions; `pytesseract` hook available when external Tesseract is installed.
- **Persistence & Hybrid Search:** Dual SQLite architecture (`data/scientific.sqlite3` with 16 relational tables + `data/search.sqlite3` with SQLite **FTS5** full-text search and dense/sparse vector storage). Supports local offline `sentence-transformers` (`paraphrase-multilingual-MiniLM-L12-v2`, 384 dimensions, Apache-2.0, 15,524 chunks) as well as deterministic bilingual `lexical-vectors` (11,582 chunks) with a conservative `0.60` cosine gate for lexical-free semantic matches.
- **Programmatic Grounding & Optional External AI (Unconfigured by Default):**
  - **Local Mode (Default):** Fully functional offline with zero API keys, returning verbatim NASA excerpts, row/page locations, DOIs, and SHA-256 checksums.
  - **Google Gemini Adapter (`src/gemini_provider.py`):** Supports `gemini-2.5-flash` via REST (`responseSchema` JSON enforcement), blocks private `local_upload` excerpts (`filter_public_nasa_evidence`), enforces rolling caps (`10/min`, `250/day` per server, `40/session`), and validates every returned claim through `validate_claims()`. *Stage 3 status: implemented and tested with mocked HTTP responses, rate-limit checks, and claim-validation tests; no live Gemini API call is claimed. Setup and live-check scripts are included, and an API key is optional.*
  - **Optional VLM Visual Review (`src/visual_review.py`):** Requires explicit per-page user consent, rejects digits/measurements in qualitative inferences, and quarantines candidate overlays in `analysis_results` with `needs_human_review = True`.
- **Quality Assurance:** `pytest` (164 passing offline tests recorded in Stage 3), `ruff`, `mypy` (19 files checked in the recorded Stage 3 validation), `compileall`, `pip check`, Git LFS-free binary byte preservation via `.gitattributes`, and Playwright Chromium verification across desktop and mobile viewports.
```

---

## 9. Innovation and Impact

```markdown
1. **Epistemological Rigor Over Black-Box Summarization:** Rather than dumping NASA files into an unconstrained chatbot, the system tags data roles at the individual column index (`condition`, `reported_result`, `simulation`, `derived`, `metadata`), keeping numerical CFD predictions (`PSI-117`) and tabulated calculations (`PSI-159`) visibly separated from reported outcomes and test conditions.
2. **Conservative Physical Guardrails:** Preserves raw NASA dimensional anomalies (such as `Burning rate; mm` in FLEX) and refuses silent `psig`-to-`psia` conversions or cross-table overlays when axes/units are incompatible, preventing subtle analytical errors common in automated data tools.
3. **Code-Enforced Grounding (`validate_claims`):** AI output is treated as untrusted candidate selection—every claim must match a retrieved source ID, an exact contiguous substring in the source text, matching numeric tokens, and the source's evidence category before reaching the screen.
4. **Dual-Audience Bilingual Access:** Bridges public STEM outreach and engineering triage in both English and Portuguese, pairing 5-question Guided Journeys for newcomers with deterministic `0–100` Reading Priority ranking and ISA-Tab metadata auditing for technical researchers.
```

---

## 10. Scientific Limitations

```text
1. Selected Subset, Not Full NASA Telemetry: The 40 preserved documents (82.1 MB) exclude multi-gigabyte raw ISS video archives and high-frequency raw sensor telemetry streams.
2. Typed Records Are Not Independent Experiments: The 26,803 typed rows in `observations` combine simulation time steps (16,081), reported outcomes (5,302), setup conditions (3,472), identifiers (1,088), publication references (495), derived calculations (333), and metadata/context (32)—they do not represent 26,803 independent fire tests.
3. Preserved Source Ambiguities & Coverage Gaps:
   - `PSI-62` has ISA metadata only in the collected public selection (no numerical output tables or report in this archive).
   - `PSI-69` retains the ambiguous raw column `Burning rate; mm` and includes a FLEX-2 requirements PDF cataloged by NASA under PSI-69.
   - `PSI-102` includes a 1-page CAD ignitor coil drawing lacking an embedded text layer (`partial` extraction without external Tesseract OCR).
   - `PSI-117` includes ReadMe composition conventions (`XO2=0.21`, `XN2=74/85`, `XO3=Balance`) with unstandardized notation kept raw.
   - Multiple `Saffire` and `PSI-117` columns omit declared units and remain explicitly marked as undeclared.
4. Heuristic Discovery Score Only: The `0–100` Reading Priority score measures term/pillar/file coverage to guide literature reading order—it is not a validated measure of flammability, ignition risk, detector efficacy, or fire suppression performance.
5. External AI & Verification Boundaries: No live Gemini or VLM API validation is claimed for the final release; Gemini is optional and was locally unconfigured in the Stage 3 record, no automated benchmark of combustion-domain RAG precision/recall by independent domain experts has been performed, and the application carries no NASA endorsement or spacecraft safety certification.
```

---

## 11. Future Applications

```text
1. **Expansion Across NASA PSI Combustion Investigations:** The manifest-driven pipeline (`scripts/fetch_psi_tables.py`, `src/pipeline.py`) can ingest additional PSI investigations as public tables, PDFs, or time-series datasets become available without modifying core schemas.
2. **Automated OCR for Legacy Engineering Drawings:** Deploying the workbench in a container with Tesseract OCR installed will unlock full text indexing for scanned or CAD-based engineering schematics such as `PSI-102`'s ignitor assembly drawing.
3. **Live Cloud Deployment & Community Exploration:** Hosting the read-only public instance (`PSI_READONLY_MODE=1`) on Streamlit Community Cloud with a companion GitHub Pages showcase (`docs/index.html`) allows students, educators, and space-safety teams to explore microgravity combustion evidence directly in any browser.
4. **Expert Domain Evaluation & Multimodal Verification:** Independent review by microgravity combustion researchers (including curated question-answering benchmarks and human verification of plotted figure extractions) can evaluate retrieval recall and extend qualitative PDF diagram review workflows.
```


---

## 12. Algorithms and Scientific Methodology

```text
The pipeline preserves original files and records SHA-256 digests, source URLs, investigation identifiers, versions, and DOI references. It extracts PDF text/pages and multi-block spreadsheet or CSV tables, then stores source positions and typed observations in SQLite. Evidence categories distinguish conditions, reported results, simulations, derived calculations, and metadata. Pint normalizes compatible units only when their meaning is declared; ambiguous or gauge pressures are not silently promoted to absolute pressures.

Search combines SQLite FTS5 with vector similarity and structured filters that apply physical constraints to the same original table row. Public deployments can use deterministic bilingual lexical vectors without downloading a large language or embedding model; local installations may use the optional 384-dimensional multilingual embedding model. Retrieved passages retain source identifiers and page/row locations. The reading-priority algorithm uses transparent application, query-term, and local-coverage components (up to 50, 30, and 20 points respectively); this score recommends what to read first, rather than estimating material risk. Comparison checks expose differences in units, evidence roles, and source coverage instead of assuming that every study is quantitatively comparable.
```

## 13. Artificial Intelligence Disclosure

```text
AI coding assistance was used in project development and documentation. Scientific measurements were not generated by AI. The application works without an API key: its default evidence mode searches preserved NASA records and returns source passages and citations. Optional local semantic embeddings support retrieval when installed; the lightweight public configuration uses lexical vectors and SQLite FTS5.

The optional Google Gemini integration receives eligible retrieved public NASA passages and proposes excerpts and short explanations. Code checks citation identifiers, literal quotations, numeric consistency, and evidence-role constraints, with fallback to local evidence on provider failures. These checks reduce specific unsupported outputs; they do not establish independent scientific correctness. Private local-upload passages are excluded from this provider workflow. Optional visual model review requires explicit consent and labels output as inference requiring human review. Gemini/VLM live API performance has not been validated in this release, and independent scientific and retrieval-quality evaluation remain pending.
```

## 14. Expected Impact

```text
Flame in Freefall helps students, educators, and researchers trace microgravity combustion explanations back to NASA sources. Guided bilingual workflows lower the barrier to exploring fire prevention, smoke detection, and suppression research; source-role labels and unit caveats help users recognize when evidence supports a comparison and when it does not. The intended impact is more accessible and reproducible scientific exploration, rather than certified spacecraft safety decisions. Educational effectiveness and engineering outcomes have not yet been measured independently.
```

## 15. Project Links for the Submission

- Source code: https://github.com/kiriworks-co/flame-in-freefall
- Public application (verified without login): https://flame-in-freefall-kiriworks.streamlit.app/
- Source repository currently remains private; the application itself is public and searchable.
- Provenance: [DATA_PROVENANCE.md](DATA_PROVENANCE.md) and [STAGE2_SOURCE_AUDIT.md](STAGE2_SOURCE_AUDIT.md).
- AI disclosure: [AI_USAGE.md](AI_USAGE.md).
- Final release and validation status: [FINAL_RELEASE_STATUS_PTBR.md](FINAL_RELEASE_STATUS_PTBR.md).
