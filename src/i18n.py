"""Centralized bilingual localization (English default + Portuguese PT-BR) and domain glossaries."""
from __future__ import annotations

from typing import Any

import streamlit as st

DEFAULT_LANG = "en"
LANGUAGE_OPTIONS: dict[str, str] = {
    "en": "English (EN)",
    "pt": "Português (PT-BR)",
}

SECTION_KEYS: list[str] = [
    "home",
    "investigations",
    "explorer",
    "compare",
    "assistant",
    "visual_review",
    "sources",
]

_SECTION_ALIASES: dict[str, str] = {
    "home": "home",
    "home / overview": "home",
    "visão geral": "home",
    "início / visão geral": "home",
    "investigations": "investigations",
    "investigações": "investigations",
    "investigações nasa": "investigations",
    "explorer": "explorer",
    "data explorer": "explorer",
    "explorador de dados": "explorer",
    "arquivos do experimento": "explorer",
    "compare": "compare",
    "comparar": "compare",
    "comparar estudos": "compare",
    "assistant": "assistant",
    "scientific assistant": "assistant",
    "assistente científico": "assistant",
    "busca e assistente": "assistant",
    "visual_review": "visual_review",
    "visual page review": "visual_review",
    "revisão visual": "visual_review",
    "sources": "sources",
    "sources & methodology": "sources",
    "fontes e metodologia": "sources",
    "ingestão e fontes": "sources",
}


def normalize_section(value: str | None) -> str:
    """Normalize canonical, English, or legacy Portuguese section identifiers."""
    if not value:
        return "home"
    return _SECTION_ALIASES.get(str(value).strip().casefold(), "home")


def get_lang() -> str:
    """Return active session language ('en' by default)."""
    raw = str(st.session_state.get("lang", DEFAULT_LANG)).strip().lower()
    return "pt" if raw.startswith("pt") else "en"


def set_lang(lang: str) -> None:
    """Update active session language cleanly."""
    st.session_state["lang"] = "pt" if str(lang).strip().lower().startswith("pt") else "en"


def section_label(section_key: str, lang: str | None = None) -> str:
    """Return localized navigation label for a canonical section key."""
    return t(f"nav.{section_key}", lang=lang)


# ----------------------------------------------------------------------------- Investigation scientific summaries
# Original NASA PSI IDs, official titles, DOIs, and filenames are NEVER altered.

INVESTIGATION_PROFILES: dict[str, dict[str, dict[str, str]]] = {
    "PSI-25": {
        "en": {
            "pillar": "Prevention",
            "objective": "Burning and Suppression of Solids II (BASS-II): examine upward, downward, and opposed-flow flame spread over solid fuels in microgravity.",
            "relevance": "Supports spacecraft material flammability screening and cabin airflow limits for fire prevention.",
            "caveat": "Includes 16-page SRD, experimental conditions CSV, and a single proofsheet image PDF (not raw sensor telemetry).",
        },
        "pt": {
            "pillar": "Prevenção",
            "objective": "Burning and Suppression of Solids II (BASS-II): investigar propagação de chama em combustíveis sólidos em microgravidade sob fluxos opostos e concorrentes.",
            "relevance": "Apoia a triagem de inflamabilidade de materiais e limites de ventilação para prevenção de incêndios em espaçonaves.",
            "caveat": "Inclui SRD de 16 páginas, CSV de condições experimentais e um proofsheet em imagem (não é telemetria bruta de sensores).",
        },
    },
    "PSI-26": {
        "en": {
            "pillar": "Prevention",
            "objective": "Burning and Suppression of Solids (BASS): catalog microgravity solid-fuel burn tests across varying geometries and oxygen levels.",
            "relevance": "Provides baseline solid-material combustion test conditions aboard the ISS.",
            "caveat": "CSV is primarily a test/sample catalog; does not establish full flame-spread curves or safety certification.",
        },
        "pt": {
            "pillar": "Prevenção",
            "objective": "Burning and Suppression of Solids (BASS): catalogar ensaios de queima de sólidos em microgravidade com diferentes geometrias e níveis de O₂.",
            "relevance": "Fornece condições de base para estudos de combustão de materiais sólidos a bordo da ISS.",
            "caveat": "O CSV é sobretudo um catálogo de ensaios/amostras; não traz curvas completas de propagação nem certificação de segurança.",
        },
    },
    "PSI-68": {
        "en": {
            "pillar": "Suppression",
            "objective": "Flame Extinguishment Experiment 2 (FLEX-2): study spherical droplet combustion, soot formation, and cool-flame extinction.",
            "relevance": "Explores extinction regimes of liquid fuel droplets under controlled oxygen and diluent atmospheres.",
            "caveat": "Experimental table reports test conditions and parameter ranges rather than complete time-series histories.",
        },
        "pt": {
            "pillar": "Supressão",
            "objective": "Flame Extinguishment Experiment 2 (FLEX-2): estudar combustão esférica de gotas, formação de fuligem e extinção de chamas frias.",
            "relevance": "Investiga regimes de extinção de gotas líquidas sob concentrações controladas de oxigênio e diluentes.",
            "caveat": "A tabela experimental contém condições e intervalos de parâmetros, não séries temporais completas.",
        },
    },
    "PSI-69": {
        "en": {
            "pillar": "Suppression",
            "objective": "Flame Extinguishment Experiment (FLEX): measure droplet ignition, burning duration, and visible flame extinction diameters in freefall.",
            "relevance": "Informs fire suppression thresholds (limiting O₂ index and diluent effects) in microgravity.",
            "caveat": "Header 'Burning rate; mm' is dimensionally ambiguous (preserved raw). NASA catalogs a FLEX-2 requirements PDF under PSI-69 (explicitly flagged).",
        },
        "pt": {
            "pillar": "Supressão",
            "objective": "Flame Extinguishment Experiment (FLEX): medir ignição de gotas, tempo de queima e diâmetro de extinção visível em queda livre.",
            "relevance": "Contribui para entender limiares de supressão (índice limite de O₂ e efeito de diluentes) em microgravidade.",
            "caveat": "O cabeçalho 'Burning rate; mm' tem unidade dimensional ambígua (preservado bruto). O catálogo NASA associa um PDF de FLEX-2 a PSI-69 (sinalizado).",
        },
    },
    "PSI-98": {
        "en": {
            "pillar": "Prevention",
            "objective": "Spacecraft Fire Experiment I (Saffire-I): large-scale flame growth over cotton-fiberglass fabric inside an uncrewed Cygnus resupply vehicle.",
            "relevance": "Bridges small ISS chamber tests to spacecraft-scale cabin fire behavior.",
            "caveat": "Summary CSV has 4 rows with partial/missing units; avoid cross-study pooling without original reports.",
        },
        "pt": {
            "pillar": "Prevenção",
            "objective": "Spacecraft Fire Experiment I (Saffire-I): propagação de chama em larga escala em tecido algodão-fibra de vidro dentro de cargueiro Cygnus não tripulado.",
            "relevance": "Conecta ensaios em pequena escala na ISS ao comportamento real de incêndios em escala de cabine espacial.",
            "caveat": "O CSV resumo tem 4 linhas com unidades heterogêneas ou ausentes; não agrupar curvas sem relatório original.",
        },
    },
    "PSI-99": {
        "en": {
            "pillar": "Prevention",
            "objective": "Spacecraft Fire Experiment II (Saffire-II): evaluate flame spread across nine distinct spacecraft material samples in orbital flight.",
            "relevance": "Compares ignition and spread behavior across candidate cabin materials under realistic airflow.",
            "caveat": "Contains sparse cells and mixed/missing unit declarations in some table headers.",
        },
        "pt": {
            "pillar": "Prevenção",
            "objective": "Spacecraft Fire Experiment II (Saffire-II): avaliar propagação de chama em nove amostras distintas de materiais espaciais em voo orbital.",
            "relevance": "Compara comportamento de ignição e propagação entre materiais candidatos de cabine sob escoamento realista.",
            "caveat": "Contém células vazias e cabeçalhos com declarações de unidade ausentes ou heterogêneas.",
        },
    },
    "PSI-100": {
        "en": {
            "pillar": "Prevention",
            "objective": "Spacecraft Fire Experiment III (Saffire-III): investigate large-scale flame propagation under higher spacecraft airflow velocity.",
            "relevance": "Examines how elevated ventilation rates alter flame spread length and heat release in microgravity.",
            "caveat": "2-row summary table lacks explicit unit labels on several columns; units are never guessed.",
        },
        "pt": {
            "pillar": "Prevenção",
            "objective": "Spacecraft Fire Experiment III (Saffire-III): investigar propagação de chama em larga escala sob maior velocidade de ventilação.",
            "relevance": "Examina como taxas mais altas de ventilação alteram extensão da chama e liberação de calor em microgravidade.",
            "caveat": "Tabela resumo de 2 linhas sem unidades explícitas em várias colunas; unidades nunca são presumidas.",
        },
    },
    "PSI-101": {
        "en": {
            "pillar": "Detection",
            "objective": "Smoke Aerosol Measurement Experiment - Reflight (SAME-R): characterize particle size distributions of smoke generated by spacecraft materials.",
            "relevance": "Guides false-alarm reduction and early-smoke detector sensitivity for crewed habitats.",
            "caveat": "Describes sample configurations, aging, and stated mass-loss rate; not a full detector-efficiency benchmark.",
        },
        "pt": {
            "pillar": "Detecção",
            "objective": "Smoke Aerosol Measurement Experiment - Reflight (SAME-R): caracterizar distribuição de tamanho de partículas de fumaça de materiais espaciais.",
            "relevance": "Orienta redução de alarmes falsos e sensibilidade de detectores de fumaça em habitats tripulados.",
            "caveat": "Descreve configurações de amostra, envelhecimento e taxa declarada de perda de massa; não é benchmark completo de eficácia de detector.",
        },
    },
    "PSI-102": {
        "en": {
            "pillar": "Detection",
            "objective": "Smoke Aerosol Measurement Experiment (SAME): measure smoke aerosol characteristics from overheated wire insulation and materials.",
            "relevance": "Directly informs ISS and deep-space smoke detector design (also referenced in NASA Spinoff fire detectors).",
            "caveat": "Includes 68-page Final Science Report PDF and 1-page ignitor coil CAD drawing (no text layer; OCR needs Tesseract).",
        },
        "pt": {
            "pillar": "Detecção",
            "objective": "Smoke Aerosol Measurement Experiment (SAME): medir aerossóis de fumaça gerados por superaquecimento de fios e materiais.",
            "relevance": "Base direta para projeto de detectores de fumaça da ISS e missões profundas (citado em spinoffs NASA).",
            "caveat": "Inclui relatório científico final de 68 páginas e desenho CAD de 1 página sem camada textual (OCR requer Tesseract).",
        },
    },
    "NASA-CONTEXT": {
        "en": {
            "pillar": "Context",
            "objective": "Official NASA documentation: 'A Researcher's Guide to ISS Combustion Science' and the 'Complete PSI Database Guide'.",
            "relevance": "Provides scientific background on microgravity combustion physics and how PSI datasets are structured.",
            "caveat": "Educational/reference context only — kept strictly separate from empirical PSI experimental records.",
        },
        "pt": {
            "pillar": "Contexto",
            "objective": "Documentação oficial NASA: 'A Researcher's Guide to ISS Combustion Science' e 'Complete PSI Database Guide'.",
            "relevance": "Fornece base científica sobre física da combustão em microgravidade e estrutura dos dados no repositório PSI.",
            "caveat": "Apenas contexto educacional e documental — mantido estritamente separado de registros experimentais PSI.",
        },
    },
}


