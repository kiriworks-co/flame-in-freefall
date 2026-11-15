"""Global NASA catalog, evidence retrieval, assistant, comparison, and methodology views."""
from __future__ import annotations

import json
import os
import re
import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from . import storage, views
from .assistant import answer, llm_configured
from .comparison import compare_tables
from .extractors import render_pdf_page
from .i18n import (
    SECTION_KEYS,
    evidence_label,
    get_lang,
    investigation_profile,
    normalize_section,
    status_label,
    t,
    translate_comparison_reason,
    translate_relevance_reason,
    translate_retrieval_warning,
)
from .pipeline import is_public_readonly
from .relevance import rank_investigations
from .retrieval import safe_source_url
from .storage import PROJECT_DIR

ROOT = Path(__file__).resolve().parents[1]
SECTIONS = SECTION_KEYS
EVIDENCE_LABELS = {
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
}

_PILLAR_KEY_MAP = {
    "Prevenção": "Prevention",
    "Detecção": "Detection",
    "Supressão": "Suppression",
    "Prevention": "Prevention",
    "Detection": "Detection",
    "Suppression": "Suppression",
    "Context": "Context",
    "Contexto": "Context",
}


def _json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _study(experiment: dict) -> str:
    return str(experiment.get("psi_id") or experiment.get("study_id") or experiment.get("investigation_id") or experiment["id"])


def _safe_url(url: Any) -> str | None:
    return safe_source_url(url) or None


def _doi_url(value: Any) -> str | None:
    doi = str(value or "").removeprefix("https://doi.org/")
    return f"https://doi.org/{doi}" if re.fullmatch(r"10\.\d{4,9}/[^\s<>]+", doi) else None


def _document_notices(study_id: str, document: dict, lang: str | None = None) -> list[str]:
    active = (lang or get_lang()).lower()
    is_pt = active.startswith("pt")
    provenance = document.get("provenance") or document
    notices = []
    if provenance.get("classification_note"):
        notices.append(str(provenance["classification_note"]))
    for field in provenance.get("field_classification", []):
        if field.get("warning"):
            notices.append(f"{field.get('header', 'Field')}: {field['warning']}")
    filename = document.get("name") or document.get("filename", "")
    if study_id == "PSI-69" and "FLEX Engineering Requirements Document" in filename:
        if is_pt:
            notices.append(
                "O catálogo NASA associa este PDF a PSI-69, mas a capa identifica FLEX-2. "
                "A associação de catálogo não demonstra que os requisitos se aplicam ao FLEX original."
            )
        else:
            notices.append(
                "NASA catalog links this PDF under PSI-69, while the cover identifies FLEX-2. "
                "Catalog association does not prove requirements apply to original FLEX."
            )
    return list(dict.fromkeys(notices))


@st.cache_resource(show_spinner=False)
def _retrieval_index(model_path: str):
    """Reuse local model weights between Streamlit reruns, without caching results."""
    from .retrieval import RetrievalIndex

    return RetrievalIndex()


def _indexed_chunk_count() -> int:
    search_db = PROJECT_DIR / "data" / "search.sqlite3"
    if not search_db.exists():
        return 0
    try:
        with sqlite3.connect(search_db) as conn:
            row = conn.execute("SELECT count(*) FROM chunks").fetchone()
        return int(row[0]) if row else 0
    except sqlite3.Error:
        return 0


def catalog(experiments: list[dict]) -> list[dict]:
    entries = _json(ROOT / "resources/manifests/priority_investigations.json", {}).get("investigations", [])
    by_id = {_study(exp): exp for exp in experiments}
    result = []
    for entry in entries:
        exp = by_id.get(entry["id"])
        downloaded = _json(ROOT / "data/psi_downloads" / entry["id"] / "source_manifest.json", {})
        result.append({
            **entry,
            "experiment": exp,
            "download_manifest": downloaded,
            "documents": exp.get("documents", []) if exp else [],
            "document_count": len(exp.get("documents", [])) if exp else 0,
        })
    return result


def _open_experiment(identifier: str) -> None:
    st.session_state["active_experiment_id"] = identifier
    st.session_state["workspace_section"] = "explorer"


def _jump_section(section_key: str, **updates: Any) -> None:
    st.session_state["workspace_section"] = normalize_section(section_key)
    for k, v in updates.items():
        st.session_state[k] = v


def _source_link(label: str, url: Any) -> None:
    safe = _safe_url(url)
    if safe:
        st.link_button(label, safe)


def _study_id_for(experiments: list[dict], psi_id: str) -> str:
    for exp in experiments:
        if _study(exp) == psi_id:
            return str(exp["id"])
    return str(experiments[0]["id"]) if experiments else ""


# ----------------------------------------------------------------------------- Home / Overview


