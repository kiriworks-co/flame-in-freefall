"""Interactive, evidence-grounded guided journeys and chart explainers."""
from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

from . import extractors, storage
from .design_system import render_five_question_framework, style_scientific_figure
from .i18n import (
    evidence_label,
    get_lang,
    investigation_profile,
    normalize_section,
    quantity_label,
    t,
)
from .quantities import split_header

TOTAL_STEPS = 4


def extract_display_unit(col_name: str, meta: dict[str, Any] | None = None, language: str | None = None) -> str:
    """Resolve an axis unit from column metadata or raw NASA header suffixes."""
    unit = str((meta or {}).get("unit") or "").strip()
    if unit:
        return unit
    _, header_unit = split_header(col_name)
    if header_unit:
        return header_unit
    if ";" in col_name:
        suffix = col_name.split(";")[-1].strip()
        if suffix and len(suffix) <= 32:
            return suffix
    lower = col_name.lower()
    if "% by vol" in lower:
        return "% by vol"
    if "(ppm)" in lower:
        return "ppm"
    active = language or get_lang()
    return "unit not declared" if active == "en" else "unidade não declarada"


def chart_evidence_roles(entry: dict[str, Any], columns: list[str]) -> dict[str, str]:
    """Resolve exact selected-column provenance without promoting reported outcomes."""
    table = entry.get("table") or {}
    fallback = table.get("evidence_kind") or (entry.get("document") or {}).get("evidence_kind") or "unclassified"
    table_columns = table.get("columns", [])
    roles = {}
    for column in columns:
        index = table_columns.index(column) if column in table_columns else -1
        field = next((f for f in table.get("field_classification", []) if f.get("column_index") == index), None)
        roles[column] = str((field or {}).get("role") or (field or {}).get("evidence_kind") or fallback)
    return roles


def render_term_help(lang: str) -> None:
    """Render an optional plain-English/Portuguese glossary of core combustion terms."""
    with st.expander(t("chart_guide.term_help_title", lang), expanded=False):
        st.markdown(
            f"- **{t('glossary.microgravity_term', lang)}:** {t('glossary.microgravity_def', lang)}\n"
            f"- **{t('glossary.o2_term', lang)}:** {t('glossary.o2_def', lang)}\n"
            f"- **{t('glossary.drop_diam_term', lang)}:** {t('glossary.drop_diam_def', lang)}\n"
            f"- **{t('glossary.psi_term', lang)}:** {t('glossary.psi_def', lang)}"
        )


def render_chart_explanation(
    entry: dict[str, Any],
    x_col: str,
    y_cols: list[str],
    x_meta: dict[str, Any] | None,
    y_metas: list[dict[str, Any]],
    params: dict[str, Any] | None,
    experiment: dict[str, Any],
    lang: str,
) -> None:
    """Display a plain-language guide beside every interactive scientific plot."""
    study_id = str(experiment.get("psi_id") or experiment.get("id") or "NASA PSI")
    source_name = str(
        entry.get("document_name")
        or (entry.get("document") or {}).get("name")
        or (entry.get("table") or {}).get("name")
        or experiment.get("name")
        or study_id
    )
    selected_roles = chart_evidence_roles(entry, [x_col, *y_cols])
    role_text = " · ".join(f"{column}: {evidence_label(kind, lang)}" for column, kind in selected_roles.items())

    x_unit = extract_display_unit(x_col, x_meta, lang)
    y_parts = []
    for col, ym in zip(y_cols, y_metas):
        y_unit = extract_display_unit(col, ym, lang)
        qty = quantity_label(str(ym.get("quantity") or ""), lang)
        y_parts.append(f"`{col}` ({y_unit}; {qty})")
    y_summary = ", ".join(y_parts) if y_parts else "`value`"

    cautions = [t("chart_guide.caution_default", lang, study_id=study_id)]
    joined_names = " ".join([x_col, *y_cols]).lower()
    if "burning rate; mm" in joined_names:
        cautions.insert(0, t("chart_guide.caution_burning_mm", lang))

    mode_bits = []
    if params:
        if params.get("normalize") and params.get("normalize") != "nenhuma":
            mode_bits.append(f"normalize={params['normalize']}")
        if params.get("baseline") and params.get("baseline") != "nenhuma":
            mode_bits.append(f"baseline={params['baseline']}")
        if params.get("derived") and params.get("derived") not in ("nenhuma", "original"):
            mode_bits.append(f"derived={params['derived']}")
    if mode_bits:
        cautions.append(t("chart_guide.caution_series_mode", lang, mode=", ".join(mode_bits)))

    interpret_text = (
        t("chart_guide.note_condition_only", lang)
        if set(selected_roles.values()) == {"condition"}
        else t("chart_guide.note_trend", lang, x=x_col, y=", ".join(y_cols))
    )

    with st.container(border=True):
        st.markdown(f"#### {t('chart_guide.title', lang)}")
        st.markdown(
            f"- **{t('chart_guide.shows_label', lang)}** `{', '.join(y_cols)}` vs. `{x_col}`\n"
            f"- **{t('chart_guide.axes_label', lang)}** X: `{x_col}` (`{x_unit}`) · Y: {y_summary}\n"
            f"- **{t('chart_guide.source_label', lang)}** `{study_id}` · `{source_name}` — *{role_text}*\n"
            f"- **{t('chart_guide.interpret_label', lang)}** {interpret_text}\n"
            f"- **{t('chart_guide.caution_label', lang)}** {' '.join(cautions)}"
        )