# ----------------------------------------------------------------------------- Central translation dictionary

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        # App & Sidebar
        "app.title": "PSI Flame Microgravity",
        "app.subtitle": "NASA Space Apps 2026 · Flame in Freefall",
        "sidebar.language": "Language / Idioma",
        "sidebar.nav_label": "Workspace Navigation",
        "sidebar.readonly_badge": "Public Read-Only Mode · Verified NASA Archive",
        "sidebar.local_badge": "Local Research Workspace · SQLite + SHA-256",
        "sidebar.footer_note": "Original NASA PSI records preserved with immutable SHA-256 verification. Never a fire-safety certification.",

        # Navigation
        "nav.home": "Home / Overview",
        "nav.investigations": "Investigations",
        "nav.explorer": "Data Explorer",
        "nav.compare": "Compare",
        "nav.assistant": "Scientific Assistant",
        "nav.visual_review": "Visual Page Review",
        "nav.sources": "Sources & Methodology",

        # Home / Overview
        "home.title": "Flame in Freefall: Microgravity Combustion Explorer",
        "home.lead": (
            "Explore authentic NASA Physical Sciences Informatics (PSI) datasets aboard the International Space Station "
            "and spacecraft experiments — built for judges, students, engineers, and curious minds."
        ),
        "home.what_title": "Why does fire behave differently in freefall?",
        "home.what_body": (
            "On Earth, hot combustion gases are lighter than cool surrounding air, so **gravity creates buoyancy**: "
            "hot gases rise and pull fresh oxygen inward, producing a familiar teardrop flame.\n\n"
            "In orbital **microgravity (freefall)**, buoyancy nearly vanishes. Without upward convection, flames turn **spherical**, "
            "heat and combustion products linger around the fuel, **cool flames** can persist at lower temperatures, and "
            "smoke particles grow larger before drifting slowly along cabin ventilation — changing every rule of spacecraft fire safety."
        ),
        "home.problem_title": "What this application solves",
        "home.problem_body": (
            "NASA's PSI repository hosts high-value combustion data spread across heterogeneous CSV tables, engineering PDFs, "
            "and science reports with inconsistent units (`psia`, `psig`, `mmHg`, `cm/s`, `mole fraction`). "
            "**PSI Flame Microgravity** unifies 9 priority investigations into a transparent, verifiable workspace where "
            "**test conditions are never confused with measured outcomes**, units are conservatively normalized, and every claim links back to an exact NASA document, page/row, and SHA-256 hash."
        ),
        "home.metric_studies": "NASA PSI Studies",
        "home.metric_docs": "Preserved NASA Files",
        "home.metric_tables": "Extracted Tables",
        "home.metric_chunks": "Indexed Chunks",
        "home.extraction_caption": "Extraction status: {processed} processed · {partial} partial · {failed} failed. See Sources & Methodology for full provenance.",
        "home.pillars_title": "What can you investigate? Three Pillars of Spacecraft Fire Safety",
        "home.pillar_prevention": "Prevention",
        "home.pillar_prevention_studies": "BASS · BASS-II · Saffire-I / II / III",
        "home.pillar_prevention_desc": "How solid cabin materials ignite and spread flames under microgravity airflow and oxygen levels.",
        "home.pillar_detection": "Detection",
        "home.pillar_detection_studies": "SAME · SAME-R",
        "home.pillar_detection_desc": "How smoke particle sizes and aerosols behave without buoyancy so spacecraft detectors catch fires early.",
        "home.pillar_suppression": "Suppression",
        "home.pillar_suppression_studies": "FLEX · FLEX-2",
        "home.pillar_suppression_desc": "How liquid fuel droplets burn, form cool flames, and extinguish as oxygen or inert diluents vary.",
        "home.pillar_coverage": "{imported} of {total} priority NASA investigations loaded",
        "home.tour_title": "3-Minute Guided Tour (Recommended Starting Path)",
        "home.tour_subtitle": "Follow these 4 steps to explore the complete scientific workflow without needing combustion expertise:",
        "home.tour_s1_title": "1. Browse NASA Investigations",
        "home.tour_s1_desc": "See the 9 PSI studies organized by Prevention, Detection, and Suppression with official DOIs and caveats.",
        "home.tour_s1_btn": "Open Investigations →",
        "home.tour_s2_title": "2. Inspect FLEX (PSI-69) Data",
        "home.tour_s2_desc": "Open interactive tables, charts, variable glossaries, and raw source rows for droplet extinction.",
        "home.tour_s2_btn": "Explore PSI-69 Data →",
        "home.tour_s3_title": "3. Compare Experiments Safely",
        "home.tour_s3_desc": "Check why BASS-II and FLEX cannot be merged blindly when methodologies or units diverge.",
        "home.tour_s3_btn": "Compare Studies →",
        "home.tour_s4_title": "4. Query the Evidence Assistant",
        "home.tour_s4_desc": "Run filtered searches (e.g., FLEX with 18%–25% O₂) and verify exact NASA page and row citations.",
        "home.tour_s4_btn": "Launch Assistant →",
        "home.start_cta": "Start Guided Investigation (Open PSI-69 Data Explorer)",
        "home.warning_conditions": (
            "Scientific Integrity Notice: Experimental tables frequently describe test conditions or catalogs. "
            "By themselves, they do not prove flame propagation speed, suppression efficacy, or spacecraft fire-safety certification."
        ),
        "home.no_docs": "No documents are currently imported. Run `scripts/ingest_nasa.py` or inspect Sources & Methodology.",

        # Investigations
        "inv.title": "NASA PSI Investigations Catalog",
        "inv.lead": "Browse authentic Physical Sciences Informatics (PSI) studies prioritized for spacecraft fire safety. Original titles, DOIs, and file hashes are preserved verbatim.",
        "inv.search_label": "Filter investigations by keyword",
        "inv.search_placeholder": "e.g., FLEX, BASS, SAME, Saffire, droplet, smoke",
        "inv.pillar_label": "Fire-safety pillar",
        "inv.pillar_all": "All",
        "inv.pillar_prevention": "Prevention",
        "inv.pillar_detection": "Detection",
        "inv.pillar_suppression": "Suppression",
        "inv.pillar_context": "Context",
        "inv.list_header": "Available NASA Investigations ({count})",
        "inv.status_imported": "Imported & verified",
        "inv.status_downloaded": "Downloaded, awaiting ingestion",
        "inv.status_pending": "Awaiting download",
        "inv.docs_count": "{count} document(s) in archive",
        "inv.objective_label": "Scientific objective",
        "inv.relevance_label": "Spacecraft safety relevance",
        "inv.caveat_label": "Documented scope & caveats",
        "inv.btn_nasa": "NASA PSI Record",
        "inv.btn_doi": "Confirmed DOI",
        "inv.doi_candidate": "Catalog DOI (to be confirmed): {doi}",
        "inv.extraction_list": "Documents: {items}",
        "inv.btn_open": "Open in Data Explorer",
        "inv.empty": "No investigation matches your current filter. Clear the search text or select 'All'.",

        # Data Explorer
        "exp.title": "Data Explorer",
        "exp.subtitle": "Inspect original NASA tables, interactive charts, physical quantities, PDF pages, and SHA-256 verification for any study.",
        "exp.select_study": "Active investigation / experiment",
        "exp.select_placeholder": "Select a study",
        "exp.readonly_notice": "Public deployment runs in read-only mode: original NASA datasets and analyses are interactive, while local file uploads and archive edits are disabled.",
        "exp.glossary_title": "Variable & Unit Glossary (Guide for Newcomers)",
        "exp.glossary_body": (
            "- **Oxygen mole fraction (`0.00–1.00`)**: Fraction of O₂ molecules in the test gas (Earth air is ≈ `0.21` or `21%`).\n"
            "- **`psia` vs `psig` vs `mmHg`**: `psia` is absolute pressure; `psig` is gauge pressure relative to ambient; unreferenced `psi` or `mmHg` is never guessed as absolute.\n"
            "- **Extinction diameter (`mm`)**: Droplet size when the visible flame goes out.\n"
            "- **`Burning rate; mm` (PSI-69 caveat)**: Original NASA header has ambiguous dimensions (`mm` instead of `mm/s` or `mm²/s`), so it is preserved raw and excluded from automatic rate conversion.\n"
            "- **Test Condition vs Reported Result**: Input setup parameters (`condition`) are kept separate from post-test measurements (`reported_result`)."
        ),
        "exp.manage_local": "Local Archive Management (Create experiment / Upload files)",
        "exp.new_name": "New local experiment name",
        "exp.new_name_ph": "e.g., Custom Flame Test 01",
        "exp.new_desc": "Description",
        "exp.new_desc_ph": "Objective or initial notes",
        "exp.create_btn": "Create experiment",
        "exp.empty_archive": "No experiments found in the archive yet.",
        "exp.tab_overview": "Overview & Variables",
        "exp.tab_explorer": "Interactive Charts",
        "exp.tab_tables": "Tables & Source Rows",
        "exp.tab_docs": "Documents & Integrity",
        "exp.tab_pdf": "PDF Reader & Search",
        "exp.tab_isa": "ISA-Tab Metadata",
        "exp.created_updated": "Created {created} · Updated {updated}",
        "exp.no_desc": "Add a description to record the objective or context of this experiment.",
        "exp.metric_docs": "Documents",
        "exp.metric_pdfs": "PDFs",
        "exp.metric_tables": "Tables",
        "exp.metric_extracted": "Extracted",
        "exp.metric_storage": "Storage",
        "exp.partial_warn": "{failed} file(s) failed extraction and {partial} had partial extraction. Original bytes remain preserved.",
        "exp.ready_ok": "All imported documents are indexed and original bytes are intact.",
        "exp.no_docs_hint": "Import files in the Documents & Integrity tab to organize data.",
        "exp.metric_blocks": "Data blocks detected",
        "exp.metric_alerts": "Quality alerts",
        "exp.metric_alerts_help": "Possible swapped headers, missing axes, mixed percentage/fraction scales, etc.",
        "exp.metric_notes": "Automated notes",
        "exp.local_folder": "Local archive path",
        "exp.edit_meta": "Edit experiment title & description",
        "exp.edit_name": "Name",
        "exp.edit_desc": "Description",
        "exp.save_btn": "Save changes",
        "exp.recent_files": "Documents in this study",
        "exp.col_file": "File",
        "exp.col_format": "Format",
        "exp.col_extraction": "Extraction",
        "exp.col_tables": "Tables",
        "exp.col_imported": "Imported",

        # Views: Study Overview / Catalog / Explorer / Tables / PDF / ISA
        "view.study_summary": "Study Summary & Physical Quantities",
        "view.metric_datasets": "Analyzed datasets",
        "view.metric_rows": "Data rows",
        "view.metric_quantities": "Physical quantities",
        "view.quantities_identified": "Identified physical quantities",
        "view.study_objective": "Investigation Objective (ISA-Tab)",
        "view.no_isa": "No ISA-Tab metadata file (`i_Investigation*.txt`) was found in this study (PSI-XX CSV/PDF studies store metadata in `source_manifest.json`).",
        "view.analyzed_data": "Variable Statistical Summary",
        "view.analyzed_caption": "Descriptive statistics of numeric columns extracted from this study's data blocks.",
        "view.inspect_dataset": "Filter summary by dataset",
        "view.select_dataset": "Select dataset",
        "view.export_analyzed": "Export variable summary (CSV)",
        "view.no_numeric": "No numeric variables were extracted for statistical summary.",
        "view.synthesis": "Descriptive Synthesis",
        "view.synthesis_body": "Analyzed **{datasets} dataset(s)** across **{rows} rows**, yielding **{variables} numeric variable summaries**.",
        "view.synthesis_note": "This summary is purely descriptive. Physical interpretation and hypothesis validation require domain review against original NASA papers.",
        "view.dataset_catalog": "Dataset Block Catalog",
        "view.no_tables": "No structured tables were extracted from this study.",
        "view.filter_text": "Filter catalog by text",
        "view.filter_type": "Chart / table type",
        "view.only_warnings": "Alerts only",
        "view.crossref_title": "Cross-reference between index tables & data blocks",
        "view.no_crossref": "No index table with 'Data ID' and 'description' columns was found.",
        "view.explorer_intro": "Select a dataset, confirm the suggested axes, and pick a chart type. Reversible column fixes and advanced transforms stay tucked away so raw data is never hidden.",
        "view.no_numeric_datasets": "No numeric datasets available for plotting in this study.",
        "view.docs_filter": "Filter by source document",
        "view.datasets_select": "Datasets (select multiple to overlay)",
        "view.select_one_dataset": "Select at least one dataset.",
        "view.available_fixes": "Available reversible fixes (original file is never modified)",
        "exp.derived_cols": "Derived columns (advanced)",
        "view.derived_op": "Derived operation",
        "view.derived_name": "Column name",
        "view.derived_add": "Add derived column",
        "view.derived_clear": "Clear derived columns",
        "view.suggested_type": "Suggested plot type: **{kind}**",
        "view.x_axis": "X axis",
        "view.y_axis": "Y axis / series",
        "view.chart_header": "Visualization",
        "view.chart_type": "Chart type",
        "view.sort_x": "Sort by X",
        "view.log_x": "Log X",
        "view.log_y": "Log Y",
        "view.adv_adjust": "Advanced adjustments & curve filtering",
        "view.baseline": "Baseline subtraction",
        "view.normalize": "Normalization",
        "view.smooth": "Smoothing window (pts)",
        "view.max_points": "Max points (0 = all)",
        "view.x_min": "X min",
        "view.x_max": "X max",
        "view.facet": "Separate panel per dataset",
        "view.on_grid": "Interpolate onto common grid",
        "view.on_grid_help": "Useful for comparing profiles sampled at different spatial/time grids.",
        "view.need_3_cols": "X-Y-color scatter requires at least 3 numeric columns and a selected Y axis.",
        "view.color_var": "Color variable",
        "view.select_y_warning": "Select at least one Y column with numeric values.",
        "view.series_analysis": "Plotted series analysis",
        "view.series_analysis_note": "Statistics reflect the currently plotted points (including active filters/transforms). A linear slope is only a mathematical fit; verify physical units before interpreting.",
        "view.linear_fit": "Linear fit",
        "view.peak_width": "Peak & FWHM",
        "view.last_positive": "Last positive point",
        "view.fit_start": "Linear fit window: X start",
        "view.fit_end": "Linear fit window: X end",
        "view.fit_window_warn": "Window end must exceed window start; linear fit omitted.",
        "view.dl_analysis": "Download series analysis (CSV)",
        "view.export_trace": "Export & Provenance",
        "view.dl_plotted_csv": "Plotted data (CSV)",
        "view.dl_transforms_json": "Transforms & provenance (JSON)",
        "view.dl_chart_html": "Interactive chart (HTML)",
        "view.tables_header": "Tables & Source Rows",
        "view.select_table": "Select table / block",
        "view.source_origin": "Origin: {doc} · {loc}",
        "view.overrides_active": "User column overrides are active in this view (see Interactive Charts). Original file bytes remain unchanged.",
        "view.columns_schema": "Column Schema & Units",
        "view.export_csv": "Export table (CSV)",
        "view.show_pdf_page": "Render source PDF page",
        "view.pdf_reader": "PDF Reader & Keyword Search",
        "view.no_pdfs": "No PDF files in this study.",
        "view.pdf_reader_note": "Searches text and captions in English & Portuguese. Matches jump directly to the rendered original PDF page so extracted text is never mistaken for the source layout.",
        "view.pdf_search_label": "Search inside study PDFs",
        "view.pdf_search_ph": "e.g., droplet extinction cool flame ozone",
        "view.pdf_not_found": "No matches found. Scanned drawings without an OCR layer may not be text-searchable.",
        "view.pdf_matches_count": "{count} page(s) matched. Open a page below:",
        "view.open_page": "Open page",
        "view.pdf_page_heading": "Document Page Viewer",
        "view.pdf_open_select": "Active PDF",
        "view.pdf_page_num": "Physical page number",

        # Documents & Integrity tab
        "docs.title": "Documents & Cryptographic Integrity",
        "docs.upload_desc": "Upload batch files locally. Each original is assigned an immutable SHA-256 digest isolated to this experiment.",
        "docs.upload_disabled": "Public read-only mode: uploads and re-extraction are disabled to protect archive integrity.",
        "docs.select_files": "Select files",
        "docs.upload_help": "CSV, TSV, XLS, XLSX, PDF, images, DOCX, and TXT (including ISA-Tab i_Investigation*.txt).",
        "docs.import_btn": "Import & extract",
        "docs.no_docs": "No documents attached to this experiment.",
        "docs.index_header": "Document Inventory",
        "docs.details_header": "Integrity Verification & Raw Download",
        "docs.select_doc": "Document",
        "docs.sha_label": "SHA-256 of original file",
        "docs.reprocess_btn": "Reprocess document",
        "docs.verify_btn": "Verify SHA-256",
        "docs.verify_ok": "Original file matches the recorded SHA-256 digest.",
        "docs.verify_fail": "Original file does NOT match the recorded SHA-256 digest!",
        "docs.download_original": "Download original NASA/source file",
        "docs.extracted_meta": "Extracted document metadata",
        "docs.extracted_text": "Extracted text preview",

        # Compare
        "cmp.title": "Compare Investigations Safely",
        "cmp.lead": (
            "Inspect table schemas, units, and evidence categories across 2 or 3 NASA studies side by side. "
            "Measurements are only marked compatible for quantitative pooling when quantities, units, test conditions, and methodologies match."
        ),
        "cmp.presets_label": "Quick Comparison Presets",
        "cmp.preset_flex_bass": "FLEX (PSI-69) vs BASS-II (PSI-25)",
        "cmp.preset_same": "SAME (PSI-102) vs SAME-R (PSI-101)",
        "cmp.preset_saffire": "Saffire-I (PSI-98) vs Saffire-II (PSI-99)",
        "cmp.select_studies": "Select 2 or 3 studies to compare",
        "cmp.why_title": "Why can't all measurements be compared directly?",
        "cmp.why_body": (
            "- **Different physical scales**: Droplet extinction diameters (FLEX, `mm`) measure liquid spherical flames, whereas Saffire (`cm/s`, burn length) tracks flat solid fabrics.\n"
            "- **Conditions vs Measurements**: A table of planned test conditions (`condition`) cannot be pooled with measured experimental outcomes (`reported_result`).\n"
            "- **Unreferenced pressures**: Pressures reported in `mmHg` or unspecified `psi` without ambient reference cannot be equated to `psia`."
        ),
        "cmp.selected_tables": "Selected Study Tables",
        "cmp.no_table": "This study has no extracted tables.",
        "cmp.choose_table": "Table to inspect",
        "cmp.compatible_ok": "Declared dimensions, methodology, and conditions match. Still verify the original documents before pooling values.",
        "cmp.incompatible_warn": "Joint quantitative pooling NOT validated — inspect differences below:",
        "cmp.select_min": "Select at least two studies (or click a preset above) to inspect schemas side by side.",
        "cmp.relevance_title": "Reading Priority Ranking (Not a Fire-Risk Score)",
        "cmp.relevance_caption": "Deterministic 0–100 score (Application match up to 50 + Query terms up to 30 + Local file coverage up to 20) to help prioritize which studies to read first. Never a material flammability or safety ranking.",
        "cmp.application_label": "Spacecraft safety focus",
        "cmp.app_habitat": "Habitat Prevention (BASS / Saffire)",
        "cmp.app_detection": "Smoke Detection (SAME / SAME-R)",
        "cmp.app_suppression": "Fire Suppression (FLEX / FLEX-2)",
        "cmp.query_label": "Topic keywords for reading priority",

        # Scientific Assistant
        "ast.title": "Evidence-First Scientific Assistant",
        "ast.subtitle": "Bilingual search (EN / PT) · Deterministic physical unit filters · Verifiable NASA citations with page/row provenance",
        "ast.mode_semantic": "Retrieval engine: Hybrid SQLite FTS5 + local multilingual embeddings (no external API needed)",
        "ast.mode_lexical": "Retrieval engine: SQLite FTS5 + EN/PT lexical vectors (offline & deterministic; no generative AI)",
        "ast.llm_unconfigured_banner": (
            "**Evidence Retrieval Mode (LLM unconfigured):** Answers display verbatim NASA excerpts, exact table rows, and source hashes directly. "
            "No generative AI text is synthesized or fabricated."
        ),
        "ast.llm_configured_banner": (
            "**Verified Extractive LLM Mode available:** When enabled below, the configured LLM may only select literal quotes from retrieved sources — "
            "paraphrases and unsupported numbers are automatically rejected in code."
        ),
        "ast.examples_title": "Example Research Questions (Click to run)",
        "ast.ex1_label": "FLEX droplet O₂ conditions (18–25%)",
        "ast.ex1_q": "What are the experimental conditions and extinction diameters for FLEX?",
        "ast.ex2_label": "BASS-II flow velocity & oxygen",
        "ast.ex2_q": "BASS-II flow velocity and oxygen concentration conditions",
        "ast.ex3_label": "SAME smoke aerosol detection",
        "ast.ex3_q": "SAME smoke aerosol particle detection flight tests",
        "ast.ex4_label": "Saffire flame spread materials",
        "ast.ex4_q": "Saffire spacecraft material flame spread test conditions",
        "ast.ex5_label": "Unsupported query guard demo",
        "ast.ex5_q": "quasizebraunobtainium unsupported microgravity claim",
        "ast.studies_filter": "Filter by NASA investigation (empty = search all 9 studies + guides)",
        "ast.question_label": "Research question",
        "ast.question_help": "Ask about experimental conditions, fuels, oxygen levels, or documents. Never use as a safety certification.",
        "ast.filters_expander": "Physical & numerical filters (applied on the same source row)",
        "ast.o2_check": "Filter O₂ mole fraction",
        "ast.o2_min": "Min O₂ (fraction, 0–1)",
        "ast.o2_max": "Max O₂ (fraction, 0–1)",
        "ast.p_check": "Filter absolute pressure",
        "ast.p_min": "Min pressure (psia)",
        "ast.p_max": "Max pressure (psia)",
        "ast.v_check": "Filter flow velocity",
        "ast.v_min": "Min velocity (cm/s)",
        "ast.v_max": "Max velocity (cm/s)",
        "ast.fuel_label": "Documented fuel",
        "ast.fuel_ph": "e.g., heptane, methanol",
        "ast.filters_note": "Units and pressure reference must be explicitly declared in the source row. Unreferenced mmHg/psi values are never assumed to be psia.",
        "ast.use_llm": "Use configured external LLM for verbatim excerpt selection",
        "ast.use_llm_help": "Sends only your question and top retrieved snippets to the configured endpoint. Disabled when unconfigured.",
        "ast.submit_btn": "Search NASA Evidence",
        "ast.empty_query_warn": "Please enter a research question.",
        "ast.range_error": "Minimum filter value must be less than or equal to maximum.",
        "ast.spinner": "Searching NASA PSI evidence…",
        "ast.results_header": "Answer & Verifiable Evidence",
        "ast.last_query": "Query · {studies}",
        "ast.mode_caption": "Execution mode: {mode}",
        "ast.ev_nature": "Nature: {kind} · ref {ref}",
        "ast.btn_source": "Permanent NASA Source",
        "ast.btn_doi": "DOI",
        "ast.btn_download": "Download cited original",
        "ast.btn_view_page": "View cited PDF page",

        # Visual Page Review
        "vis.title": "Visual Page Review (PDF Inspector)",
        "vis.lead": "Inspect original PDF diagrams, equipment drawings, and charts page by page. Optional VLM interpretation is strictly a qualitative human-review candidate.",
        "vis.warning": "Visual review never digitizes exact graph numbers, never creates measurements, and never enters the scientific search index.",
        "vis.presets_label": "Recommended NASA Pages to Inspect",
        "vis.preset_same": "SAME Final Report · p. 13 (Smoke Detector)",
        "vis.preset_bass": "BASS-II SRD · p. 2 (Science Requirements)",
        "vis.preset_guide": "NASA Researcher's Guide · p. 36 (Droplet Combustion)",
        "vis.select_pdf": "Original PDF document",
        "vis.page_num": "Physical PDF page",
        "vis.render_btn": "Render Page Locally",
        "vis.vlm_header": "Optional VLM Qualitative Review",
        "vis.vlm_unconfigured": "VLM provider not configured (`VLM_MODEL` / `VLM_API_KEY`). Local PDF rendering works 100% offline.",
        "vis.vlm_consent": "Explicitly send ONLY this rendered page image to the configured VLM endpoint",
        "vis.vlm_consent_help": "Image leaves the host only when checked. Output remains an unverified inference.",
        "vis.vlm_btn": "Request Qualitative Review Candidate",

        # Sources & Methodology
        "src.title": "Sources, Provenance & Scientific Methodology",
        "src.lead": "Complete transparency on where NASA data comes from, how units and embeddings work, what AI does and does not do, and known dataset limitations.",
        "src.sec1_title": "1. NASA PSI Data Origins & Provenance",
        "src.sec1_body": (
            "- **Primary source**: NASA Physical Sciences Informatics (PSI) Data Repository (`https://psi.nasa.gov/physci/repo/search?q=combustion`).\n"
            "- **Dataset scope**: **9 PSI investigations** (`PSI-25`, `PSI-26`, `PSI-68`, `PSI-69`, `PSI-98`, `PSI-99`, `PSI-100`, `PSI-101`, `PSI-102`) + **2 official NASA context guides**, totaling **16 authentic NASA files (7,881,267 bytes)**.\n"
            "- **Immutable integrity**: Every downloaded file is stored untouched alongside its UTC access timestamp, permanent PSI API URL, confirmed DOI, and SHA-256 digest. Ephemeral signed S3 download links are never stored."
        ),
        "src.sec2_title": "2. Extraction, Unit Normalization & Data Categories",
        "src.sec2_body": (
            "- **Conservative Pint normalization**: Only explicitly documented units are converted (`1 atm = 14.6959 psia`, `1 m/s = 100 cm/s`, `°C → K`, `% O₂ → mole fraction`).\n"
            "- **Reference protection**: Unreferenced `psi` or `mmHg` is never silently converted to absolute `psia`; gauge pressure (`psig`) requires an independent ambient reference.\n"
            "- **Strict evidence separation**: `condition` (test setup), `sample` (catalog metadata), `reported_result` (published outcomes), `derived` (e.g. partial O₂ pressure), and `document_context` never mix silently."
        ),
        "src.sec3_title": "3. Hybrid Retrieval, Grounding & AI Disclosure",
        "src.sec3_body": (
            "- **Offline-first retrieval**: Combines SQLite **FTS5** full-text search with either local multilingual embeddings (`paraphrase-multilingual-MiniLM-L12-v2`, 384-d) when configured or deterministic EN/PT **lexical vectors**.\n"
            "- **Numeric row filtering**: Physical filters (O₂, pressure, velocity, fuel) evaluate typed observations strictly within the **same source row**.\n"
            "- **Programmatic grounding**: When an optional LLM is configured, it can only select verbatim excerpts from retrieved sources; invented claims, paraphrases, and unverified numbers are rejected in code."
        ),
        "src.sec4_title": "4. Known Limitations & Scientific Caveats",
        "src.sec4_body": (
            "- **Ambiguous header in PSI-69**: `Burning rate; mm` in `PSI-69_Experimental table_FLEX.csv` lacks a time unit (`mm` vs `mm/s` or `mm²/s`) and is kept raw without conversion.\n"
            "- **Catalog mismatch in PSI-69**: The requirements PDF linked by NASA under `PSI-69` bears **FLEX-2** on its cover; this warning is surfaced everywhere that file appears.\n"
            "- **Partial OCR**: The 1-page SAME ignitor wire drawing (`PSI-102`) has no embedded text layer; full OCR requires Tesseract.\n"
            "- **Not a certification**: No independent domain validation, raw video/sensor telemetry acquisition, or spacecraft safety certification is claimed."
        ),
        "src.archive_title": "Verified NASA File Inventory & Raw Downloads",
        "src.ingestion_title": "Archive Synchronization & Background Jobs",
        "src.ingestion_desc": "NASA downloads and ingestion are decoupled from normal browsing. Locally, you can re-verify or re-index downloaded files below.",
        "src.ingestion_readonly": "Public read-only deployment: SQLite scientific registry and search index are automatically initialized on startup; manual re-ingestion is disabled.",
        "src.ingestion_btn": "Sync local downloads & update search index",
        "src.refresh_btn": "Refresh catalog cache",
        "src.jobs_header": "Ingestion Job History",
        "src.footer_provenance": "Full URLs, versions, SHA-256 digests, and coverage gaps are documented in `docs/DATA_PROVENANCE.md`.",
        "src.job_missing": "Job not found. Check ingestion logs below.",
        "src.job_status": "Ingestion status: {status}",
        "src.job_done": "Processing finished. Refresh the catalog to inspect new documents.",
        "src.cli_commands": "Local NASA CLI fetch & ingest commands (developers)",
        "src.dl_original": "Download original bytes",
        "src.orig_err": "Original unavailable: {error}.",
        "home.explore_pillar_btn": "Filter {pillar} →",
        "inv.context_badge": "Official NASA Documentation & Context",
        "view.overview_heading": "Experiment Summary",
        "view.no_description": "No experiment description recorded yet.",
        "view.isa_objective_heading": "Investigation Objective (ISA-Tab)",
        "view.source_file": "Source: {name}",
        "view.view_by_dataset": "Inspect descriptive table by dataset",
        "view.conclusion_heading": "Descriptive Conclusion",
        "view.auto_notes": "Automated notes ({count})",
        "view.no_fixes": "No suggested column fixes for this table.",
        "view.fix_swap": "Swap headers '{a}' and '{b}'",
        "view.fix_swap_help": "Enable if column headers appear inverted relative to the plotted values.",
        "view.fix_borrow": "Use axis from '{table}' (assumption)",
        "view.fix_borrow_help": "Uses a sibling table axis. Kept reversible and clearly marked as an assumption.",
        "view.fix_pct": "Convert {cols} from % to fraction",
        "view.fix_pct_help": "Harmonizes percentage vs fraction scales across sibling blocks.",
        "view.explorer_empty_hint": "Import spreadsheets or CSVs with numeric columns to plot experimental data.",
        "view.derived_ignored": "Derived column '{name}' ignored: {error}",
        "view.crossref_empty": "No index table with 'Data ID' and 'description' columns found.",
        "view.crossref_item": "{icon} Data ID {data_id} · {sources} source(s) · {blocks} data block(s)",
        "view.crossref_data": "Data: {doc} › {block}",
        "view.catalog_empty": "Import spreadsheets, CSVs, or DOCX files to list extracted dataset blocks.",
        "view.derived_const": "Constant (optional)",
        "view.derived_col_b": "Second column",
        "view.col_dataset": "Dataset / Table",
        "view.col_doc": "Document",
        "view.col_format": "Format",
        "view.col_rows": "Rows",
        "view.col_cols": "Columns",
        "view.col_qty": "Quantity",
        "view.col_unit": "Unit",
        "view.col_chart": "Suggested Chart",
        "view.col_alerts": "Alerts",
        "view.col_x": "Suggested X",
        "view.col_y": "Suggested Y",
        "view.col_variable": "Variable",
        "view.col_mean": "Mean",
        "view.col_min": "Min",
        "view.col_max": "Max",
        "view.col_std": "Std",
        "view.col_series": "Series",
        "view.col_index_doc": "Index Doc",
        "view.col_file": "File",
        "view.col_imported": "Imported",
        "view.baseline_none": "None (raw)",
        "view.baseline_min": "Subtract minimum",
        "view.baseline_first": "First N points mean",
        "view.norm_none": "None (raw)",
        "view.norm_peak": "Peak = 1.0",
        "view.norm_minmax": "Min–Max [0, 1]",
        "view.normalized_suffix": "(normalized: {mode})",
        "view.value_axis": "value",
        "view.no_pdf_page_err": "Could not render PDF page (verify PyMuPDF): {error}",
        "view.pdf_no_match_body": "No matching text passages found across imported PDFs.",
        "view.isa_heading": "Study Metadata (ISA-Tab)",
        "view.isa_period": "Investigation period: {start} to {end}",
        "view.isa_submitted": "submitted {submitted} · public release {released}",
        "view.isa_empty_warn": "No factors, assays, or protocols populated in ISA file: {sections}.",
        "view.isa_col_section": "Section",
        "view.isa_col_field": "Field",
        "view.isa_col_value": "Value",
        "view.chart_type_line": "Line",
        "view.chart_type_line_pts": "Line with markers",
        "view.chart_type_scatter": "Scatter",
        "view.chart_type_bar": "Bar",
        "view.chart_type_heatmap": "Matrix Heatmap",
        "view.chart_type_xyc": "X–Y–Color Scatter",
        "cmp.table_rows": "{rows} rows",
        "cmp.col_study": "Study",
        "cmp.col_name": "Investigation Title",
        "cmp.col_score": "Score (0–100)",
        "cmp.col_reasons": "Ranking Rationale",
        "ast.all_studies": "All NASA investigations",
        "ast.orig_unavailable": "Original file unavailable: {error}. Run ingestion from Sources & Methodology.",
        "ast.page_render_err": "Could not render page: {error}",
        "vis.no_pdfs": "No PDF files are currently imported.",
        "vis.doc_caption": "Document SHA-256 `{sha}` · page {page} of {total}",
        "vis.preview_caption": "{name} · page {page}",
        "vis.preview_unavailable": "Preview unavailable: {error}",
        "vis.vlm_spinner": "Requesting qualitative page interpretation…",
        "vis.vlm_failed": "Review did not complete: {err_type}. No scientific observation was created.",
        "vis.candidate_header": "Qualitative Candidate for Human Review",
        "vis.candidate_status": "Status: {status} · nature: inference · human review required",
        "vis.region_label": "Region {idx} · {kind}",
        "vis.region_coords_note": "Normalized bounding coordinates only; not measured physical values.",
        "vis.region_text_note": "Unverified candidate text",
        "vis.download_json": "Download review candidate (JSON)",
        "vis.human_note_label": "Human reviewer note",
        "vis.human_note_help": "Record what you verified against the original PDF. Notes never promote inferences into measurements.",
        "vis.save_note_btn": "Save human review note",
        "vis.save_note_ok": "Note saved. Output stays classified as an inference separate from primary data.",
        "vis.human_saved_at": "Human review recorded at {utc}",
        "view.isa_untitled": "Untitled study",
        "view.isa_objective": "Objective",
        "view.isa_obj_missing": "Objective not stated in ISA-Tab metadata.",
        "view.isa_hypothesis": "Hypothesis",
        "view.isa_hyp_missing": "Hypothesis not stated in ISA-Tab metadata.",
        "view.isa_approach": "Experimental approach",
        "view.isa_no_obj": "No ISA-Tab objective or hypothesis metadata imported for this study.",
        "view.no_stats_conclusion": "Not enough numeric results extracted to compose a quantitative summary.",
        "view.col_observations": "Observations",
        "view.col_median": "Median",
        "view.col_label": "Label",
        "view.col_params": "Parameters",
        "view.col_kind": "Type",
        "view.col_num_values": "Numeric values",
        "view.col_source_row": "Source row",
        "view.crossref_files": "**Data files referenced in index tables:** {total} · unimported: {missing}",
        "view.manual_swap_a": "Swap headers (manual): col A",
        "view.manual_swap_b": "col B",
        "view.manual_swap_apply": "Apply",
        "view.sheet_titles": "Sheet title(s): {titles}",
        "view.label_params": "Label parameters: {params}",
        "view.columns_heading": "Columns",
        "view.derived_default_name": "derived",
        "view.pdf_matched_terms": "Matched terms: {terms}",
        "view.pdf_page_line": "{rank}. {name} · page {page}",
        "view.rows_suffix": "{rows} rows",
        "view.fit_n": "Fit points",
        "view.fit_slope": "Slope",
        "view.fit_intercept": "Intercept",
        "view.fit_r": "Pearson r",
        "view.fit_r2": "R²",
        "view.peak_x": "Peak X",
        "view.peak_y": "Peak Y",
        "view.peak_fwhm": "FWHM",
        "view.last_x_pos": "Last X (Y > 0)",
        "view.last_y_pos": "Y at last point",
        "view.isa_keywords": "Keywords",
        "view.isa_publications": "Publications",
        "view.isa_contacts": "Contacts",
        "docs.job_running": "Background import or reprocessing running. Local uploads preserve local provenance.",
        "docs.job_refresh": "Refresh job status",
        "docs.job_done": "Processing completed: originals, extractions, scientific registry, and search index synchronized.",
        "docs.job_partial": "Partial processing. Check warnings below; original files remain intact.",
        "docs.job_err": "Processing {status}: {error}",
        "docs.job_result": "Local processing result",
        "docs.outdated_warn": "{count} document(s) were extracted by an earlier schema version. Reprocess safely from preserved originals.",
        "docs.reprocess_all": "Reprocess outdated documents",
        "docs.col_size": "Size",
        "docs.col_pages": "Pages / Chunks",
        "docs.col_status": "Status",
        "docs.read_fail": "Could not read original: {error}",
        "docs.open_fail": "Could not open document: {error}",
        "docs.img_preview_err": "Preview unavailable for this image file.",
        "docs.formulas_found": "Formulas detected ({count})",
        "docs.preview_truncated": "\n… preview truncated",
    },
    "pt": {
        # App & Sidebar
        "app.title": "PSI Flame Microgravity",
        "app.subtitle": "NASA Space Apps 2026 · Flame in Freefall",
        "sidebar.language": "Idioma / Language",
        "sidebar.nav_label": "Navegação",
        "sidebar.readonly_badge": "Modo Público Somente Leitura · Acervo NASA Verificado",
        "sidebar.local_badge": "Ambiente Local de Pesquisa · SQLite + SHA-256",
        "sidebar.footer_note": "Arquivos originais NASA PSI preservados com verificação SHA-256 imutável. Não constitui laudo ou certificação de segurança.",

        # Navigation
        "nav.home": "Início / Visão Geral",
        "nav.investigations": "Investigações",
        "nav.explorer": "Explorador de Dados",
        "nav.compare": "Comparar",
        "nav.assistant": "Assistente Científico",
        "nav.visual_review": "Revisão Visual",
        "nav.sources": "Fontes e Metodologia",

        # Home / Overview
        "home.title": "Flame in Freefall: Explorador de Combustão em Microgravidade",
        "home.lead": (
            "Explore dados reais do repositório NASA Physical Sciences Informatics (PSI) obtidos na Estação Espacial Internacional (ISS) "
            "e em experimentos espaciais — projetado para jurados, estudantes, engenheiros e entusiastas."
        ),
        "home.what_title": "Por que o fogo é diferente em queda livre (microgravidade)?",
        "home.what_body": (
            "Na Terra, gases quentes da combustão são mais leves que o ar frio ao redor, gerando **empuxo (convecção natural)**: "
            "o ar quente sobe e puxa oxigênio novo pela base, formando a chama em formato de gota.\n\n"
            "Em **microgravidade orbital (queda livre)**, o empuxo praticamente desaparece. Sem convecção ascendente, as chamas tornam-se **esféricas**, "
            "o calor e os gases permanecem ao redor do combustível, **chamas frias** podem persistir em temperaturas menores e partículas de fumaça "
            "crescem mais enquanto seguem lentamente a ventilação da cabine — mudando todas as regras de segurança contra incêndio no espaço."
        ),
        "home.problem_title": "Qual problema este aplicativo resolve?",
        "home.problem_body": (
            "Os dados públicos do NASA PSI estão dispersos em planilhas CSV heterogêneas, PDFs de engenharia e relatórios científicos com unidades "
            "divergentes (`psia`, `psig`, `mmHg`, `cm/s`, fração molar). O **PSI Flame Microgravity** reúne 9 investigações prioritárias em um painel transparente "
            "onde **condições de ensaio nunca se confundem com medições**, unidades são normalizadas de forma conservadora e cada resposta aponta para o arquivo NASA, página/linha e hash SHA-256."
        ),
        "home.metric_studies": "Estudos NASA PSI",
        "home.metric_docs": "Originais NASA",
        "home.metric_tables": "Tabelas Extraídas",
        "home.metric_chunks": "Trechos Indexados",
        "home.extraction_caption": "Estado da extração: {processed} processados · {partial} parciais · {failed} com falha. Detalhes em Fontes e Metodologia.",
        "home.pillars_title": "O que você pode investigar? Os 3 Pilares da Segurança contra Incêndio Espacial",
        "home.pillar_prevention": "Prevenção",
        "home.pillar_prevention_studies": "BASS · BASS-II · Saffire-I / II / III",
        "home.pillar_prevention_desc": "Como materiais sólidos de cabine entram em ignição e propagam chamas sob fluxos de ar e níveis de O₂ em microgravidade.",
        "home.pillar_detection": "Detecção",
        "home.pillar_detection_studies": "SAME · SAME-R",
        "home.pillar_detection_desc": "Como o tamanho das partículas de fumaça e aerossóis se comporta sem empuxo para calibrar detectores espaciais.",
        "home.pillar_suppression": "Supressão",
        "home.pillar_suppression_studies": "FLEX · FLEX-2",
        "home.pillar_suppression_desc": "Como gotas de combustível queimam, formam chamas frias e se extinguem conforme variam O₂ e diluentes inertes.",
        "home.pillar_coverage": "{imported} de {total} investigações prioritárias importadas",
        "home.tour_title": "Roteiro Guiado de 3 Minutos (Caminho Recomendado)",
        "home.tour_subtitle": "Siga estes 4 passos para percorrer todo o fluxo científico sem precisar de conhecimento prévio em combustão:",
        "home.tour_s1_title": "1. Explorar Investigações NASA",
        "home.tour_s1_desc": "Conheça os 9 estudos PSI organizados em Prevenção, Detecção e Supressão, com DOIs oficiais e ressalvas.",
        "home.tour_s1_btn": "Abrir Investigações →",
        "home.tour_s2_title": "2. Inspecionar Dados do FLEX (PSI-69)",
        "home.tour_s2_desc": "Veja tabelas interativas, gráficos, glossário de variáveis e linhas originais de extinção de gotas.",
        "home.tour_s2_btn": "Explorar Dados PSI-69 →",
        "home.tour_s3_title": "3. Comparar Estudos com Rigor",
        "home.tour_s3_desc": "Veja por que BASS-II e FLEX não devem ser misturados quando metodologias ou unidades diferem.",
        "home.tour_s3_btn": "Comparar Estudos →",
        "home.tour_s4_title": "4. Consultar o Assistente com Evidências",
        "home.tour_s4_desc": "Execute buscas com filtros físicos (ex.: FLEX com 18%–25% de O₂) e citações verificáveis de página e linha.",
        "home.tour_s4_btn": "Abrir Assistente →",
        "home.start_cta": "Iniciar Roteiro Guiado (Abrir Explorador de Dados PSI-69)",
        "home.warning_conditions": (
            "Aviso de Integridade Científica: Tabelas experimentais frequentemente descrevem condições de ensaio ou catálogos. "
            "Sozinhas, não demonstram velocidade de propagação, eficácia de supressão nem certificação de segurança."
        ),
        "home.no_docs": "Nenhum documento importado ainda. Execute `scripts/ingest_nasa.py` ou veja Fontes e Metodologia.",

        # Investigations
        "inv.title": "Catálogo de Investigações NASA PSI",
        "inv.lead": "Explore estudos autênticos do repositório NASA Physical Sciences Informatics (PSI). Títulos originais, DOIs e hashes são mantidos sem alteração.",
        "inv.search_label": "Filtrar investigações por palavra-chave",
        "inv.search_placeholder": "Ex.: FLEX, BASS, SAME, Saffire, gota, fumaça",
        "inv.pillar_label": "Pilar de segurança",
        "inv.pillar_all": "Todos",
        "inv.pillar_prevention": "Prevenção",
        "inv.pillar_detection": "Detecção",
        "inv.pillar_suppression": "Supressão",
        "inv.pillar_context": "Contexto",
        "inv.list_header": "Investigações NASA disponíveis ({count})",
        "inv.status_imported": "Importado e verificado",
        "inv.status_downloaded": "Baixado, aguardando ingestão",
        "inv.status_pending": "Aguardando coleta",
        "inv.docs_count": "{count} documento(s) no acervo",
        "inv.objective_label": "Objetivo científico",
        "inv.relevance_label": "Relevância para segurança espacial",
        "inv.caveat_label": "Escopo e ressalvas documentadas",
        "inv.btn_nasa": "Registro NASA PSI",
        "inv.btn_doi": "DOI confirmado na fonte",
        "inv.doi_candidate": "DOI do catálogo (a confirmar): {doi}",
        "inv.extraction_list": "Documentos: {items}",
        "inv.btn_open": "Abrir no Explorador de Dados",
        "inv.empty": "Nenhuma investigação corresponde aos filtros atuais. Limpe o termo ou selecione 'Todos'.",

        # Data Explorer
        "exp.title": "Explorador de Dados",
        "exp.subtitle": "Inspecione tabelas originais NASA, gráficos interativos, grandezas físicas, páginas PDF e integridade SHA-256 por investigação.",
        "exp.select_study": "Investigação / experimento ativo",
        "exp.select_placeholder": "Selecionar estudo",
        "exp.readonly_notice": "Ambiente público em modo somente leitura: os dados e gráficos NASA são interativos, mas uploads locais e edições de arquivo estão desativados.",
        "exp.glossary_title": "Glossário de Variáveis e Unidades (Guia para Iniciantes)",
        "exp.glossary_body": (
            "- **Fração molar de oxigênio (`0,00–1,00`)**: Proporção de moléculas de O₂ no gás do ensaio (ar terrestre ≈ `0,21` ou `21%`).\n"
            "- **`psia` vs `psig` vs `mmHg`**: `psia` é pressão absoluta; `psig` é pressão manométrica relativa ao ambiente; `psi` ou `mmHg` sem referência nunca são presumidos absolutos.\n"
            "- **Diâmetro de extinção (`mm`)**: Tamanho da gota no instante em que a chama visível se apaga.\n"
            "- **`Burning rate; mm` (ressalva PSI-69)**: O cabeçalho original da NASA tem dimensão ambígua (`mm` em vez de `mm/s` ou `mm²/s`), sendo preservado bruto sem conversão.\n"
            "- **Condição de Ensaio vs Resultado Reportado**: Parâmetros de entrada (`condition`) ficam separados de resultados pós-ensaio (`reported_result`)."
        ),
        "exp.manage_local": "Gerenciamento Local de Experimentos (Criar / Enviar arquivos)",
        "exp.new_name": "Nome do novo experimento local",
        "exp.new_name_ph": "Ex.: Ensaio de chama 01",
        "exp.new_desc": "Descrição",
        "exp.new_desc_ph": "Objetivo ou observações iniciais",
        "exp.create_btn": "Criar experimento",
        "exp.empty_archive": "Ainda não há experimentos no acervo.",
        "exp.tab_overview": "Visão Geral e Variáveis",
        "exp.tab_explorer": "Gráficos Interativos",
        "exp.tab_tables": "Tabelas e Linhas Originais",
        "exp.tab_docs": "Documentos e Integridade",
        "exp.tab_pdf": "Leitor e Busca em PDFs",
        "exp.tab_isa": "Metadados ISA-Tab",
        "exp.created_updated": "Criado em {created} · Atualizado em {updated}",
        "exp.no_desc": "Adicione uma descrição para registrar o objetivo ou o contexto deste experimento.",
        "exp.metric_docs": "Documentos",
        "exp.metric_pdfs": "PDFs",
        "exp.metric_tables": "Tabelas",
        "exp.metric_extracted": "Extraídos",
        "exp.metric_storage": "Armazenamento",
        "exp.partial_warn": "{failed} arquivo(s) com falha total e {partial} com extração parcial. Os originais foram preservados para consulta.",
        "exp.ready_ok": "Todos os documentos importados foram indexados e os bytes originais permanecem preservados.",
        "exp.no_docs_hint": "Importe arquivos na aba Documentos e Integridade para começar.",
        "exp.metric_blocks": "Blocos de dados detectados",
        "exp.metric_alerts": "Alertas de qualidade",
        "exp.metric_alerts_help": "Rótulos trocados, eixos ausentes, escalas misturadas (% vs fração), etc.",
        "exp.metric_notes": "Observações automáticas",
        "exp.local_folder": "Pasta local do acervo",
        "exp.edit_meta": "Editar nome e descrição do experimento",
        "exp.edit_name": "Nome",
        "exp.edit_desc": "Descrição",
        "exp.save_btn": "Salvar alterações",
        "exp.recent_files": "Documentos neste estudo",
        "exp.col_file": "Arquivo",
        "exp.col_format": "Formato",
        "exp.col_extraction": "Extração",
        "exp.col_tables": "Tabelas",
        "exp.col_imported": "Importado em",

        # Views
        "view.study_summary": "Resumo do Estudo e Grandezas Físicas",
        "view.metric_datasets": "Conjuntos analisados",
        "view.metric_rows": "Linhas de dados",
        "view.metric_quantities": "Grandezas físicas",
        "view.quantities_identified": "Grandezas físicas identificadas",
        "view.study_objective": "Objetivo do Experimento (ISA-Tab)",
        "view.no_isa": "Não foram encontrados arquivos ISA-Tab (`i_Investigation*.txt`) neste estudo (estudos PSI-XX usam `source_manifest.json`).",
        "view.analyzed_data": "Resumo Estatístico das Variáveis",
        "view.analyzed_caption": "Estatísticas descritivas das colunas numéricas extraídas dos conjuntos deste estudo.",
        "view.inspect_dataset": "Filtrar resumo por conjunto de dados",
        "view.select_dataset": "Selecionar conjunto",
        "view.export_analyzed": "Exportar resumo estatístico (CSV)",
        "view.no_numeric": "Não foram encontrados dados numéricos suficientes para resumo estatístico.",
        "view.synthesis": "Síntese Descritiva",
        "view.synthesis_body": "Analisados **{datasets} conjunto(s) de dados**, contendo **{rows} linhas**, com **{variables} resumos estatísticos de variáveis numéricas**.",
        "view.synthesis_note": "Esta síntese é puramente descritiva. A interpretação física dos resultados requer revisão científica nos documentos originais NASA.",
        "view.dataset_catalog": "Catálogo de Blocos de Dados",
        "view.no_tables": "Nenhuma tabela estruturada foi extraída deste estudo.",
        "view.filter_text": "Filtrar catálogo por texto",
        "view.filter_type": "Tipo de tabela / gráfico",
        "view.only_warnings": "Somente com alertas",
        "view.crossref_title": "Referência cruzada entre tabelas-índice e blocos de dados",
        "view.no_crossref": "Nenhuma tabela-índice com colunas 'Data ID' e 'descrição' foi encontrada.",
        "view.explorer_intro": "Selecione um conjunto, confirme os eixos sugeridos e escolha o tipo de gráfico. Correções reversíveis e transformações avançadas ficam recolhidas para não esconder o dado original.",
        "view.no_numeric_datasets": "Não há conjuntos de dados numéricos para plotagem neste estudo.",
        "view.docs_filter": "Filtrar por documento de origem",
        "view.datasets_select": "Conjuntos de dados (selecione vários para sobrepor)",
        "view.select_one_dataset": "Selecione ao menos um conjunto de dados.",
        "view.available_fixes": "Correções reversíveis disponíveis (o arquivo original nunca é alterado)",
        "exp.derived_cols": "Colunas derivadas (avançado)",
        "view.derived_op": "Operação derivada",
        "view.derived_name": "Nome da coluna",
        "view.derived_add": "Adicionar coluna derivada",
        "view.derived_clear": "Limpar colunas derivadas",
        "view.suggested_type": "Tipo de gráfico sugerido: **{kind}**",
        "view.x_axis": "Eixo X",
        "view.y_axis": "Eixo(s) Y / série",
        "view.chart_header": "Gráfico",
        "view.chart_type": "Tipo de gráfico",
        "view.sort_x": "Ordenar por X",
        "view.log_x": "X logarítmico",
        "view.log_y": "Y logarítmico",
        "view.adv_adjust": "Ajustes e filtros avançados de curva",
        "view.baseline": "Linha de base",
        "view.normalize": "Normalização",
        "view.smooth": "Suavização (pontos)",
        "view.max_points": "Máx. pontos (0 = todos)",
        "view.x_min": "X mínimo",
        "view.x_max": "X máximo",
        "view.facet": "Um painel por conjunto",
        "view.on_grid": "Interpolar em grade comum",
        "view.on_grid_help": "Útil para comparar perfis medidos em malhas diferentes.",
        "view.need_3_cols": "O mapa X–Y–cor exige ao menos 3 colunas numéricas e um eixo Y selecionado.",
        "view.color_var": "Variável de cor",
        "view.select_y_warning": "Selecione ao menos uma coluna Y com valores numéricos.",
        "view.series_analysis": "Análises das séries plotadas",
        "view.series_analysis_note": "As estatísticas usam exatamente os pontos plotados (incluindo filtros/transformações). Uma inclinação linear é apenas tendência matemática; confirme unidades antes de interpretar.",
        "view.linear_fit": "Ajuste linear",
        "view.peak_width": "Pico e largura (FWHM)",
        "view.last_positive": "Último ponto positivo",
        "view.fit_start": "Janela do ajuste linear: X inicial",
        "view.fit_end": "Janela do ajuste linear: X final",
        "view.fit_window_warn": "O fim da janela precisa ser maior que o início; ajuste linear omitido.",
        "view.dl_analysis": "Baixar análises (CSV)",
        "view.export_trace": "Exportar e Rastreabilidade",
        "view.dl_plotted_csv": "Dados plotados (CSV)",
        "view.dl_transforms_json": "Transformações e origem (JSON)",
        "view.dl_chart_html": "Gráfico interativo (HTML)",
        "view.tables_header": "Tabelas e Linhas de Origem",
        "view.select_table": "Selecionar tabela / bloco",
        "view.source_origin": "Origem: {doc} · {loc}",
        "view.overrides_active": "Esta visualização aplica correções do usuário (veja Gráficos Interativos). O arquivo original não foi alterado.",
        "view.columns_schema": "Esquema de Colunas e Unidades",
        "view.export_csv": "Exportar tabela (CSV)",
        "view.show_pdf_page": "Ver página original do PDF",
        "view.pdf_reader": "Leitor e Busca em PDFs",
        "view.no_pdfs": "Não há arquivos PDF neste estudo.",
        "view.pdf_reader_note": "A pesquisa localiza páginas por termos em português e inglês. Os resultados abrem a página original renderizada para não substituir o documento real pelo texto extraído.",
        "view.pdf_search_label": "Pesquisar nos PDFs do estudo",
        "view.pdf_search_ph": "Ex.: extinção chama fria ozônio gota",
        "view.pdf_not_found": "Nada encontrado. Desenhos digitalizados sem camada OCR podem não ter texto pesquisável.",
        "view.pdf_matches_count": "{count} página(s) localizada(s). Selecione uma abaixo:",
        "view.open_page": "Abrir página",
        "view.pdf_page_heading": "Visualizador de Página do Documento",
        "view.pdf_open_select": "PDF ativo",
        "view.pdf_page_num": "Número físico da página",

        # Documents & Integrity tab
        "docs.title": "Documentos e Integridade Criptográfica",
        "docs.upload_desc": "Importe arquivos locais em lote. Cada original recebe um hash SHA-256 imutável isolado neste experimento.",
        "docs.upload_disabled": "Modo público somente leitura: uploads locais e reprocessamento estão desativados para preservar o acervo.",
        "docs.select_files": "Selecionar arquivos",
        "docs.upload_help": "CSV, TSV, XLS, XLSX, PDF, imagens, DOCX e TXT (inclui ISA-Tab i_Investigation*.txt).",
        "docs.import_btn": "Importar e extrair",
        "docs.no_docs": "Nenhum documento associado a este experimento.",
        "docs.index_header": "Inventário de Documentos",
        "docs.details_header": "Verificação de Integridade e Download Original",
        "docs.select_doc": "Documento",
        "docs.sha_label": "SHA-256 do arquivo original",
        "docs.reprocess_btn": "Reprocessar este",
        "docs.verify_btn": "Verificar SHA-256",
        "docs.verify_ok": "O original corresponde ao SHA-256 registrado.",
        "docs.verify_fail": "O conteúdo do original NÃO corresponde ao SHA-256 registrado!",
        "docs.download_original": "Baixar original NASA/fonte",
        "docs.extracted_meta": "Metadados extraídos do documento",
        "docs.extracted_text": "Prévia do texto extraído",

        # Compare
        "cmp.title": "Comparar Investigações com Rigor",
        "cmp.lead": (
            "Inspecione esquemas de tabelas, unidades e categorias de evidência entre 2 ou 3 estudos NASA lado a lado. "
            "Resultados só são considerados compatíveis para comparação quantitativa quando grandezas, unidades, condições e metodologias coincidem."
        ),
        "cmp.presets_label": "Atalhos de Comparação",
        "cmp.preset_flex_bass": "FLEX (PSI-69) vs BASS-II (PSI-25)",
        "cmp.preset_same": "SAME (PSI-102) vs SAME-R (PSI-101)",
        "cmp.preset_saffire": "Saffire-I (PSI-98) vs Saffire-II (PSI-99)",
        "cmp.select_studies": "Selecione 2 ou 3 estudos para comparar",
        "cmp.why_title": "Por que nem todas as medições podem ser comparadas diretamente?",
        "cmp.why_body": (
            "- **Escalas físicas distintas**: Diâmetros de extinção de gotas (FLEX, `mm`) medem chamas esféricas líquidas, enquanto Saffire (`cm/s`, comprimento de queima) avalia tecidos planos.\n"
            "- **Condições vs Medições**: Uma tabela de condições planejadas de ensaio (`condition`) não pode ser fundida com resultados medidos (`reported_result`).\n"
            "- **Pressões sem referência**: Pressões em `mmHg` ou `psi` sem referência ambiente explícita não equivalem a `psia`."
        ),
        "cmp.selected_tables": "Tabelas Selecionadas",
        "cmp.no_table": "Este estudo não possui tabelas extraídas.",
        "cmp.choose_table": "Tabela para inspecionar",
        "cmp.compatible_ok": "Dimensões, metodologia e condições declaradas coincidem. Ainda assim, confira os originais antes de agrupar valores.",
        "cmp.incompatible_warn": "Comparação quantitativa conjunta NÃO validada — veja os motivos abaixo:",
        "cmp.select_min": "Selecione ao menos dois estudos (ou use um atalho acima) para comparar esquemas lado a lado.",
        "cmp.relevance_title": "Prioridade de Leitura (Não é Ranking de Risco)",
        "cmp.relevance_caption": "Score determinístico de 0–100 (Aplicação até 50 + Termos da consulta até 30 + Cobertura local até 20) para orientar leitura. Não mede inflamabilidade nem risco de material.",
        "cmp.application_label": "Foco de segurança espacial",
        "cmp.app_habitat": "Prevenção em Habitat (BASS / Saffire)",
        "cmp.app_detection": "Detecção de Fumaça (SAME / SAME-R)",
        "cmp.app_suppression": "Supressão de Chamas (FLEX / FLEX-2)",
        "cmp.query_label": "Palavras-chave para priorizar leitura",

        # Scientific Assistant
        "ast.title": "Assistente Científico Baseado em Evidências",
        "ast.subtitle": "Busca bilíngue (PT / EN) · Filtros físicos determinísticos · Citações verificáveis NASA com página e linha",
        "ast.mode_semantic": "Motor de busca: SQLite FTS5 híbrido + embeddings multilíngues locais (sem API externa obrigatória)",
        "ast.mode_lexical": "Motor de busca: SQLite FTS5 + vetores lexicais PT/EN (offline e determinístico; sem IA generativa)",
        "ast.llm_unconfigured_banner": (
            "**Modo Busca de Evidências (LLM não configurado):** As respostas exibem trechos literais da NASA, linhas exatas de tabelas e hashes originais. "
            "Nenhum texto generativo é sintetizado ou inventado."
        ),
        "ast.llm_configured_banner": (
            "**Modo LLM Extrativo Verificado disponível:** Quando habilitado abaixo, o LLM só pode selecionar trechos literais das fontes recuperadas — "
            "paráfrases e números sem apoio são rejeitados automaticamente em código."
        ),
        "ast.examples_title": "Perguntas de Pesquisa Prontas (Clique para preencher e testar)",
        "ast.ex1_label": "Condições de O₂ no FLEX (18–25%)",
        "ast.ex1_q": "What are the experimental conditions and extinction diameters for FLEX?",
        "ast.ex2_label": "Velocidade e oxigênio no BASS-II",
        "ast.ex2_q": "BASS-II flow velocity and oxygen concentration conditions",
        "ast.ex3_label": "Detecção de fumaça no SAME",
        "ast.ex3_q": "SAME smoke aerosol particle detection flight tests",
        "ast.ex4_label": "Propagação de chama no Saffire",
        "ast.ex4_q": "Saffire spacecraft material flame spread test conditions",
        "ast.ex5_label": "Teste de insuficiência de evidências",
        "ast.ex5_q": "quasizebraunobtainium unsupported microgravity claim",
        "ast.studies_filter": "Filtrar por investigação NASA (vazio = consulta todos os 9 estudos + guias)",
        "ast.question_label": "Pergunta científica",
        "ast.question_help": "Pergunte por condições experimentais, combustíveis, oxigênio ou documentos. Não use como laudo de segurança.",
        "ast.filters_expander": "Filtros numéricos e físicos (aplicados na mesma linha de origem)",
        "ast.o2_check": "Filtrar fração molar de O₂",
        "ast.o2_min": "O₂ mínimo (fração, 0–1)",
        "ast.o2_max": "O₂ máximo (fração, 0–1)",
        "ast.p_check": "Filtrar pressão absoluta",
        "ast.p_min": "Pressão mínima (psia)",
        "ast.p_max": "Pressão máxima (psia)",
        "ast.v_check": "Filtrar velocidade do escoamento",
        "ast.v_min": "Velocidade mínima (cm/s)",
        "ast.v_max": "Velocidade máxima (cm/s)",
        "ast.fuel_label": "Combustível documentado",
        "ast.fuel_ph": "Ex.: heptane, methanol",
        "ast.filters_note": "Unidades e referência de pressão precisam ser explícitas na linha original. Valores em mmHg/psi sem referência nunca são presumidos psia.",
        "ast.use_llm": "Usar LLM externo configurado para seleção literal de trechos",
        "ast.use_llm_help": "Envia apenas a pergunta e os trechos recuperados ao provedor configurado. Indisponível sem credenciais.",
        "ast.submit_btn": "Pesquisar Evidências NASA",
        "ast.empty_query_warn": "Digite uma pergunta científica.",
        "ast.range_error": "O limite mínimo deve ser menor ou igual ao máximo.",
        "ast.spinner": "Recuperando evidências NASA PSI…",
        "ast.results_header": "Resposta e Evidências Verificáveis",
        "ast.last_query": "Última consulta · {studies}",
        "ast.mode_caption": "Modo de execução: {mode}",
        "ast.ev_nature": "Natureza: {kind} · referência {ref}",
        "ast.btn_source": "Fonte Permanente NASA",
        "ast.btn_doi": "DOI",
        "ast.btn_download": "Baixar original citado",
        "ast.btn_view_page": "Visualizar página citada do PDF",

        # Visual Page Review
        "vis.title": "Revisão Visual de Páginas (Inspetor de PDF)",
        "vis.lead": "Inspecione diagramas, desenhos de engenharia e gráficos nos PDFs originais. A revisão opcional por VLM gera apenas candidatos qualitativos para revisão humana.",
        "vis.warning": "A revisão visual não digitaliza valores exatos de gráficos, não cria medições científicas e não entra no índice de busca.",
        "vis.presets_label": "Páginas NASA Recomendadas para Inspeção",
        "vis.preset_same": "Relatório Final SAME · p. 13 (Detector de Fumaça)",
        "vis.preset_bass": "SRD BASS-II · p. 2 (Requisitos Científicos)",
        "vis.preset_guide": "Guia de Pesquisa NASA · p. 36 (Combustão de Gotas)",
        "vis.select_pdf": "PDF original",
        "vis.page_num": "Página física do PDF",
        "vis.render_btn": "Renderizar Página Localmente",
        "vis.vlm_header": "Interpretação Qualitativa Opcional (VLM)",
        "vis.vlm_unconfigured": "Provedor VLM não configurado (`VLM_MODEL` / `VLM_API_KEY`). A renderização local funciona 100% offline.",
        "vis.vlm_consent": "Enviar explicitamente APENAS a imagem desta página ao provedor VLM configurado",
        "vis.vlm_consent_help": "A imagem sai do servidor apenas com consentimento explícito. O resultado permanece inferência não verificada.",
        "vis.vlm_btn": "Solicitar Candidato de Revisão Visual",

        # Sources & Methodology
        "src.title": "Fontes, Proveniência e Metodologia Científica",
        "src.lead": "Transparência total sobre origem dos dados NASA, normalização de unidades, busca híbrida, uso de IA e limitações conhecidas.",
        "src.sec1_title": "1. Origem e Proveniência dos Dados NASA PSI",
        "src.sec1_body": (
            "- **Fonte primária**: NASA Physical Sciences Informatics (PSI) Data Repository (`https://psi.nasa.gov/physci/repo/search?q=combustion`).\n"
            "- **Cobertura do acervo**: **9 investigações PSI** (`PSI-25`, `PSI-26`, `PSI-68`, `PSI-69`, `PSI-98`, `PSI-99`, `PSI-100`, `PSI-101`, `PSI-102`) + **2 guias oficiais NASA**, somando **16 arquivos autênticos (7.881.267 bytes)**.\n"
            "- **Integridade imutável**: Cada arquivo baixado preserva data UTC de acesso, endpoint permanente na API PSI, DOI confirmado e hash SHA-256. URLs S3 assinadas temporárias nunca são persistidas."
        ),
        "src.sec2_title": "2. Extração, Normalização de Unidades e Categorias",
        "src.sec2_body": (
            "- **Normalização conservadora com Pint**: Apenas unidades explicitamente documentadas são convertidas (`1 atm = 14,6959 psia`, `1 m/s = 100 cm/s`, `°C → K`, `% O₂ → fração molar`).\n"
            "- **Proteção de referência**: `psi` ou `mmHg` sem referência nunca viram `psia` absoluto por suposição; pressão manométrica (`psig`) exige referência independente.\n"
            "- **Separação rigorosa de categorias**: `condition` (condição de ensaio), `sample` (catálogo), `reported_result` (resultado reportado), `derived` (cálculo derivado, ex.: pO₂) e `document_context` permanecem distintos."
        ),
        "src.sec3_title": "3. Busca Híbrida, Grounding e Uso de IA",
        "src.sec3_body": (
            "- **Recuperação local-first**: Combina SQLite **FTS5** com embeddings multilíngues locais (`paraphrase-multilingual-MiniLM-L12-v2`, 384 dimensões) quando configurados, ou vetores lexicais PT/EN determinísticos.\n"
            "- **Filtros numéricos por linha**: Filtros físicos (O₂, pressão, velocidade, combustível) verificam observações tipadas estritamente na **mesma linha de origem**.\n"
            "- **Grounding programático**: Quando um LLM opcional é configurado, ele só pode selecionar trechos literais das fontes retornadas; paráfrases e números inventados são recusados em código."
        ),
        "src.sec4_title": "4. Limitações Conhecidas e Ressalvas Científicas",
        "src.sec4_body": (
            "- **Cabeçalho ambíguo no PSI-69**: `Burning rate; mm` em `PSI-69_Experimental table_FLEX.csv` não declara unidade temporal (`mm` vs `mm/s` ou `mm²/s`) e é mantido bruto sem conversão.\n"
            "- **Divergência documental no PSI-69**: O PDF de requisitos associado pela NASA ao estudo `PSI-69` traz **FLEX-2** na capa; esse aviso aparece junto ao documento.\n"
            "- **OCR parcial**: O desenho de 1 página do ignitor SAME (`PSI-102`) não possui camada textual extraível; OCR completo depende do Tesseract.\n"
            "- **Sem certificação**: Não há validação científica independente, coleta de telemetria/vídeos brutos completos nem certificação de segurança aeroespacial."
        ),
        "src.archive_title": "Inventário de Arquivos NASA Verificados e Downloads",
        "src.ingestion_title": "Sincronização do Acervo e Tarefas em Segundo Plano",
        "src.ingestion_desc": "Downloads e ingestão NASA funcionam separados da navegação. Localmente, você pode reindexar os arquivos baixados abaixo.",
        "src.ingestion_readonly": "Implantação pública somente leitura: o registro científico SQLite e o índice de busca são inicializados automaticamente na partida; reingestão manual desativada.",
        "src.ingestion_btn": "Importar downloads e atualizar índice",
        "src.refresh_btn": "Atualizar cache do catálogo",
        "src.jobs_header": "Histórico de Processamento",
        "src.footer_provenance": "URLs permanentes, versões, hashes SHA-256 e lacunas estão documentados em `docs/DATA_PROVENANCE.md`.",
        "src.job_missing": "Job não encontrado. Consulte os registros de ingestão.",
        "src.job_status": "Estado da ingestão: {status}",
        "src.job_done": "Processamento encerrado. Atualize o catálogo para ler os novos documentos.",
        "src.cli_commands": "Comandos locais de coleta e ingestão NASA (desenvolvedores)",
        "src.dl_original": "Baixar bytes originais",
        "src.orig_err": "Original indisponível: {error}.",
        "home.explore_pillar_btn": "Filtrar {pillar} →",
        "inv.context_badge": "Documentação e Contexto Oficial NASA",
        "view.overview_heading": "Resumo do experimento",
        "view.no_description": "Descrição do experimento ainda não informada.",
        "view.isa_objective_heading": "Objetivo do experimento (ISA-Tab)",
        "view.source_file": "Fonte: {name}",
        "view.view_by_dataset": "Visualizar dados por conjunto",
        "view.conclusion_heading": "Conclusão descritiva",
        "view.auto_notes": "Observações automáticas ({count})",
        "view.no_fixes": "Sem correções sugeridas para esta tabela.",
        "view.fix_swap": "Trocar os rótulos de '{a}' e '{b}'",
        "view.fix_swap_help": "Ative apenas se os nomes estiverem invertidos.",
        "view.fix_borrow": "Usar o eixo de '{table}' (suposição)",
        "view.fix_borrow_help": "Suposição reversível quando o bloco não traz seu próprio eixo.",
        "view.fix_pct": "Converter {cols} de % para fração",
        "view.fix_pct_help": "Equaliza escala entre blocos irmãos.",
        "view.explorer_empty_hint": "Importe planilhas ou CSV com dados experimentais numéricos.",
        "view.derived_ignored": "Coluna derivada '{name}' ignorada: {error}",
        "view.crossref_empty": "Nenhuma tabela-índice com colunas 'Data ID' e 'descrição' foi encontrada.",
        "view.crossref_item": "{icon} Data ID {data_id} · {sources} fonte(s) · {blocks} bloco(s) de dados",
        "view.crossref_data": "Dados: {doc} › {block}",
        "view.catalog_empty": "Importe planilhas, CSV ou DOCX para listar os conjuntos de dados.",
        "view.derived_const": "Constante (opcional)",
        "view.derived_col_b": "Segunda coluna",
        "view.col_dataset": "Conjunto / Tabela",
        "view.col_doc": "Documento",
        "view.col_format": "Formato",
        "view.col_rows": "Linhas",
        "view.col_cols": "Colunas",
        "view.col_qty": "Grandeza",
        "view.col_unit": "Unidade",
        "view.col_chart": "Gráfico Sugerido",
        "view.col_alerts": "Alertas",
        "view.col_x": "X sugerido",
        "view.col_y": "Y sugerido",
        "view.col_variable": "Variável",
        "view.col_mean": "Média",
        "view.col_min": "Mín",
        "view.col_max": "Máx",
        "view.col_std": "Desvio",
        "view.col_series": "Série",
        "view.col_index_doc": "Índice",
        "view.col_file": "Arquivo",
        "view.col_imported": "Importado",
        "view.baseline_none": "Nenhuma (bruto)",
        "view.baseline_min": "Subtrair mínimo",
        "view.baseline_first": "Média dos primeiros N",
        "view.norm_none": "Nenhuma (bruto)",
        "view.norm_peak": "Pico = 1,0",
        "view.norm_minmax": "Mín–Máx [0, 1]",
        "view.normalized_suffix": "(normalizado: {mode})",
        "view.value_axis": "valor",
        "view.no_pdf_page_err": "Não foi possível renderizar a página (PyMuPDF instalado?): {error}",
        "view.pdf_no_match_body": "Nenhuma ocorrência localizada nos PDFs importados.",
        "view.isa_heading": "Metadados dos estudos (ISA-Tab)",
        "view.isa_period": "Período da investigação: {start} a {end}",
        "view.isa_submitted": "enviado {submitted} · liberação pública {released}",
        "view.isa_empty_warn": "Sem fatores, ensaios ou protocolos descritos no ISA: {sections}.",
        "view.isa_col_section": "Seção",
        "view.isa_col_field": "Campo",
        "view.isa_col_value": "Valor",
        "view.chart_type_line": "Linha",
        "view.chart_type_line_pts": "Linha com pontos",
        "view.chart_type_scatter": "Dispersão",
        "view.chart_type_bar": "Barras",
        "view.chart_type_heatmap": "Mapa de calor (matriz)",
        "view.chart_type_xyc": "Mapa X–Y–cor",
        "cmp.table_rows": "{rows} linhas",
        "cmp.col_study": "Estudo",
        "cmp.col_name": "Título da Investigação",
        "cmp.col_score": "Score (0–100)",
        "cmp.col_reasons": "Fundamentos",
        "ast.all_studies": "Todas as investigações NASA",
        "ast.orig_unavailable": "Original indisponível: {error}. Reimporte a cópia verificada em Fontes e Metodologia.",
        "ast.page_render_err": "Não foi possível renderizar a página: {error}",
        "vis.no_pdfs": "Não há PDF importado no acervo.",
        "vis.doc_caption": "Documento SHA-256 `{sha}` · página {page} de {total}",
        "vis.preview_caption": "{name} · página {page}",
        "vis.preview_unavailable": "Prévia indisponível: {error}",
        "vis.vlm_spinner": "Solicitando interpretação qualitativa…",
        "vis.vlm_failed": "Revisão não concluída: {err_type}. Nenhuma observação científica foi criada.",
        "vis.candidate_header": "Candidato para Revisão Humana",
        "vis.candidate_status": "Estado: {status} · natureza: inferência · revisão humana necessária",
        "vis.region_label": "Região {idx} · {kind}",
        "vis.region_coords_note": "Coordenadas normalizadas de localização; não são valores físicos medidos.",
        "vis.region_text_note": "Texto candidato não verificado",
        "vis.download_json": "Baixar candidato de revisão (JSON)",
        "vis.human_note_label": "Comentário da revisão humana",
        "vis.human_note_help": "Registre o que conferiu no original. O comentário não promove inferências a medições.",
        "vis.save_note_btn": "Registrar comentário de revisão",
        "vis.save_note_ok": "Comentário registrado. O resultado permanece uma inferência separada dos dados primários.",
        "vis.human_saved_at": "Comentário humano registrado em {utc}",
        "view.isa_untitled": "Estudo sem título",
        "view.isa_objective": "Objetivo",
        "view.isa_obj_missing": "Objetivo não declarado nos metadados.",
        "view.isa_hypothesis": "Hipótese",
        "view.isa_hyp_missing": "Hipótese não declarada nos metadados.",
        "view.isa_approach": "Abordagem experimental",
        "view.isa_no_obj": "Não foram encontrados objetivos ou hipóteses nos metadados ISA-Tab importados.",
        "view.no_stats_conclusion": "Ainda não existem resultados numéricos suficientes para elaborar uma conclusão baseada nos dados.",
        "view.col_observations": "Observações",
        "view.col_median": "Mediana",
        "view.col_label": "Rótulo",
        "view.col_params": "Parâmetros",
        "view.col_kind": "Tipo",
        "view.col_num_values": "Valores numéricos",
        "view.col_source_row": "Linha original",
        "view.crossref_files": "**Arquivos de dados citados em índices:** {total} · não importados: {missing}",
        "view.manual_swap_a": "Trocar rótulos (manual): coluna A",
        "view.manual_swap_b": "coluna B",
        "view.manual_swap_apply": "Aplicar",
        "view.sheet_titles": "Título(s) da planilha: {titles}",
        "view.label_params": "Parâmetros do rótulo: {params}",
        "view.columns_heading": "Colunas",
        "view.derived_default_name": "derivada",
        "view.pdf_matched_terms": "Termos localizados: {terms}",
        "view.pdf_page_line": "{rank}. {name} · página {page}",
        "view.rows_suffix": "{rows} linhas",
        "view.fit_n": "Pontos no ajuste",
        "view.fit_slope": "Inclinação",
        "view.fit_intercept": "Intercepto",
        "view.fit_r": "Correlação linear (r)",
        "view.fit_r2": "R²",
        "view.peak_x": "X do pico",
        "view.peak_y": "Y do pico",
        "view.peak_fwhm": "Largura a meia altura",
        "view.last_x_pos": "Último X com Y > 0",
        "view.last_y_pos": "Y nesse ponto",
        "view.isa_keywords": "Palavras-chave",
        "view.isa_publications": "Publicações",
        "view.isa_contacts": "Contatos",
        "docs.job_running": "Importação ou reprocessamento em segundo plano. Uploads locais mantêm origem local.",
        "docs.job_refresh": "Atualizar processamento",
        "docs.job_done": "Processamento concluído: originais, extrações, registro científico e busca sincronizados.",
        "docs.job_partial": "Processamento parcial. Consulte os avisos abaixo; os originais foram preservados.",
        "docs.job_err": "Processamento {status}: {error}",
        "docs.job_result": "Resultado do processamento local",
        "docs.outdated_warn": "{count} documento(s) extraído(s) por versão anterior. Reprocesse a partir dos originais abaixo.",
        "docs.reprocess_all": "Reprocessar documentos desatualizados",
        "docs.col_size": "Tamanho",
        "docs.col_pages": "Páginas / trechos",
        "docs.col_status": "Status",
        "docs.read_fail": "Não foi possível ler o original: {error}",
        "docs.open_fail": "Não foi possível abrir o documento: {error}",
        "docs.img_preview_err": "Pré-visualização indisponível para este arquivo.",
        "docs.formulas_found": "Fórmulas encontradas ({count})",
        "docs.preview_truncated": "\n… conteúdo truncado na prévia",
    },
}