def show_overview(experiments: list[dict]) -> None:
    lang = get_lang()
    st.title(t("home.title", lang))
    st.markdown(f"<p class='psi-lead'>{t('home.lead', lang)}</p>", unsafe_allow_html=True)

    records = catalog(experiments)
    documents = [doc for exp in experiments for doc in exp.get("documents", [])]
    flex_id = _study_id_for(experiments, "PSI-69")
    bass2_id = _study_id_for(experiments, "PSI-25")

    if flex_id:
        st.button(
            t("home.start_cta", lang),
            type="primary",
            key="home-start-cta",
            on_click=_open_experiment,
            args=(flex_id,),
        )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(t("home.metric_studies", lang), sum(bool(row["experiment"]) for row in records))
    m2.metric(t("home.metric_docs", lang), len(documents))
    m3.metric(t("home.metric_tables", lang), sum(doc.get("table_count", 0) for doc in documents))
    m4.metric(t("home.metric_chunks", lang), _indexed_chunk_count())

    failures = sum(doc.get("status") == "erro" for doc in documents)
    partial = sum(doc.get("status") == "parcial" for doc in documents)
    st.caption(
        t(
            "home.extraction_caption",
            lang,
            processed=len(documents) - failures - partial,
            partial=partial,
            failed=failures,
        )
    )

    col_left, col_right = st.columns(2)
    with col_left:
        with st.container(border=True):
            st.subheader(t("home.what_title", lang))
            st.markdown(t("home.what_body", lang))
    with col_right:
        with st.container(border=True):
            st.subheader(t("home.problem_title", lang))
            st.markdown(t("home.problem_body", lang))

    st.header(t("home.pillars_title", lang))
    pillars = [
        ("Prevention", "home.pillar_prevention", "home.pillar_prevention_studies", "home.pillar_prevention_desc"),
        ("Detection", "home.pillar_detection", "home.pillar_detection_studies", "home.pillar_detection_desc"),
        ("Suppression", "home.pillar_suppression", "home.pillar_suppression_studies", "home.pillar_suppression_desc"),
    ]
    p_cols = st.columns(3)
    for idx, (pillar_key, title_k, studies_k, desc_k) in enumerate(pillars):
        covered = [
            r for r in records if _PILLAR_KEY_MAP.get(investigation_profile(r["id"], "en").get("pillar", ""), "") == pillar_key
            or pillar_key.casefold() in r.get("category", "").casefold()
        ]
        pillar_label = t(title_k, lang)
        with p_cols[idx]:
            with st.container(border=True):
                st.subheader(pillar_label)
                st.caption(t(studies_k, lang))
                st.write(t(desc_k, lang))
                st.caption(t("home.pillar_coverage", lang, imported=sum(bool(r["experiment"]) for r in covered), total=len(covered)))
                st.button(
                    t("home.explore_pillar_btn", lang, pillar=pillar_label),
                    key=f"home-pillar-{pillar_key}",
                    use_container_width=True,
                    on_click=_jump_section,
                    args=("investigations",),
                    kwargs={"inv_pillar_filter": pillar_key},
                )

    st.header(t("home.tour_title", lang))
    st.write(t("home.tour_subtitle", lang))
    t_cols = st.columns(2)
    tour_steps = [
        ("tour-1", "home.tour_s1_title", "home.tour_s1_desc", "home.tour_s1_btn", "investigations", {"inv_pillar_filter": "All"}),
        ("tour-2", "home.tour_s2_title", "home.tour_s2_desc", "home.tour_s2_btn", "explorer", {"active_experiment_id": flex_id}),
        ("tour-3", "home.tour_s3_title", "home.tour_s3_desc", "home.tour_s3_btn", "compare", {"cmp_selected_studies": [s for s in ["PSI-69", "PSI-25"] if s in {_study(e) for e in experiments}] or ([] if not bass2_id else [])}),
        ("tour-4", "home.tour_s4_title", "home.tour_s4_desc", "home.tour_s4_btn", "assistant", {}),
    ]
    for idx, (btn_key, title_k, desc_k, btn_k, target_sec, updates) in enumerate(tour_steps):
        with t_cols[idx % 2]:
            with st.container(border=True):
                st.markdown(f"**{t(title_k, lang)}**")
                st.write(t(desc_k, lang))
                st.button(
                    t(btn_k, lang),
                    key=f"home-{btn_key}",
                    on_click=_jump_section,
                    args=(target_sec,),
                    kwargs=updates,
                )

    st.warning(t("home.warning_conditions", lang))
    if not documents:
        st.info(t("home.no_docs", lang))


# ----------------------------------------------------------------------------- Investigations Catalog


