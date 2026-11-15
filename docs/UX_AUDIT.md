# UX/UI & Accessibility Audit — Flame in Freefall (Baseline `16acce4`)

**Target Product:** Flame in Freefall (`PSI Flame Microgravity` — NASA Space Apps Challenge 2026)  
**Baseline Audited:** Branch `feat/spaceapps-public-release`, checkpoint `checkpoint/pre-final-product-overhaul` (`16acce4`)  
**Standards Applied:** Nielsen's 10 Usability Heuristics · WCAG 2.2 AA · Progressive Disclosure · Responsive Layout (`1440×1000`, `768×1024`, `375×812`, `200%` zoom)

---

## 1. Key Problems Identified in Baseline `16acce4`

1. **Header & Viewport Spacing Overlap (WCAG 1.4.10 Reflow / Visual Hierarchy)**
   - `[data-testid="stMainBlockContainer"]` used `padding-top: 1.5rem`, allowing Streamlit's fixed top header bar to visually crowd page titles and action buttons at `375px` mobile widths and `200%` zoom.
   - *Fix:* Increase main block top padding to `3.25rem` (`3.5rem` on viewports `<= 48rem`), set restrained container `max-width: 88rem`, and enforce consistent vertical spacing tokens.

2. **Exposed Developer Chrome (Nielsen #8 — Aesthetic & Minimalist Design)**
   - `.streamlit/config.toml` omitted `[client] toolbarMode = "viewer"`, causing developer-oriented `Deploy` and menu controls to appear in public-facing views.
   - Primary UI captions (`home.chunk_caption_lexical`, `sidebar.local_badge`, `ast.mode_lexical`) exposed internal developer tokens (`SQLite + SHA-256`, `RAG_EMBEDDING_MODEL`, `lexical vectors`, `VLM_MODEL`).
   - *Fix:* Configure `[client] toolbarMode = "viewer"` and `showErrorDetails = "none"` in `.streamlit/config.toml`, hide `[data-testid="stDeployButton"]` while keeping sidebar toggle controls functional, and rewrite primary UI copy in clear scientific language (moving engineering diagnostics to an optional Advanced/Technical drawer).

3. **Unobvious Navigation Context & Language Switcher (Nielsen #1 — Visibility of System Status)**
   - Users inside Data Explorer, Compare, or Assistant saw no persistent top breadcrumb/location indicator and had to use the sidebar to return Home (except when arriving from an active Guided Journey).
   - The sidebar language control read `"Language / Idioma"` without the unmistakable segmented **`Language: [EN | PT-BR]`** treatment and quick top-bar toggle.
   - *Fix:* Add a persistent top Context & Navigation Bar displaying **Where you are**, 1-click **Home** and **Back / Return** controls, and a segmented language switcher synced across desktop and mobile without resetting session state or filters.

4. **Missing Explicit 5-Question Structure in Guided Journeys (Comprehension & Progressive Disclosure)**
   - Steps in `src/guided_journeys.py` mixed explanations and charts without an explicit, repeatable mental model answering what a first-time visitor needs at every stage:
     1. *What am I exploring?*
     2. *Why does it matter?*
     3. *What does the NASA evidence show?*
     4. *What can I conclude?*
     5. *What are the limitations?*
   - *Fix:* Upgrade all 4 steps of Journey 1 and Journey 2 to present this structured 5-question comprehension framework alongside interactive visuals and NASA PDF previews before optional raw tables.

5. **Chart-Second Ordering in Data Explorer (`Tab 0`)**
   - Opening Data Explorer defaulted to `Overview & Variables` (`Tab 0`), showing KPI metrics, ISA-Tab text, and a wide statistics DataFrame before any interactive chart (`Tab 1`).
   - *Fix:* Add an immediate visual distribution/relationship preview chart with *"How to Read This Chart"* guidance inside `Tab 0` before any descriptive table, and unify Plotly styling via `style_scientific_figure()`.

6. **Disconnected Space Apps Challenge Pillars (`SUMMARIZE · RANK · INTERPRET`)**
   - Study summarization, 0–100 reading priority ranking, and spacecraft interpretation existed in code (`src/relevance.py`, `src/comparison.py`, `src/i18n.py`) but were fragmented across separate pages.
   - *Fix:* Create `src/challenge_engine.py` and surface an interactive **Space Apps Challenge Hub (SUMMARIZE · RANK · INTERPRET)** on the Homepage, plus richer ranking visualizations in **Compare** and structured **SUMMARIZE / INTERPRET** synthesis cards in **Data Explorer** and **Scientific Assistant**.

7. **Static Assistant Form & Missing Google Gemini API Support**
   - **Scientific Assistant** rendered answers in a single Markdown block rather than a conversational `st.chat_message` research flow, and lacked first-class Google Gemini API (`GEMINI_API_KEY` / `GOOGLE_API_KEY`) support.
   - *Fix:* Upgrade the Assistant UI with `st.chat_message` visual conversation turns, **SUMMARIZE / INTERPRET** cards, preserved 2-row (`3+2`) beginner-friendly quick questions, and an optional privacy-safe `src/gemini_provider.py` supporting `gemini-2.5-flash` with strict `validate_claims()` verification and offline deterministic fallback.

---

## 2. Nielsen Heuristics & WCAG 2.2 AA Verification Matrix

| Principle / Criterion | Issue in `16acce4` | Remediation Implemented |
|---|---|---|
| **H1: Visibility of system status** | No top page breadcrumb when navigating directly | Persistent top context bar showing active section, journey step progress, and AI/evidence status |
| **H2: Match real world / Plain language** | Developer strings (`lexical vectors`, `SQLite + SHA-256`, `RAG_EMBEDDING_MODEL`) in primary UI | Plain-language scientific explanations in primary view; engineering details moved to collapsible Technical Diagnostics |
| **H3: User control & freedom** | Back button missing on non-journey pages; language switch needed two glances | Persistent `Home` + `Back` actions in top bar + clear `← Back` / `Continue →` step footer + prominent `Language: [EN \| PT-BR]` pill |
| **H6: Recognition rather than recall** | Required users to recall experiment acronyms (`PSI-69`, `PSI-102`) | Homepage entry cards + 5-question step headers + Space Apps Challenge Hub (`SUMMARIZE · RANK · INTERPRET`) |
| **WCAG 1.4.3 Contrast (>= 4.5:1)** | `#A44426` on light neutral `#FAFAF7` was borderline (~5.1:1), body muted captions `#666` needed tightening | Deep aerospace navy `#0F1D2B` (~16.5:1), secondary slate `#3E4C59` (~8.6:1), terracotta-flame `#B84A24` (~4.8:1), ocean blue `#1D5B86` (~6.9:1) |
| **WCAG 1.4.10 Reflow / 200% Zoom** | `padding-top: 1.5rem` risked fixed header overlap | `padding-top: 3.25rem` desktop / `3.5rem` mobile; responsive flex/grid wrapping with zero horizontal overflow |
| **WCAG 2.4.7 Focus Visible** | Basic focus ring on buttons/radios | High-contrast `3px solid #B84A24` focus-visible outline across buttons, links, inputs, tabs, and segmented controls |
| **WCAG 2.5.8 Target Size (>= 44px)** | Compact controls could dip under 42px on dense bars | Minimum interactive height `2.65rem` (`42.4px–44px`) enforced on primary buttons, links, and pill toggles |