def t(key: str, lang: str | None = None, **kwargs: Any) -> str:
    """Look up a localized string by key with optional format parameters."""
    active = (lang or get_lang()).lower()
    table = TRANSLATIONS["pt" if active.startswith("pt") else "en"]
    template = table.get(key) or TRANSLATIONS["en"].get(key) or key
    return template.format(**kwargs) if kwargs else template


# ----------------------------------------------------------------------------- Domain label helpers

_EVIDENCE_LABELS: dict[str, dict[str, str]] = {
    "en": {
        "condition": "Test condition",
        "sample": "Sample / catalog",
        "measurement": "Reported outcome",
        "calculation": "Derived calculation",
        "inference": "Inference",
        "context": "Document context",
        "document_context": "Document context",
        "unclassified": "Unclassified",
        "mixed_conditions_and_reported_results": "Conditions & reported outcomes",
        "engineering_or_publication": "Engineering document / publication",
        "reported_result": "Reported outcome (not independent validation)",
        "derived": "Derived calculation",
    },
    "pt": {
        "condition": "Condição de ensaio",
        "sample": "Amostra / catálogo",
        "measurement": "Resultado reportado",
        "calculation": "Cálculo derivado",
        "inference": "Inferência",
        "context": "Contexto documental",
        "document_context": "Contexto documental",
        "unclassified": "Não classificado",
        "mixed_conditions_and_reported_results": "Condições e resultados reportados",
        "engineering_or_publication": "Documento de engenharia ou publicação",
        "reported_result": "Resultado reportado (não validação independente)",
        "derived": "Cálculo derivado",
    },
}