def show_catalog(experiments: list[dict]) -> None:
    lang = get_lang()
    st.title(t("inv.title", lang))
    st.write(t("inv.lead", lang))

    records = catalog(experiments)
    by_study = {_study(e): e for e in experiments}
    if "NASA-CONTEXT" in by_study:
        ctx_exp = by_study["NASA-CONTEXT"]
        records.append({
            "id": "NASA-CONTEXT",
            "name": ctx_exp.get("name", "NASA Combustion Research Guides"),
            "category": "Context",
            "nasa_record_url": "https://www.nasa.gov/wp-content/uploads/2023/05/iss-combustion-science.pdf",
            "doi_candidate": "",
            "experiment": ctx_exp,
            "download_manifest": _json(ROOT / "resources/official/source_manifest.json", {}),
            "documents": ctx_exp.get("documents", []),
            "document_count": len(ctx_exp.get("documents", [])),
        })

    f1, f2 = st.columns([2, 1])
    query = f1.text_input(
        t("inv.search_label", lang),
        placeholder=t("inv.search_placeholder", lang),
        key="inv_search_query",
    )
    pillar_opts = ["All", "Prevention", "Detection", "Suppression", "Context"]
    if st.session_state.get("inv_pillar_filter") not in pillar_opts:
        st.session_state["inv_pillar_filter"] = "All"
    pillar = f2.selectbox(
        t("inv.pillar_label", lang),
        pillar_opts,
        format_func=lambda opt: t(f"inv.pillar_{opt.lower()}", lang),
        key="inv_pillar_filter",
    )

    filtered: list[dict] = []
    for row in records:
        profile_en = investigation_profile(row["id"], "en")
        profile_loc = investigation_profile(row["id"], lang)
        row_pillar = profile_en.get("pillar") or _PILLAR_KEY_MAP.get(row.get("category", "").split("/")[0].strip(), "Context")
        searchable = f"{row['id']} {row['name']} {row.get('category', '')} {profile_loc.get('objective', '')} {profile_loc.get('relevance', '')}".casefold()
        if query.strip().casefold() not in searchable:
            continue
        if pillar != "All" and pillar != row_pillar:
            continue
        filtered.append({**row, "_pillar": row_pillar, "_profile": profile_loc})

    st.header(t("inv.list_header", lang, count=len(filtered)))
    for row in filtered:
        exp = row["experiment"]
        profile = row["_profile"]
        pillar_text = t(f"inv.pillar_{row['_pillar'].lower()}", lang)
        with st.container(border=True):
            st.subheader(f"{row['id']} · {row['name']}")
            if exp:
                status_text = t("inv.status_imported", lang)
            elif row["download_manifest"].get("downloaded_csvs"):
                status_text = t("inv.status_downloaded", lang)
            else:
                status_text = t("inv.status_pending", lang)
            st.caption(f"{pillar_text} · {status_text} · {t('inv.docs_count', lang, count=row['document_count'])}")

            if profile:
                st.markdown(f"**{t('inv.objective_label', lang)}:** {profile.get('objective', '')}")
                st.markdown(f"**{t('inv.relevance_label', lang)}:** {profile.get('relevance', '')}")
                if profile.get("caveat"):
                    st.caption(f"**{t('inv.caveat_label', lang)}:** {profile['caveat']}")
            elif exp and exp.get("description"):
                st.write(exp["description"])

            provenance = row["download_manifest"]
            doi = provenance.get("doi") or (exp or {}).get("doi")
            link_cols = st.columns(3)
            with link_cols[0]:
                _source_link(t("inv.btn_nasa", lang), row.get("nasa_record_url"))
            with link_cols[1]:
                if _doi_url(doi):
                    _source_link(t("inv.btn_doi", lang), _doi_url(doi))
                elif row.get("doi_candidate"):
                    st.caption(t("inv.doi_candidate", lang, doi=row["doi_candidate"]))
            with link_cols[2]:
                if exp:
                    st.button(
                        t("inv.btn_open", lang),
                        key=f"nasa-open-{row['id']}",
                        type="primary",
                        on_click=_open_experiment,
                        args=(exp["id"],),
                    )
            if exp and exp.get("documents"):
                doc_summary = ", ".join(
                    f"{doc.get('name', 'Document')}: {status_label(doc.get('status'), lang)}"
                    for doc in exp.get("documents", [])
                )
                st.caption(t("inv.extraction_list", lang, items=doc_summary))
            elif provenance.get("error"):
                st.caption(str(provenance["error"]))

    if not filtered:
        st.info(t("inv.empty", lang))


# ----------------------------------------------------------------------------- Evidence & Scientific Assistant


def _original_for(evidence: dict, experiments: list[dict]) -> tuple[dict, dict] | None:
    digest = evidence.get("sha256") or evidence.get("document_sha256")
    study = evidence.get("study_id")
    for exp in experiments:
        if study and _study(exp) != study and exp["id"] != study:
            continue
        for doc in exp.get("documents", []):
            if doc.get("sha256") == digest:
                return exp, doc
    return None


