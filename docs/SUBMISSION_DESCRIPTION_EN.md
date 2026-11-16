# Flame in Freefall — NASA Space Apps Challenge 2026 Submission Description

---

## Short Version (Summary / Submission Card)

### Project Title
**Flame in Freefall** (`PSI Flame Microgravity`)

### Elevator Pitch
On Earth, buoyancy stretches fires into rising teardrops; in orbital freefall, flames turn spherical, smoke lingers in cabin airflow, and low-temperature cool flames persist. **Flame in Freefall** turns **12 real NASA Physical Sciences Informatics (PSI) combustion investigations** and **2 official NASA guides** into a bilingual (`EN` / `PT-BR`), cryptographically verified (`SHA-256`) scientific workbench where anyone can **SUMMARIZE**, **RANK**, and **INTERPRET** microgravity fire evidence—without fabricating measurements or confusing test conditions with flight certification.

### Concise Problem & Solution
NASA's public PSI repository holds authentic International Space Station and spacecraft fire research scattered across heterogeneous CSVs, spreadsheets, engineering PDFs, and ISA-Tab metadata with conflicting units (`psia`, `psig`, `mmHg`, `cm/s`, mole fractions) and mixed evidence types. **Flame in Freefall** unifies **40 preserved NASA files (82.1 MB)** into an offline-capable SQLite + hybrid search (`FTS5` + 384-d embeddings) platform with conservative `Pint` unit guards, chart-first visualizations, structured 4-step guided journeys, cross-study compatibility checks, and an evidence-grounded assistant (with optional Google Gemini excerpt selection validated programmatically in code).

---

## Extended Version (Full Technical & Scientific Submission)

### Project Title
**Flame in Freefall** (`PSI Flame Microgravity`)

### Elevator Pitch
**Flame in Freefall** is a verifiable, bilingual (`English` / `Portuguese PT-BR`) scientific exploration platform built on **12 real NASA PSI microgravity combustion investigations** and **2 official NASA reference guides**. Designed for judges, students, engineers, and researchers, it combines guided discovery journeys with a rigorous scientific workbench to **SUMMARIZE** experiments, **RANK** reading priority transparently, and **INTERPRET** spacecraft fire-safety implications while strictly separating test conditions, reported experimental outcomes, CFD simulations, calculations, and metadata.

---

### Problem
Inside a spacecraft in orbital freefall (`~0g`), natural upward buoyancy nearly vanishes. Flames no longer rise like teardrops; instead, hot gases surround the fuel symmetrically, oxygen arrives via slow molecular diffusion or gentle cabin ventilation fans, soot particles stay suspended longer, and liquid or gaseous fuels can sustain low-temperature **cool flames**. Understanding these dynamics is critical for spacecraft **Prevention**, **Detection**, and **Suppression**.

However, working directly with public NASA PSI datasets presents major hurdles:
1. **Fragmented heterogeneous formats:** flight data, simulations, engineering requirements, and final reports are distributed across `cp1252` and `utf-8-sig` CSVs, XLSX ReadMe workbooks, multi-page PDFs, CAD drawings, and ISA-Tab archives.
2. **Mixed evidence roles:** a CSV listing planned chamber mixtures (`condition`) looks structurally identical to a file of post-test measurements (`reported_result`) or computational fluid dynamics (`simulation`) curves.
3. **Unit pitfalls:** unreferenced `mmHg`, gauge pressure (`psig`) vs. absolute pressure (`psia`), and ambiguous headers such as `Burning rate; mm` in `PSI-69` (which omits a time unit) can silently corrupt naive analysis.
4. **Risk of ungrounded AI summaries:** generic LLM chatbots frequently invent numbers, merge incompatible test scales, or misrepresent setup parameters as flight safety ratings.

---