_QUANTITY_LABELS: dict[str, dict[str, str]] = {
    "en": {
        "time": "time",
        "length": "position / distance",
        "diameter": "diameter",
        "temperature": "temperature",
        "pressure": "pressure",
        "strain_rate": "strain rate",
        "fraction": "molar / mass fraction",
        "equivalence_ratio": "equivalence ratio",
        "intensity": "signal / intensity",
        "burning_rate": "burning rate",
        "ratio": "dimensionless ratio",
        "oxygen": "oxygen",
        "velocity": "velocity",
        "fuel": "fuel",
        "rate": "rate",
        "mass_rate": "mass loss rate",
        "unknown": "unclassified",
    },
    "pt": {
        "time": "tempo",
        "length": "posição / distância",
        "diameter": "diâmetro",
        "temperature": "temperatura",
        "pressure": "pressão",
        "strain_rate": "taxa de estiramento",
        "fraction": "fração (molar / mássica)",
        "equivalence_ratio": "razão de equivalência",
        "intensity": "sinal / intensidade",
        "burning_rate": "taxa de queima",
        "ratio": "razão adimensional",
        "oxygen": "oxigênio",
        "velocity": "velocidade",
        "fuel": "combustível",
        "rate": "taxa",
        "mass_rate": "taxa de perda de massa",
        "unknown": "não classificada",
    },
}