def render_heatmap_explanation(entry: dict[str, Any], experiment: dict[str, Any], lang: str) -> None:
    """Render a plain-language guide below correlation heatmaps."""
    study_id = str(experiment.get("psi_id") or experiment.get("id") or "NASA PSI")
    source_name = str(
        entry.get("document_name")
        or (entry.get("document") or {}).get("name")
        or (entry.get("table") or {}).get("name")
        or experiment.get("name")
        or study_id
    )
    with st.container(border=True):
        st.markdown(f"#### {t('chart_guide.title', lang)}")
        st.markdown(
            f"- **{t('chart_guide.shows_label', lang)}** "
            f"{t('chart_guide.heatmap_shows', lang, dataset=source_name)}\n"
            f"- **{t('chart_guide.source_label', lang)}** `{study_id}` · `{source_name}`\n"
            f"- **{t('chart_guide.caution_label', lang)}** {t('chart_guide.heatmap_caution', lang)}"
        )


def _journey_steps() -> dict[str, int]:
    steps = st.session_state.setdefault("journey_steps", {})
    if not isinstance(steps, dict):
        steps = {}
        st.session_state["journey_steps"] = steps
    return steps


def current_journey() -> tuple[str | None, int]:
    """Return active journey id ('journey_1'|'journey_2'|None) and clamped step."""
    jid = st.session_state.get("active_journey")
    if jid not in {"journey_1", "journey_2"}:
        return None, 1
    steps = _journey_steps()
    step = int(steps.get(jid, 1) or 1)
    step = max(1, min(TOTAL_STEPS, step))
    steps[jid] = step
    return str(jid), step


def start_journey(journey_id: str, step: int = 1) -> None:
    """Activate a guided journey cleanly from Home or Journey handoffs."""
    steps = _journey_steps()
    steps[journey_id] = max(1, min(TOTAL_STEPS, int(step)))
    st.session_state["active_journey"] = journey_id
    st.session_state["workspace_section"] = "home"


def stop_journey() -> None:
    """Exit guided journey back to the Discovery Home page."""
    st.session_state["active_journey"] = None
    st.session_state["workspace_section"] = "home"


def _step_delta(journey_id: str, delta: int) -> None:
    steps = _journey_steps()
    curr = int(steps.get(journey_id, 1) or 1)
    steps[journey_id] = max(1, min(TOTAL_STEPS, curr + delta))
    st.session_state["active_journey"] = journey_id


