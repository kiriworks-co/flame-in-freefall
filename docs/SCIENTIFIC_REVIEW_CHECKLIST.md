# Scientific Review Checklist — Flame in Freefall (`PSI Flame Microgravity`)

Use this checklist when auditing scientific claims, visualizations, rankings, and NASA provenance across all workspace views (`Home`, `Guided Journeys`, `Investigations`, `Data Explorer`, `Compare`, `Scientific Assistant`, `Visual Page Review`, and `Sources & Methodology`).

---

## 1. Original NASA Archive & Unit Preservation

- [x] **Verbatim NASA identifiers & DOIs**: All 9 PSI investigations (`PSI-25`, `PSI-26`, `PSI-68`, `PSI-69`, `PSI-98`, `PSI-99`, `PSI-100`, `PSI-101`, `PSI-102`) preserve official NASA PSI URLs, study versions, and DOIs listed in [DATA_PROVENANCE.md](DATA_PROVENANCE.md).
- [x] **Ambiguous header `Burning rate; mm` (`PSI-69_Experimental table_FLEX.csv`)**: Original NASA unit header specifies length (`mm`) without time. Preserved verbatim with explicit warnings in `Data Explorer`, `Guided Journey 1`, `Compare`, and `Challenge Hub` — never silently rewritten to `mm/s` or `mm^2/s`.
- [x] **Gauge vs. absolute pressure (`psig` vs. `psia`)**: `src/units.py` forbids inventing ambient cabin pressure when no reference baseline is documented in the source row.
- [x] **Missing/heterogeneous units (`Saffire-I`, `Saffire-II`, `Saffire-III`)**: Unstated column units stay marked as uncertified/missing rather than guessed.
- [x] **Numeric encoding & formatting**: `cp1252` in `PSI-69` CSV and `utf-8-sig` elsewhere preserved accurately at extraction without altering raw cell values.

---

## 2. Document Provenance & Cross-Study Boundaries

- [x] **`FLEX-2` PDF inside `PSI-69` tree**: `PSI-69_Engineering Documents_FLEX Engineering Requirements Document.pdf` is archived under `PSI-69` by NASA, while its cover reads **FLEX-2 Engineering Requirements**. An explicit notice surfaces whenever this document appears in `Data Explorer`, `Scientific Assistant`, or `Challenge Hub` so FLEX-2 engineering requirements are never attributed blindly to original FLEX droplets.
- [x] **`SAME` CAD Ignitor Assembly (`PSI-102`)**: `PSI-102_Engineering Documents_60089MFHA415 Ignitor Wire Coil Assembly (for 0 .250 OD samples).pdf` (1 page) is a technical CAD drawing lacking an embedded text layer. Explicitly flagged as `partial` extraction (full OCR depends on optional external Tesseract).
- [x] **`BASS-II` Contact Proofsheet (`PSI-25`)**: `PSI-25_Raw Data_GMT2014_202_BASS_S220M_TPO5b_ProofSheet.pdf` is a photographic contact sheet, not a digitized telemetry stream.
- [x] **NASA Context Guides separated from empirical runs**: `researchers_guide.pdf` and `psi_database_guide.pdf` (`NASA-CONTEXT`) are labeled as educational/reference background and never mixed into quantitative experimental tables.

---

## 3. Evidence Role Separation & Heuristic Ranking Boundaries

- [x] **Role separation enforced**: Test conditions (`condition`), material/sample descriptors (`sample`), reported experimental outcomes (`measurement`), deterministic summaries/regressions (`calculation`), and qualitative visual interpretations (`inference`) remain separated across charts, tables, and AI outputs.
- [x] **`0–100` Reading Priority Ranking (`RANK` in `Compare` & `Challenge Hub`)**: Computed transparently from application-pillar term relevance (`0–50`), query term overlap (`0–30`), and local artifact coverage (`0–20`) in [`src/relevance.py`](../src/relevance.py) and [`src/challenge_engine.py`](../src/challenge_engine.py).
  - Never presented as a material flammability score, fire-risk rating, detector performance grade, or suppression effectiveness certification.
- [x] **Cross-study comparison (`Compare`)**: Explicit compatibility check highlights mismatched units, differing row granularity (sample catalog vs. ignition test run), and missing shared physical axes before plotting.

---

## 4. AI Assistant & Visual Review Guardrails

- [x] **Offline-first retrieval (`RetrievalIndex`)**: Operates locally via SQLite `FTS5` + deterministic `lexical-vectors` (1,517 structural chunks cleanly isolated offline, or 2,711 token-window semantic chunks when a local embedding model is configured).
- [x] **Optional Google Gemini API (`src/gemini_provider.py`) & OpenAI-compatible adapters (`src/assistant.py`)**:
  - Blocked from external transmission whenever matched passages originate solely from private `local_upload` documents (`filter_public_nasa_evidence`).
  - Rate-limited (rolling 10 requests/min and 40 requests/session cap) with caching and clean fallback to deterministic offline citations on timeout or quota/HTTP error.
  - All LLM claims pass `validate_claims()` requiring literal excerpt verification, matching numbers/categories, and exact cited document IDs before display.
- [x] **Visual Page Review (`src/visual_review.py` + `src/vlm_review.py`)**: Qualitative PDF visual overlays are opt-in per page, quarantined to `analysis_results`, stamped `needs_human_review = True`, and never feed back into numeric tables or retrieval indices.