_CHART_LABELS: dict[str, dict[str, str]] = {
    "en": {
        "time_series": "Time series",
        "spatial_profile": "Spatial profile",
        "limit_curve": "Limit curve",
        "parametric": "Parametric (X–Y)",
        "matrix": "Matrix / heatmap",
        "distribution": "Distribution",
        "catalog": "Catalog (text)",
    },
    "pt": {
        "time_series": "Série temporal",
        "spatial_profile": "Perfil espacial",
        "limit_curve": "Curva de limite",
        "parametric": "Paramétrico (X–Y)",
        "matrix": "Matriz / campo",
        "distribution": "Distribuição",
        "catalog": "Catálogo (texto)",
    },
}

_STATUS_LABELS: dict[str, dict[str, str]] = {
    "en": {
        "processado": "processed",
        "parcial": "partial",
        "erro": "error",
        "não processado": "unprocessed",
    },
    "pt": {
        "processado": "processado",
        "parcial": "parcial",
        "erro": "erro",
        "não processado": "não processado",
    },
}


def evidence_label(kind: str | None, lang: str | None = None) -> str:
    active = "pt" if (lang or get_lang()).lower().startswith("pt") else "en"
    key = str(kind or "unclassified")
    return _EVIDENCE_LABELS[active].get(key, key)