def show_evidence(evidence: list[dict], experiments: list[dict]) -> None:
    lang = get_lang()
    for position, item in enumerate(evidence, 1):
        label = f"{position}. {item.get('study_id', '')} · {item.get('document_name', 'Document')} · {item.get('location', '')}"
        with st.expander(label, expanded=position == 1):
            kind = item.get("evidence_kind", "unclassified")
            st.caption(t("ast.ev_nature", lang, kind=evidence_label(kind, lang), ref=item.get("id", "")))
            st.text(item.get("text", ""))
            b1, b2 = st.columns(2)
            with b1:
                _source_link(t("ast.btn_source", lang), item.get("source_url"))
            with b2:
                _source_link(t("ast.btn_doi", lang), _doi_url(item.get("doi")))
            st.code(item.get("sha256", ""), language=None)
            original = _original_for(item, experiments)
            if original:
                exp, doc = original
                for notice in _document_notices(_study(exp), doc, lang=lang):
                    st.warning(notice)
                try:
                    content = storage.read_original(exp, doc)
                except (OSError, ValueError) as error:
                    st.error(t("ast.orig_unavailable", lang, error=error))
                    continue
                d_col, p_col = st.columns(2)
                with d_col:
                    st.download_button(
                        t("ast.btn_download", lang),
                        content,
                        file_name=doc["name"],
                        key=f"evidence-download-{position}-{item['id']}",
                    )
                if doc.get("extension") == ".pdf" and item.get("page"):
                    with p_col:
                        if st.button(t("ast.btn_view_page", lang), key=f"evidence-page-{position}-{item['id']}"):
                            try:
                                image = render_pdf_page(content, int(item["page"]))
                                st.image(image, caption=t("vis.preview_caption", lang, name=doc["name"], page=item["page"]))
                            except (OSError, ValueError, RuntimeError) as error:
                                st.error(t("ast.page_render_err", lang, error=error))


def _select_example_query(
    question: str,
    studies: list[str],
    available_studies: list[str],
    o2_enabled: bool = False,
    o2_min: float = 0.18,
    o2_max: float = 0.25,
) -> None:
    st.session_state["ast_question_input"] = question
    st.session_state["ast_studies_filter"] = [s for s in studies if s in available_studies]
    st.session_state["ast_o2_enabled"] = o2_enabled
    st.session_state["ast_o2_min"] = o2_min
    st.session_state["ast_o2_max"] = o2_max
    st.session_state["ast_p_enabled"] = False
    st.session_state["ast_v_enabled"] = False
    st.session_state["ast_fuel_input"] = ""
    st.session_state["ast_pending_autorun"] = True