def open_study_from_journey(
    section_key: str,
    study_id: str | None = None,
    experiments: list[dict[str, Any]] | None = None,
    preset_question: str | None = None,
) -> None:
    """Navigate to an advanced section while preserving active journey return state."""
    target = normalize_section(section_key)
    st.session_state["workspace_section"] = target
    if study_id and experiments:
        for exp in experiments:
            if exp.get("psi_id") == study_id or exp.get("id") == study_id:
                st.session_state["active_experiment_id"] = exp["id"]
                break
    if target == "assistant" and preset_question:
        st.session_state["ast_question_input"] = preset_question
        st.session_state["ast_studies_filter"] = [study_id] if study_id else []
        st.session_state["ast_o2_enabled"] = False
        st.session_state["ast_pending_autorun"] = True


def _find_experiment(experiments: list[dict[str, Any]], psi_id: str) -> dict[str, Any] | None:
    for exp in experiments:
        if exp.get("psi_id") == psi_id or exp.get("id") == psi_id:
            return exp
    return None


@st.cache_data(show_spinner=False, max_entries=8)
def _cached_pdf_page_png(exp_id: str, doc_name: str, page_number: int, dpi: int = 135) -> bytes | None:
    for exp in storage.list_experiments():
        if exp.get("id") == exp_id:
            for doc in exp.get("documents", []):
                if doc.get("name") == doc_name:
                    try:
                        raw = storage.read_original(exp, doc)
                        return extractors.render_pdf_page(raw, page_number, dpi=dpi)
                    except Exception:
                        return None
    return None


@st.cache_data(show_spinner=False, max_entries=12)
def _cached_evidence_snippets(query: str, study_id: str, limit: int = 3) -> list[dict[str, Any]]:
    from .retrieval import RetrievalIndex

    db_path = storage.PROJECT_DIR / "data" / "search.sqlite3"
    if not db_path.exists():
        return []
    try:
        idx = RetrievalIndex(db_path)
        hits = idx.search(query, study_ids=[study_id] if study_id else None, limit=limit)
        out: list[dict[str, Any]] = []
        for h in hits:
            out.append(
                {
                    "study_id": str(h.get("study_id") or study_id),
                    "document_name": str(h.get("document_name") or ""),
                    "page": h.get("page"),
                    "row": h.get("row"),
                    "evidence_kind": str(h.get("evidence_kind") or "document_context"),
                    "text": str(h.get("text") or "").strip(),
                    "sha256": str(h.get("sha256") or ""),
                    "doi": str(h.get("doi") or ""),
                    "score": float(h.get("score") or 0.0),
                }
            )
        return out
    except Exception:
        return []


def _load_primary_csv_entry(
    experiment: dict[str, Any] | None,
) -> tuple[dict[str, Any] | None, pd.DataFrame, list[dict[str, Any]]]:
    if not experiment:
        return None, pd.DataFrame(), []
    from .views import collect_entries, entry_frame

    entries = collect_entries(experiment)
    if not entries:
        return None, pd.DataFrame(), []
    csv_entry = next(
        (e for e in entries if str(e.get("document_name", "")).lower().endswith(".csv")),
        entries[0],
    )
    df, metas = entry_frame(csv_entry, entries, experiment.get("column_overrides") or {})
    return csv_entry, df, metas


def _render_evidence_cards(snippets: list[dict[str, Any]], lang: str) -> None:
    if not snippets:
        st.info(t("ast.no_evidence", lang))
        return
    for item in snippets:
        ev = evidence_label(item["evidence_kind"], lang)
        loc = []
        if item.get("page"):
            loc.append(f"p. {item['page']}")
        if item.get("row"):
            loc.append(f"row {item['row']}")
        loc_txt = f" · {', '.join(loc)}" if loc else ""
        with st.container(border=True):
            st.caption(f"**{item['study_id']}** · `{item['document_name']}`{loc_txt} · {ev}")
            excerpt = item["text"]
            st.markdown(excerpt[:420] + ("…" if len(excerpt) > 420 else ""))
            if item.get("sha256"):
                st.caption(f"SHA-256: `{item['sha256'][:16]}…`")


