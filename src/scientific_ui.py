"""Global NASA catalog, evidence retrieval, assistant, comparison, and methodology views."""
from __future__ import annotations

import html
import json
import os
import re
import sqlite3
from collections.abc import Callable
from pathlib import Path
from typing import Any
from uuid import uuid4

import pandas as pd
import streamlit as st

from . import storage, views
from .assistant import answer, llm_configured
from .challenge_engine import (
    build_priority_ranking,
    build_spacecraft_interpretation,
    build_study_summary,
)
from .comparison import compare_tables
from .design_system import inject_global_styles, render_hero_banner, render_pillar_badge
from .extractors import render_pdf_page
from .gemini_provider import gemini_status_summary
from .i18n import (
    SECTION_KEYS,
    evidence_label,
    get_lang,
    investigation_profile,
    normalize_section,
    status_label,
    t,
    translate_comparison_reason,
    translate_retrieval_warning,
)
from .pipeline import is_public_readonly
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


def _indexed_chunk_info() -> tuple[int, str]:
    """Return total indexed chunks and active chunking/vector mode from SQLite."""
    search_db = PROJECT_DIR / "data" / "search.sqlite3"
    if not search_db.exists():
        return 0, "lexical-vectors"
    try:
        with sqlite3.connect(search_db) as conn:
            row = conn.execute("SELECT count(*), max(model) FROM chunks").fetchone()
        if not row:
            return 0, "lexical-vectors"
        return int(row[0] or 0), str(row[1] or "lexical-vectors")
    except sqlite3.Error:
        return 0, "lexical-vectors"


def _indexed_chunk_count() -> int:
    count, _mode = _indexed_chunk_info()
    return count


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


def _render_challenge_hub(experiments: list[dict], records: list[dict], lang: str) -> None:
    """Interactive SUMMARIZE · RANK · INTERPRET workbench directly on Home."""
    st.divider()
    st.header(t("hub.title", lang))
    st.caption(t("hub.subtitle", lang))
    exp_by_id = {_study(e): e for e in experiments}
    study_ids = [sid for sid in exp_by_id if sid != "NASA-CONTEXT"]
    if not study_ids:
        study_ids = list(exp_by_id)
    if not study_ids:
        return

    default_sid = "PSI-69" if "PSI-69" in exp_by_id else study_ids[0]
    t_sum, t_rank, t_interp = st.tabs([
        t("hub.tab_summarize", lang),
        t("hub.tab_rank", lang),
        t("hub.tab_interpret", lang),
    ])

    with t_sum:
        if "hub_sum_study" in st.session_state and st.session_state["hub_sum_study"] not in study_ids:
            st.session_state["hub_sum_study"] = default_sid
        chosen_sum = st.selectbox(
            t("hub.select_study", lang),
            options=study_ids,
            index=study_ids.index(default_sid),
            format_func=lambda s: exp_by_id[s].get("name", s)
            if str(exp_by_id[s].get("name", s)).startswith(s)
            else f"{s} · {exp_by_id[s].get('name', s)}",
            key="hub_sum_study",
        )
        safe_sum = chosen_sum if chosen_sum in exp_by_id else default_sid
        target_exp = exp_by_id[safe_sum]
        summary = build_study_summary(target_exp, lang)
        with st.container(border=True):
            render_pillar_badge(summary["pillar"])
            display_title = (
                summary["title"]
                if str(summary["title"]).startswith(str(summary["study_id"]))
                else f"{summary['study_id']} · {summary['title']}"
            )
            st.subheader(display_title)
            st.markdown(f"**{t('hub.summarize_objective', lang)}:** {summary['objective']}")
            c_cov, c_role = st.columns(2)
            c_cov.markdown(f"**{t('hub.summarize_coverage', lang)}:** {summary['archive_coverage']}")
            c_role.markdown(f"**{t('hub.summarize_roles', lang)}:** {summary['evidence_roles']}")
            if summary["caveats"]:
                st.warning(summary["caveats"][0])
            if summary["citations"]:
                st.caption(
                    f"**{t('hub.summarize_citations', lang)}:** "
                    + ", ".join(f"{c['document']} ({c['status']})" for c in summary["citations"])
                )
            st.button(
                t("inv.btn_open", lang),
                key=f"hub-open-{safe_sum}",
                on_click=_open_experiment,
                args=(target_exp["id"],),
            )

    with t_rank:
        st.caption(t("hub.rank_intro", lang))
        app_opts = ["habitat", "detection", "suppression"]
        if "hub_rank_app" in st.session_state and st.session_state["hub_rank_app"] not in app_opts:
            st.session_state["hub_rank_app"] = "habitat"
        app_labels = {
            "habitat": t("cmp.app_habitat", lang),
            "detection": t("cmp.app_detection", lang),
            "suppression": t("cmp.app_suppression", lang),
        }
        chosen_app = st.selectbox(
            t("cmp.application_label", lang),
            app_opts,
            format_func=lambda opt: app_labels.get(opt, opt),
            key="hub_rank_app",
        )
        safe_app = chosen_app if chosen_app in app_opts else "habitat"
        rank_rows = build_priority_ranking(
            [{**r, "description": (r["experiment"] or {}).get("description", "")} for r in records],
            application=safe_app,
            query="microgravity combustion",
            language=lang,
        )[:4]
        for row in rank_rows:
            with st.container(border=True):
                rc1, rc2 = st.columns([3.0, 1.2], vertical_alignment="center")
                rc1.markdown(f"**#{row['rank']} · {row['study_id']} · {row['name']}**")
                rc1.caption(row["reasons_text"])
                rc2.metric(t("cmp.col_score", lang), f"{row['score']:.0f}/100")
                st.progress(min(1.0, max(0.0, row["score"] / 100.0)))

    with t_interp:
        if "hub_interp_study" in st.session_state and st.session_state["hub_interp_study"] not in study_ids:
            st.session_state["hub_interp_study"] = default_sid
        chosen_interp = st.selectbox(
            t("hub.select_study", lang),
            options=study_ids,
            index=study_ids.index(default_sid),
            format_func=lambda s: exp_by_id[s].get("name", s)
            if str(exp_by_id[s].get("name", s)).startswith(s)
            else f"{s} · {exp_by_id[s].get('name', s)}",
            key="hub_interp_study",
        )
        safe_interp = chosen_interp if chosen_interp in exp_by_id else default_sid
        interp = build_spacecraft_interpretation(exp_by_id[safe_interp], lang)
        with st.container(border=True):
            render_pillar_badge(interp["pillar"])
            st.markdown(f"**{t('hub.interpret_obs', lang)}:** {interp['observation_scope']}")
            st.markdown(f"**{t('hub.interpret_impl', lang)}:** {interp['engineering_implication']}")
            st.info(f"**{t('hub.interpret_limit', lang)}:** {interp['scientific_boundary']}")


