"""Centralized bilingual localization (English default + Portuguese PT-BR) and domain glossaries."""
from __future__ import annotations

from typing import Any

import streamlit as st

DEFAULT_LANG = "en"
LANGUAGE_OPTIONS: dict[str, str] = {
    "en": "EN",
    "pt": "PT-BR",
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
    "PSI-62": {
        "en": {
            "pillar": "Prevention",
            "objective": "Develop unsteady flamelet generated manifold (UFGM) models of concurrent solid-fuel flame spread in microgravity, benchmarked against BASS and BASS-II experiments using two-color tomography.",
            "relevance": "Supports investigation of modeled material flammability boundaries and radiation/chemistry coupling.",
            "caveat": "Ground modeling investigation. Only ISA-Tab research metadata and publication references are available in the supplied/public archive; no independent measured series or numerical simulation outputs were supplied.",
        },
        "pt": {
            "pillar": "Prevenção",
            "objective": "Desenvolver modelos UFGM (unsteady flamelet generated manifolds) de propagação concorrente de chama em sólidos em microgravidade, comparados aos experimentos BASS e BASS-II por tomografia de duas cores.",
            "relevance": "Apoia a investigação de limites modelados de inflamabilidade e do acoplamento entre radiação e química.",
            "caveat": "Investigação de modelagem em solo. O acervo fornecido/público contém apenas metadados ISA-Tab e referências bibliográficas; não foram fornecidas séries medidas independentes nem resultados numéricos de simulação.",
        },
    },
    "PSI-117": {
        "en": {
            "pillar": "Suppression",
            "objective": "Investigate how external thermal and convective perturbations affect droplet cool-flame dynamics using multidimensional CFD models informed by FLEX flight data.",
            "relevance": "Examines cool-flame oscillation, extinction and transitions through simulation and comparisons with reported experimental observations.",
            "caveat": "Ground CFD investigation: analyzed CSVs contain simulations and selected experimental reference series. Expt/Sim/Model labels remain distinct; absent units are not inferred, and presentation plots are not digitized as exact measurements.",
        },
        "pt": {
            "pillar": "Supressão",
            "objective": "Investigar o efeito de perturbações térmicas e convectivas externas na dinâmica de chamas frias de gotas com modelos CFD multidimensionais apoiados em dados de voo FLEX.",
            "relevance": "Examina oscilação, extinção e transições de chamas frias por simulações e comparações com observações experimentais reportadas.",
            "caveat": "Investigação CFD em solo: os CSVs analisados contêm simulações e séries experimentais de referência selecionadas. Expt/Sim/Model permanecem distintos; unidades ausentes não são inferidas e gráficos das apresentações não viram medições exatas.",
        },
    },
    "PSI-159": {
        "en": {
            "pillar": "Suppression",
            "objective": "ACME CFI-G (Cool Flames Investigation with Gases): investigate spherical cool diffusion flames of gaseous fuels aboard the ISS, supported by CFD and chemical-kinetics studies.",
            "relevance": "Studies cool-flame regimes across fuel mixtures, normal/inverse flow, pressure and flow conditions.",
            "caveat": "Engineering and final-report PDFs provide documentary evidence; experimental tables include run conditions and selected reported outcomes, not raw sensor telemetry. Simulation predictions and reported flight observations must remain distinct.",
        },
        "pt": {
            "pillar": "Supressão",
            "objective": "ACME CFI-G (Cool Flames Investigation with Gases): investigar chamas frias de difusão esférica de combustíveis gasosos na ISS, com apoio de CFD e estudos de cinética química.",
            "relevance": "Estuda regimes de chama fria com diferentes misturas, fluxos normais/inversos, pressões e vazões.",
            "caveat": "Os PDFs de engenharia e relatório final fornecem evidência documental; tabelas experimentais incluem condições de ensaios e resultados reportados selecionados, não telemetria bruta. Previsões de simulação e observações de voo reportadas permanecem distintas.",
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
        "view.evidence_nature": "Evidence type: {kind}",
        "view.field_nature": "Source classification by column",
        "view.source_basis": "Classification basis",
        "view.simulation_notice": "Numerical predictions are not experimental measurements. Keep simulation and experimental reference series distinct; unclassified columns remain unvalidated.",
        "view.incompatible_axes": "These series have different or undeclared quantities/units. Inspect one series at a time; no common-axis overlay or interpolation is produced.",
        "app.title": "Flame in Freefall",
        "app.subtitle": "NASA Space Apps 2026 · Microgravity Combustion Explorer",
        "sidebar.language": "Language: EN | PT-BR",
        "sidebar.nav_label": "Workspace Navigation",
        "sidebar.readonly_badge": "Verified NASA Research Archive · Public Showcase",
        "sidebar.local_badge": "Verified NASA Research Archive · Local Edition",
        "sidebar.footer_note": "Original NASA PSI files are preserved verbatim with cryptographic verification. Scientific discovery tool only — never a flight certification.",

        # Persistent Context Bar
        "topbar.where": "Where you are",
        "topbar.home": "🏠 Home",
        "topbar.back": "← Back",

        # Navigation
        "nav.home": "Home / Overview",
        "nav.investigations": "Investigations",
        "nav.explorer": "Data Explorer",
        "nav.compare": "Compare",
        "nav.assistant": "Scientific Assistant",
        "nav.visual_review": "Visual Page Review",
        "nav.sources": "Sources & Methodology",

        # Home / Overview
        "home.title": "Explore the Science of Fire in Space",
        "home.subtitle": "Analyze microgravity combustion and spacecraft fire safety using authentic NASA Physical Sciences Informatics (PSI) datasets, charts, and verifiable citations.",
        "home.lead": (
            "Explore authentic NASA Physical Sciences Informatics (PSI) datasets aboard the International Space Station "
            "and spacecraft experiments — built for judges, students, engineers, and curious minds."
        ),
        "home.plain_intro": (
            "Inside an orbiting spacecraft, astronauts and cabin air are in continuous freefall — buoyancy vanishes, flames turn spherical, "
            "smoke lingers along cabin airflow, and low-temperature cool flames can persist. Flame in Freefall organizes real NASA PSI flight "
            "and ground combustion research to support transparent spacecraft fire-safety investigation."
        ),
        "home.start_title": "Choose How You Want to Explore",
        "home.exp_a_badge": "Guided Discovery · 4 Steps (~3 min)",
        "home.exp_a_title": "Discover the Science",
        "home.exp_a_desc": (
            "Learn why freefall turns flames into spheres, walk through NASA's FLEX droplet study, and read a real flight chart step by step."
        ),
        "home.exp_a_btn": "Discover the Science →",
        "home.exp_b_badge": "Spacecraft Safety · 4 Steps (~3 min)",
        "home.exp_b_title": "Explore Fire Safety",
        "home.exp_b_desc": (
            "Investigate cabin fire safety across Prevention (BASS-II, Saffire), Detection (SAME), and Suppression (FLEX, ACME CFI-G)."
        ),
        "home.exp_b_btn": "Explore Fire Safety →",
        "home.exp_c_badge": "Direct Research Workbench",
        "home.exp_c_title": "Investigate NASA Data",
        "home.exp_c_desc": (
            "Open interactive plots, inspect original NASA tables and PDFs with preserved units, compare studies, or query the grounded assistant."
        ),
        "home.exp_c_btn_data": "Investigate NASA Data →",
        "home.exp_c_btn_assistant": "Ask Evidence-First Scientific Assistant →",
        "home.exp_c_btn_studies": "Browse All 12 NASA Investigations →",
        "home.compare_title": "Earth vs. Microgravity: What Changes When Gravity Stops Pulling Air Up?",
        "home.earth_title": "On Earth (1g Gravity)",
        "home.earth_points": (
            "- **Teardrop flame:** Hot exhaust gas rises quickly because it is lighter than cool surrounding air.\n"
            "- **Buoyant draft:** Rising heat continually pulls fresh oxygen inward at the base of the flame.\n"
            "- **Rising smoke:** Buoyancy lifts smoke plumes straight toward ceiling detectors.\n"
            "- **Rapid cooling:** Natural upward convection sheds heat away from burning surfaces."
        ),
        "home.space_title": "In Spacecraft Freefall (~0g Microgravity)",
        "home.space_points": (
            "- **Spherical flame:** Without upward buoyancy, heated gases expand symmetrically into a glowing sphere.\n"
            "- **Diffusion & cabin airflow:** Oxygen reaches fires mainly through slow molecular diffusion or spacecraft fans.\n"
            "- **Suspended smoke:** Soot particles linger and grow larger while drifting gently with cabin ventilation.\n"
            "- **Cool flames possible:** Some liquid droplets continue reacting cleanly below normal hot-flame temperatures."
        ),
        "home.glossary_title": "Key Scientific Terms Explained Simply",
        "home.archive_title": "Verified NASA Evidence Inside This Workspace",
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
            "**PSI Flame Microgravity** unifies 12 priority investigations into a transparent, verifiable workspace where "
            "**test conditions are never confused with measured outcomes**, units are conservatively normalized, and every claim links back to an exact NASA document, page/row, and SHA-256 hash."
        ),
        "home.metric_studies": "NASA PSI Studies",
        "home.metric_docs": "Preserved NASA Files",
        "home.metric_tables": "Extracted Tables",
        "home.metric_chunks": "Searchable Evidence Segments",
        "home.metric_chunks_semantic": "Searchable Evidence Segments",
        "home.metric_chunks_lexical": "Searchable Evidence Segments",
        "home.chunk_caption_semantic": (
            "{chunks} multilingual searchable passages indexed across {docs} authentic NASA documents."
        ),
        "home.chunk_caption_lexical": (
            "{chunks} verified passages and table rows indexed locally across {docs} authentic NASA documents."
        ),
        "home.tech_diag_label": "Technical archive & search engine diagnostics (optional)",
        "home.extraction_caption": "Archive status: {processed} fully processed · {partial} partial · {failed} failed. Inspect exact provenance in Sources & Methodology.",
        "home.pillars_title": "Three Pillars of Spacecraft Fire Safety in NASA PSI",
        "home.pillar_prevention": "Prevention",
        "home.pillar_prevention_studies": "BASS · BASS-II · Saffire-I / II / III · PSI-62 (UFGM metadata)",
        "home.pillar_prevention_desc": "How solid cabin materials ignite, spread flames, and are modeled under microgravity airflow and oxygen levels.",
        "home.pillar_detection": "Detection",
        "home.pillar_detection_studies": "SAME · SAME-R",
        "home.pillar_detection_desc": "How smoke particle sizes and aerosols behave without buoyancy so spacecraft detectors catch fires early.",
        "home.pillar_suppression": "Suppression",
        "home.pillar_suppression_studies": "FLEX · FLEX-2 · PSI-117 (Cool-Flame CFD) · PSI-159 (ACME CFI-G)",
        "home.pillar_suppression_desc": "How liquid fuel droplets and gaseous cool flames burn, oscillate, and extinguish as oxygen or diluents vary.",
        "home.pillar_coverage": "{imported} of {total} priority NASA investigations loaded",
        "home.warning_conditions": (
            "Scientific Integrity Notice: Experimental tables frequently describe test conditions or catalogs. "
            "By themselves, they do not prove flame propagation speed, suppression efficacy, or spacecraft fire-safety certification."
        ),
        "home.no_docs": "No documents are currently imported. Inspect Sources & Methodology to check archive status.",

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
        "ast.mode_semantic": "Search mode: Multilingual hybrid semantic & full-text search (offline-capable)",
        "ast.mode_lexical": "Search mode: Exact NASA keyword & unit-aware table retrieval (offline-capable)",
        "ast.llm_unconfigured_banner": (
            "**Verified Local Evidence Mode:** Answers present exact NASA excerpts, typed table values, and traceable source provenance with zero fabricated claims."
        ),
        "ast.llm_configured_banner": (
            "**Optional Grounded AI Synthesis Available:** When enabled, the AI assistant selects verbatim passages strictly from retrieved public NASA records and verifies every citation in code."
        ),
        "ast.diag_title": "Technical retrieval & AI configuration diagnostics",
        "ast.chat_user_label": "Research question",
        "ast.chat_assistant_label": "Evidence-grounded response",
        "ast.synth_summary_heading": "SUMMARIZE · Matched NASA Investigation Overview",
        "ast.synth_interpret_heading": "INTERPRET · Scientific & Spacecraft Context",
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
        "ast.studies_filter": "Filter by NASA investigation (empty = search all indexed studies + guides)",
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
        "vis.vlm_unconfigured": "Optional visual AI reviewer is not configured in this environment. Local PDF page rendering works 100% offline.",
        "vis.vlm_consent": "Explicitly send ONLY this rendered page image to the configured VLM endpoint",
        "vis.vlm_consent_help": "Image leaves the host only when checked. Output remains an unverified inference.",
        "vis.vlm_btn": "Request Qualitative Review Candidate",

        # Sources & Methodology
        "src.title": "Sources, Provenance & Scientific Methodology",
        "src.lead": "Complete transparency on where NASA data comes from, how units and embeddings work, what AI does and does not do, and known dataset limitations.",
        "src.sec1_title": "1. NASA PSI Data Origins & Provenance",
        "src.sec1_body": (
            "- **Primary source**: NASA Physical Sciences Informatics (PSI) Data Repository (`https://psi.nasa.gov/physci/repo/search?q=combustion`).\n"
            "- **Dataset scope**: **{studies} PSI investigations** plus the official NASA context guides, totaling **{files} processed source files ({size} bytes)**. PSI-62 contains research metadata, PSI-117 includes simulations and experimental references, and PSI-159 includes flight-study documentation and run conditions.\n"
            "- **Immutable integrity**: Every downloaded file is stored untouched alongside its UTC access timestamp, permanent PSI API URL, confirmed DOI, and SHA-256 digest. Ephemeral signed S3 download links are never stored."
        ),
        "src.sec2_title": "2. Extraction, Unit Normalization & Data Categories",
        "src.sec2_body": (
            "- **Conservative Pint normalization**: Only explicitly documented units are converted (`1 atm = 14.6959 psia`, `1 m/s = 100 cm/s`, `°C → K`, `% O₂ → mole fraction`).\n"
            "- **Reference protection**: Unreferenced `psi` or `mmHg` is never silently converted to absolute `psia`; gauge pressure (`psig`) requires an independent ambient reference.\n"
            "- **Strict evidence separation**: `condition` (test setup), `sample` (catalog metadata), `reported_result` (published outcomes), `derived` (e.g. partial O₂ pressure), `simulation` (numerical predictions), `metadata` (research context), and `document_context` never mix silently."
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

        # Sidebar Mode & Guided Navigation
        "sidebar.mode_label": "Experience level",
        "sidebar.mode_guided": "Guided Exploration (Default)",
        "sidebar.mode_advanced": "Advanced Research (All Controls)",
        "sidebar.mode_help": (
            "Guided Exploration focuses on clear scientific explanations and hides low-level filters, hashes, "
            "and engineering diagnostics inside optional panels. Advanced Research expands technical tools directly."
        ),
        "sidebar.exit_journey": "Exit Guided Journey",
        "sidebar.return_journey": "← Return to Guided Journey (Step {step} of {total})",
        "sidebar.journey_banner": (
            "You opened **{study_id}** from a Guided Journey. Inspect any NASA tables or charts here, "
            "and click the button above when ready to resume Step {step}."
        ),

        # Beginner Glossary
        "glossary.microgravity_term": "Microgravity (~0g)",
        "glossary.microgravity_def": (
            "Continuous orbital freefall inside a spacecraft: gravity bends the orbit, but air and flames float together without upward buoyancy."
        ),
        "glossary.o2_term": "Oxygen Mole Fraction (O₂ mol frac)",
        "glossary.o2_def": (
            "Share of gas molecules in the test chamber that are oxygen. For comparison, `0.21` equals 21% oxygen — roughly Earth sea-level air."
        ),
        "glossary.drop_diam_term": "Droplet Diameter (mm)",
        "glossary.drop_diam_def": (
            "Width of an isolated spherical fuel droplet tested inside a sealed chamber (often 1–5 mm) to measure burning and extinction."
        ),
        "glossary.psi_term": "NASA PSI Archive",
        "glossary.psi_def": (
            "NASA's Physical Sciences Informatics repository of genuine spaceflight experiment files from the ISS and orbital test vehicles."
        ),

        # Guided Journeys Shared Controls
        "journey.badge_j1": "Guided Journey 1 · Understanding Fire in Microgravity",
        "journey.badge_j2": "Guided Journey 2 · Fire Safety in Spacecraft",
        "journey.step_indicator": "Step {current} of {total}",
        "journey.back": "← Back",
        "journey.continue": "Continue →",
        "journey.restart": "Restart Journey",
        "journey.exit": "Back to Discovery Home",
        "journey.open_advanced": "Technical details & provenance for this step",

        # Journey 1 — Understanding Fire in Microgravity
        "j1.s1_title": "1. Why Fire Behaves Differently in Microgravity",
        "j1.s1_purpose": "Purpose: Build clear intuition about gravity, buoyancy, and combustion before inspecting spaceflight datasets.",
        "j1.s1_explain": (
            "On Earth, hot combustion gases expand and weigh less than surrounding air, so **gravity pulls cooler air underneath and pushes hot exhaust upward**. "
            "That buoyant draft stretches a flame into its classic yellow teardrop.\n\n"
            "In orbital freefall, cabin air and warm gas weigh the same relative to the spacecraft — **buoyancy vanishes**. "
            "Instead of streaming upward, combustion products stay wrapped around the fuel while fresh oxygen enters slowly by diffusion or gentle cabin ventilation, "
            "forming a quiet, nearly **spherical blue flame**."
        ),
        "j1.s1_callout_title": "Interactive Physics Breakdown: Select an Effect to Compare 1g vs. 0g",
        "j1.s1_aspect_label": "Choose what aspect of fire to compare:",
        "j1.s1_aspect_shape": "Flame Shape (Teardrop vs. Sphere)",
        "j1.s1_aspect_o2": "How Oxygen Reaches the Flame",
        "j1.s1_aspect_temp": "Hot Flames vs. Cool Flames",
        "j1.s1_aspect_smoke": "Smoke & Soot Behavior",
        "j1.s1_desc_shape": (
            "**On Earth (`1g`):** Buoyancy stretches heated gas upward into an elongated teardrop.\n\n"
            "**In Orbit (`~0g`):** Without an 'up' direction for hot air, symmetrical heat and gas diffusion form a **spherical flame**."
        ),
        "j1.s1_desc_o2": (
            "**On Earth (`1g`):** Upward plumes pump fresh oxygen continuously toward the base of a fire.\n\n"
            "**In Orbit (`~0g`):** Oxygen arrives slowly by molecular diffusion — or along cabin air fans — dramatically changing how long droplets burn before extinguishing."
        ),
        "j1.s1_desc_temp": (
            "**In Orbit (`~0g`):** Because heat and fuel vapors linger around the droplet instead of rising away, NASA's FLEX experiments revealed liquid droplets can transition into low-temperature **cool flames** after visible hot flames go out."
        ),
        "j1.s1_desc_smoke": (
            "**On Earth (`1g`):** Buoyant plumes rush smoke up to ceiling sensors.\n\n"
            "**In Orbit (`~0g`):** Without upward convection, soot particles stay suspended longer, grow through coagulation, and travel along air vents."
        ),

        # Journey 1 Step 2
        "j1.s2_title": "2. Meet NASA's FLEX Experiment (PSI-69)",
        "j1.s2_purpose": "Purpose: See what NASA astronauts tested aboard the ISS and preview an authentic experiment page.",
        "j1.s2_explain": (
            "Inside the International Space Station's Microgravity Science Glovebox, NASA's **Flame Extinguishment Experiment (FLEX · PSI-69)** "
            "tested how tiny suspended drops of liquid fuels — such as **n-heptane** and **methanol** (typically **1–5 mm** wide) — ignite, form spherical flames, and extinguish "
            "as oxygen (`O2 mol frac`) and inert gases (`N2`, `He`, `CO2`, `Xe`) change.\n\n"
            "Here is how the experiment appears in the preserved NASA guide before we plot its numbers:"
        ),
        "j1.s2_pdf_caption": "Authentic NASA PSI-69 PDF preview (`researchers_guide.pdf`, original page {page})",
        "j1.s2_pdf_unavailable": "PDF page preview unavailable in this environment; raw text and SHA-256 record remain preserved.",
        "j1.s2_btn_explorer": "Open PSI-69 in Full Data Explorer →",

        # Journey 1 Step 3
        "j1.s3_title": "3. Inspect & Interpret Real NASA Experimental Evidence",
        "j1.s3_purpose": "Purpose: Read an authentic PSI-69 plot and verified NASA text snippets with plain-language guidance.",
        "j1.s3_explain": (
            "Below is real quantitative data extracted directly from NASA's **PSI-69 (FLEX)** CSV archive. "
            "Choose a perspective to inspect what conditions NASA tested versus what outcomes require careful scientific caution."
        ),
        "j1.s3_view_label": "Choose a real PSI-69 view:",
        "j1.s3_opt_extinction": "Atmosphere Tested: Oxygen Concentration (O₂) vs. Fuel Droplet Size (mm)",
        "j1.s3_opt_burning": "Raw Value Check: Oxygen Concentration (O₂) vs. Reported 'Burning rate; mm' (Includes Unit Caveat)",
        "j1.s3_evidence_title": "Verified NASA Excerpts Retrieved for PSI-69",
        "j1.s3_chart_missing": "Interactive PSI-69 numeric table is not loaded in this test fixture; verified NASA document excerpts remain accessible below.",

        # Journey 1 Step 4
        "j1.s4_title": "4. Scientific Findings, Provenance & Limitations",
        "j1.s4_purpose": "Purpose: Summarize what the PSI-69 data actually demonstrates and where honest scientific limits begin.",
        "j1.s4_learned_title": "What Verified NASA Evidence Shows",
        "j1.s4_learned_body": (
            "- **Spherical droplet flames behave sensitively to oxygen fraction and diluent gas:** PSI-69 tables record exact oxygen mole fractions (`O2 mol frac`), pressures, and initial droplet diameters across isolated orbital runs.\n"
            "- **Two-stage / cool-flame dynamics appear in FLEX records:** Real NASA guide excerpts document cool-flame behavior after apparent visible extinction.\n"
            "- **Source quirks are transparently preserved:** Our ingestion audit preserves NASA's exact cover notice (`FLEX-2` inside the PSI-69 PDF bundle) and flags columns like `Burning rate; mm` without inventing missing time units."
        ),
        "j1.s4_limits_title": "What This Experiment Does NOT Establish Alone",
        "j1.s4_limits_body": (
            "- Isolated **1–5 mm fuel droplets** inside a quiescent chamber do **not** represent full-scale fires in spacecraft wires, foam, or fabrics.\n"
            "- Rows listing chamber gas mixtures (`O2 mol frac`, `N2`, pressure) represent **test conditions**, not standalone suppression certification.\n"
            "- Never merge droplet combustion tables (`PSI-69`) directly with solid-material flame spread (`PSI-25 · BASS-II`) without checking experimental geometry and units."
        ),
        "j1.s4_next_title": "Recommended Next Actions",
        "j1.s4_btn_j2": "Start Journey 2: Spacecraft Fire Safety →",
        "j1.s4_btn_assistant": "Ask Evidence Assistant about FLEX →",
        "j1.s4_btn_explorer": "Open PSI-69 in Data Explorer →",

        # Journey 2 — Fire Safety in Spacecraft
        "j2.s1_title": "1. Why Fire Is a Unique Hazard on Spacecraft",
        "j2.s1_purpose": "Purpose: Understand why orbital exploration changes fire ignition, smoke detection, and extinguishment.",
        "j2.s1_explain": (
            "Inside a spacecraft cabin, crews cannot evacuate outdoors or vent an uncontrolled fire without risking depressurization. "
            "Continuous cabin circulation fans move air gently across cables, batteries, and fabrics — meaning fire behaves very differently than in a room on Earth.\n\n"
            "NASA's PSI fire-safety investigations examine three mission-critical safety questions:"
        ),
        "j2.s1_risk_cards": (
            "- **Ignition & Material Spread:** Future deep-space cabins may use **higher oxygen concentrations at lower pressures** so astronauts can prepare for spacewalks — raising questions about how thin plastics and fabrics burn under slow cabin ventilation.\n"
            "- **Hidden Smoke & Late Alarms:** Without upward plumes carrying soot straight to the ceiling, smoke particles coalesce differently in microgravity, requiring detectors tuned for actual space aerosol particle sizes.\n"
            "- **Extinction Limits:** Halon or CO₂ suppression and lower oxygen levels behave differently when buoyancy disappears and **cool flames** can persist."
        ),

        # Journey 2 Step 2
        "j2.s2_title": "2. Prevention, Detection, and Suppression Across NASA PSI",
        "j2.s2_purpose": "Purpose: Select a spacecraft fire-safety pillar to inspect which authentic NASA studies address it.",
        "j2.s2_pillar_select": "Select a fire-safety defense layer to explore:",
        "j2.s2_pillar_prevention_detail": (
            "**Studies in archive:** `BASS (PSI-26)`, `BASS-II (PSI-25)`, `Saffire-I (PSI-98)`, `Saffire-II (PSI-99)`, `Saffire-III (PSI-100)`, `UFGM Modeling (PSI-62 · metadata only)`\n\n"
            "**Safety focus:** Measure and model how **solid fuels** (polymers, cotton/fiberglass composites, wire-like samples) ignite and spread flames under forced cabin airflow velocities and varying oxygen concentrations."
        ),
        "j2.s2_pillar_detection_detail": (
            "**Studies in archive:** `SAME (PSI-102)`, `SAME-R (PSI-101)`\n\n"
            "**Safety focus:** Characterize **smoke aerosol particle size distributions** produced by overheated wire insulation and spacecraft materials in microgravity so optical and ionization spacecraft smoke alarms avoid false negatives or false alarms."
        ),
        "j2.s2_pillar_suppression_detail": (
            "**Studies in archive:** `FLEX (PSI-69)`, `FLEX-2 (PSI-68)`, `Cool-Flame CFD (PSI-117 · simulations + reference series)`, `ACME CFI-G (PSI-159)`\n\n"
            "**Safety focus:** Establish **extinction boundaries**, oxygen concentration limits, inert gas dilution effects, spherical droplet flame lifetimes, and cool-flame regimes."
        ),
        "j2.s2_loaded_studies": "Loaded NASA investigations matching this pillar ({count}):",

        # Journey 2 Step 3
        "j2.s3_title": "3. Examine Real NASA Fire-Safety Evidence",
        "j2.s3_purpose": "Purpose: Inspect real NASA charts, PDFs, and excerpts across Prevention (BASS-II), Detection (SAME), and Suppression (FLEX).",
        "j2.s3_focus_label": "Choose an authentic evidence slice to examine:",
        "j2.s3_focus_bass": "Prevention Evidence · BASS-II (PSI-25) Solid Fuel Flame Data",
        "j2.s3_focus_same": "Detection Evidence · SAME (PSI-102) Microgravity Smoke Report",
        "j2.s3_focus_compare": "Cross-Pillar Check · Why Prevention (BASS-II) & Suppression (FLEX) Must Not Be Blindly Merged",
        "j2.s3_same_pdf_caption": "Authentic NASA PSI-102 PDF preview (`SAME` final report, page {page})",
        "j2.s3_compare_callout": (
            "**Scientific Integrity Check:** Even though both `PSI-25 (BASS-II)` and `PSI-69 (FLEX)` study spacecraft fire safety, "
            "one measures **solid materials under forced airflow** while the other measures **isolated liquid fuel droplets** in quiescent gas. "
            "Comparing insights conceptually is valuable — pooling raw numbers into a single axis would mislead!"
        ),

        # Journey 2 Step 4
        "j2.s4_title": "4. How Findings May Inform Spacecraft Safety Research",
        "j2.s4_purpose": "Purpose: Translate experimental observations into careful, evidence-bounded engineering takeaways.",
        "j2.s4_findings_title": "Key Research Implications Grounded in This Archive",
        "j2.s4_findings_body": (
            "- **Ventilation & Atmosphere Design (Prevention · BASS-II / Saffire):** Flammability thresholds depend on **both oxygen fraction and airflow velocity** — low-speed cabin fans can sustain solid-fuel flames near oxygen extinction limits.\n"
            "- **Smoke Detector Calibration (Detection · SAME):** Microgravity combustion generates **different particle-size distributions** than normal-gravity fire tests; smoke-detector thresholds must reflect orbital aerosol physics.\n"
            "- **Suppression & Re-ignition Caution (Suppression · FLEX):** Droplet extinction data show that extinguished visible flames can leave lingering heat or **cool-flame chemistry** if oxygen rises again."
        ),
        "j2.s4_caveats_title": "Honest Scope & Engineering Limitations",
        "j2.s4_caveats_body": (
            "- These PSI datasets support **scientific insight and hypothesis validation**, **not flight-hardware fire certification** on their own.\n"
            "- Imported NASA bundles vary in completeness (`processed` vs. `partial` where auxiliary binary formats require specialized tools).\n"
            "- Every claim made inside this platform can be checked directly against the raw source file, page/row index, and SHA-256 fingerprint."
        ),
        "j2.s4_next_title": "Continue Exploring With Full Research Tools",
        "j2.s4_btn_compare": "Open Study Comparison Tool →",
        "j2.s4_btn_assistant": "Ask Assistant About Spacecraft Fire Safety →",
        "j2.s4_btn_explorer": "Inspect BASS-II (PSI-25) in Explorer →",

        # Chart Explanations
        "chart_guide.title": "How to Read This Chart",
        "chart_guide.shows_label": "What this chart shows:",
        "chart_guide.axes_label": "Axes & units:",
        "chart_guide.source_label": "NASA source & data role:",
        "chart_guide.interpret_label": "How to interpret:",
        "chart_guide.caution_label": "Important caveat:",
        "chart_guide.term_help_title": "Glossary of variables & units in this view",
        "chart_guide.role_measurement": "Experimental observations / measured quantities",
        "chart_guide.role_condition": "Test conditions / chamber setup parameters",
        "chart_guide.role_mixed": "Mixed table (both test settings and observed values)",
        "chart_guide.note_condition_only": (
            "Points primarily show which test configurations NASA ran rather than proving a physical response curve."
        ),
        "chart_guide.note_trend": (
            "Read left-to-right across the horizontal variable (`{x}`) and see how `{y}` rises, drops, or spreads across individual NASA test runs."
        ),
        "chart_guide.caution_default": (
            "Applies strictly to the documented setup, fuel geometry, and rows in {study_id}; avoid extrapolating directly to full spacecraft cabins."
        ),
        "chart_guide.caution_burning_mm": (
            "Source header `'Burning rate; mm'` lists `'mm'` without a time unit (`'/s'`); check the source NASA PDF/notes before citing it as a burning rate speed."
        ),
        "chart_guide.caution_series_mode": "Derived chart adjustment active: `{mode}` (raw values remain preserved in the underlying table).",
        "chart_guide.explorer_controls_label": "Customize chart variables, filters, or derived transforms (Advanced Controls)",
        "chart_guide.heatmap_shows": "Spearman correlation matrix across numeric columns in `{dataset}`.",
        "chart_guide.heatmap_caution": "Strong correlation highlights variables moving together in these rows — it never proves physical causation by itself.",

        # Assistant Plain-Language Guide
        "ast_guide.filters_expander": "Advanced filters, study selection & index diagnostics",
        "ast_guide.examples_hint": "Try a beginner-friendly question (runs automatically):",
        "ast_guide.summary_title": "Plain-Language Guide to These Results",
        "ast_guide.summary_counts": "Retrieved **{matches}** verified passage(s) or table row(s) across **{studies}** NASA investigation(s): {study_list}.",
        "ast_guide.summary_how": (
            "How to verify each card below: look at the **evidence label** (`Measurement`, `Test Condition`, or `Document Context`) "
            "before citing a number, and click **View Exact Source** or the provenance header to inspect the original file, page/row, and SHA-256 fingerprint."
        ),
        "ast_guide.summary_no_llm": (
            "Running in **Verified Local Evidence Mode** (no AI synthesis required): the cards below present verbatim NASA records without ungrounded text."
        ),
        "ast_guide.summary_caveat_prefix": "Primary scientific caveat across matched studies: ",

        # Data Explorer visual-first preview & Challenge Hub
        "view.overview_preview_title": "Visual First Look · Experimental Data Preview",
        "view.overview_preview_caption": "Primary variables plotted automatically before tabular statistics; switch to Interactive Charts to adjust axes, fits, or transforms.",
        "hub.title": "Space Apps Challenge 2026 Hub · SUMMARIZE · RANK · INTERPRET",
        "hub.subtitle": "Inspect any NASA study through the three core scientific workflows — directly anchored to original files and honest caveats.",
        "hub.tab_summarize": "1. SUMMARIZE Study",
        "hub.tab_rank": "2. RANK Priority",
        "hub.tab_interpret": "3. INTERPRET Safety Impact",
        "hub.select_study": "Choose a NASA investigation to summarize or interpret",
        "hub.summarize_objective": "Scientific objective",
        "hub.summarize_coverage": "Archive coverage",
        "hub.summarize_roles": "Documented evidence roles",
        "hub.summarize_citations": "Verified NASA records",
        "hub.rank_intro": "Select a spacecraft fire-safety pillar to rank reading priority (0–100 index of relevance & local evidence coverage — never a fire-risk rating).",
        "hub.interpret_obs": "What verified NASA files contain",
        "hub.interpret_impl": "Spacecraft safety engineering relevance",
        "hub.interpret_limit": "Scientific boundary & caveat",

        # 5-Question Guided Journey Framework
        "journey.q_heading": "Structured Discovery Guide (5 Key Questions)",
        "journey.q_exploring": "What am I exploring?",
        "journey.q_why_matters": "Why does it matter?",
        "journey.q_evidence_shows": "What does the NASA evidence show?",
        "journey.q_conclusion": "What can I conclude?",
        "journey.q_limitations": "What are the limitations?",

        "j1.s1_q_exploring": "How removing upward buoyancy (~0g microgravity) changes flame shape, oxygen delivery, and smoke motion compared with Earth (1g).",
        "j1.s1_q_why": "Inside an orbiting spacecraft, crews cannot open windows or rely on rising hot air; invisible flame and smoke shifts change cabin fire behavior.",
        "j1.s1_q_evidence": "NASA ISS physics guides establish symmetrical spherical diffusion flames and lingering combustion gases without natural upward convection.",
        "j1.s1_q_conclude": "Fire behavior in space follows diffusion and cabin airflow rather than buoyancy, setting the foundation for orbital combustion tests.",
        "j1.s1_q_limits": "Conceptual 1g vs 0g comparison illustrates physical mechanisms — it does not predict ignition thresholds for specific hardware materials.",

        "j1.s2_q_exploring": "NASA's Flame Extinguishment Experiment (FLEX · PSI-69), which tested suspended n-heptane and methanol liquid droplets aboard the ISS.",
        "j1.s2_q_why": "Liquid fuels burn cleanly as ideal spheres in 0g, letting scientists measure oxygen extinction limits without convective distortion.",
        "j1.s2_q_evidence": "Archived NASA Researcher's Guide pages, PSI-69 CSV tables, and engineering requirements document orbital test configurations and droplet runs.",
        "j1.s2_q_conclude": "FLEX isolates spherical burning and transitions toward cool-flame regimes under varied O₂ and inert diluent concentrations.",
        "j1.s2_q_limits": "NASA catalogs a FLEX-2 requirements PDF under PSI-69 (cover says FLEX-2); isolated 1–5 mm droplets differ from cabin solid materials.",

        "j1.s3_q_exploring": "Quantitative PSI-69 FLEX relationships linking oxygen mole fraction (`O2 mol frac`) to droplet extinction diameter and raw logged variables.",
        "j1.s3_q_why": "Reading real experimental distributions shows which chamber oxygen/diluent mixtures NASA actually explored.",
        "j1.s3_q_evidence": "Plotted points directly display recorded PSI-69 CSV test rows alongside verbatim NASA citations and page/row locations.",
        "j1.s3_q_conclude": "Droplet extinction diameters cluster by fuel type and ambient oxygen concentration across documented orbital test runs.",
        "j1.s3_q_limits": "Column `'Burning rate; mm'` omits a time unit in the original NASA header and is displayed raw with explicit unit caution.",

        "j1.s4_q_exploring": "Key scientific takeaways and honest empirical boundaries from FLEX (PSI-69) before exploring full-cabin safety systems.",
        "j1.s4_q_why": "Good spaceflight science avoids over-claiming: distinguishing controlled droplet tests from multi-material spacecraft cabins prevents unsafe assumptions.",
        "j1.s4_q_evidence": "Verified FLEX CSV records and ISS Researcher's Guide passages trace cool flames, diluent effects, and explicit header warnings.",
        "j1.s4_q_conclude": "Oxygen fraction, inert diluent gas, and droplet size strongly shape microgravity extinction, while preserving original NASA caveats.",
        "j1.s4_q_limits": "Single-droplet microgravity experiments cannot replace material-flammability screening (`BASS-II`) or aerosol smoke testing (`SAME`).",

        "j2.s1_q_exploring": "Why closed spacecraft atmospheres, slow circulation fans, and absence of upward smoke plumes make orbital fire protection unique.",
        "j2.s1_q_why": "A crewed cabin cannot vent rapidly without depressurization; prevention, fast smoke alarms, and reliable suppression must work together.",
        "j2.s1_q_evidence": "NASA PSI organizes research across solid-fuel spread (`BASS`/`Saffire`), smoke aerosols (`SAME`), and droplet extinguishment (`FLEX`).",
        "j2.s1_q_conclude": "Effective spacecraft fire safety demands multi-layer coordination calibrated specifically to microgravity physics rather than Earth assumptions.",
        "j2.s1_q_limits": "Overview introduces the three safety pillars; quantitative inspection happens in Steps 2–3 using verified PSI records.",

        "j2.s2_q_exploring": "Which authentic NASA PSI investigations belong to Prevention, Detection, or Suppression in our verified archive.",
        "j2.s2_q_why": "Mapping each NASA campaign (`BASS-II`, `Saffire`, `SAME`, `FLEX`) prevents mixing incompatible test setups during analysis.",
        "j2.s2_q_evidence": "The original nine safety investigations and the newly integrated PSI-62, PSI-117 and PSI-159 studies are indexed with preserved DOIs and originals. Research metadata, simulations, experimental references and test conditions remain distinct evidence types.",
        "j2.s2_q_conclude": "Solid fabric/polymer airflow tests cover Prevention, aerosol particle sizing covers Detection, and droplet tests illuminate Suppression.",
        "j2.s2_q_limits": "Studies differ in test scale (glovebox droplets vs Cygnus cabin fabrics) and table evidence types (`condition` vs `reported_result`).",

        "j2.s3_q_exploring": "Direct NASA data & documents across Prevention (`BASS-II · PSI-25`), Detection (`SAME · PSI-102`), and cross-study compatibility.",
        "j2.s3_q_why": "Seeing actual O₂ vs CO₂ points and smoke-detector aerosol reports reveals how orbital data informs cabin thresholds.",
        "j2.s3_q_evidence": "BASS-II charts show O₂% vs CO₂% by solid material, and SAME p. 13 details optical/ionization smoke detector aerosol measurements.",
        "j2.s3_q_conclude": "Forced airflow sustains low-oxygen solid combustion (`BASS-II`) while 0g smoke particle sizing differs from 1g alarms (`SAME`).",
        "j2.s3_q_limits": "`PSI-25` and `PSI-69` measure fundamentally different fuels and geometries and must never be pooled into a single regression axis.",

        "j2.s4_q_exploring": "How empirical NASA PSI findings translate safely into spacecraft atmosphere, detector, and suppression research guidance.",
        "j2.s4_q_why": "Synthesizing verified takeaways equips researchers and students to ask sharper follow-up questions in Compare and Scientific Assistant.",
        "j2.s4_q_evidence": "Cross-pillar takeaways align directly with indexed `BASS-II`, `Saffire`, `SAME`, and `FLEX` records checked against SHA-256 provenance.",
        "j2.s4_q_conclude": "Ventilation limits, orbital aerosol sizing, and cool-flame extinction bounds emerge as interconnected microgravity fire-safety insights.",
        "j2.s4_q_limits": "These public PSI datasets provide research understanding and test transparency — never flight-hardware fire certification.",
    },
    "pt": {
        # App & Sidebar
        "view.evidence_nature": "Natureza da evidência: {kind}",
        "view.field_nature": "Classificação de origem por coluna",
        "view.source_basis": "Base da classificação",
        "view.simulation_notice": "Previsões numéricas não são medições experimentais. Mantenha simulações e séries experimentais de referência distintas; colunas não classificadas permanecem sem validação.",
        "view.incompatible_axes": "As séries têm grandezas/unidades diferentes ou não declaradas. Inspecione uma série por vez; não é gerada sobreposição em eixo comum nem interpolação.",
        "app.title": "Flame in Freefall",
        "app.subtitle": "NASA Space Apps 2026 · Explorador de Combustão em Microgravidade",
        "sidebar.language": "Idioma: EN | PT-BR",
        "sidebar.nav_label": "Navegação",
        "sidebar.readonly_badge": "Acervo Científico NASA Verificado · Demonstração Pública",
        "sidebar.local_badge": "Acervo Científico NASA Verificado · Edição Local",
        "sidebar.footer_note": "Arquivos originais NASA PSI preservados com verificação criptográfica. Ferramenta de descoberta científica — nunca constitui certificação de voo.",

        # Persistent Context Bar
        "topbar.where": "Onde você está",
        "topbar.home": "🏠 Início",
        "topbar.back": "← Voltar",

        # Navigation
        "nav.home": "Início / Visão Geral",
        "nav.investigations": "Investigações",
        "nav.explorer": "Explorador de Dados",
        "nav.compare": "Comparar",
        "nav.assistant": "Assistente Científico",
        "nav.visual_review": "Revisão Visual",
        "nav.sources": "Fontes e Metodologia",

        # Home / Overview
        "home.title": "Explore a Ciência do Fogo no Espaço",
        "home.subtitle": "Analise a combustão em microgravidade e a segurança contra incêndio em espaçonaves usando dados reais do repositório NASA PSI, gráficos e citações verificáveis.",
        "home.lead": (
            "Explore dados reais do repositório NASA Physical Sciences Informatics (PSI) obtidos na Estação Espacial Internacional (ISS) "
            "e em experimentos espaciais — projetado para jurados, estudantes, engenheiros e curiosos."
        ),
        "home.plain_intro": (
            "Dentro de uma espaçonave em órbita, astronautas e o ar da cabine permanecem em queda livre contínua — o empuxo desaparece, "
            "chamas tornam-se esféricas, a fumaça segue a ventilação da cabine e chamas frias podem persistir. O Flame in Freefall organiza estudos "
            "reais da NASA (PSI) para apoiar investigações transparentes de segurança contra incêndio espacial."
        ),
        "home.start_title": "Escolha Como Você Quer Explorar",
        "home.exp_a_badge": "Descoberta Guiada · 4 Passos (~3 min)",
        "home.exp_a_title": "Descobrir a Ciência",
        "home.exp_a_desc": (
            "Entenda por que a queda livre transforma chamas em esferas, conheça o estudo FLEX da NASA e interprete um gráfico orbital real."
        ),
        "home.exp_a_btn": "Descobrir a Ciência →",
        "home.exp_b_badge": "Segurança Espacial · 4 Passos (~3 min)",
        "home.exp_b_title": "Explorar Segurança contra Incêndio",
        "home.exp_b_desc": (
            "Investigue a proteção em naves nas três frentes: Prevenção (BASS-II, Saffire), Detecção (SAME) e Supressão (FLEX, ACME CFI-G)."
        ),
        "home.exp_b_btn": "Explorar Segurança contra Incêndio →",
        "home.exp_c_badge": "Bancada Direta de Pesquisa",
        "home.exp_c_title": "Investigar Dados da NASA",
        "home.exp_c_desc": (
            "Abra gráficos interativos, inspecione tabelas e PDFs originais da NASA com unidades preservadas, compare estudos ou consulte o assistente."
        ),
        "home.exp_c_btn_data": "Investigar Dados da NASA →",
        "home.exp_c_btn_assistant": "Consultar Assistente Científico Baseado em Evidências →",
        "home.exp_c_btn_studies": "Ver Todas as 12 Investigações NASA →",
        "home.compare_title": "Terra vs. Microgravidade: O Que Muda Sem o Empuxo?",
        "home.earth_title": "Na Terra (Gravidade 1g)",
        "home.earth_points": (
            "- **Chama em gota:** Os gases quentes sobem rapidamente por serem mais leves que o ar frio ao redor.\n"
            "- **Corrente natural:** O ar quente ascendente puxa oxigênio novo para a base da chama.\n"
            "- **Fumaça ascendente:** O empuxo leva a fumaça direto ao teto, onde ficam os detectores.\n"
            "- **Resfriamento contínuo:** A convecção natural dissipa o calor do material em combustão."
        ),
        "home.space_title": "Em Queda Livre Orbital (~0g Microgravidade)",
        "home.space_points": (
            "- **Chama esférica:** Sem direção ascendente, os gases aquecidos formam uma esfera simétrica ao redor do combustível.\n"
            "- **Difusão e ventilação:** O oxigênio chega ao fogo principalmente por difusão lenta ou pelos ventiladores da cabine.\n"
            "- **Fumaça em suspensão:** Partículas de fuligem crescem e derivam devagar com o fluxo de ar da nave.\n"
            "- **Chamas frias possíveis:** Certos combustíveis líquidos continuam reagindo abaixo da temperatura de chamas quentes."
        ),
        "home.glossary_title": "Termos Científicos Explicados de Forma Simples",
        "home.archive_title": "Acervo Real da NASA Carregado Neste Aplicativo",
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
            "divergentes (`psia`, `psig`, `mmHg`, `cm/s`, fração molar). O **PSI Flame Microgravity** reúne 12 investigações prioritárias em um painel transparente "
            "onde **condições de ensaio nunca se confundem com medições**, unidades são normalizadas de forma conservadora e cada resposta aponta para o arquivo NASA, página/linha e hash SHA-256."
        ),
        "home.metric_studies": "Estudos NASA PSI",
        "home.metric_docs": "Originais NASA",
        "home.metric_tables": "Tabelas Extraídas",
        "home.metric_chunks": "Segmentos Pesquisáveis",
        "home.metric_chunks_semantic": "Segmentos Pesquisáveis",
        "home.metric_chunks_lexical": "Segmentos Pesquisáveis",
        "home.chunk_caption_semantic": (
            "{chunks} passagens multilíngues pesquisáveis indexadas em {docs} documentos autênticos da NASA."
        ),
        "home.chunk_caption_lexical": (
            "{chunks} passagens e linhas de tabela verificadas indexadas localmente em {docs} documentos autênticos da NASA."
        ),
        "home.tech_diag_label": "Diagnóstico técnico do acervo e motor de busca (opcional)",
        "home.extraction_caption": "Estado do acervo: {processed} completos · {partial} parciais · {failed} com falha. Proveniência detalhada em Fontes e Metodologia.",
        "home.pillars_title": "Três Pilares da Segurança contra Incêndio Espacial no NASA PSI",
        "home.pillar_prevention": "Prevenção",
        "home.pillar_prevention_studies": "BASS · BASS-II · Saffire-I / II / III · PSI-62 (metadados UFGM)",
        "home.pillar_prevention_desc": "Como materiais sólidos de cabine entram em ignição, propagam chamas e são modelados sob fluxos de ar e níveis de O₂ em microgravidade.",
        "home.pillar_detection": "Detecção",
        "home.pillar_detection_studies": "SAME · SAME-R",
        "home.pillar_detection_desc": "Como o tamanho das partículas de fumaça e aerossóis se comporta sem empuxo para calibrar detectores espaciais.",
        "home.pillar_suppression": "Supressão",
        "home.pillar_suppression_studies": "FLEX · FLEX-2 · PSI-117 (CFD Chamas Frias) · PSI-159 (ACME CFI-G)",
        "home.pillar_suppression_desc": "Como gotas de combustível e chamas frias gasosas queimam, oscilam e se extinguem conforme variam O₂ e diluentes.",
        "home.pillar_coverage": "{imported} de {total} investigações prioritárias importadas",
        "home.warning_conditions": (
            "Aviso de Integridade Científica: Tabelas experimentais frequentemente descrevem condições de ensaio ou catálogos. "
            "Sozinhas, não demonstram velocidade de propagação, eficácia de supressão nem certificação de segurança."
        ),
        "home.no_docs": "Nenhum documento importado ainda. Consulte Fontes e Metodologia para verificar o estado do acervo.",

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
        "ast.mode_semantic": "Modo de busca: busca semântica multilíngue e textual híbrida (funciona offline)",
        "ast.mode_lexical": "Modo de busca: busca exata por palavras-chave NASA e tabelas com unidades físicas (offline)",
        "ast.llm_unconfigured_banner": (
            "**Modo Evidência Local Verificada:** As respostas exibem trechos exatos da NASA, linhas tipadas de tabela e rastreabilidade completa sem inventar conclusões."
        ),
        "ast.llm_configured_banner": (
            "**Síntese por IA com Verificação Disponível:** Quando ativado, o assistente seleciona passagens literais estritamente dos documentos NASA recuperados e valida cada citação em código."
        ),
        "ast.diag_title": "Diagnóstico técnico de busca e configuração de IA",
        "ast.chat_user_label": "Pergunta de pesquisa",
        "ast.chat_assistant_label": "Resposta fundamentada em evidências",
        "ast.synth_summary_heading": "RESUMO · Visão dos Estudos NASA Correspondentes",
        "ast.synth_interpret_heading": "INTERPRETAÇÃO · Contexto Científico e de Segurança Espacial",
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
        "ast.studies_filter": "Filtrar por investigação NASA (vazio = consulta todos os estudos indexados + guias)",
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
        "vis.vlm_unconfigured": "Revisor visual por IA opcional não configurado neste ambiente. A renderização local de páginas PDF funciona 100% offline.",
        "vis.vlm_consent": "Enviar explicitamente APENAS a imagem desta página ao provedor VLM configurado",
        "vis.vlm_consent_help": "A imagem sai do servidor apenas com consentimento explícito. O resultado permanece inferência não verificada.",
        "vis.vlm_btn": "Solicitar Candidato de Revisão Visual",

        # Sources & Methodology
        "src.title": "Fontes, Proveniência e Metodologia Científica",
        "src.lead": "Transparência total sobre origem dos dados NASA, normalização de unidades, busca híbrida, uso de IA e limitações conhecidas.",
        "src.sec1_title": "1. Origem e Proveniência dos Dados NASA PSI",
        "src.sec1_body": (
            "- **Fonte primária**: NASA Physical Sciences Informatics (PSI) Data Repository (`https://psi.nasa.gov/physci/repo/search?q=combustion`).\n"
            "- **Cobertura do acervo**: **{studies} investigações PSI** e guias oficiais NASA, somando **{files} arquivos de origem processados ({size} bytes)**. PSI-62 contém metadados de pesquisa, PSI-117 inclui simulações e referências experimentais e PSI-159 inclui documentação de voo e condições de ensaios.\n"
            "- **Integridade imutável**: Cada arquivo baixado preserva data UTC de acesso, endpoint permanente na API PSI, DOI confirmado e hash SHA-256. URLs S3 assinadas temporárias nunca são persistidas."
        ),
        "src.sec2_title": "2. Extração, Normalização de Unidades e Categorias",
        "src.sec2_body": (
            "- **Normalização conservadora com Pint**: Apenas unidades explicitamente documentadas são convertidas (`1 atm = 14,6959 psia`, `1 m/s = 100 cm/s`, `°C → K`, `% O₂ → fração molar`).\n"
            "- **Proteção de referência**: `psi` ou `mmHg` sem referência nunca viram `psia` absoluto por suposição; pressão manométrica (`psig`) exige referência independente.\n"
            "- **Separação rigorosa de categorias**: `condition` (condição de ensaio), `sample` (catálogo), `reported_result` (resultado reportado), `derived` (cálculo derivado, ex.: pO₂) `simulation` (previsões numéricas), `metadata` (contexto de pesquisa) e `document_context` permanecem distintos."
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

        # Sidebar Mode & Guided Navigation
        "sidebar.mode_label": "Nível de experiência",
        "sidebar.mode_guided": "Exploração Guiada (Padrão)",
        "sidebar.mode_advanced": "Pesquisa Avançada (Todos os Controles)",
        "sidebar.mode_help": (
            "A Exploração Guiada destaca explicações científicas claras e mantém filtros avançados, hashes "
            "e diagnósticos técnicos recolhidos. A Pesquisa Avançada exibe todas as ferramentas diretamente."
        ),
        "sidebar.exit_journey": "Sair da Jornada Guiada",
        "sidebar.return_journey": "← Voltar à Jornada Guiada (Passo {step} de {total})",
        "sidebar.journey_banner": (
            "Você abriu **{study_id}** a partir de uma Jornada Guiada. Explore tabelas e gráficos da NASA aqui "
            "e clique no botão acima quando quiser retomar o Passo {step}."
        ),

        # Beginner Glossary
        "glossary.microgravity_term": "Microgravidade (~0g)",
        "glossary.microgravity_def": (
            "Condição contínua de queda livre em órbita: a gravidade curva a trajetória da nave, mas ar e chamas flutuam juntos sem empuxo ascendente."
        ),
        "glossary.o2_term": "Fração Molar de Oxigênio (O₂ mol frac)",
        "glossary.o2_def": (
            "Proporção de moléculas na câmara de teste que são oxigênio. Como referência, `0.21` equivale a 21% de O₂ — próximo ao ar atmosférico terrestre."
        ),
        "glossary.drop_diam_term": "Diâmetro da Gota (mm)",
        "glossary.drop_diam_def": (
            "Largura de uma gota esférica de combustível líquido suspensa em câmara selada (tipicamente 1 a 5 mm) para medir queima e extinção."
        ),
        "glossary.psi_term": "Repositório NASA PSI",
        "glossary.psi_def": (
            "Banco público Physical Sciences Informatics da NASA com arquivos reais de experimentos realizados na ISS e em naves orbitais."
        ),

        # Guided Journeys Shared Controls
        "journey.badge_j1": "Jornada Guiada 1 · Entendendo o Fogo em Microgravidade",
        "journey.badge_j2": "Jornada Guiada 2 · Segurança contra Incêndio em Espaçonaves",
        "journey.step_indicator": "Passo {current} de {total}",
        "journey.back": "← Voltar",
        "journey.continue": "Continuar →",
        "journey.restart": "Reiniciar Jornada",
        "journey.exit": "Voltar ao Início",
        "journey.open_advanced": "Detalhes técnicos e proveniência deste passo",

        # Journey 1 — Understanding Fire in Microgravity
        "j1.s1_title": "1. Por Que o Fogo se Comporta Diferente em Microgravidade",
        "j1.s1_purpose": "Objetivo: Construir intuição física sobre gravidade, empuxo e combustão antes de abrir tabelas espaciais.",
        "j1.s1_explain": (
            "Na Terra, os gases quentes da chama se expandem e ficam menos densos que o ar frio ao redor, fazendo a **gravidade puxar o ar frio por baixo e empurrar o gás quente para cima**. "
            "Essa corrente ascendente alonga a chama em seu formato clássico de gota amarela.\n\n"
            "Em queda livre orbital, o ar frio e o gás quente têm o mesmo peso relativo na cabine — **o empuxo desaparece**. "
            "Em vez de subir, os produtos da combustão permanecem ao redor do combustível enquanto o oxigênio entra devagar por difusão ou ventilação, "
            "formando uma **chama esférica azulada** e discreta."
        ),
        "j1.s1_callout_title": "Comparação Interativa: Escolha um Efeito Físico (1g vs. 0g)",
        "j1.s1_aspect_label": "Selecione qual aspecto do fogo deseja comparar:",
        "j1.s1_aspect_shape": "Formato da Chama (Gota vs. Esfera)",
        "j1.s1_aspect_o2": "Como o Oxigênio Chega ao Fogo",
        "j1.s1_aspect_temp": "Chamas Quentes vs. Chamas Frias",
        "j1.s1_aspect_smoke": "Comportamento da Fumaça e Fuligem",
        "j1.s1_desc_shape": (
            "**Na Terra (`1g`):** O empuxo estica os gases aquecidos para cima formando uma chama em gota.\n\n"
            "**Em Órbita (`~0g`):** Sem 'em cima' nem 'embaixo' para o ar quente subir, a difusão simétrica molda uma **chama esférica**."
        ),
        "j1.s1_desc_o2": (
            "**Na Terra (`1g`):** Plumas ascendentes renovam o oxigênio continuamente na base da chama.\n\n"
            "**Em Órbita (`~0g`):** O oxigênio chega devagar por difusão molecular — ou pela ventilação da cabine — alterando o tempo de queima e a extinção."
        ),
        "j1.s1_desc_temp": (
            "**Em Órbita (`~0g`):** Como calor e vapores de combustível permanecem ao redor da gota sem escapar por convecção, os experimentos FLEX da NASA registraram transições para **chamas frias** de baixa temperatura após o apagamento da chama visível."
        ),
        "j1.s1_desc_smoke": (
            "**Na Terra (`1g`):** O empuxo leva a fumaça rapidamente até detectores no teto.\n\n"
            "**Em Órbita (`~0g`):** Sem convecção ascendente, partículas de fuligem permanecem suspensas, crescem por aglomeração e seguem o fluxo de ventilação."
        ),

        # Journey 1 Step 2
        "j1.s2_title": "2. Conheça o Experimento NASA FLEX (PSI-69)",
        "j1.s2_purpose": "Objetivo: Ver o que os astronautas realmente testaram na ISS e observar uma página original do guia NASA.",
        "j1.s2_explain": (
            "Dentro da Microgravity Science Glovebox da Estação Espacial Internacional, o **Flame Extinguishment Experiment (FLEX · PSI-69)** "
            "investigou como pequenas gotas suspensas de combustíveis líquidos — como **n-heptano** e **metanol** (tipicamente **1 a 5 mm** de diâmetro) — entram em ignição, formam chamas esféricas e se extinguem "
            "quando variam a fração de oxigênio (`O2 mol frac`) e gases inertes (`N2`, `He`, `CO2`, `Xe`).\n\n"
            "Veja abaixo como o estudo é documentado no arquivo original da NASA antes de analisarmos seus dados:"
        ),
        "j1.s2_pdf_caption": "Prévia real do PDF NASA PSI-69 (`researchers_guide.pdf`, página original {page})",
        "j1.s2_pdf_unavailable": "Prévia em imagem da página PDF indisponível neste ambiente; o texto extraído e o SHA-256 seguem preservados.",
        "j1.s2_btn_explorer": "Abrir PSI-69 no Explorador Completo →",

        # Journey 1 Step 3
        "j1.s3_title": "3. Inspecionar e Interpretar Evidências Reais da NASA",
        "j1.s3_purpose": "Objetivo: Ler um gráfico real do estudo PSI-69 e trechos verificados da NASA com guia explicativo.",
        "j1.s3_explain": (
            "Abaixo estão dados quantitativos reais extraídos diretamente do arquivo CSV do estudo **PSI-69 (FLEX)**. "
            "Escolha uma visualização para distinguir condições testadas pela NASA de valores que exigem ressalva de unidade."
        ),
        "j1.s3_view_label": "Escolha uma visão real dos dados PSI-69:",
        "j1.s3_opt_extinction": "Atmosfera Testada: Concentração de Oxigênio (O₂) vs. Diâmetro da Gota (mm)",
        "j1.s3_opt_burning": "Verificação de Valor Bruto: Concentração de Oxigênio (O₂) vs. 'Burning rate; mm' (Com Ressalva de Unidade)",
        "j1.s3_evidence_title": "Trechos Verificados da NASA Recuperados para o PSI-69",
        "j1.s3_chart_missing": "A tabela numérica interativa do PSI-69 não está carregada nesta amostra; os trechos documentais verificados seguem abaixo.",

        # Journey 1 Step 4
        "j1.s4_title": "4. Descobertas Científicas, Proveniência e Limitações",
        "j1.s4_purpose": "Objetivo: Sintetizar o que o conjunto PSI-69 comprova de fato e onde começam os limites da evidência.",
        "j1.s4_learned_title": "O Que as Evidências Verificadas da NASA Mostram",
        "j1.s4_learned_body": (
            "- **Chamas esféricas respondem diretamente ao nível de oxigênio e diluentes:** As tabelas do PSI-69 documentam frações molares de O₂ (`O2 mol frac`), pressões e diâmetros iniciais de gota em corridas orbitais reais.\n"
            "- **Dinâmica de duas etapas e chamas frias:** Documentos do FLEX registram regimes de chama fria persistentes após a extinção visual.\n"
            "- **Anomalias documentais preservadas com transparência:** Nossa auditoria mantém o aviso real da capa (`FLEX-2` dentro do pacote PSI-69) e sinaliza colunas como `Burning rate; mm` sem adivinhar unidades ausentes."
        ),
        "j1.s4_limits_title": "O Que Este Experimento NÃO Comprova Sozinho",
        "j1.s4_limits_body": (
            "- **Gotas isoladas de 1–5 mm** em câmara fechada **não** equivalem a incêndios reais em cabos, espumas ou tecidos de cabine.\n"
            "- Linhas com composições de câmara (`O2 mol frac`, `N2`, pressão) documentam **condições de ensaio**, não certificação de extinção operacional.\n"
            "- Tabelas de gotas (`PSI-69`) não podem ser somadas diretamente com propagação em sólidos (`PSI-25 · BASS-II`) sem verificar geometria e unidades."
        ),
        "j1.s4_next_title": "Próximos Passos Recomendados",
        "j1.s4_btn_j2": "Ir para Jornada 2: Segurança contra Incêndio Espacial →",
        "j1.s4_btn_assistant": "Perguntar ao Assistente sobre o FLEX →",
        "j1.s4_btn_explorer": "Abrir PSI-69 no Explorador de Dados →",

        # Journey 2 — Fire Safety in Spacecraft
        "j2.s1_title": "1. Por Que Incêndios São um Risco Único em Espaçonaves",
        "j2.s1_purpose": "Objetivo: Compreender por que a exploração orbital altera ignição, detecção de fumaça e combate ao fogo.",
        "j2.s1_explain": (
            "Em uma nave espacial, a tripulação não pode evacuar para o exterior nem abrir janelas sem risco de despressurização. "
            "Ventiladores contínuos circulam o ar por cabos, baterias e painéis — fazendo o fogo seguir dinâmicas muito diferentes das de um ambiente na Terra.\n\n"
            "As investigações de combustão do acervo NASA PSI atacam três questões críticas de engenharia:"
        ),
        "j2.s1_risk_cards": (
            "- **Ignição e Propagação em Materiais:** Futuras missões profundas podem operar com **maior fração de oxigênio e menor pressão** — exigindo dados reais de como polímeros e tecidos queimam sob ventilação lenta.\n"
            "- **Fumaça Sem Empuxo e Alarmes Tardios:** Sem correntes ascendentes até o teto, aerossóis de fumaça coalescem de maneira diferente em microgravidade, exigindo sensores calibrados para partículas espaciais reais.\n"
            "- **Limites de Extinção:** Supressão por diluentes ou redução de oxigênio se comporta de outro modo quando o empuxo desaparece e podem surgir **chamas frias**."
        ),

        # Journey 2 Step 2
        "j2.s2_title": "2. Prevenção, Detecção e Supressão no Acervo NASA PSI",
        "j2.s2_purpose": "Objetivo: Selecionar um pilar de segurança para ver quais estudos autênticos da NASA o investigam.",
        "j2.s2_pillar_select": "Escolha uma camada de defesa contra incêndio espacial:",
        "j2.s2_pillar_prevention_detail": (
            "**Estudos no acervo:** `BASS (PSI-26)`, `BASS-II (PSI-25)`, `Saffire-I (PSI-98)`, `Saffire-II (PSI-99)`, `Saffire-III (PSI-100)`, `Modelagem UFGM (PSI-62 · apenas metadados)`\n\n"
            "**Foco de segurança:** Medir e modelar como **combustíveis sólidos** (polímeros, compósitos de algodão/fibra, amostras tipo fio) entram em ignição e propagam chamas sob diferentes velocidades de ar e níveis de O₂."
        ),
        "j2.s2_pillar_detection_detail": (
            "**Estudos no acervo:** `SAME (PSI-102)`, `SAME-R (PSI-101)`\n\n"
            "**Foco de segurança:** Caracterizar a **distribuição de tamanho de partículas de fumaça e aerossóis** gerados por materiais espaciais superaquecidos em microgravidade para calibrar detectores sem falsos alarmes ou falhas."
        ),
        "j2.s2_pillar_suppression_detail": (
            "**Estudos no acervo:** `FLEX (PSI-69)`, `FLEX-2 (PSI-68)`, `CFD Chamas Frias (PSI-117 · simulações + séries de referência)`, `ACME CFI-G (PSI-159)`\n\n"
            "**Foco de segurança:** Determinar **limites de extinção**, efeito de gases inertes, concentração mínima de oxigênio, tempo de vida de gotas e regimes de chama fria."
        ),
        "j2.s2_loaded_studies": "Investigações NASA carregadas neste pilar ({count}):",

        # Journey 2 Step 3
        "j2.s3_title": "3. Examinar Evidências Reais de Segurança Espacial",
        "j2.s3_purpose": "Objetivo: Inspecionar gráficos, PDFs e trechos reais de Prevenção (BASS-II), Detecção (SAME) e Supressão (FLEX).",
        "j2.s3_focus_label": "Selecione uma evidência real para examinar:",
        "j2.s3_focus_bass": "Prevenção · BASS-II (PSI-25) Dados de Chama em Combustível Sólido",
        "j2.s3_focus_same": "Detecção · SAME (PSI-102) Relatório de Fumaça em Microgravidade",
        "j2.s3_focus_compare": "Checagem entre Pilares · Por Que BASS-II (Prevenção) e FLEX (Supressão) Não Podem Ser Misturados",
        "j2.s3_same_pdf_caption": "Prévia real do PDF NASA PSI-102 (Relatório final `SAME`, página {page})",
        "j2.s3_compare_callout": (
            "**Controle de Integridade Científica:** Embora `PSI-25 (BASS-II)` e `PSI-69 (FLEX)` investiguem segurança contra incêndio no espaço, "
            "um mede **materiais sólidos sob fluxo de ar forçado** e o outro mede **gotas líquidas isoladas** em atmosfera parada. "
            "Comparar lições científicas entre eles é útil — misturar seus números brutos no mesmo eixo seria metodologicamente errado."
        ),

        # Journey 2 Step 4
        "j2.s4_title": "4. Como Esses Achados Orientam a Engenharia de Segurança",
        "j2.s4_purpose": "Objetivo: Traduzir observações experimentais em sínteses de engenharia rigorosamente delimitadas pelos dados.",
        "j2.s4_findings_title": "Implicações Científicas Fundamentadas Neste Acervo",
        "j2.s4_findings_body": (
            "- **Ventilação e Atmosfera de Cabine (Prevenção · BASS-II / Saffire):** Limites de inflamabilidade dependem **tanto da fração de oxigênio quanto da velocidade do fluxo de ar** — ventiladores de baixa velocidade podem sustentar combustão em sólidos.\n"
            "- **Calibração de Detectores de Fumaça (Detecção · SAME):** A combustão em microgravidade gera **perfis de tamanho de partículas distintos** dos ensaios na Terra; detectores orbitais precisam considerar a física de aerossóis sem empuxo.\n"
            "- **Supressão e Risco de Re-ignição (Supressão · FLEX):** Ensaios de gotas indicam que o apagamento visível pode deixar **química de chama fria** ou calor residual capaz de reacender se o O₂ subir."
        ),
        "j2.s4_caveats_title": "Fronteiras Reais de Escopo e Limitações",
        "j2.s4_caveats_body": (
            "- Os conjuntos PSI sustentam **compreensão científica e validação de hipóteses**, **não substituem certificação de voo de hardware**.\n"
            "- Pacotes públicos da NASA variam em completude (`processed` vs. `partial` quando há arquivos auxiliares em formatos binários especializados).\n"
            "- Toda afirmação exibida neste aplicativo pode ser rastreada até o arquivo fonte exato, página/linha e hash SHA-256."
        ),
        "j2.s4_next_title": "Continuar Explorando nas Ferramentas Completas",
        "j2.s4_btn_compare": "Abrir Comparador de Estudos →",
        "j2.s4_btn_assistant": "Consultar Assistente Sobre Segurança Espacial →",
        "j2.s4_btn_explorer": "Inspecionar BASS-II (PSI-25) no Explorador →",

        # Chart Explanations
        "chart_guide.title": "Como Ler Este Gráfico",
        "chart_guide.shows_label": "O que mostra:",
        "chart_guide.axes_label": "Eixos e unidades:",
        "chart_guide.source_label": "Fonte NASA e natureza dos dados:",
        "chart_guide.interpret_label": "Como interpretar:",
        "chart_guide.caution_label": "Ressalva importante:",
        "chart_guide.term_help_title": "Glossário de variáveis e unidades desta visualização",
        "chart_guide.role_measurement": "Observações experimentais / medições diretas",
        "chart_guide.role_condition": "Condições de ensaio / parâmetros configurados na câmara",
        "chart_guide.role_mixed": "Tabela mista (parâmetros de ensaio e variáveis observadas)",
        "chart_guide.note_condition_only": (
            "Os pontos mostram principalmente quais combinações de teste a NASA executou, e não uma curva física isolada de causa e efeito."
        ),
        "chart_guide.note_trend": (
            "Leia da esquerda para a direita ao longo de `{x}` e observe como `{y}` sobe, cai ou se dispersa entre os ensaios registrados da NASA."
        ),
        "chart_guide.caution_default": (
            "Aplica-se estritamente ao aparato, combustível e linhas documentadas em {study_id}; evite extrapolar diretamente para toda uma cabine espacial."
        ),
        "chart_guide.caution_burning_mm": (
            "O cabeçalho original `'Burning rate; mm'` informa `'mm'` sem unidade de tempo (`'/s'`); verifique a definição no PDF NASA antes de citar velocidade de queima."
        ),
        "chart_guide.caution_series_mode": "Ajuste derivado ativo no gráfico: `{mode}` (os dados originais seguem intactos na tabela).",
        "chart_guide.explorer_controls_label": "Personalizar eixos, filtros ou transformações (Controles Avançados)",
        "chart_guide.heatmap_shows": "Matriz de correlação de Spearman entre colunas numéricas de `{dataset}`.",
        "chart_guide.heatmap_caution": "Correlação mostra variação conjunta nestas linhas — nunca comprova causalidade física isoladamente.",

        # Assistant Plain-Language Guide
        "ast_guide.filters_expander": "Filtros avançados, seleção de estudos e diagnóstico do índice",
        "ast_guide.examples_hint": "Clique em uma pergunta introdutória (executa automaticamente):",
        "ast_guide.summary_title": "Guia em Linguagem Simples Sobre Estes Resultados",
        "ast_guide.summary_counts": "Foram encontrados **{matches}** trecho(s) ou linha(s) verificados em **{studies}** investigação(ões) NASA: {study_list}.",
        "ast_guide.summary_how": (
            "Como validar cada cartão abaixo: confira o **rótulo de evidência** (`Medição`, `Condição de Ensaio` ou `Contexto`) "
            "antes de citar valores e use **Ver fonte exata** para inspecionar arquivo, página/linha e hash SHA-256."
        ),
        "ast_guide.summary_no_llm": (
            "Executando em **Modo Evidência Local Verificada** (sem síntese especulativa): os cartões abaixo exibem registros originais literais da NASA."
        ),
        "ast_guide.summary_caveat_prefix": "Principal limite científico entre os estudos encontrados: ",

        # Data Explorer visual-first preview & Challenge Hub
        "view.overview_preview_title": "Visão Visual Inicial · Prévia dos Dados Experimentais",
        "view.overview_preview_caption": "Principais variáveis plotadas antes das estatísticas em tabela; use Gráficos Interativos para ajustar eixos ou curvas.",
        "hub.title": "Hub Space Apps Challenge 2026 · RESUMIR · RANQUEAR · INTERPRETAR",
        "hub.subtitle": "Inspecione qualquer investigação da NASA pelos três pilares do desafio — sempre ancorado nos arquivos originais e em ressalvas transparentes.",
        "hub.tab_summarize": "1. RESUMIR Estudo",
        "hub.tab_rank": "2. RANQUEAR Prioridade",
        "hub.tab_interpret": "3. INTERPRETAR Segurança",
        "hub.select_study": "Escolha uma investigação NASA para resumir ou interpretar",
        "hub.summarize_objective": "Objetivo científico",
        "hub.summarize_coverage": "Cobertura do acervo",
        "hub.summarize_roles": "Papéis de evidência documentados",
        "hub.summarize_citations": "Registros NASA verificados",
        "hub.rank_intro": "Escolha um pilar de segurança contra incêndio espacial para ordenar a prioridade de leitura (índice de 0–100 de relevância e acervo local — nunca ranking de risco).",
        "hub.interpret_obs": "O que os arquivos verificados da NASA contêm",
        "hub.interpret_impl": "Relevância para engenharia de segurança espacial",
        "hub.interpret_limit": "Fronteira científica e ressalva",

        # 5-Question Guided Journey Framework
        "journey.q_heading": "Guia Estruturado de Descoberta (5 Perguntas-Chave)",
        "journey.q_exploring": "O que estou explorando?",
        "journey.q_why_matters": "Por que isso importa?",
        "journey.q_evidence_shows": "O que a evidência NASA mostra?",
        "journey.q_conclusion": "O que posso concluir?",
        "journey.q_limitations": "Quais são as limitações?",

        "j1.s1_q_exploring": "Como remover o empuxo ascendente (~0g em microgravidade) transforma formato da chama, chegada de oxigênio e movimento da fumaça em comparação com a Terra (1g).",
        "j1.s1_q_why": "Em uma nave orbital, astronautas não podem abrir janelas nem contar com o ar quente subindo; mudanças invisíveis no fogo e na fumaça alteram o risco na cabine.",
        "j1.s1_q_evidence": "Guias físicos da NASA na ISS demonstram chamas esféricas simétricas por difusão e retenção de gases quentes sem convecção natural.",
        "j1.s1_q_conclude": "O fogo no espaço obedece à difusão e à ventilação da cabine em vez de empuxo, criando a base para todos os ensaios orbitais.",
        "j1.s1_q_limits": "Comparar 1g vs 0g ilustra mecanismos físicos fundamentais — não determina limiares exatos de ignição para materiais específicos.",

        "j1.s2_q_exploring": "O experimento Flame Extinguishment Experiment (FLEX · PSI-69), que testou gotas líquidas suspensas de n-heptano e metanol a bordo da ISS.",
        "j1.s2_q_why": "Combustíveis líquidos formam esferas ideais em 0g, permitindo medir limiares de extinção por oxigênio sem distorção convectiva.",
        "j1.s2_q_evidence": "Páginas do Researcher's Guide, tabelas CSV do PSI-69 e requisitos de engenharia preservados documentam ensaios orbitais de gotas.",
        "j1.s2_q_conclude": "O FLEX isola a combustão esférica e revela transições para regimes de chama fria sob variações de O₂ e diluentes inertes.",
        "j1.s2_q_limits": "A NASA associa um PDF de requisitos do FLEX-2 sob PSI-69 (capa indica FLEX-2); gotas isoladas de 1–5 mm diferem de materiais sólidos de cabine.",

        "j1.s3_q_exploring": "Relações quantitativas reais do PSI-69 FLEX ligando fração molar de oxigênio (`O2 mol frac`) ao diâmetro de extinção e variáveis registradas.",
        "j1.s3_q_why": "Ler distribuições experimentais autênticas mostra exatamente quais combinações de oxigênio e diluentes a NASA investigou.",
        "j1.s3_q_evidence": "Os pontos plotados exibem diretamente linhas do CSV PSI-69 acompanhadas de citações literais NASA e localizações página/linha.",
        "j1.s3_q_conclude": "Diâmetros de extinção agrupam-se por combustível e concentração ambiente de oxigênio ao longo dos ensaios orbitais registrados.",
        "j1.s3_q_limits": "A coluna `'Burning rate; mm'` omite unidade de tempo no cabeçalho original da NASA e aparece bruta com ressalva explícita.",

        "j1.s4_q_exploring": "Lições científicas principais e limites empíricos honestos do FLEX (PSI-69) antes de investigar sistemas de segurança de cabine.",
        "j1.s4_q_why": "Boa ciência espacial evita exageros: separar ensaios controlados de gotas de incêndios em múltiplos materiais evita suposições inseguras.",
        "j1.s4_q_evidence": "Registros CSV verificados do FLEX e passagens do Guia da ISS rastreiam chamas frias, efeito de diluentes e alertas explícitos de cabeçalho.",
        "j1.s4_q_conclude": "Fração de oxigênio, gás inerte e tamanho da gota governam a extinção em microgravidade, preservando todas as ressalvas NASA.",
        "j1.s4_q_limits": "Gotas isoladas não substituem triagem de inflamabilidade de sólidos (`BASS-II`) nem ensaios de aerossol de fumaça (`SAME`).",

        "j2.s1_q_exploring": "Por que atmosferas fechadas de naves, ventiladores suaves e ausência de plumas ascendentes tornam o combate a incêndio espacial único.",
        "j2.s1_q_why": "Uma cabine tripulada não pode ser ventilada para o exterior sem despressurizar; prevenção, alarme precoce e supressão precisam atuar juntas.",
        "j2.s1_q_evidence": "O acervo NASA PSI organiza estudos em propagação em sólidos (`BASS`/`Saffire`), aerossóis de fumaça (`SAME`) e extinção de gotas (`FLEX`).",
        "j2.s1_q_conclude": "A segurança espacial requer defesa em múltiplas camadas calibradas para a física da microgravidade, não para suposições terrestres.",
        "j2.s1_q_limits": "Esta etapa apresenta os três pilares; a inspeção quantitativa com registros PSI ocorre nos Passos 2 e 3.",

        "j2.s2_q_exploring": "Quais investigações autênticas NASA PSI pertencem a Prevenção, Detecção ou Supressão em nosso acervo verificado.",
        "j2.s2_q_why": "Mapear cada campanha NASA (`BASS-II`, `Saffire`, `SAME`, `FLEX`) impede misturar configurações experimentais incompatíveis.",
        "j2.s2_q_evidence": "As nove investigações originais de segurança e os estudos PSI-62, PSI-117 e PSI-159 recém-integrados estão indexados com DOIs e originais preservados. Metadados de pesquisa, simulações, referências experimentais e condições de ensaio permanecem distintos.",
        "j2.s2_q_conclude": "Ensaios com tecidos/polímeros atendem Prevenção, partículas de aerossol atendem Detecção e ensaios com gotas fundamentam Supressão.",
        "j2.s2_q_limits": "As campanhas diferem em escala (gotas na glovebox vs tecidos no Cygnus) e natureza tabular (`condition` vs `reported_result`).",

        "j2.s3_q_exploring": "Dados e documentos NASA em Prevenção (`BASS-II · PSI-25`), Detecção (`SAME · PSI-102`) e checagem de compatibilidade entre pilares.",
        "j2.s3_q_why": "Visualizar pontos reais de O₂ vs CO₂ e relatórios de detectores de fumaça mostra como dados orbitais orientam limites operacionais.",
        "j2.s3_q_evidence": "Gráficos do BASS-II relacionam O₂% vs CO₂% por material sólido, enquanto SAME p. 13 detalha medições de partículas em detectores.",
        "j2.s3_q_conclude": "Escoamento forçado sustenta queima de sólidos em baixo oxigênio (`BASS-II`) e partículas em 0g diferem de alarmes em 1g (`SAME`).",
        "j2.s3_q_limits": "`PSI-25` e `PSI-69` medem combustíveis e geometrias diferentes e nunca devem ser fundidos em um único eixo quantitativo.",

        "j2.s4_q_exploring": "Como achados empíricos NASA PSI apoiam decisões sobre atmosfera, detecção precoce e pesquisa de supressão sem ultrapassar os dados.",
        "j2.s4_q_why": "Sintetizar resultados verificados prepara pesquisadores e estudantes para consultas aprofundadas em Comparar e Assistente Científico.",
        "j2.s4_q_evidence": "As implicações alinham-se diretamente aos acervos `BASS-II`, `Saffire`, `SAME` e `FLEX` auditados por hash criptográfico.",
        "j2.s4_q_conclude": "Limites de ventilação, distribuição orbital de aerossóis e regimes de chama fria compõem uma visão integrada de segurança.",
        "j2.s4_q_limits": "Esses acervos públicos PSI oferecem transparência e entendimento científico — nunca substituem certificação de hardware de voo.",
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
        "simulation": "Numerical simulation (not a measurement)",
        "metadata": "Research metadata / bibliographic context",
        "identifier_or_unclassified": "Identifier or unclassified source field",
        "mixed_experiment_and_simulation": "Experimental references & numerical simulations (distinct series)",
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
        "simulation": "Simulação numérica (não é medição)",
        "metadata": "Metadados de pesquisa / contexto bibliográfico",
        "identifier_or_unclassified": "Identificador ou campo de origem não classificado",
        "mixed_experiment_and_simulation": "Referências experimentais e simulações numéricas (séries distintas)",
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