def quantity_label(quantity: str | None, lang: str | None = None) -> str:
    active = "pt" if (lang or get_lang()).lower().startswith("pt") else "en"
    key = str(quantity or "unknown")
    return _QUANTITY_LABELS[active].get(key, key)


def chart_label(chart_type: str | None, lang: str | None = None) -> str:
    active = "pt" if (lang or get_lang()).lower().startswith("pt") else "en"
    key = str(chart_type or "")
    return _CHART_LABELS[active].get(key, key)


def status_label(status: str | None, lang: str | None = None) -> str:
    active = "pt" if (lang or get_lang()).lower().startswith("pt") else "en"
    key = str(status or "—")
    return _STATUS_LABELS[active].get(key, key)


def translate_comparison_reason(reason: str, lang: str | None = None) -> str:
    """Translate comparison incompatibility messages produced by src/comparison.py."""
    active = "pt" if (lang or get_lang()).lower().startswith("pt") else "en"
    if active == "pt":
        return reason
    if reason == "Selecione duas ou três tabelas.":
        return "Select two or three tables."
    if reason == "Grandezas, unidades, condições ou metodologias diferem entre as tabelas.":
        return "Physical quantities, units, test conditions, or methodologies differ across tables."
    if ": condições, catálogo ou natureza não validada; não equivale a medições." in reason:
        study = reason.split(":", 1)[0]
        return f"{study}: contains test conditions, catalog metadata, or unvalidated nature — not equivalent to measurements."
    if ": metodologia e condições comparáveis não documentadas." in reason:
        study = reason.split(":", 1)[0]
        return f"{study}: comparable methodology and test conditions are not documented."
    if ": dimensões/unidades insuficientes para comparação quantitativa." in reason:
        study = reason.split(":", 1)[0]
        return f"{study}: insufficient dimensions or explicit units for quantitative comparison."
    return reason


