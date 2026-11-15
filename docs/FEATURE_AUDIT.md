# Feature & Capability Audit — Flame in Freefall (`PSI Flame Microgravity`)

**Repository:** `PROJETO TESTE FLAME MICROGRAVITY`  
**Branch:** `feat/spaceapps-public-release`  
**Checkpoint Baseline:** `checkpoint/pre-final-product-overhaul` (`16acce4`)

---

## 1. Preserved Core Scientific Architecture

| Capability / Module | Implementation | Status | Notes |
|---|---|---|---|
| **9 NASA PSI Investigations & 2 Official Guides** | `data/psi_downloads/`, `resources/official/`, `resources/manifests/` | **Preserved** | `PSI-25`, `PSI-26`, `PSI-68`, `PSI-69`, `PSI-98`, `PSI-99`, `PSI-100`, `PSI-101`, `PSI-102` + ISS/PSI guides (`16` verified files, SHA-256 verified) |
| **SQLite Persistence & Ingestion** | `src/storage.py`, `src/scientific_store.py`, `src/extractors.py`, `src/pipeline.py` | **Preserved** | Cold-start `ensure_scientific_bootstrap()` creates `scientific.sqlite3` & `search.sqlite3` cleanly (`1,517` deterministic offline structural chunks or `2,711` local semantic token chunks) |
| **Conservative Unit Engine** | `src/units.py` | **Preserved** | Pint conversions; preserves `psig` vs `psia` separation and raw `Burning rate; mm` ambiguity without fabricated assumptions |
| **Hybrid Scientific Search & Numeric Filters** | `src/retrieval.py` | **Preserved** | SQLite `FTS5` + offline `lexical-vectors` or optional local `paraphrase-multilingual-MiniLM-L12-v2` embeddings; row-aligned physical filters |
| **Evidence-First Extractive Verification** | `src/assistant.py` | **Preserved & Extended** | `validate_claims()` rejects ungrounded claims, numeric mismatches, and category drift |
| **Table Compatibility & Comparison** | `src/comparison.py`, `src/relevance.py` | **Preserved** | Schema/unit checks before plotting; transparent `0–100` heuristic reading-priority ranking (`relevance` never equated to fire safety score) |
| **Offline Visual Page Review** | `src/visual_review.py`, `src/vlm_review.py` | **Preserved** | PyMuPDF page rendering + quarantined `inference` overlays (`needs_human_review = True`) |
| **Security & Read-Only Controls** | `app.py`, `src/pipeline.py`, `tests/test_security_regressions.py` | **Preserved** | Path traversal checks, inert Markdown escaping, size limits, automatic cloud `is_public_readonly()` |

---

## 2. Redesigned UX, UI, Bilingual, and AI Enhancements

| Enhancement | Module(s) | Status | Verification Summary |
|---|---|---|---|
| **Aerospace Daylight Design System** | `src/design_system.py`, `docs/DESIGN_SYSTEM.md`, `.streamlit/config.toml` | **Implemented & Browser-Verified** | High-contrast palette (`#0F1D2B`, `#B84A24`, `#1D5B86`), tabular numbers, responsive tablet/mobile column wrapping, `[client] toolbarMode = "viewer"` (hides developer `Deploy` chrome), `initial_sidebar_state="auto"` |
| **Persistent Top Context & Navigation Bar** | `src/design_system.py`, `app.py` | **Implemented & Browser-Verified** | Displays *Where you are*, active journey state, `← Back`, `🏠 Home`, and quick `EN ↔ PT-BR` toggle synchronized with sidebar `Language: [EN | PT-BR]` |
| **Discovery Homepage & Challenge Hub** | `src/scientific_ui.py`, `src/challenge_engine.py`, `src/i18n.py` | **Implemented & Verified** | Plain-English title/subtitle, 3 starting cards (Journeys 1 & 2 + Research Tools), and interactive **`SUMMARIZE · RANK · INTERPRET`** tabs with safe option handling across language switches |
| **Structured 5-Question Guided Journeys** | `src/guided_journeys.py` | **Implemented & Verified** | All 4 steps of Journeys 1 & 2 follow *What am I exploring? · Why does it matter? · What does NASA evidence show? · What can I conclude? · What are the limitations?* with interactive Plotly charts, PDF previews, and fixed PT pillar filters |
| **Chart-First Data Explorer & Style Standard** | `src/views.py`, `src/design_system.py` | **Implemented & Verified** | Added interactive **Visual First Look** plot + **SUMMARIZE & INTERPRET** frame directly inside `Tab 0` before wide descriptive tables; unified Plotly layout (`style_scientific_figure`) |
| **Conversational Assistant & Gemini Provider** | `src/gemini_provider.py`, `src/assistant.py`, `src/scientific_ui.py` | **Implemented (Unconfigured Locally)** | `st.chat_message` turns + optional Google Gemini adapter (`gemini-2.5-flash` via `GEMINI_API_KEY`/`GOOGLE_API_KEY`), `filter_public_nasa_evidence` blocking `local_upload`, rolling rate caps (`10/min`, `40/session`), verified with mocked HTTP tests and deterministic offline fallback |
| **Complete English / Português (PT-BR) Parity** | `src/i18n.py` | **Implemented & Verified** | Complete EN/PT key parity tested automatically; preserves canonical NASA titles, DOIs, and raw experimental headers |