### Solution
**Flame in Freefall** preserves the authentic NASA PSI bytes verbatim and wraps them in a transparent, evidence-first analytical architecture:
- **Cryptographic Provenance:** Every source file is stored untouched alongside its `SHA-256` digest, confirmed NASA DOI, study version, and permanent PSI URL (never expired S3 links).
- **Guided Discovery & Visual Clarity:** Visitors begin with an immediate visual comparison of `1g` Earth vs. `~0g` orbital combustion, real-time archive metrics, three structured entry paths (*Discover the Science*, *Explore Fire Safety*, *Investigate NASA Data*), two 4-step **Guided Journeys** framed around **5 Scientific Questions**, and an interactive **Space Apps Challenge Hub (`SUMMARIZE · RANK · INTERPRET`)**.
- **Rigorous Data & Search Workbench:** Researchers can inspect multi-block tables, generate Plotly visualizations paired with *"How to Read This Chart"* guides, run row-aligned physical filters, verify compatibility across 2–3 studies before comparing, render original PDF pages locally, and query a hybrid RAG assistant that works 100% offline or with optional Google Gemini grounding.

---

### Main Features
1. **Home & Space Apps Challenge Hub (`SUMMARIZE · RANK · INTERPRET`):** Instant study summarization anchored to archived files, deterministic `0–100` reading-priority ranking across habitat prevention, smoke detection, and flame suppression, and structured safety boundary interpretation.
2. **Guided Journeys 1 & 2 (5-Question Framework):** Beginner-friendly 4-step interactive walkthroughs covering buoyancy vs. diffusion (`1g` vs `0g`), `PSI-69 (FLEX)` droplet extinction plots, and the three defense layers (`BASS-II` / `Saffire` prevention, `SAME` smoke detection, `FLEX` / `CFI-G` suppression) with persistent journey return state.
3. **NASA Investigations Catalog:** Searchable catalog of all 12 NASA PSI investigations and 2 official guides with confirmed DOIs, permanent links, safety-pillar filters, documented caveats, and 1-click jump into Data Explorer.
4. **6-Tab Data Explorer:**
   - *Overview & Variables:* Visual First Look preview chart, identified physical quantities, descriptive summary, and unit glossary.
   - *Interactive Charts:* Line, scatter, bar, correlation heatmap, and X–Y–Color plots with reversible column swaps, derived operations, linear fits, peak/FWHM analysis, and CSV/JSON/HTML exports.
   - *Tables & Source Rows:* Raw extracted blocks with per-column evidence classification (`condition`, `reported_result`, `simulation`, `derived`, `metadata`) and Data-ID cross-referencing.
   - *Documents & Integrity:* Live `SHA-256` verification, raw NASA file downloads, and extracted metadata/text previews.
   - *PDF Reader & Search:* Bilingual keyword search jumping directly to locally rendered physical PDF pages.
   - *ISA-Tab Metadata:* Structured view of `i_Investigation*.txt` fields, publications, and contacts.
5. **Safe Cross-Study Comparator & Reading Priority Matrix:** Enforces physical quantity, unit, condition, and methodology checks before declaring two tables quantitatively comparable, paired with a transparent `0–100` reading-priority score.
6. **Evidence-First Scientific Assistant:** Hybrid retrieval (**SQLite FTS5** + 384-d local embeddings or deterministic lexical vectors) with row-aligned filters (`O₂ mole fraction`, absolute `psia` pressure, flow velocity `cm/s`, fuel), clickable citations, and optional Google Gemini integration (`gemini-2.5-flash`) enforced by programmatic validation.
7. **Visual Page Review (Offline PDF Inspector):** Page-by-page PDF diagram viewer (`PyMuPDF`) with optional consent-gated VLM qualitative review strictly quarantined as `inference` (`needs_human_review = True`).
8. **Bilingual (`EN` / `PT-BR`) & Public Read-Only Safety:** Single synchronized top-bar language selector and automatic `PSI_READONLY_MODE` protection for public deployments.

---