def translate_relevance_reason(reason: str, lang: str | None = None) -> str:
    """Translate deterministic relevance explanation strings from src/relevance.py."""
    active = "pt" if (lang or get_lang()).lower().startswith("pt") else "en"
    if active == "pt":
        return reason
    return (
        reason.replace("Aplicação:", "Application match:")
        .replace("Sem termo específico da aplicação (+0)", "No application-specific match (+0)")
        .replace("Consulta:", "Query terms:")
        .replace(" termos (", " terms (")
        .replace("Arquivos locais:", "Local files:")
    )


def translate_retrieval_warning(warning: str, lang: str | None = None) -> str:
    """Translate backend retrieval warnings for display without mutating core RetrievalIndex."""
    active = "pt" if (lang or get_lang()).lower().startswith("pt") else "en"
    if active == "pt":
        return warning
    if "Índice criado com outro modelo" in warning:
        return "Index was built with another model: re-indexing recommended; lexical search evidence remains preserved."
    if "RAG_EMBEDDING_MODEL deve apontar" in warning:
        return "RAG_EMBEDDING_MODEL must point to an existing local model directory; lexical retrieval active."
    if warning.startswith("Modelo local indisponível:"):
        return warning.replace("Modelo local indisponível:", "Local embedding model unavailable:").replace(
            "busca lexical ativa.", "lexical retrieval active."
        )
    return warning


