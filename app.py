"""Streamlit entry point for PSI Flame Microgravity — bilingual public & local explorer."""

from __future__ import annotations

import os
from datetime import datetime
from io import BytesIO
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src import scientific_ui, views
from src.design_system import inject_global_styles, render_context_navigation_bar
from src.extractors import SCHEMA_VERSION, SUPPORTED_EXTENSIONS
from src.guided_journeys import TOTAL_STEPS, current_journey, stop_journey
from src.i18n import (
    DEFAULT_LANG,
    LANGUAGE_OPTIONS,
    SECTION_KEYS,
    get_lang,
    normalize_section,
    section_label,
    set_lang,
    status_label,
    t,
)
from src.local_jobs import enqueue_refresh_experiment, enqueue_uploads
from src.pipeline import ensure_scientific_bootstrap, is_public_readonly, job_status
from src.quantities import load_rules
from src.storage import (
    CONFIG_DIR,
    DATA_DIR,
    create_experiment,
    list_experiments,
    load_extraction,
    read_original,
    update_experiment,
    verify_original,
)

st.set_page_config(
    page_title="PSI Flame Microgravity",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="auto",
)

_SECRET_KEYS = (
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "GEMINI_MODEL",
    "RAG_BASE_URL",
    "RAG_MODEL",
    "RAG_API_KEY",
    "RAG_EMBEDDING_MODEL",
    "VLM_BASE_URL",
    "VLM_MODEL",
    "VLM_API_KEY",
    "PSI_READONLY_MODE",
)


def _sync_streamlit_secrets() -> None:
    """Propagate optional Streamlit Cloud secrets into process environment without overwriting."""
    try:
        secrets = st.secrets
        for key in _SECRET_KEYS:
            if not os.environ.get(key) and key in secrets:
                value = str(secrets[key]).strip()
                if value:
                    os.environ[key] = value
    except Exception:
        return


@st.cache_resource(show_spinner=False)
def _bootstrap_archive() -> dict:
    """Initialize SQLite scientific registry and search index once on cold start."""
    return ensure_scientific_bootstrap()


load_dotenv(Path(__file__).resolve().parent / ".env", override=False)
_sync_streamlit_secrets()
load_rules(CONFIG_DIR / "quantity_rules.json")
_bootstrap_archive()


def _date_label(value: str | None) -> str:
    if not value:
        return "—"
    try:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone(ZoneInfo("America/Sao_Paulo"))
        return parsed.strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return str(value)