def _render_step_header(journey_id: str, step: int, title_key: str, purpose_key: str, lang: str) -> None:
    badge_key = "journey.badge_j1" if journey_id == "journey_1" else "journey.badge_j2"
    st.caption(f"{t(badge_key, lang)} · **{t('journey.step_indicator', lang, current=step, total=TOTAL_STEPS)}**")
    st.progress(step / TOTAL_STEPS)
    st.title(t(title_key, lang))
    st.info(t(purpose_key, lang))


def _render_step_footer(journey_id: str, step: int, lang: str) -> None:
    st.divider()
    c1, c2, c3, c4 = st.columns([1.2, 1.4, 1.3, 1.2])
    c1.button(
        t("journey.back", lang),
        key=f"gj_{journey_id}_back_{step}",
        disabled=step <= 1,
        use_container_width=True,
        on_click=_step_delta,
        args=(journey_id, -1),
    )
    c2.button(
        t("journey.exit", lang),
        key=f"gj_{journey_id}_exit_{step}",
        use_container_width=True,
        on_click=stop_journey,
    )
    c3.button(
        t("journey.restart", lang),
        key=f"gj_{journey_id}_restart_{step}",
        use_container_width=True,
        on_click=start_journey,
        args=(journey_id, 1),
    )
    c4.button(
        t("journey.continue", lang),
        key=f"gj_{journey_id}_next_{step}",
        type="primary",
        disabled=step >= TOTAL_STEPS,
        use_container_width=True,
        on_click=_step_delta,
        args=(journey_id, 1),
    )


def _five_q_labels(lang: str) -> dict[str, str]:
    return {
        "exploring": t("journey.q_exploring", lang),
        "why_matters": t("journey.q_why_matters", lang),
        "evidence_shows": t("journey.q_evidence_shows", lang),
        "conclusion": t("journey.q_conclusion", lang),
        "limitations": t("journey.q_limitations", lang),
    }


def _render_step_five_questions(prefix: str, lang: str) -> None:
    render_five_question_framework(
        heading=t("journey.q_heading", lang),
        q_labels=_five_q_labels(lang),
        exploring=t(f"{prefix}_q_exploring", lang),
        why_matters=t(f"{prefix}_q_why", lang),
        evidence_shows=t(f"{prefix}_q_evidence", lang),
        conclusion=t(f"{prefix}_q_conclude", lang),
        limitations=t(f"{prefix}_q_limits", lang),
    )


def _render_scatter_from_columns(
    df: pd.DataFrame,
    metas: list[dict[str, Any]],
    entry: dict[str, Any],
    experiment: dict[str, Any],
    x_col: str,
    y_col: str,
    color_col: str | None,
    lang: str,
) -> None:
    if df.empty or x_col not in df.columns or y_col not in df.columns:
        st.info(t("j1.s3_chart_missing", lang))
        return
    work = df.copy()
    work[x_col] = pd.to_numeric(work[x_col], errors="coerce")
    work[y_col] = pd.to_numeric(work[y_col], errors="coerce")
    work = work.dropna(subset=[x_col, y_col])
    if work.empty:
        st.info(t("j1.s3_chart_missing", lang))
        return

    meta_by_name = {str(m["name"]): m for m in metas}
    x_meta = meta_by_name.get(x_col)
    y_meta = meta_by_name.get(y_col, {"name": y_col, "unit": "", "quantity": "unknown"})
    x_unit = extract_display_unit(x_col, x_meta)
    y_unit = extract_display_unit(y_col, y_meta)
    use_color = color_col if (color_col and color_col in work.columns) else None
    fig = px.scatter(
        work,
        x=x_col,
        y=y_col,
        color=use_color,
        template="plotly_white",
        labels={x_col: f"{x_col} ({x_unit})", y_col: f"{y_col} ({y_unit})"},
    )
    style_scientific_figure(fig, title=f"{experiment.get('psi_id', 'NASA PSI')} · {y_col}", height=400)
    st.plotly_chart(fig, use_container_width=True)
    render_chart_explanation(entry, x_col, [y_col], x_meta, [y_meta], None, experiment, lang)
    render_term_help(lang)