def show_search(experiments: list[dict]) -> None:
    lang = get_lang()
    st.title(t("ast.title", lang))
    st.caption(t("ast.subtitle", lang))

    index = _retrieval_index(os.getenv("RAG_EMBEDDING_MODEL", "").strip())
    has_llm = llm_configured()
    st.caption(t("ast.mode_semantic", lang) if index.model is not None else t("ast.mode_lexical", lang))
    st.caption(t("ast.mode_caption", lang, mode=index.mode))

    if has_llm:
        st.success(t("ast.llm_configured_banner", lang))
    else:
        st.info(t("ast.llm_unconfigured_banner", lang))

    studies = sorted({_study(e) for e in experiments})

    st.subheader(t("ast.examples_title", lang))
    examples = [
        ("ex1", "ast.ex1_label", "ast.ex1_q", ["PSI-69"], True, 0.18, 0.25),
        ("ex2", "ast.ex2_label", "ast.ex2_q", ["PSI-25"], False, 0.18, 0.25),
        ("ex3", "ast.ex3_label", "ast.ex3_q", ["PSI-102"], False, 0.18, 0.25),
        ("ex4", "ast.ex4_label", "ast.ex4_q", ["PSI-98", "PSI-99", "PSI-100"], False, 0.18, 0.25),
        ("ex5", "ast.ex5_label", "ast.ex5_q", [], False, 0.18, 0.25),
    ]
    ex_cols = st.columns(len(examples))
    for idx, (ex_id, label_k, q_k, ex_studies, o2_on, o2_lo, o2_hi) in enumerate(examples):
        ex_cols[idx].button(
            t(label_k, lang),
            key=f"ast-{ex_id}",
            use_container_width=True,
            on_click=_select_example_query,
            args=(t(q_k, lang), ex_studies, studies, o2_on, o2_lo, o2_hi),
        )

    st.session_state.setdefault("ast_question_input", t("ast.ex1_q", lang))
    st.session_state.setdefault("ast_studies_filter", [])
    st.session_state["ast_studies_filter"] = [s for s in st.session_state["ast_studies_filter"] if s in studies]

    selected = st.multiselect(t("ast.studies_filter", lang), studies, key="ast_studies_filter")
    with st.form("scientific-query"):
        question = st.text_area(
            t("ast.question_label", lang),
            help=t("ast.question_help", lang),
            key="ast_question_input",
        )
        with st.expander(t("ast.filters_expander", lang)):
            c_o1, c_o2, c_o3 = st.columns(3)
            oxygen = c_o1.checkbox(t("ast.o2_check", lang), key="ast_o2_enabled")
            o2min = c_o2.number_input(t("ast.o2_min", lang), min_value=0.0, max_value=1.0, value=0.18, step=0.01, key="ast_o2_min")
            o2max = c_o3.number_input(t("ast.o2_max", lang), min_value=0.0, max_value=1.0, value=0.25, step=0.01, key="ast_o2_max")

            c_p1, c_p2, c_p3 = st.columns(3)
            pressure = c_p1.checkbox(t("ast.p_check", lang), key="ast_p_enabled")
            pmin = c_p2.number_input(t("ast.p_min", lang), min_value=0.0, value=0.0, key="ast_p_min")
            pmax = c_p3.number_input(t("ast.p_max", lang), min_value=0.0, value=30.0, key="ast_p_max")

            c_v1, c_v2, c_v3 = st.columns(3)
            velocity = c_v1.checkbox(t("ast.v_check", lang), key="ast_v_enabled")
            vmin = c_v2.number_input(t("ast.v_min", lang), value=0.0, key="ast_v_min")
            vmax = c_v3.number_input(t("ast.v_max", lang), value=100.0, key="ast_v_max")

            fuel = st.text_input(t("ast.fuel_label", lang), placeholder=t("ast.fuel_ph", lang), key="ast_fuel_input")
            st.caption(t("ast.filters_note", lang))

        use_llm = st.checkbox(
            t("ast.use_llm", lang),
            value=False,
            disabled=not has_llm,
            help=t("ast.use_llm_help", lang),
        )
        submitted = st.form_submit_button(t("ast.submit_btn", lang), type="primary")

    autorun = bool(st.session_state.pop("ast_pending_autorun", False))
    if submitted or autorun:
        if not question.strip():
            st.warning(t("ast.empty_query_warn", lang))
            return
        if (oxygen and o2min > o2max) or (pressure and pmin > pmax) or (velocity and vmin > vmax):
            st.error(t("ast.range_error", lang))
            return
        filters = []
        if oxygen:
            filters.append({"field": "oxygen_fraction", "unit": "fraction", "min": o2min, "max": o2max})
        if pressure:
            filters.append({"field": "pressure", "unit": "psia", "reference": "absolute", "min": pmin, "max": pmax})
        if velocity:
            filters.append({"field": "velocity", "unit": "cm/s", "min": vmin, "max": vmax})
        if fuel.strip():
            filters.append({"field": "fuel", "value": fuel.strip()})
        with st.spinner(t("ast.spinner", lang)):
            result = answer(
                question,
                index,
                study_ids=selected or None,
                numeric_filters=filters or None,
                language=lang,
                use_llm=bool(use_llm and has_llm),
            )
        st.session_state["scientific_answer"] = result
        st.session_state["scientific_query_context"] = {
            "question": question,
            "studies": ", ".join(selected) if selected else t("ast.all_studies", lang),
            "filters": filters,
        }

    result = st.session_state.get("scientific_answer")
    if result:
        st.header(t("ast.results_header", lang))
        context = st.session_state.get("scientific_query_context", {})
        if context:
            st.caption(t("ast.last_query", lang, studies=context["studies"]))
            st.text(context["question"])
        # The assistant constructs this text and escapes source-authored Markdown.
        # Raw evidence remains inert st.text below; HTML is never enabled.
        st.markdown(result.get("text", ""), unsafe_allow_html=False)
        st.caption(t("ast.mode_caption", lang, mode=result.get("mode", "retrieval")))
        for warning in result.get("warnings", []):
            st.warning(translate_retrieval_warning(str(warning), lang))
        show_evidence(result.get("evidence", []), experiments)


# ----------------------------------------------------------------------------- Compare


def _set_compare_preset(study_ids: list[str], available: dict[str, Any]) -> None:
    st.session_state["cmp_selected_studies"] = [s for s in study_ids if s in available]