def _entry_card_html(badge: str, title: str, desc: str) -> str:
    return (
        "<div class='psi-entry-card-body'>"
        f"<div class='psi-entry-kicker'>{html.escape(badge, quote=True)}</div>"
        f"<div class='psi-entry-title'>{html.escape(title, quote=True)}</div>"
        f"<p class='psi-entry-desc'>{html.escape(desc, quote=True)}</p>"
        "</div>"
    )


def show_overview(experiments: list[dict]) -> None:
    from .guided_journeys import render_active_journey, start_journey

    if render_active_journey(experiments):
        return

    lang = get_lang()
    st.title(t("home.title", lang))
    st.markdown(f"<p class='psi-lead'>{t('home.subtitle', lang)}</p>", unsafe_allow_html=True)
    render_hero_banner(t("app.subtitle", lang), t("home.plain_intro", lang), lang=lang)

    records = catalog(experiments)
    documents = [doc for exp in experiments for doc in exp.get("documents", [])]
    flex_id = _study_id_for(experiments, "PSI-69")
    chunk_count, chunk_model = _indexed_chunk_info()
    is_semantic = chunk_model.startswith("local-semantic:")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(t("home.metric_studies", lang), sum(bool(row["experiment"]) for row in records))
    m2.metric(t("home.metric_docs", lang), len(documents))
    m3.metric(t("home.metric_tables", lang), sum(doc.get("table_count", 0) for doc in documents))
    m4.metric(t("home.metric_chunks", lang), chunk_count)

    failures = sum(doc.get("status") == "erro" for doc in documents)
    partial = sum(doc.get("status") == "parcial" for doc in documents)
    chunk_note = (
        t("home.chunk_caption_semantic", lang, chunks=chunk_count, docs=len(documents))
        if is_semantic
        else t("home.chunk_caption_lexical", lang, chunks=chunk_count, docs=len(documents))
    )
    st.caption(
        chunk_note
        + " "
        + t(
            "home.extraction_caption",
            lang,
            processed=len(documents) - failures - partial,
            partial=partial,
            failed=failures,
        )
    )

    st.header(t("home.start_title", lang))
    c1, c2, c3 = st.columns(3, gap="medium")
    with c1.container(border=True):
        st.markdown(
            _entry_card_html(t("home.exp_a_badge", lang), t("home.exp_a_title", lang), t("home.exp_a_desc", lang)),
            unsafe_allow_html=True,
        )
        st.button(
            t("home.exp_a_btn", lang),
            type="primary",
            key="home-start-j1",
            use_container_width=True,
            on_click=start_journey,
            args=("journey_1", 1),
        )
    with c2.container(border=True):
        st.markdown(
            _entry_card_html(t("home.exp_b_badge", lang), t("home.exp_b_title", lang), t("home.exp_b_desc", lang)),
            unsafe_allow_html=True,
        )
        st.button(
            t("home.exp_b_btn", lang),
            type="primary",
            key="home-start-j2",
            use_container_width=True,
            on_click=start_journey,
            args=("journey_2", 1),
        )
    with c3.container(border=True):
        st.markdown(
            _entry_card_html(t("home.exp_c_badge", lang), t("home.exp_c_title", lang), t("home.exp_c_desc", lang)),
            unsafe_allow_html=True,
        )
        if flex_id:
            st.button(
                t("home.exp_c_btn_data", lang),
                type="primary",
                key="home-open-explorer",
                use_container_width=True,
                on_click=_open_experiment,
                args=(flex_id,),
            )
        else:
            st.button(
                t("home.exp_c_btn_data", lang),
                type="primary",
                key="home-open-explorer",
                use_container_width=True,
                on_click=_jump_section,
                args=("explorer",),
            )

    q1, q2 = st.columns(2, gap="medium")
    q1.button(
        t("home.exp_c_btn_studies", lang),
        key="home-open-studies",
        use_container_width=True,
        on_click=_jump_section,
        args=("investigations",),
        kwargs={"inv_pillar_filter": "All"},
    )
    q2.button(
        t("home.exp_c_btn_assistant", lang),
        key="home-open-assistant",
        use_container_width=True,
        on_click=_jump_section,
        args=("assistant",),
    )

    _render_challenge_hub(experiments, records, lang)

    with st.expander(t("home.compare_title", lang), expanded=False):
        col_earth, col_space = st.columns(2, gap="medium")
        with col_earth.container(border=True):
            st.subheader(t("home.earth_title", lang))
            st.markdown(t("home.earth_points", lang))
        with col_space.container(border=True):
            st.subheader(t("home.space_title", lang))
            st.markdown(t("home.space_points", lang))

    with st.expander(t("home.glossary_title", lang), expanded=False):
        st.markdown(
            f"- **{t('glossary.microgravity_term', lang)}:** {t('glossary.microgravity_def', lang)}\n"
            f"- **{t('glossary.o2_term', lang)}:** {t('glossary.o2_def', lang)}\n"
            f"- **{t('glossary.drop_diam_term', lang)}:** {t('glossary.drop_diam_def', lang)}\n"
            f"- **{t('glossary.psi_term', lang)}:** {t('glossary.psi_def', lang)}"
        )

    with st.expander(t("home.tech_diag_label", lang), expanded=False):
        raw_model = chunk_model.split(":", 1)[-1]
        model_short = "local SentenceTransformer" if re.fullmatch(r"[0-9a-f]{32,40}", raw_model) else raw_model
        gemini_info = gemini_status_summary(lang)
        st.caption(f"Index profile: `{model_short}` ({chunk_count} indexed entries)")
        st.caption(gemini_info["summary"])

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
            render_pillar_badge(pillar_text, key_hint=row["_pillar"])
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
            if item.get("field_classification"):
                st.caption(" · ".join(
                    f"{field.get('header', field.get('source_column_index', ''))}: "
                    f"{evidence_label(field.get('role') or field.get('evidence_kind'), lang)}"
                    for field in item["field_classification"]
                ))
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