def _render_journey_1(experiments: list[dict[str, Any]], step: int, lang: str) -> None:
    psi69 = _find_experiment(experiments, "PSI-69")
    nasa_ctx = _find_experiment(experiments, "NASA-CONTEXT")

    if step == 1:
        _render_step_header("journey_1", step, "j1.s1_title", "j1.s1_purpose", lang)
        st.markdown(t("j1.s1_explain", lang))
        c1, c2 = st.columns(2, gap="large")
        with c1.container(border=True):
            st.subheader(t("home.earth_title", lang))
            st.markdown(t("home.earth_points", lang))
        with c2.container(border=True):
            st.subheader(t("home.space_title", lang))
            st.markdown(t("home.space_points", lang))

        st.subheader(t("j1.s1_callout_title", lang))
        aspects = ["shape", "o2", "temp", "smoke"]
        chosen = st.radio(
            t("j1.s1_aspect_label", lang),
            options=aspects,
            format_func=lambda code: t(f"j1.s1_aspect_{code}", lang),
            horizontal=True,
            key="gj_j1_s1_aspect",
        )
        with st.container(border=True):
            st.markdown(t(f"j1.s1_desc_{chosen}", lang))
        _render_step_five_questions("j1.s1", lang)
        render_term_help(lang)

    elif step == 2:
        _render_step_header("journey_1", step, "j1.s2_title", "j1.s2_purpose", lang)
        st.markdown(t("j1.s2_explain", lang))
        left, right = st.columns([1.05, 1.0], gap="large")
        with left:
            prof = investigation_profile("PSI-69", lang)
            with st.container(border=True):
                st.markdown("**PSI-69 · FLEX**")
                if prof.get("objective"):
                    st.markdown(f"**{t('inv.objective_label', lang)}:** {prof['objective']}")
                if prof.get("relevance"):
                    st.markdown(f"**{t('inv.relevance_label', lang)}:** {prof['relevance']}")
                if prof.get("caveat"):
                    st.warning(f"**{t('inv.caveat_label', lang)}:** {prof['caveat']}")
            st.button(
                t("j1.s2_btn_explorer", lang),
                key="gj_j1_s2_open_psi69",
                on_click=open_study_from_journey,
                args=("explorer", "PSI-69", experiments),
            )
        with right:
            png = None
            caption = ""
            if nasa_ctx:
                for doc in nasa_ctx.get("documents", []):
                    if doc.get("name") == "researchers_guide.pdf" and int(doc.get("page_count") or 0) >= 36:
                        png = _cached_pdf_page_png(str(nasa_ctx["id"]), "researchers_guide.pdf", 36)
                        caption = t("j1.s2_pdf_caption", lang, page=36)
                        break
            if png is None and psi69:
                for doc in psi69.get("documents", []):
                    if str(doc.get("name", "")).lower().endswith(".pdf"):
                        png = _cached_pdf_page_png(str(psi69["id"]), str(doc["name"]), 1)
                        caption = f"{doc['name']} (p. 1)"
                        break
            if png:
                st.image(png, caption=caption, use_container_width=True)
            else:
                st.info(t("j1.s2_pdf_unavailable", lang))
        _render_step_five_questions("j1.s2", lang)

    elif step == 3:
        _render_step_header("journey_1", step, "j1.s3_title", "j1.s3_purpose", lang)
        st.markdown(t("j1.s3_explain", lang))
        view_mode = st.radio(
            t("j1.s3_view_label", lang),
            options=["extinction", "burning"],
            format_func=lambda code: t(f"j1.s3_opt_{code}", lang),
            key="gj_j1_s3_view",
        )
        entry, df, metas = _load_primary_csv_entry(psi69)
        if psi69 and entry is not None and not df.empty:
            y_col = (
                "Visible flame extinction diameter; mm"
                if view_mode == "extinction"
                else "Burning rate; mm"
            )
            _render_scatter_from_columns(
                df,
                metas,
                entry,
                psi69,
                "O initial ambient composition; mole fraction",
                y_col,
                "Fuel",
                lang,
            )
        else:
            st.info(t("j1.s3_chart_missing", lang))

        st.subheader(t("j1.s3_evidence_title", lang))
        snippets = _cached_evidence_snippets("FLEX droplet extinction oxygen cool flame", "PSI-69", limit=3)
        _render_evidence_cards(snippets, lang)
        _render_step_five_questions("j1.s3", lang)

    else:
        _render_step_header("journey_1", step, "j1.s4_title", "j1.s4_purpose", lang)
        c1, c2 = st.columns(2, gap="large")
        with c1.container(border=True):
            st.subheader(t("j1.s4_learned_title", lang))
            st.markdown(t("j1.s4_learned_body", lang))
        with c2.container(border=True):
            st.subheader(t("j1.s4_limits_title", lang))
            st.markdown(t("j1.s4_limits_body", lang))
        _render_step_five_questions("j1.s4", lang)

        st.subheader(t("j1.s4_next_title", lang))
        b1, b2, b3 = st.columns(3)
        b1.button(
            t("j1.s4_btn_j2", lang),
            type="primary",
            key="gj_j1_to_j2",
            use_container_width=True,
            on_click=start_journey,
            args=("journey_2", 1),
        )
        b2.button(
            t("j1.s4_btn_assistant", lang),
            key="gj_j1_to_assistant",
            use_container_width=True,
            on_click=open_study_from_journey,
            args=("assistant", "PSI-69", experiments, "How does oxygen mole fraction relate to droplet extinction in FLEX (PSI-69)?"),
        )
        b3.button(
            t("j1.s4_btn_explorer", lang),
            key="gj_j1_to_explorer",
            use_container_width=True,
            on_click=open_study_from_journey,
            args=("explorer", "PSI-69", experiments),
        )

    _render_step_footer("journey_1", step, lang)