def translate_quality_flag(flag: dict[str, Any], lang: str | None = None) -> str:
    """Return a localized explanation for a table quality flag."""
    active = "pt" if (lang or get_lang()).lower().startswith("pt") else "en"
    msg = str(flag.get("message", ""))
    if active == "pt":
        return msg
    code = str(flag.get("code", ""))
    cols = flag.get("columns", [])
    col0 = cols[0] if cols else ""
    col1 = cols[1] if len(cols) > 1 else ""
    mapping = {
        "sem_cabecalho": "No header row was detected; columns received provisional names.",
        "valores_ausentes": f"Column '{col0}' contains missing/empty cells.",
        "texto_em_coluna_numerica": f"Column '{col0}' contains text cells that are ignored in numeric plots.",
        "intervalos_em_celulas": f"Column '{col0}' contains ranges or approximations; min/max helper columns were added.",
        "sinal_negativo": f"Column '{col0}' includes negative baseline noise; avoid direct logarithmic scaling.",
        "rotulos_trocados": f"'{col0}' is not monotonic while '{col1}' looks like an axis; column headers may be swapped.",
        "eixo_ausente": f"'{col0}' is not monotonic and no other axis column was found in this block.",
        "deslocamento_constante": f"'{col1}' equals '{col0}' plus a constant offset.",
        "x_fora_de_ordem": f"'{col0}' is not sorted; the chart explorer sorts by X before connecting points.",
        "x_decrescente": f"'{col0}' is sorted in descending order.",
        "x_repetido": f"'{col0}' contains repeated X values.",
        "percentual_vs_fracao": f"'{col0}' uses percentages (0–100) while sibling blocks use fractions (0–1).",
        "comprimento_diferente": "Block row count differs slightly from sibling blocks with the same headers.",
    }
    return mapping.get(code, msg)


def investigation_profile(study_id: str, lang: str | None = None) -> dict[str, str]:
    """Return localized scientific profile metadata for a known NASA PSI study."""
    active = "pt" if (lang or get_lang()).lower().startswith("pt") else "en"
    return INVESTIGATION_PROFILES.get(study_id, {}).get(active, {})