def _render_evidence_summary(result: dict[str, Any], experiments: list[dict], lang: str) -> None:
    """Summarize matched studies, evidence provenance, and scientific boundaries in plain language."""
    ev_items = list(result.get("evidence") or [])
    matched_studies: list[str] = []
    for item in ev_items:
        sid = str(item.get("study_id") or "")
        if sid and sid not in matched_studies:
            matched_studies.append(sid)

    with st.container(border=True):
        st.markdown(f"#### {t('ast_guide.summary_title', lang)}")
        if ev_items:
            st.markdown(
                t(
                    "ast_guide.summary_counts",
                    lang,
                    matches=len(ev_items),
                    studies=len(matched_studies),
                    study_list=", ".join(f"`{s}`" for s in matched_studies),
                )
            )
            st.markdown(t("ast_guide.summary_how", lang))
            top_caveat = investigation_profile(matched_studies[0], lang).get("caveat") if matched_studies else ""
            if top_caveat:
                st.caption(t("ast_guide.summary_caveat_prefix", lang) + str(top_caveat))
        if result.get("mode") != "llm":
            st.caption(t("ast_guide.summary_no_llm", lang))


def _render_matched_synthesis(result: dict[str, Any], experiments: list[dict], lang: str) -> None:
    """Render SUMMARIZE and INTERPRET synthesis cards for matched studies in plain language."""
    ev_items = list(result.get("evidence") or [])
    if not ev_items:
        return
    exp_by_sid = {_study(e): e for e in experiments}
    first_sid = next((str(i.get("study_id") or "") for i in ev_items if str(i.get("study_id") or "") in exp_by_sid), "")
    if not first_sid:
        return
    exp = exp_by_sid[first_sid]
    summary = build_study_summary(exp, lang)
    interp = build_spacecraft_interpretation(exp, lang)
    c1, c2 = st.columns(2, gap="medium")
    with c1.container(border=True):
        render_pillar_badge(summary["pillar"])
        st.markdown(f"**{t('ast.synth_summary_heading', lang)}** (`{first_sid}`)")
        if summary["objective"]:
            st.write(summary["objective"])
        st.caption(summary["archive_coverage"])
    with c2.container(border=True):
        st.markdown(f"**{t('ast.synth_interpret_heading', lang)}**")
        st.markdown(f"- **{t('hub.interpret_obs', lang)}:** {interp['observation_scope']}")
        st.markdown(f"- **{t('hub.interpret_impl', lang)}:** {interp['engineering_implication']}")
        st.caption(interp["scientific_boundary"])