### Scientific Methodology
- **Conservative Dimensional Normalization (`Pint`):** Converts only explicitly declared units (`1 atm = 14.6959 psia`, `1 m/s = 100 cm/s`, `°C → K`, `% O₂ → mole fraction`). Gauge pressures (`psig`) and unreferenced `mmHg`/`psi` are never silently treated as `psia`; `Burning rate; mm` in `PSI-69` remains raw with explicit warnings.
- **Strict Role Separation:** Each column index in `scientific.sqlite3` (`26,803` typed observation values across `117` tables and `10,114` tabular rows) carries its source role (`16,081` simulation, `5,302` reported_result, `3,472` condition, `1,088` identifier_or_unclassified, `495` engineering_or_publication, `333` derived, `27` metadata, `5` context). These `26,803` typed cells are explicitly documented as extracted field values, **never** as `26,803` independent experiments.
- **Preserved Anomalies & Placeholders:** Three 56-byte ISA placeholder files (`s_PSI-62.txt`, `s_PSI-117.txt`, `s_PSI-159.txt` containing `"Do not use this"`) and two empty inner ZIPs in `PSI-117` are preserved for auditability and excluded from scientific claims. The `PSI-69` PDF bearing `FLEX-2` on its cover is flagged everywhere it appears.
- **No Unwarranted Pooling:** Plots and comparisons block silent mixing of incompatible units or independent time axes (such as multi-block columns in `PSI-117` CSVs).

---

### NASA Data Sources
Primary source: **NASA Physical Sciences Informatics (PSI)** (`https://psi.nasa.gov/physci/repo/search?q=combustion`) — **12 PSI investigations + 2 official NASA guides**, totaling **40 preserved documents (82,099,713 bytes; 37 substantive files + 3 ISA placeholders)**:

- **Prevention:**
  - `PSI-25` — **BASS-II** (*Burning and Suppression of Solids II*, DOI `10.60555/4qc4-de67`)
  - `PSI-26` — **BASS** (*Burning and Suppression of Solids*, DOI `10.60555/58h4-dy80`)
  - `PSI-62` — **Concurrent Flame Spread Modeling (UFGM)** (DOI `10.60555/e9xp-ex83`, *metadata-only public ISA archive*)
  - `PSI-98` — **Saffire-I** (DOI `10.60555/0t15-1z43`)
  - `PSI-99` — **Saffire-II** (DOI `10.60555/2chp-m469`)
  - `PSI-100` — **Saffire-III** (DOI `10.60555/040q-4h36`)
- **Detection:**
  - `PSI-101` — **SAME-R** (*Smoke Aerosol Measurement Experiment - Reflight*, DOI `10.60555/2np7-jv14`)
  - `PSI-102` — **SAME** (*Smoke Aerosol Measurement Experiment*, DOI `10.60555/gd4k-8h62`)
- **Suppression & Cool Flames:**
  - `PSI-68` — **FLEX-2** (DOI `10.60555/byp8-h018`)
  - `PSI-69` — **FLEX** (*Flame Extinguishment Experiment*, DOI `10.60555/mbq8-0451`)
  - `PSI-117` — **Cool Flame Dynamics (CFD / FLEX Comparison)** (DOI `10.60555/gz0q-b577`, 9 CSVs separating CFD and experimental reference series + 4 PDF presentations + XLSX ReadMe + ISA metadata)
  - `PSI-159` — **ACME CFI-G** (*Cool Flames Investigation with Gases*, DOI `10.60555/cyt1-kh64`, Normal/Inverse Flames CSVs + Engineering & 93-p. Final Report PDFs + ISA metadata)
- **Official NASA Reference Guides (`NASA-CONTEXT`):**
  - *A Researcher's Guide to ISS Combustion Science* (`researchers_guide.pdf`)
  - *Complete PSI Database Guide* (`psi_database_guide.pdf`)

---

### Technology Stack
- **Language & Runtime:** Python 3.11+ (tested locally on Python 3.12.14, pinned to `3.11` for cloud portability)
- **Interface & Visualization:** Streamlit (`>=1.57`), Plotly (`>=5.18`), custom Aerospace Laboratory Daylight CSS/SVG design system
- **Data, Units & Documents:** Pandas, NumPy, Pint (`>=0.24`), PyMuPDF (`>=1.23`), openpyxl, xlrd, python-docx, Pillow
- **Storage & Retrieval:** SQLite (`scientific.sqlite3` + `search.sqlite3` with `FTS5`), scikit-learn, optional `sentence-transformers` (`paraphrase-multilingual-MiniLM-L12-v2`, 384-d)
- **AI & QA:** Optional Google Gemini REST API (`gemini-2.5-flash` via `urllib.request`), `pytest` (164 passing offline tests), `ruff`, `mypy`