def _render_journey_2(experiments: list[dict[str, Any]], step: int, lang: str) -> None:
    psi25 = _find_experiment(experiments, "PSI-25")
    psi69 = _find_experiment(experiments, "PSI-69")
    psi102 = _find_experiment(experiments, "PSI-102")

    if step == 1:
        _render_step_header("journey_2", step, "j2.s1_title", "j2.s1_purpose", lang)
        st.markdown(t("j2.s1_explain", lang))
        with st.container(border=True):
            st.markdown(t("j2.s1_risk_cards", lang))
        _render_step_five_questions("j2.s1", lang)
        render_term_help(lang)

    elif step == 2:
        _render_step_header("journey_2", step, "j2.s2_title", "j2.s2_purpose", lang)
        pillar = st.radio(
            t("j2.s2_pillar_select", lang),
            options=["prevention", "detection", "suppression"],
            format_func=lambda code: t(f"home.pillar_{code}", lang),
            horizontal=True,
            key="gj_j2_s2_pillar",
        )
        with st.container(border=True):
            st.markdown(t(f"j2.s2_pillar_{pillar}_detail", lang))

        matched = [
            exp
            for exp in experiments
            if investigation_profile(str(exp.get("psi_id") or ""), "en").get("pillar", "").casefold() == pillar
        ]
        st.caption(t("j2.s2_loaded_studies", lang, count=len(matched)))
        if matched:
            cols = st.columns(min(3, len(matched)))
            for idx, exp in enumerate(matched):
                sid = str(exp.get("psi_id") or exp.get("id"))
                with cols[idx % len(cols)].container(border=True):
                    st.markdown(f"**{sid}**")
                    st.caption(str(exp.get("name", "")))
                    st.button(
                        t("inv.btn_open", lang),
                        key=f"gj_j2_s2_open_{sid}",
                        on_click=open_study_from_journey,
                        args=("explorer", sid, experiments),
                    )
        _render_step_five_questions("j2.s2", lang)

    elif step == 3:
        _render_step_header("journey_2", step, "j2.s3_title", "j2.s3_purpose", lang)
        focus = st.radio(
            t("j2.s3_focus_label", lang),
            options=["bass", "same", "compare"],
            format_func=lambda code: t(f"j2.s3_focus_{code}", lang),
            key="gj_j2_s3_focus",
        )
        if focus == "bass":
            entry, df, metas = _load_primary_csv_entry(psi25)
            if psi25 and entry is not None and not df.empty:
                _render_scatter_from_columns(
                    df,
                    metas,
                    entry,
                    psi25,
                    "Calibrated  initial O2 % by vol",
                    "Final CO2 % by vol",
                    "Fuel Sample Material",
                    lang,
                )
            else:
                st.info(t("j1.s3_chart_missing", lang))
            snippets = _cached_evidence_snippets("BASS-II solid fuel airflow oxygen", "PSI-25", limit=2)
            _render_evidence_cards(snippets, lang)

        elif focus == "same":
            c_left, c_right = st.columns([1.05, 1.0], gap="large")
            with c_left:
                png = None
                if psi102:
                    report = "PSI-102_Reports_SAME_Final Science Report.pdf"
                    png = _cached_pdf_page_png(str(psi102["id"]), report, 13)
                if png:
                    st.image(png, caption=t("j2.s3_same_pdf_caption", lang, page=13), use_container_width=True)
                else:
                    st.info(t("j1.s2_pdf_unavailable", lang))
            with c_right:
                _entry, df_same, _m = _load_primary_csv_entry(psi102)
                if not df_same.empty:
                    st.markdown("**PSI-102_Experimental table_SAME.csv**")
                    st.dataframe(df_same, use_container_width=True, hide_index=True)
                snippets = _cached_evidence_snippets("SAME smoke aerosol particle diameter detector", "PSI-102", limit=2)
                _render_evidence_cards(snippets, lang)

        else:
            st.warning(t("j2.s3_compare_callout", lang))
            c1, c2 = st.columns(2, gap="large")
            for col, study_exp, sid in [(c1, psi25, "PSI-25"), (c2, psi69, "PSI-69")]:
                with col.container(border=True):
                    prof = investigation_profile(sid, lang)
                    st.markdown(f"### {sid} · {(study_exp or {}).get('name', sid)}")
                    st.markdown(f"**{t('inv.objective_label', lang)}:** {prof.get('objective', '')}")
                    if prof.get("caveat"):
                        st.caption(prof["caveat"])
        _render_step_five_questions("j2.s3", lang)

    else:
        _render_step_header("journey_2", step, "j2.s4_title", "j2.s4_purpose", lang)
        c1, c2 = st.columns(2, gap="large")
        with c1.container(border=True):
            st.subheader(t("j2.s4_findings_title", lang))
            st.markdown(t("j2.s4_findings_body", lang))
        with c2.container(border=True):
            st.subheader(t("j2.s4_caveats_title", lang))
            st.markdown(t("j2.s4_caveats_body", lang))
        _render_step_five_questions("j2.s4", lang)

        st.subheader(t("j2.s4_next_title", lang))
        b1, b2, b3 = st.columns(3)
        b1.button(
            t("j2.s4_btn_compare", lang),
            type="primary",
            key="gj_j2_to_compare",
            use_container_width=True,
            on_click=open_study_from_journey,
            args=("compare", "PSI-25", experiments),
        )
        b2.button(
            t("j2.s4_btn_assistant", lang),
            key="gj_j2_to_assistant",
            use_container_width=True,
            on_click=open_study_from_journey,
            args=(
                "assistant",
                "PSI-102",
                experiments,
                "What does SAME (PSI-102) show about microgravity smoke aerosol particles?",
            ),
        )
        b3.button(
            t("j2.s4_btn_explorer", lang),
            key="gj_j2_to_explorer",
            use_container_width=True,
            on_click=open_study_from_journey,
            args=("explorer", "PSI-25", experiments),
        )

    _render_step_footer("journey_2", step, lang)


def render_active_journey(experiments: list[dict[str, Any]]) -> bool:
    """Render Journey 1 or Journey 2 when active. Returns True if handled."""
    jid, step = current_journey()
    if jid is None:
        return False
    lang = get_lang()
    if jid == "journey_1":
        _render_journey_1(experiments, step, lang)
        return True
    if jid == "journey_2":
        _render_journey_2(experiments, step, lang)
        return True
    return False