def show_comparison(experiments: list[dict]) -> None:
    lang = get_lang()
    st.title(t("cmp.title", lang))
    st.write(t("cmp.lead", lang))

    mapping = {_study(exp): exp for exp in experiments}
    st.caption(t("cmp.presets_label", lang))
    p_cols = st.columns(3)
    presets = [
        ("flex-bass", "cmp.preset_flex_bass", ["PSI-69", "PSI-25"]),
        ("same", "cmp.preset_same", ["PSI-102", "PSI-101"]),
        ("saffire", "cmp.preset_saffire", ["PSI-98", "PSI-99"]),
    ]
    for idx, (pkey, label_k, ids) in enumerate(presets):
        p_cols[idx].button(
            t(label_k, lang),
            key=f"cmp-preset-{pkey}",
            use_container_width=True,
            on_click=_set_compare_preset,
            args=(ids, mapping),
        )

    with st.expander(t("cmp.why_title", lang)):
        st.markdown(t("cmp.why_body", lang))

    st.session_state.setdefault("cmp_selected_studies", [])
    st.session_state["cmp_selected_studies"] = [s for s in st.session_state["cmp_selected_studies"] if s in mapping]

    selection = st.multiselect(
        t("cmp.select_studies", lang),
        list(mapping),
        max_selections=3,
        key="cmp_selected_studies",
    )
    if len(selection) >= 2:
        st.header(t("cmp.selected_tables", lang))
        entries = []
        for study in selection:
            exp = mapping[study]
            available = views.collect_entries(exp)
            st.subheader(study)
            if not available:
                st.info(t("cmp.no_table", lang))
                continue
            chosen = st.selectbox(
                t("cmp.choose_table", lang),
                range(len(available)),
                format_func=lambda n, a=available: a[n]["table"]["name"],
                key=f"compare-table-{study}",
            )
            entry = available[chosen]
            entries.append({
                **entry,
                "study_id": study,
                "evidence_kind": entry["document"].get("evidence_kind", "unknown"),
                "source": entry["document"].get("source_url", ""),
            })
        comparison = compare_tables(entries)
        if comparison["compatible"]:
            st.success(t("cmp.compatible_ok", lang))
        else:
            st.warning(t("cmp.incompatible_warn", lang))
            for reason in comparison["reasons"]:
                st.write(f"• {translate_comparison_reason(reason, lang)}")
        for profile in comparison["profiles"]:
            st.write(f"**{profile['study_id']}** · {profile['table']} · {t('cmp.table_rows', lang, rows=profile['rows'])}")
            st.dataframe(pd.DataFrame(profile["columns"]), hide_index=True, use_container_width=True)
    else:
        st.info(t("cmp.select_min", lang))

    st.divider()
    st.header(t("cmp.relevance_title", lang))
    st.caption(t("cmp.relevance_caption", lang))
    app_opts = ["habitat", "detection", "suppression"]
    app_labels = {
        "habitat": t("cmp.app_habitat", lang),
        "detection": t("cmp.app_detection", lang),
        "suppression": t("cmp.app_suppression", lang),
    }
    application = st.selectbox(
        t("cmp.application_label", lang),
        app_opts,
        format_func=lambda opt: app_labels.get(opt, opt),
        key="cmp_application",
    )
    question = st.text_input(t("cmp.query_label", lang), value="microgravity combustion", key="cmp_query")
    records = [{**r, "description": (r["experiment"] or {}).get("description", "")} for r in catalog(experiments)]
    ranked = rank_investigations(records, query=question, application=application)
    st.dataframe(
        pd.DataFrame([
            {
                t("cmp.col_study", lang): r.get("id") or r.get("study_id"),
                t("cmp.col_name", lang): r.get("name"),
                t("cmp.col_score", lang): r.get("score"),
                t("cmp.col_reasons", lang): "; ".join(translate_relevance_reason(reason, lang) for reason in r.get("reasons", [])),
            }
            for r in ranked
        ]),
        hide_index=True,
        use_container_width=True,
    )


# ----------------------------------------------------------------------------- Sources & Methodology


@st.fragment(run_every=2)
def _job_monitor(job_id: str) -> None:
    from .pipeline import job_status

    lang = get_lang()
    job = job_status(job_id)
    if not job:
        st.info(t("src.job_missing", lang))
        return
    st.write(t("src.job_status", lang, status=job.get("status", "unknown")))
    st.progress(min(1.0, max(0.0, float(job.get("progress") or 0))))
    if job.get("error"):
        st.error(str(job["error"]))
    result = job.get("result") or job.get("result_json")
    if result:
        try:
            st.json(json.loads(result) if isinstance(result, str) else result)
        except ValueError:
            st.text(str(result))
    if job.get("status") in {"completed", "complete", "succeeded", "partial", "failed", "interrupted"}:
        st.caption(t("src.job_done", lang))


