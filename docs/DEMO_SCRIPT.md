# 3-Minute Live Demo Script (EN & PT-BR) — NASA Space Apps 2026

This guided demonstration highlights the complete scientific, UX, and provenance workflow without requiring prior combustion expertise. It mirrors the 4-step **Guided Tour** built into **Home / Overview**.

---

## 0:00 – 0:45 | Home / Overview & Language Switcher (`home`)
1. Open the app (`English (EN)` active by default) and highlight:
   - *Why does fire behave differently in freefall?* (buoyancy loss → spherical flames, cool flames, slower smoke clearing).
   - Live metrics across **9 NASA PSI Studies**, **16 Preserved NASA Files**, **31 Extracted Tables**, and **1,517 Indexed Chunks**.
2. Demonstrate instant bilingual access: toggle `Language / Idioma` in the sidebar to **Português (PT-BR)**, show UI localization updating cleanly while NASA study IDs (`PSI-69`, `BASS-II`) and source data stay immutable, then switch back to **English (EN)** (or continue in either language).

## 0:45 – 1:30 | Investigations & Data Explorer (`investigations` → `explorer`)
1. Click **Investigations** (or click step 1 in the Guided Tour) and filter by **Suppression** to inspect `PSI-69 · FLEX` (objective, spacecraft safety relevance, verified DOI `10.60555/mbq8-0451`, and documented caveats).
2. Click **Open in Data Explorer** (`PSI-69`):
   - Expand **Variable & Unit Glossary** to clarify `O₂ mole fraction`, `psia vs psig`, and why `Burning rate; mm` is kept raw.
   - Inspect **Interactive Charts** (Plotly visualization) and **Tables & Source Rows** showing original CSV row numbers.
   - Open **Documents & Integrity** to verify immutable **SHA-256** verification and original byte download (while public uploads stay safely disabled in read-only cloud mode).

## 1:30 – 2:15 | Compare Safely (`compare`)
1. Switch to **Compare** and click the quick preset **FLEX (PSI-69) vs BASS-II (PSI-25)**.
2. Highlight the explicit scientific guardrail: *Joint quantitative pooling NOT validated* — explaining why droplet extinction data (`mm`) and solid-fuel test conditions cannot be merged blindly.
3. Show the deterministic **0–100 Reading Priority Ranking** below, explicitly clarifying that it ranks reading relevance rather than fire risk.

## 2:15 – 3:00 | Evidence-First Assistant & Sources (`assistant` → `sources`)
1. Open **Scientific Assistant**:
   - Note the transparent disclosure banner when external LLM generation is unconfigured (*Evidence Retrieval Mode*).
   - Click Example Question 1 (**FLEX droplet O₂ conditions (18–25%)**) to filter `PSI-69` rows matching `0.18 <= O₂ <= 0.25`. Inspect verbatim cited text, permanent NASA link, DOI, and **SHA-256**.
   - Click Example Question 5 (**Unsupported query guard demo**) to demonstrate zero hallucination when evidence is absent.
2. Finish briefly on **Sources & Methodology** (`sources`) and **Visual Page Review** (`visual_review`, optional `SAME Final Report · p. 13` local render) emphasizing verifiable NASA provenance (`https://psi.nasa.gov/physci/repo/search?q=combustion`).