def show_search(experiments: list[dict]) -> None:
    lang = get_lang()
    is_advanced = st.session_state.get("interaction_mode", "guided") == "advanced"
    st.title(t("ast.title", lang))
    st.markdown(f"<p class='psi-lead'>{t('ast.subtitle', lang)}</p>", unsafe_allow_html=True)

    index = _retrieval_index(os.getenv("RAG_EMBEDDING_MODEL", "").strip())
    has_llm = llm_configured()
    gemini_status = gemini_status_summary(lang)
    studies = sorted({_study(e) for e in experiments})

    if has_llm:
        st.success(t("ast.llm_configured_banner", lang))
    else:
        st.info(t("ast.llm_unconfigured_banner", lang))

    st.caption(t("ast_guide.examples_hint", lang))
    examples = [
        ("ex1", "ast.ex1_label", "ast.ex1_q", ["PSI-69"], True, 0.18, 0.25),
        ("ex2", "ast.ex2_label", "ast.ex2_q", ["PSI-25"], False, 0.18, 0.25),
        ("ex3", "ast.ex3_label", "ast.ex3_q", ["PSI-102"], False, 0.18, 0.25),
        ("ex4", "ast.ex4_label", "ast.ex4_q", ["PSI-98", "PSI-99", "PSI-100"], False, 0.18, 0.25),
        ("ex5", "ast.ex5_label", "ast.ex5_q", [], False, 0.18, 0.25),
    ]
    for start in range(0, len(examples), 3):
        row_items = examples[start : start + 3]
        ex_cols = st.columns(len(row_items))
        for idx, (ex_id, label_k, q_k, ex_studies, o2_on, o2_lo, o2_hi) in enumerate(row_items):
            ex_cols[idx].button(
                t(label_k, lang),
                key=f"ast-{ex_id}",
                use_container_width=True,
                on_click=_select_example_query,
                args=(t(q_k, lang), ex_studies, studies, o2_on, o2_lo, o2_hi),
            )

    st.session_state.setdefault("ast_question_input", t("ast.ex1_q", lang))
    st.session_state.setdefault("ast_studies_filter", [])
    st.session_state.setdefault("ast_o2_enabled", False)
    st.session_state.setdefault("ast_o2_min", 0.18)
    st.session_state.setdefault("ast_o2_max", 0.25)
    st.session_state.setdefault("ast_p_enabled", False)
    st.session_state.setdefault("ast_p_min", 0.0)
    st.session_state.setdefault("ast_p_max", 30.0)
    st.session_state.setdefault("ast_v_enabled", False)
    st.session_state.setdefault("ast_v_min", 0.0)
    st.session_state.setdefault("ast_v_max", 100.0)
    st.session_state["ast_studies_filter"] = [s for s in st.session_state["ast_studies_filter"] if s in studies]
    active_filter_set = bool(st.session_state.get("ast_studies_filter") or st.session_state.get("ast_o2_enabled"))

    with st.expander(t("ast_guide.filters_expander", lang), expanded=is_advanced or active_filter_set):
        selected = st.multiselect(t("ast.studies_filter", lang), studies, key="ast_studies_filter")
        st.caption(t("ast.mode_semantic", lang) if index.model is not None else t("ast.mode_lexical", lang))
        st.caption(f"{gemini_status['badge']} · {gemini_status['summary']}")
        with st.expander(t("ast.diag_title", lang), expanded=False):
            st.caption(t("ast.mode_caption", lang, mode=index.mode))

    with st.form("scientific-query"):
        question = st.text_area(
            t("ast.question_label", lang),
            help=t("ast.question_help", lang),
            key="ast_question_input",
        )
        with st.expander(t("ast.filters_expander", lang), expanded=is_advanced):
            c_o1, c_o2, c_o3 = st.columns(3)
            oxygen = c_o1.checkbox(t("ast.o2_check", lang), key="ast_o2_enabled")
            o2min = c_o2.number_input(t("ast.o2_min", lang), min_value=0.0, max_value=1.0, step=0.01, key="ast_o2_min")
            o2max = c_o3.number_input(t("ast.o2_max", lang), min_value=0.0, max_value=1.0, step=0.01, key="ast_o2_max")

            c_p1, c_p2, c_p3 = st.columns(3)
            pressure = c_p1.checkbox(t("ast.p_check", lang), key="ast_p_enabled")
            pmin = c_p2.number_input(t("ast.p_min", lang), min_value=0.0, key="ast_p_min")
            pmax = c_p3.number_input(t("ast.p_max", lang), min_value=0.0, key="ast_p_max")

            c_v1, c_v2, c_v3 = st.columns(3)
            velocity = c_v1.checkbox(t("ast.v_check", lang), key="ast_v_enabled")
            vmin = c_v2.number_input(t("ast.v_min", lang), key="ast_v_min")
            vmax = c_v3.number_input(t("ast.v_max", lang), key="ast_v_max")

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
        session_id = str(st.session_state.setdefault("_gemini_session_id", uuid4().hex[:12]))
        with st.spinner(t("ast.spinner", lang)):
            result = answer(
                question,
                index,
                study_ids=selected or None,
                numeric_filters=filters or None,
                language=lang,
                use_llm=bool(use_llm and has_llm),
                session_id=session_id,
            )
        st.session_state["scientific_answer"] = result
        st.session_state["scientific_query_context"] = {
            "question": question,
            "studies": ", ".join(selected) if selected else t("ast.all_studies", lang),
            "filters": filters,
        }

    saved_result = st.session_state.get("scientific_answer")
    if isinstance(saved_result, dict) and saved_result:
        st.header(t("ast.results_header", lang))
        context = st.session_state.get("scientific_query_context", {})
        if context:
            with st.chat_message("user"):
                st.caption(t("ast.last_query", lang, studies=context["studies"]))
                st.text(context["question"])
        with st.chat_message("assistant"):
            st.caption(t("ast.chat_assistant_label", lang))
            _render_evidence_summary(saved_result, experiments, lang)
            _render_matched_synthesis(saved_result, experiments, lang)
            # The assistant constructs this text and escapes source-authored Markdown.
            # Raw evidence remains inert st.text below; HTML is never enabled.
            st.markdown(saved_result.get("text", ""), unsafe_allow_html=False)
            for warning in saved_result.get("warnings", []):
                st.warning(translate_retrieval_warning(str(warning), lang))
            if is_advanced:
                st.caption(t("ast.mode_caption", lang, mode=saved_result.get("mode", "retrieval")))
        show_evidence(saved_result.get("evidence", []), experiments)