def show_ingestion(experiments: list[dict]) -> None:
    from .pipeline import enqueue_ingestion
    from .scientific_store import ScientificStore

    lang = get_lang()
    readonly = is_public_readonly()
    st.title(t("src.title", lang))
    st.write(t("src.lead", lang))

    m1, m2 = st.columns(2)
    with m1:
        with st.container(border=True):
            st.subheader(t("src.sec1_title", lang))
            st.markdown(t("src.sec1_body", lang))
        with st.container(border=True):
            st.subheader(t("src.sec3_title", lang))
            st.markdown(t("src.sec3_body", lang))
    with m2:
        with st.container(border=True):
            st.subheader(t("src.sec2_title", lang))
            st.markdown(t("src.sec2_body", lang))
        with st.container(border=True):
            st.subheader(t("src.sec4_title", lang))
            st.markdown(t("src.sec4_body", lang))

    st.divider()
    st.header(t("src.ingestion_title", lang))
    if readonly:
        st.info(t("src.ingestion_readonly", lang))
    else:
        st.write(t("src.ingestion_desc", lang))
        with st.expander(t("src.cli_commands", lang)):
            st.code(
                "python scripts/fetch_nasa_resources.py --guide --psi-manual\n"
                "python scripts/fetch_psi_tables.py --ids PSI-25 PSI-26 PSI-68 PSI-69 PSI-98 PSI-99 PSI-100 PSI-101 PSI-102\n"
                "python scripts/fetch_psi_tables.py --ids PSI-69 PSI-25 PSI-102 --pdfs\n"
                "python scripts/ingest_nasa.py",
                language="powershell",
            )
        c1, c2 = st.columns(2)
        if c1.button(t("src.ingestion_btn", lang), type="primary"):
            st.session_state["ingestion_job_id"] = enqueue_ingestion()
        if c2.button(t("src.refresh_btn", lang)):
            views.clear_cache()
            st.rerun()
        if st.session_state.get("ingestion_job_id"):
            _job_monitor(st.session_state["ingestion_job_id"])

    jobs = ScientificStore().jobs()
    if jobs:
        with st.expander(t("src.jobs_header", lang), expanded=False):
            st.dataframe(pd.DataFrame(jobs), hide_index=True, use_container_width=True)

    st.header(t("src.archive_title", lang))
    for exp in experiments:
        for doc in exp.get("documents", []):
            with st.expander(f"{_study(exp)} · {doc['name']}"):
                st.code(doc.get("sha256", ""), language=None)
                st.caption(f"{doc.get('size_bytes', 0):,} bytes · {status_label(doc.get('status'), lang)}")
                for notice in _document_notices(_study(exp), doc, lang=lang):
                    st.warning(notice)
                st.json(doc.get("provenance") or doc.get("source") or {})
                try:
                    content = storage.read_original(exp, doc)
                    st.download_button(
                        t("src.dl_original", lang),
                        content,
                        doc["name"],
                        key=f"source-download-{exp['id']}-{doc['id']}",
                    )
                except (OSError, ValueError) as error:
                    st.error(t("src.orig_err", lang, error=error))
    st.caption(t("src.footer_provenance", lang))


# ----------------------------------------------------------------------------- Visual Page Review


def _select_visual_preset(pdfs: list[tuple[dict, dict]], study_hint: str, page: int) -> None:
    for idx, (exp, doc) in enumerate(pdfs):
        if _study(exp) == study_hint or study_hint in doc.get("name", ""):
            st.session_state["visual-document"] = idx
            st.session_state[f"visual-page-{doc['sha256']}"] = page
            try:
                content = storage.read_original(exp, doc)
                from .visual_review import render_verified_page

                st.session_state["visual_preview"] = (doc["sha256"], page, render_verified_page(content, page, doc["sha256"]))
            except (OSError, ValueError, RuntimeError):
                pass
            return