def _bytes_label(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{value:.1f} GB"


def _format_experiment(experiment_id: str, experiment_map: dict[str, dict], lang: str | None = None) -> str:
    if experiment_id in experiment_map:
        exp = experiment_map[experiment_id]
        psi_id = exp.get("psi_id") or exp.get("study_id") or ""
        name = exp.get("name", experiment_id)
        return f"{psi_id} · {name}" if psi_id and not name.startswith(psi_id) else name
    return t("exp.select_placeholder", lang)


def _load_one(experiment: dict, document: dict) -> dict:
    return load_extraction(experiment, document)


def _default_experiment_id(experiments: list[dict]) -> str:
    for exp in experiments:
        if (exp.get("psi_id") or exp.get("study_id") or exp.get("id")) == "PSI-69":
            return str(exp["id"])
    return str(experiments[0]["id"]) if experiments else ""


def _on_language_change() -> None:
    set_lang(str(st.session_state.get("lang_selector", DEFAULT_LANG)))


def _toggle_language() -> None:
    next_code = "pt" if get_lang() == "en" else "en"
    set_lang(next_code)
    st.session_state["lang_selector"] = next_code


def _go_home() -> None:
    stop_journey()
    st.session_state["workspace_section"] = "home"


def _go_back() -> None:
    history = st.session_state.get("nav_history") or []
    if history:
        prev = history.pop()
        st.session_state["nav_history"] = history
        st.session_state["workspace_section"] = normalize_section(prev)
        st.session_state["_skip_nav_push"] = True
    else:
        _go_home()


def _show_overview(experiment: dict) -> None:
    lang = get_lang()
    readonly = is_public_readonly()
    documents = experiment.get("documents", [])
    pdf_count = sum(doc.get("extension") == ".pdf" for doc in documents)
    table_count = sum(doc.get("table_count", 0) for doc in documents)
    processed_count = sum(doc.get("status") in {"processado", "parcial"} for doc in documents)
    partial_count = sum(doc.get("status") == "parcial" for doc in documents)
    failed_count = sum(doc.get("status") == "erro" for doc in documents)
    total_size = sum(int(doc.get("size_bytes", 0)) for doc in documents)

    st.subheader(t("exp.tab_overview", lang))
    st.caption(
        t(
            "exp.created_updated",
            lang,
            created=_date_label(experiment.get("created_at")),
            updated=_date_label(experiment.get("updated_at")),
        )
    )
    if experiment.get("description"):
        st.write(experiment["description"])
    else:
        st.write(t("exp.no_desc", lang))

    metric_columns = st.columns(5)
    metric_columns[0].metric(t("exp.metric_docs", lang), len(documents))
    metric_columns[1].metric(t("exp.metric_pdfs", lang), pdf_count)
    metric_columns[2].metric(t("exp.metric_tables", lang), table_count)
    metric_columns[3].metric(t("exp.metric_extracted", lang), processed_count)
    metric_columns[4].metric(t("exp.metric_storage", lang), _bytes_label(total_size))

    if failed_count or partial_count:
        st.warning(t("exp.partial_warn", lang, failed=failed_count, partial=partial_count))
    elif documents:
        st.success(t("exp.ready_ok", lang))
    else:
        st.info(t("exp.no_docs_hint", lang))

    quality = views.quality_summary(experiment)
    if quality["tabelas"]:
        q1, q2, q3 = st.columns(3)
        q1.metric(t("exp.metric_blocks", lang), quality["dados"])
        q2.metric(t("exp.metric_alerts", lang), quality.get("aviso", 0), help=t("exp.metric_alerts_help", lang))
        q3.metric(t("exp.metric_notes", lang), quality.get("info", 0))

    views.show_study_overview(experiment)

    is_advanced = st.session_state.get("interaction_mode", "guided") == "advanced"
    if not readonly or documents:
        with st.expander(t("journey.open_advanced", lang), expanded=is_advanced):
            if not readonly:
                st.markdown(f"**{t('exp.local_folder', lang)}**")
                st.code(str(DATA_DIR / experiment["folder"]), language=None)
                with st.expander(t("exp.edit_meta", lang)):
                    with st.form(f"edit-{experiment['id']}"):
                        name = st.text_input(t("exp.edit_name", lang), value=experiment.get("name", ""))
                        description = st.text_area(t("exp.edit_desc", lang), value=experiment.get("description", ""), height=90)
                        submitted = st.form_submit_button(t("exp.save_btn", lang), type="primary")
                    if submitted:
                        try:
                            update_experiment(experiment, name, description)
                            st.rerun()
                        except ValueError as error:
                            st.error(str(error))

            if documents:
                st.markdown(f"**{t('exp.recent_files', lang)}**")
                recent = sorted(documents, key=lambda doc: doc.get("uploaded_at", ""), reverse=True)[:6]
                st.dataframe(
                    pd.DataFrame([
                        {
                            t("exp.col_file", lang): doc.get("name"),
                            t("exp.col_format", lang): doc.get("extension", "").lstrip(".").upper(),
                            t("exp.col_extraction", lang): status_label(doc.get("status"), lang),
                            t("exp.col_tables", lang): doc.get("table_count", 0),
                            t("exp.col_imported", lang): _date_label(doc.get("uploaded_at")),
                        }
                        for doc in recent
                    ]),
                    hide_index=True,
                    use_container_width=True,
                )


def _show_documents(experiment: dict) -> None:
    lang = get_lang()
    readonly = is_public_readonly()
    st.subheader(t("docs.title", lang))

    if readonly:
        st.info(t("docs.upload_disabled", lang))
    else:
        st.write(t("docs.upload_desc", lang))
        uploads = st.file_uploader(
            t("docs.select_files", lang),
            type=sorted(extension.lstrip(".") for extension in SUPPORTED_EXTENSIONS),
            accept_multiple_files=True,
            key=f"upload-{experiment['id']}",
            help=t("docs.upload_help", lang),
        )
        if st.button(t("docs.import_btn", lang), type="primary", disabled=not uploads, key=f"import-{experiment['id']}"):
            try:
                st.session_state[f"local-job-{experiment['id']}"] = enqueue_uploads(
                    experiment, [(uploaded.name, uploaded.getvalue()) for uploaded in uploads or []]
                )
            except ValueError as error:
                st.error(str(error))

        local_job = st.session_state.get(f"local-job-{experiment['id']}")
        if local_job:
            status = job_status(local_job)
            if status:
                if status["status"] in {"queued", "running"}:
                    st.info(t("docs.job_running", lang))
                    st.progress(float(status.get("progress", 0)))
                    if st.button(t("docs.job_refresh", lang), key=f"local-job-refresh-{experiment['id']}"):
                        views.clear_cache()
                        st.rerun()
                elif status["status"] == "completed":
                    st.success(t("docs.job_done", lang))
                elif status["status"] == "partial":
                    st.warning(t("docs.job_partial", lang))
                else:
                    st.error(t("docs.job_err", lang, status=status["status"], error=status.get("error") or ""))
                if status.get("result_json"):
                    with st.expander(t("docs.job_result", lang)):
                        st.json(status["result_json"])
            experiment = next((item for item in list_experiments() if item["id"] == experiment["id"]), experiment)

    documents = experiment.get("documents", [])
    if not documents:
        st.info(t("docs.no_docs", lang))
        return

    if not readonly:
        outdated = [doc for doc in documents if doc.get("schema_version", 1) < SCHEMA_VERSION]
        if outdated:
            st.warning(t("docs.outdated_warn", lang, count=len(outdated)))
            if st.button(t("docs.reprocess_all", lang), key=f"reprocess-all-{experiment['id']}"):
                st.session_state[f"local-job-{experiment['id']}"] = enqueue_refresh_experiment(
                    experiment, document_ids=[doc["id"] for doc in outdated], reextract=True
                )
                st.rerun()

    st.markdown(f"**{t('docs.index_header', lang)}**")
    st.dataframe(
        pd.DataFrame([
            {
                t("exp.col_file", lang): doc.get("name"),
                t("exp.col_format", lang): doc.get("extension", "").lstrip(".").upper(),
                t("docs.col_size", lang): _bytes_label(int(doc.get("size_bytes", 0))),
                t("docs.col_status", lang): status_label(doc.get("status"), lang),
                t("exp.col_tables", lang): doc.get("table_count", 0),
                t("docs.col_pages", lang): doc.get("page_count", 0),
                t("exp.col_imported", lang): _date_label(doc.get("uploaded_at")),
            }
            for doc in documents
        ]),
        hide_index=True,
        use_container_width=True,
    )

    st.markdown(f"**{t('docs.details_header', lang)}**")
    selected_id = st.selectbox(
        t("docs.select_doc", lang),
        options=[doc["id"] for doc in documents],
        format_func=lambda identifier: next(doc["name"] for doc in documents if doc["id"] == identifier),
        key=f"document-detail-{experiment['id']}",
    )
    document = next(doc for doc in documents if doc["id"] == selected_id)
    col_a, col_b = st.columns([3, 1])
    with col_a:
        st.caption(t("docs.sha_label", lang))
        st.code(document.get("sha256", ""), language=None)
    with col_b:
        if not readonly:
            if st.button(t("docs.reprocess_btn", lang), key=f"reprocess-{selected_id}"):
                try:
                    st.session_state[f"local-job-{experiment['id']}"] = enqueue_refresh_experiment(
                        experiment, document_ids=[selected_id], reextract=True
                    )
                    st.rerun()
                except (OSError, ValueError) as error:
                    st.error(str(error))
        if st.button(t("docs.verify_btn", lang), key=f"verify-{selected_id}"):
            try:
                if verify_original(experiment, document):
                    st.success(t("docs.verify_ok", lang))
                else:
                    st.error(t("docs.verify_fail", lang))
            except (OSError, ValueError) as error:
                st.error(t("docs.read_fail", lang, error=error))

    try:
        original = read_original(experiment, document)
        st.download_button(
            t("docs.download_original", lang),
            data=original,
            file_name=document["name"],
            mime="application/octet-stream",
            key=f"download-{selected_id}",
        )
        extraction = _load_one(experiment, document)
    except (OSError, ValueError, KeyError) as error:
        st.error(t("docs.open_fail", lang, error=error))
        return

    if document.get("extension") in {".jpg", ".jpeg", ".png", ".tif", ".tiff"}:
        try:
            st.image(BytesIO(original), caption=document["name"], use_container_width=True)
        except Exception:
            st.caption(t("docs.img_preview_err", lang))
    if extraction.get("warnings"):
        for warning in extraction["warnings"]:
            st.warning(warning)
    metadata = extraction.get("metadata", {})
    if metadata:
        with st.expander(t("docs.extracted_meta", lang)):
            st.json(metadata)
    if extraction.get("formulas"):
        with st.expander(t("docs.formulas_found", lang, count=len(extraction["formulas"]))):
            st.dataframe(pd.DataFrame(extraction["formulas"]), hide_index=True, use_container_width=True)
    preview = extraction.get("text", "")
    if preview:
        with st.expander(t("docs.extracted_text", lang)):
            st.text(preview[:12000] + (t("docs.preview_truncated", lang) if len(preview) > 12000 else ""))


def _show_data_explorer(experiments: list[dict]) -> None:
    lang = get_lang()
    readonly = is_public_readonly()
    scientific_ui.inject_dashboard_css()

    st.title(t("exp.title", lang))
    st.markdown(f"<p class='psi-lead'>{t('exp.subtitle', lang)}</p>", unsafe_allow_html=True)

    with st.expander(t("exp.glossary_title", lang), expanded=False):
        st.markdown(t("exp.glossary_body", lang))

    if readonly:
        st.info(t("exp.readonly_notice", lang))
    else:
        with st.expander(t("exp.manage_local", lang), expanded=False):
            with st.form("create-experiment", clear_on_submit=True):
                new_name = st.text_input(t("exp.new_name", lang), placeholder=t("exp.new_name_ph", lang))
                new_description = st.text_area(t("exp.new_desc", lang), placeholder=t("exp.new_desc_ph", lang), height=75)
                create = st.form_submit_button(t("exp.create_btn", lang), type="primary", use_container_width=True)
            if create:
                try:
                    created = create_experiment(new_name, new_description)
                    st.session_state["active_experiment_id"] = created["id"]
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))

    if not experiments:
        st.info(t("exp.empty_archive", lang))
        return

    experiment_map = {item["id"]: item for item in experiments}
    options = [item["id"] for item in experiments]
    if st.session_state.get("active_experiment_id") not in experiment_map:
        st.session_state["active_experiment_id"] = _default_experiment_id(experiments)

    selected_id = st.selectbox(
        t("exp.select_study", lang),
        options=options,
        format_func=lambda identifier: _format_experiment(identifier, experiment_map, lang),
        key="active_experiment_id",
    )
    experiment = experiment_map[selected_id]

    tabs = st.tabs([
        t("exp.tab_overview", lang),
        t("exp.tab_explorer", lang),
        t("exp.tab_tables", lang),
        t("exp.tab_docs", lang),
        t("exp.tab_pdf", lang),
        t("exp.tab_isa", lang),
    ])
    with tabs[0]:
        _show_overview(experiment)
    with tabs[1]:
        views.show_explorer(experiment)
    with tabs[2]:
        views.show_tables(experiment)
        st.divider()
        views.show_catalog(experiment)
    with tabs[3]:
        _show_documents(experiment)
    with tabs[4]:
        views.show_search(experiment)
    with tabs[5]:
        views.show_metadata(experiment)