---

### AI Usage
AI inside **Flame in Freefall** is strictly bounded, optional, and subordinate to deterministic scientific verification:
1. **Offline Hybrid Retrieval:** Combines SQLite `FTS5` with local 384-d semantic vectors (`paraphrase-multilingual-MiniLM-L12-v2`) or deterministic EN/PT lexical vectors—requiring zero external API keys to search 15,524 indexed passages and cite exact pages/rows.
2. **Optional Google Gemini Grounding (`src/gemini_provider.py` + `src/assistant.py`):** When an API key is configured, `filter_public_nasa_evidence()` blocks private local uploads from leaving the host; Gemini receives only the top retrieved public NASA passages and returns structured JSON (`citation`, verbatim `quote`, `kind`, and optional 1-sentence anchored `explanation`) constrained by `responseSchema` and per-session (`40`) / server (`10/min`, `250/day`) rate caps.
3. **Code-Enforced Verification (`validate_claims`):** Every claim and optional explanation is checked programmatically in Python: ungrounded citations, non-verbatim quotes, unsupported numbers, safety-certification claims, or condition/simulation-to-measurement relabeling are rejected automatically.
4. **Isolated Visual Candidate Mode:** Optional VLM inspection of an explicitly chosen PDF page is quarantined in `analysis_results` as `inference` (`needs_human_review = True`).

---

### Innovation
- **Programmatic Scientific Grounding (Not Prompt-Only Guardrails):** Grounding invariants live in Python verification code rather than trusting LLM instructions alone.
- **Anti-Conflation Tabular Engine:** Automatically detects multi-block NASA spreadsheets, classifies column provenance (`condition` vs `reported_result` vs `simulation` vs `derived`), and blocks misleading cross-study overlays.
- **Dual-Audience Experience:** Bridges approachable 4-step science storytelling (with 5-question comprehension guides and a `1g` vs `0g` schematic) with audit-grade traceability (`SHA-256`, DOI, page/row links) in a single portable application.

---

### Spacecraft Fire Safety Relevance
**Flame in Freefall** helps engineers, educators, and mission planners inspect real orbital evidence across all three layers of spacecraft fire defense:
- **Prevention (`BASS`, `BASS-II`, `Saffire I–III`, `PSI-62`):** Examine how cabin airflow and elevated oxygen atmospheres influence solid-material ignition and flame spread.
- **Detection (`SAME`, `SAME-R`):** Explore how smoke particle-size distributions shift without buoyancy, informing spacecraft fire-detector calibration.
- **Suppression (`FLEX`, `FLEX-2`, `PSI-117`, `PSI-159`):** Inspect diluent extinction limits, spherical droplet lifetimes, and low-temperature cool-flame behavior.

---

### Limitations
- **No NASA endorsement and no independent scientific validation claimed:** All insights are exploratory and strictly derived from public NASA PSI files; the owner's independent scientific review remains pending.
- **Not a fire-safety certification tool:** Reading priority scores (`0–100`), descriptive statistics, and linear trend fits never certify materials or spacecraft hardware for flight.
- **Source coverage bounds:** High-rate raw telemetry videos and gigabyte binary datasets remain on NASA PSI; `PSI-62` exposes metadata only; `PSI-69` preserves ambiguous `Burning rate; mm` and cataloged `FLEX-2` PDF notices; `PSI-102` CAD drawing OCR depends on external Tesseract; three `s_*.txt` ISA files are empty placeholders.
- **Gemini live key pending owner setup:** The Google Gemini provider is complete and verified against mocked HTTP responses and rate-limit tests, while live cloud inference activates once the owner supplies a Google AI Studio key.

---

### Future Potential
- Incorporate additional combustion studies from NASA PSI and OSDR (with continued strict namespace separation).
- Add automated Tesseract/OCR pipelines for scanned legacy engineering schematics while maintaining human-review tags.
- Support direct user-contributed annotation packs and reproducible Jupyter/CSV analysis bundle exports for classroom and engineering team reviews.