def show_visual_review(experiments: list[dict]) -> None:
    from dataclasses import asdict

    from .visual_review import (
        configuration,
        provider_label,
        record_human_review,
        render_verified_page,
        review_pdf_page,
        save_review,
    )

    lang = get_lang()
    st.title(t("vis.title", lang))
    st.write(t("vis.lead", lang))
    st.warning(t("vis.warning", lang))

    pdfs = [(exp, doc) for exp in experiments for doc in exp.get("documents", []) if doc.get("extension") == ".pdf"]
    if not pdfs:
        st.info(t("vis.no_pdfs", lang))
        return

    st.caption(t("vis.presets_label", lang))
    vp_cols = st.columns(3)
    vp_cols[0].button(t("vis.preset_same", lang), key="vis-preset-same", use_container_width=True, on_click=_select_visual_preset, args=(pdfs, "PSI-102", 13))
    vp_cols[1].button(t("vis.preset_bass", lang), key="vis-preset-bass", use_container_width=True, on_click=_select_visual_preset, args=(pdfs, "PSI-25", 2))
    vp_cols[2].button(t("vis.preset_guide", lang), key="vis-preset-guide", use_container_width=True, on_click=_select_visual_preset, args=(pdfs, "iss-combustion", 36))

    selected = st.selectbox(
        t("vis.select_pdf", lang),
        range(len(pdfs)),
        format_func=lambda n: f"{_study(pdfs[n][0])} · {pdfs[n][1]['name']}",
        key="visual-document",
    )
    experiment, document = pdfs[selected]
    page_count = max(1, min(500, int(document.get("page_count") or 1)))
    page = int(
        st.number_input(
            t("vis.page_num", lang),
            min_value=1,
            max_value=page_count,
            value=1,
            step=1,
            key=f"visual-page-{document['sha256']}",
        )
    )
    digest = document["sha256"]
    st.caption(t("vis.doc_caption", lang, sha=digest, page=page, total=document.get("page_count", "?")))
    for notice in _document_notices(_study(experiment), document, lang=lang):
        st.warning(notice)

    if st.button(t("vis.render_btn", lang)):
        try:
            image = render_verified_page(storage.read_original(experiment, document), page, digest)
            st.session_state["visual_preview"] = (digest, page, image)
        except (OSError, ValueError, RuntimeError) as error:
            st.error(t("vis.preview_unavailable", lang, error=error))

    preview = st.session_state.get("visual_preview")
    if preview and preview[:2] == (digest, page):
        st.image(preview[2], caption=t("vis.preview_caption", lang, name=document["name"], page=page))

    st.header(t("vis.vlm_header", lang))
    st.caption(provider_label())
    try:
        configured = configuration() is not None
    except ValueError:
        configured = False
    if not configured:
        st.info(t("vis.vlm_unconfigured", lang))
    consent = st.checkbox(
        t("vis.vlm_consent", lang),
        value=False,
        disabled=not configured,
        help=t("vis.vlm_consent_help", lang),
    )
    if st.button(t("vis.vlm_btn", lang), disabled=not configured or not consent):
        with st.spinner(t("vis.vlm_spinner", lang)):
            try:
                content = storage.read_original(experiment, document)
                review = review_pdf_page(content, page, digest, consent=consent)
                save_review(review, _study(experiment))
                st.session_state["visual_review_result"] = review
            except (OSError, ValueError, RuntimeError) as error:
                st.error(t("vis.vlm_failed", lang, err_type=type(error).__name__))

    review = st.session_state.get("visual_review_result")
    if review and review.document_sha256 == digest and review.page == page:
        st.header(t("vis.candidate_header", lang))
        for warning in review.warnings:
            st.warning(warning)
        st.caption(t("vis.candidate_status", lang, status=review.status))
        if review.status == "candidate":
            st.text(review.description)
            st.text(review.inference)
            for index, region in enumerate(review.regions, 1):
                with st.expander(t("vis.region_label", lang, idx=index, kind=region.kind)):
                    st.caption(t("vis.region_coords_note", lang))
                    st.text(str(region.bbox))
                    st.text(region.description)
                    st.caption(t("vis.region_text_note", lang))
                    st.text(region.text_candidate)
            st.download_button(
                t("vis.download_json", lang),
                json.dumps(asdict(review), ensure_ascii=False, indent=2).encode("utf-8"),
                f"visual-review-{digest[:12]}-p{page}.json",
                "application/json",
            )
            note = st.text_area(
                t("vis.human_note_label", lang),
                max_chars=2000,
                help=t("vis.human_note_help", lang),
            )
            if st.button(t("vis.save_note_btn", lang)):
                try:
                    reviewed = record_human_review(review, note)
                    save_review(reviewed, _study(experiment))
                    st.session_state["visual_review_result"] = reviewed
                    st.success(t("vis.save_note_ok", lang))
                except ValueError as error:
                    st.error(str(error))
            if review.human_review_note:
                st.caption(t("vis.human_saved_at", lang, utc=review.human_reviewed_utc))
                st.text(review.human_review_note)


# ----------------------------------------------------------------------------- Styling & Dispatch


def inject_dashboard_css() -> None:
    """Inject restrained, responsive scientific styling (static CSS only)."""
    # Static CSS only. Do not interpolate external document strings into HTML.
    st.html(
        """<style>
        [data-testid="stMainBlockContainer"] { max-width: 90rem; padding-top: 1.5rem; }
        h1, h2, h3 { text-wrap: balance; letter-spacing: -0.015em; }
        .psi-lead { font-size: 1.08rem; color: #3c484e; margin-top: -0.35rem; margin-bottom: 1.25rem; line-height: 1.55; }
        [data-testid="stMetricValue"], table { font-variant-numeric: tabular-nums; }
        [data-testid="stMetricLabel"] { white-space: normal !important; }
        [data-testid="stMetricLabel"] p { white-space: normal !important; overflow-wrap: break-word; }
        [data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #E3E5DF;
            border-radius: 0.65rem;
            padding: 0.85rem 1rem;
        }
        [data-testid="stText"], [data-testid="stCaptionContainer"], p { overflow-wrap: anywhere; }
        button, [data-testid="stLinkButton"] a { min-height: 2.65rem; }
        :is(button, a, input, textarea, [role="radiogroup"] label):focus-visible {
            outline: 3px solid #A44426 !important;
            outline-offset: 2px;
        }
        @media (max-width: 48rem) {
            [data-testid="stMainBlockContainer"] { padding-inline: 0.9rem; }
        }
        </style>"""
    )


def show_section(section: str, experiments: list[dict]) -> None:
    inject_dashboard_css()
    key = normalize_section(section)
    handlers = {
        "home": show_overview,
        "investigations": show_catalog,
        "compare": show_comparison,
        "assistant": show_search,
        "visual_review": show_visual_review,
        "sources": show_ingestion,
    }
    handlers[key](experiments)