def _return_to_journey() -> None:
    st.session_state["workspace_section"] = "home"


def main() -> None:
    st.session_state.setdefault("lang", DEFAULT_LANG)
    if "lang_selector" in st.session_state:
        set_lang(str(st.session_state["lang_selector"]))
    else:
        st.session_state["lang_selector"] = get_lang()

    lang = get_lang()
    inject_global_styles()
    st.session_state["workspace_section"] = normalize_section(st.session_state.get("workspace_section"))
    st.session_state.setdefault("interaction_mode", "guided")
    current_sec = st.session_state["workspace_section"]
    last_sec = st.session_state.get("_last_workspace_section")
    if last_sec and last_sec != current_sec:
        if st.session_state.pop("_skip_nav_push", False):
            pass
        else:
            history = list(st.session_state.get("nav_history") or [])
            if not history or history[-1] != last_sec:
                history.append(last_sec)
            st.session_state["nav_history"] = history[-10:]
    st.session_state["_last_workspace_section"] = current_sec

    experiments = list_experiments()
    readonly = is_public_readonly()
    jid, jstep = current_journey()

    with st.sidebar:
        st.markdown(f"## {t('app.title', lang)}")
        st.caption(t("app.subtitle", lang))
        st.radio(
            t("sidebar.language", lang),
            options=["en", "pt"],
            format_func=lambda code: LANGUAGE_OPTIONS[code],
            horizontal=True,
            key="lang_selector",
            on_change=_on_language_change,
        )
        st.divider()
        section = st.radio(
            t("sidebar.nav_label", lang),
            SECTION_KEYS,
            format_func=lambda key: section_label(key, lang),
            key="workspace_section",
        )
        st.divider()
        st.radio(
            t("sidebar.mode_label", lang),
            options=["guided", "advanced"],
            format_func=lambda mode: t(f"sidebar.mode_{mode}", lang),
            help=t("sidebar.mode_help", lang),
            key="interaction_mode",
        )
        if jid is not None:
            st.button(
                t("sidebar.exit_journey", lang),
                key="sidebar-exit-journey",
                use_container_width=True,
                on_click=stop_journey,
            )
        st.divider()
        st.caption(t("sidebar.readonly_badge", lang) if readonly else t("sidebar.local_badge", lang))
        st.caption(t("sidebar.footer_note", lang))

    active_j_label = (
        f"{t('journey.badge_' + ('j1' if jid == 'journey_1' else 'j2'), lang)} · {t('journey.step_indicator', lang, current=jstep, total=TOTAL_STEPS)}"
        if jid is not None and section == "home"
        else None
    )
    return_j_label = (
        t("sidebar.return_journey", lang, step=jstep, total=TOTAL_STEPS)
        if jid is not None and section != "home"
        else None
    )
    history_list = st.session_state.get("nav_history") or []
    render_context_navigation_bar(
        where_label=t("topbar.where", lang),
        current_location=section_label(section, lang),
        home_label=t("topbar.home", lang),
        back_label=t("topbar.back", lang),
        can_go_home=(section != "home" or jid is not None),
        on_go_home=_go_home,
        on_go_back=_go_back if (history_list or (jid is not None and section != "home")) else None,
        lang=lang,
        on_toggle_lang=_toggle_language,
        active_journey_label=active_j_label,
        return_journey_label=return_j_label,
        on_return_journey=_return_to_journey,
    )

    if section == "explorer":
        _show_data_explorer(experiments)
        return

    scientific_ui.show_section(section, experiments)


if __name__ == "__main__":
    main()