# ----------------------------------------------------------------------------- Compare


def _table_name_formatter(items: list[dict[str, Any]]) -> Callable[[int], str]:
    def _format(idx: int) -> str:
        return str(items[idx]["table"]["name"])

    return _format


def _set_compare_preset(study_ids: list[str], available: dict[str, Any]) -> None:
    st.session_state["cmp_selected_studies"] = [s for s in study_ids if s in available]


def show_comparison(experiments: list[dict]) -> None:
    lang = get_lang()
    st.title(t("cmp.title", lang))
    st.markdown(f"<p class='psi-lead'>{t('cmp.lead', lang)}</p>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(f"**{t('cmp.why_title', lang)}**")
        st.markdown(t("cmp.why_body", lang))

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
            table_indices: list[int] = list(range(len(available)))
            chosen = st.selectbox(
                t("cmp.choose_table", lang),
                table_indices,
                format_func=_table_name_formatter(available),
                key=f"compare-table-{study}",
            )
            idx = chosen if isinstance(chosen, int) and 0 <= chosen < len(available) else 0
            entry = available[idx]
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
    if "cmp_application" in st.session_state and st.session_state["cmp_application"] not in app_opts:
        st.session_state["cmp_application"] = "habitat"
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
    safe_application = application if application in app_opts else "habitat"
    question = st.text_input(t("cmp.query_label", lang), value="microgravity combustion", key="cmp_query")
    records = [{**r, "description": (r["experiment"] or {}).get("description", "")} for r in catalog(experiments)]
    ranked_rows = build_priority_ranking(records, query=question, application=safe_application, language=lang)
    for row in ranked_rows[:3]:
        with st.container(border=True):
            c_title, c_score = st.columns([3.0, 1.0], vertical_alignment="center")
            c_title.markdown(f"**#{row['rank']} · {row['study_id']} · {row['name']}**")
            c_title.caption(row["reasons_text"])
            c_score.metric(t("cmp.col_score", lang), f"{row['score']:.0f}/100")
            st.progress(min(1.0, max(0.0, row["score"] / 100.0)))
    st.dataframe(
        pd.DataFrame([
            {
                t("cmp.col_study", lang): r["study_id"],
                t("cmp.col_name", lang): r["name"],
                t("cmp.col_score", lang): r["score"],
                t("cmp.col_reasons", lang): "; ".join(r["reasons"]),
            }
            for r in ranked_rows
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
            st.markdown(t("src.sec1_body", lang,
                          studies=sum(_study(e).startswith("PSI-") for e in experiments),
                          files=sum(len(e.get("documents", [])) for e in experiments),
                          size=sum(d.get("size_bytes", 0) for e in experiments for d in e.get("documents", []))))
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
    if readonly:
        st.header(t("src.ingestion_title", lang))
        st.info(t("src.ingestion_readonly", lang))
    else:
        has_job = bool(st.session_state.get("ingestion_job_id"))
        with st.expander(t("src.ingestion_title", lang), expanded=has_job):
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

    saved_review = st.session_state.get("visual_review_result")
    if (
        saved_review is not None
        and hasattr(saved_review, "document_sha256")
        and saved_review.document_sha256 == digest
        and saved_review.page == page
    ):
        st.header(t("vis.candidate_header", lang))
        for warning in saved_review.warnings:
            st.warning(warning)
        st.caption(t("vis.candidate_status", lang, status=saved_review.status))
        if saved_review.status == "candidate":
            st.text(saved_review.description)
            st.text(saved_review.inference)
            for index, region in enumerate(saved_review.regions, 1):
                with st.expander(t("vis.region_label", lang, idx=index, kind=region.kind)):
                    st.caption(t("vis.region_coords_note", lang))
                    st.text(str(region.bbox))
                    st.text(region.description)
                    st.caption(t("vis.region_text_note", lang))
                    st.text(region.text_candidate)
            st.download_button(
                t("vis.download_json", lang),
                json.dumps(asdict(saved_review), ensure_ascii=False, indent=2).encode("utf-8"),
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
    """Inject centralized, responsive scientific styling from design_system."""
    inject_global_styles()


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
