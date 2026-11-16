"""Study data explorer views: overview, catalog, interactive charts, tables, PDF reader, and ISA-Tab metadata."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from . import storage
from .analysis import DERIVED_OPS, common_grid, derive_column, final_point, fit_linear, peak_info, prepare_series
from .challenge_engine import build_spacecraft_interpretation, build_study_summary
from .crossref import build_crossref
from .design_system import render_pillar_badge, style_scientific_figure
from .extractors import render_pdf_page
from .frames import axis_label, suggest_chart, table_to_frame
from .i18n import (
    chart_label,
    evidence_label,
    get_lang,
    quantity_label,
    t,
    translate_quality_flag,
)
from .pipeline import is_public_readonly
from .search import search_content

CHART_KEYS = ["line", "line_pts", "scatter", "bar", "heatmap", "xyc"]
_DEFAULT_CHART = {
    "time_series": "line",
    "spatial_profile": "line",
    "limit_curve": "line_pts",
    "parametric": "line_pts",
    "matrix": "heatmap",
    "distribution": "scatter",
}
_BASELINE_KEYS = ["nenhuma", "mínimo", "primeiros N"]
_BASELINE_TRANS = {
    "nenhuma": "view.baseline_none",
    "mínimo": "view.baseline_min",
    "primeiros N": "view.baseline_first",
}
_NORM_KEYS = ["nenhuma", "pico", "mín-máx"]
_NORM_TRANS = {
    "nenhuma": "view.norm_none",
    "pico": "view.norm_peak",
    "mín-máx": "view.norm_minmax",
}
_DERIVED_EN = {
    "quadrado (A²)": "square (A²)",
    "razão (A/B)": "ratio (A/B)",
    "diferença (A−B)": "difference (A−B)",
    "produto (A×B)": "product (A×B)",
    "escala (A×k)": "scale (A×k)",
    "derivada dA/dB": "derivative dA/dB",
}


def _derived_label(op: str, lang: str) -> str:
    return _DERIVED_EN.get(op, op) if lang == "en" else op


# ----------------------------------------------------------------------------- data access


@st.cache_data(show_spinner=False)
def _read_extraction(path: str, mtime: float) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def clear_cache() -> None:
    _read_extraction.clear()


def cached_extraction(experiment: dict, document: dict) -> dict[str, Any]:
    path = storage.extraction_file(experiment, document)
    return _read_extraction(str(path), path.stat().st_mtime)


def collect_entries(experiment: dict) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for document in experiment.get("documents", []):
        if document.get("status") == "erro":
            continue
        try:
            extraction = cached_extraction(experiment, document)
        except (OSError, ValueError, KeyError):
            continue
        for index, table in enumerate(extraction.get("tables", [])):
            entries.append({"key": storage.table_key(document, index), "document": document, "index": index, "table": table})
    return entries


def _label(entry: dict[str, Any], lang: str | None = None) -> str:
    active = lang or get_lang()
    return f"{entry['document']['name'][:30]} › {entry['table']['name']} ({t('view.rows_suffix', active, rows=len(entry['table']['rows']))})"


def paired_y_columns(meta: list[dict[str, Any]], x: str) -> list[str]:
    """Keep repeated source time axes paired with their own adjacent data series.

    NASA wide tables can place time/Q and a separately sampled time/Q pair on
    the same row. Matching row numbers do not make those time bases equal.
    """
    numeric = [m for m in meta if m.get("kind") in {"numeric", "range"} and m.get("n_numeric", 0)]
    selected = next((m for m in numeric if m["name"] == x), None)
    if selected is None:
        return []
    axes = [m["name"] for m in numeric if m.get("quantity") == "time"]
    if x in axes and len(axes) > 1:
        names = [m["name"] for m in numeric]
        start = names.index(x) + 1
        end = next((j for j in range(start, len(names)) if names[j] in axes), len(names))
        return names[start:end]
    return [m["name"] for m in numeric if m["name"] != x]


def _series_kind(table: dict[str, Any], column: str) -> str:
    columns = table.get("columns", [])
    index = columns.index(column) if column in columns else -1
    field: dict[str, Any] = next((f for f in table.get("field_classification", []) if f.get("column_index") == index), {})
    return str(field.get("role") or field.get("evidence_kind") or table.get("evidence_kind", "unclassified"))


def comparable_plot_axes(prepared: list[dict[str, Any]]) -> bool:
    """Overlay only explicitly matching physical axes; never guess missing units."""
    signatures = []
    for item in prepared:
        by_name = {m["name"]: m for m in item["meta"]}
        for y in item["ys"]:
            axes = [by_name.get(item["x"], {}), by_name.get(y, {})]
            signatures.append(tuple((m.get("quantity"), m.get("unit")) for m in axes))
    if len(signatures) <= 1:
        return True
    return all(q not in {None, "unknown"} and unit for signature in signatures for q, unit in signature) and all(
        signature == signatures[0] for signature in signatures[1:]
    )


def _load_effective_overrides(experiment: dict) -> dict[str, Any]:
    if is_public_readonly():
        return dict(st.session_state.get(f"session_overrides_{experiment['id']}", {}))
    return storage.load_overrides(experiment)


def entry_frame(entry: dict[str, Any], entries: list[dict[str, Any]], overrides: dict[str, Any]):
    def resolve(spec: dict[str, Any]):
        for other in entries:
            if other["document"]["sha256"] == entry["document"]["sha256"] and other["table"]["name"] == spec.get("table"):
                raw, _ = table_to_frame(other["table"])
                return raw[spec["column"]] if spec.get("column") in raw.columns else None
        return None

    return table_to_frame(entry["table"], overrides.get(entry["key"]), resolve)


def quality_summary(experiment: dict) -> dict[str, int]:
    counts = {"aviso": 0, "info": 0, "tabelas": 0, "dados": 0}
    for entry in collect_entries(experiment):
        counts["tabelas"] += 1
        counts["dados"] += entry["table"].get("block", {}).get("kind") == "data"
        for flag in entry["table"].get("flags", []):
            counts[flag["level"]] = counts.get(flag["level"], 0) + 1
    return counts


# ----------------------------------------------------------------------------- study overview tab


def show_study_overview(experiment: dict) -> None:
    """Display descriptive statistical summary and physical quantities for the selected study."""
    lang = get_lang()
    documents = experiment.get("documents", [])
    entries = collect_entries(experiment)
    data_entries = [entry for entry in entries if entry["table"].get("block", {}).get("kind") == "data"]
    overrides = _load_effective_overrides(experiment)

    total_tables = len(data_entries)
    total_rows = sum(len(entry["table"].get("rows", [])) for entry in data_entries)
    quantities = sorted({
        quantity_label(meta.get("quantity"), lang)
        for entry in data_entries
        for meta in entry["table"].get("column_meta", [])
        if meta.get("quantity") not in (None, "unknown") and meta.get("n_numeric", 0) > 0
    })

    st.subheader(t("view.overview_heading", lang))
    if experiment.get("description"):
        st.write(experiment["description"])
    else:
        st.info(t("view.no_description", lang))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t("exp.metric_docs", lang), len(documents))
    c2.metric(t("view.metric_datasets", lang), total_tables)
    c3.metric(t("view.metric_rows", lang), total_rows)
    c4.metric(t("view.metric_quantities", lang), len(quantities))

    if quantities:
        st.markdown(f"**{t('view.quantities_identified', lang)}**")
        st.write(" · ".join(quantities))

    # Chart-first Visual First Look + SUMMARIZE / INTERPRET synthesis
    preview_entry = next(
        (
            e
            for e in data_entries
            if sum(1 for m in e["table"].get("column_meta", []) if m.get("kind") in ("numeric", "range") and m.get("n_numeric", 0) > 0) >= 2
        ),
        None,
    )
    if preview_entry is not None:
        p_frame, p_meta = entry_frame(preview_entry, entries, overrides)
        numeric_cols = [c for c in p_frame.columns if pd.api.types.is_numeric_dtype(p_frame[c])]
        if len(numeric_cols) >= 2:
            suggestion = suggest_chart(p_meta, len(p_frame), "data")
            raw_x = suggestion.get("x")
            px_col = str(raw_x) if isinstance(raw_x, str) and raw_x in numeric_cols else str(numeric_cols[0])
            py_candidates = [str(c) for c in suggestion.get("y", []) if c in numeric_cols and c != px_col]
            paired = paired_y_columns(p_meta, px_col)
            py_candidates = [c for c in py_candidates if c in paired]
            py_col = py_candidates[0] if py_candidates else next(iter(paired), None)
            if py_col:
                work = p_frame[[px_col, py_col]].dropna()
                if not work.empty:
                    st.divider()
                    st.subheader(t("view.overview_preview_title", lang))
                    st.caption(t("view.overview_preview_caption", lang))
                    st.caption(t("view.evidence_nature", lang, kind=evidence_label(_series_kind(preview_entry["table"], py_col), lang)))
                    meta_map = {m["name"]: m for m in p_meta}
                    xm = meta_map.get(px_col)
                    ym = meta_map.get(py_col, {"name": py_col, "unit": "", "quantity": "unknown"})
                    preview_fig = px.scatter(
                        work,
                        x=px_col,
                        y=py_col,
                        labels={px_col: axis_label(xm) if xm else px_col, py_col: axis_label(ym)},
                    )
                    style_scientific_figure(
                        preview_fig,
                        title=f"{experiment.get('psi_id') or experiment.get('name', 'Study')} · {py_col} vs {px_col}",
                        height=360,
                    )
                    st.plotly_chart(preview_fig, use_container_width=True)
                    from .guided_journeys import render_chart_explanation

                    render_chart_explanation(preview_entry, px_col, [py_col], xm, [ym], None, experiment, lang)

    summary_card = build_study_summary(experiment, lang)
    interp_card = build_spacecraft_interpretation(experiment, lang)
    with st.container(border=True):
        s_col, i_col = st.columns(2, gap="medium")
        with s_col:
            render_pillar_badge(summary_card["pillar"])
            st.markdown(f"**{t('hub.tab_summarize', lang)}**")
            if summary_card["objective"]:
                st.write(summary_card["objective"])
            st.caption(f"{t('hub.summarize_coverage', lang)}: {summary_card['archive_coverage']}")
        with i_col:
            st.markdown(f"**{t('hub.tab_interpret', lang)}**")
            st.markdown(f"- **{t('hub.interpret_obs', lang)}:** {interp_card['observation_scope']}")
            st.markdown(f"- **{t('hub.interpret_impl', lang)}:** {interp_card['engineering_implication']}")
            st.caption(f"**{t('hub.interpret_limit', lang)}:** {interp_card['scientific_boundary']}")

    st.divider()
    st.subheader(t("view.isa_objective_heading", lang))
    isa_records = []
    for document in documents:
        if document.get("status") == "erro":
            continue
        try:
            isa = cached_extraction(experiment, document).get("isa")
            if isa:
                isa_records.append((document, isa))
        except (OSError, ValueError, KeyError):
            continue

    if isa_records:
        for document, isa in isa_records:
            study = isa.get("study", {})
            comments = isa.get("comments", {})
            title = comments.get("Proposal Title") or study.get("title") or t("view.isa_untitled", lang)
            st.markdown(f"**{title}**")
            st.markdown(f"**{t('view.isa_objective', lang)}**")
            st.write(comments.get("Objective") or t("view.isa_obj_missing", lang))
            st.markdown(f"**{t('view.isa_hypothesis', lang)}**")
            st.write(comments.get("Hypothesis") or t("view.isa_hyp_missing", lang))
            if comments.get("Approach"):
                st.markdown(f"**{t('view.isa_approach', lang)}**")
                st.write(comments["Approach"])
            if len(isa_records) > 1:
                st.caption(t("view.source_file", lang, name=document["name"]))
    else:
        st.info(t("view.isa_no_obj", lang))

    st.divider()
    st.subheader(t("view.analyzed_data", lang))

    col_doc = t("view.col_doc", lang)
    col_ds = t("view.col_dataset", lang)
    col_var = t("view.col_variable", lang)
    col_qty = t("view.col_qty", lang)
    col_unit = t("view.col_unit", lang)
    col_n = t("view.col_observations", lang)
    col_mean = t("view.col_mean", lang)
    col_med = t("view.col_median", lang)
    col_std = t("view.col_std", lang)
    col_min = t("view.col_min", lang)
    col_max = t("view.col_max", lang)

    statistical_rows = []
    for entry in data_entries:
        frame, meta = entry_frame(entry, entries, overrides)
        metadata_by_name = {item["name"]: item for item in meta}
        for column in frame.columns:
            values = pd.to_numeric(frame[column], errors="coerce").dropna()
            if values.empty:
                continue
            metadata = metadata_by_name.get(column, {})
            statistical_rows.append({
                col_doc: entry["document"]["name"],
                col_ds: entry["table"]["name"],
                col_var: column,
                col_qty: quantity_label(metadata.get("quantity"), lang),
                col_unit: metadata.get("unit") or "—",
                col_n: len(values),
                col_mean: values.mean(),
                col_med: values.median(),
                col_std: values.std(ddof=1),
                col_min: values.min(),
                col_max: values.max(),
            })

    if statistical_rows:
        statistical_frame = pd.DataFrame(statistical_rows)
        st.caption(t("view.analyzed_caption", lang))
        st.dataframe(statistical_frame, hide_index=True, use_container_width=True)

        with st.expander(t("view.view_by_dataset", lang)):
            selected_table = st.selectbox(
                t("view.select_dataset", lang),
                statistical_frame[col_ds].unique(),
                key=f"overview-table-{experiment['id']}",
            )
            st.dataframe(
                statistical_frame[statistical_frame[col_ds] == selected_table],
                hide_index=True,
                use_container_width=True,
            )

        st.download_button(
            t("view.export_analyzed", lang),
            statistical_frame.to_csv(index=False).encode("utf-8-sig"),
            "analyzed_variables.csv",
            "text/csv",
            key=f"overview-export-{experiment['id']}",
        )
    else:
        st.info(t("view.no_numeric", lang))

    st.divider()
    st.subheader(t("view.conclusion_heading", lang))
    if statistical_rows:
        st.markdown(t("view.synthesis_body", lang, datasets=total_tables, rows=total_rows, variables=len(statistical_rows)))
        if quantities:
            st.markdown(f"**{t('view.quantities_identified', lang)}:** {', '.join(quantities)}.")
        st.caption(t("view.synthesis_note", lang))
    else:
        st.info(t("view.no_stats_conclusion", lang))


def _show_flags(table: dict[str, Any], lang: str | None = None) -> None:
    active = lang or get_lang()
    kind = table.get("evidence_kind", "unclassified")
    st.caption(t("view.evidence_nature", active, kind=evidence_label(kind, active)))
    if table.get("classification_note"):
        st.caption(table["classification_note"])
    if kind in {"simulation", "mixed_experiment_and_simulation"}:
        st.warning(t("view.simulation_notice", active))
    fields = table.get("field_classification", [])
    if fields:
        with st.expander(t("view.field_nature", active)):
            st.dataframe(pd.DataFrame([
                {t("view.columns_heading", active): f.get("header", ""),
                 t("view.field_nature", active): evidence_label(f.get("role") or f.get("evidence_kind"), active),
                 t("view.source_basis", active): f.get("basis") or f.get("classification_basis") or f.get("source_marker", "")}
                for f in fields
            ]), hide_index=True, use_container_width=True)
    flags = table.get("flags", [])
    for flag in (f for f in flags if f["level"] == "aviso"):
        st.warning(translate_quality_flag(flag, active))
    notes = [f for f in flags if f["level"] != "aviso"]
    if notes:
        with st.expander(t("view.auto_notes", active, count=len(notes))):
            for flag in notes:
                st.caption("• " + translate_quality_flag(flag, active))


# ----------------------------------------------------------------------------- reversible overrides


def override_editor(experiment: dict, entry: dict[str, Any], stored: dict[str, Any]) -> dict[str, Any]:
    """Expose suggested reversible table fixes; writes to session in read-only mode or disk locally."""
    lang = get_lang()
    table, key = entry["table"], entry["key"]
    current = stored.get(key, {})
    desired: dict[str, Any] = {}
    suggestions = [f for f in table.get("flags", []) if f.get("suggest")]
    swaps: list[list[str]] = []
    for i, flag in enumerate(suggestions):
        suggest = flag["suggest"]
        flag_help = translate_quality_flag(flag, lang)
        if "swap" in suggest:
            pair = suggest["swap"]
            if st.checkbox(t("view.fix_swap", lang, a=pair[0], b=pair[1]), value=pair in current.get("swap", []), key=f"{key}-sw{i}", help=flag_help):
                swaps.append(pair)
        if "borrow_axis" in suggest:
            spec = suggest["borrow_axis"]
            if st.checkbox(t("view.fix_borrow", lang, table=spec["table"]), value=bool(current.get("borrow_axis")), key=f"{key}-bo{i}", help=flag_help):
                desired["borrow_axis"] = spec
        if "divide_by_100" in suggest:
            cols = suggest["divide_by_100"]
            if st.checkbox(t("view.fix_pct", lang, cols=", ".join(cols)), value=bool(current.get("divide_by_100")), key=f"{key}-pc{i}", help=t("view.fix_pct_help", lang)):
                desired["divide_by_100"] = cols
    columns = list(table.get("columns", []))
    if len(columns) >= 2:
        with st.container():
            c1, c2, c3 = st.columns([2, 2, 1])
            a = c1.selectbox(t("view.manual_swap_a", lang), columns, key=f"{key}-ma")
            b = c2.selectbox(t("view.manual_swap_b", lang), columns, index=1, key=f"{key}-mb")
            manual = [a, b] in current.get("swap", []) and [a, b] not in swaps
            if c3.checkbox(t("view.manual_swap_apply", lang), value=manual, key=f"{key}-mc") and a != b and [a, b] not in swaps:
                swaps.append([a, b])
    if swaps:
        desired["swap"] = swaps
    if desired != current:
        if is_public_readonly():
            sess_key = f"session_overrides_{experiment['id']}"
            sess_map = dict(st.session_state.get(sess_key, {}))
            if desired:
                sess_map[key] = desired
            else:
                sess_map.pop(key, None)
            st.session_state[sess_key] = sess_map
        else:
            storage.save_overrides(experiment, key, desired)
        stored[key] = desired
        if not desired:
            stored.pop(key, None)
    if not suggestions and not desired:
        st.caption(t("view.no_fixes", lang))
    return desired


# ----------------------------------------------------------------------------- block catalog


def show_catalog(experiment: dict) -> None:
    lang = get_lang()
    st.subheader(t("view.dataset_catalog", lang))
    entries = collect_entries(experiment)
    if not entries:
        st.info(t("view.catalog_empty", lang))
        return

    col_doc = t("view.col_doc", lang)
    col_ds = t("view.col_dataset", lang)
    col_label = t("view.col_label", lang)
    col_params = t("view.col_params", lang)
    col_rows = t("view.col_rows", lang)
    col_chart = t("view.col_chart", lang)
    col_alerts = t("view.col_alerts", lang)

    rows = []
    for e in entries:
        tb = e["table"]
        rows.append({
            col_doc: e["document"]["name"],
            col_ds: tb["name"],
            col_label: tb.get("block", {}).get("label") or "",
            col_params: ", ".join(f"{k}={v}" for k, v in tb.get("params", {}).items() if not k.endswith("_unidade")),
            "Data ID": tb.get("data_id"),
            col_rows: len(tb["rows"]),
            col_chart: chart_label(tb.get("chart", {}).get("type", ""), lang),
            col_alerts: sum(f["level"] == "aviso" for f in tb.get("flags", [])),
            "_key": e["key"],
        })
    frame = pd.DataFrame(rows)
    c1, c2, c3 = st.columns([3, 3, 2])
    text = c1.text_input(t("view.filter_text", lang), key=f"cat-text-{experiment['id']}")
    kinds = c2.multiselect(t("view.filter_type", lang), sorted(frame[col_chart].unique()), key=f"cat-kind-{experiment['id']}")
    only_warn = c3.checkbox(t("view.only_warnings", lang), key=f"cat-warn-{experiment['id']}")
    if text:
        mask = frame.drop(columns="_key").astype(str).apply(lambda col: col.str.contains(text, case=False, regex=False)).any(axis=1)
        frame = frame[mask]
    if kinds:
        frame = frame[frame[col_chart].isin(kinds)]
    if only_warn:
        frame = frame[frame[col_alerts] > 0]
    st.dataframe(frame.drop(columns="_key"), hide_index=True, use_container_width=True)

    st.markdown(f"#### {t('view.crossref_title', lang)}")
    documents = experiment.get("documents", [])
    extractions = {}
    for d in documents:
        try:
            extractions[d["sha256"]] = cached_extraction(experiment, d)
        except (OSError, ValueError, KeyError):
            continue
    cross = build_crossref(documents, extractions)
    if not cross["entries"]:
        st.caption(t("view.crossref_empty", lang))
    for item in cross["entries"]:
        icon = "⚠️" if item["conflicts"] else "✅"
        with st.expander(t("view.crossref_item", lang, icon=icon, data_id=item["data_id"], sources=len(item["sources"]), blocks=len(item["blocks"]))):
            for source in item["sources"]:
                st.markdown(f"**{source['document']}** — {source['description']}")
                st.caption(" · ".join(x for x in [source["journal"], f"figure {source['figure']}" if source["figure"] else "", source["doi"]] if x))
            for conflict in item["conflicts"]:
                st.warning(conflict)
            for block in item["blocks"]:
                st.caption(t("view.crossref_data", lang, doc=block["document"], block=block["name"]))
    if cross["files"]:
        missing = sum(not f["imported"] for f in cross["files"])
        st.markdown(t("view.crossref_files", lang, total=len(cross["files"]), missing=missing))
        st.dataframe(
            pd.DataFrame(cross["files"]).rename(
                columns={"document": t("view.col_index_doc", lang), "file": t("view.col_file", lang), "imported": t("view.col_imported", lang)}
            ),
            hide_index=True,
            use_container_width=True,
        )


# ----------------------------------------------------------------------------- interactive chart explorer


def _heatmap(frame: pd.DataFrame, meta: list[dict[str, Any]]) -> go.Figure:
    numeric = [c for c in frame.columns if pd.api.types.is_numeric_dtype(frame[c])]
    header_numbers = [c for c in numeric if pd.to_numeric(pd.Series([c]), errors="coerce").notna().all()]
    if len(header_numbers) >= 3:
        axis_y = frame[numeric[0]] if numeric[0] not in header_numbers else frame.index
        value_cols = header_numbers
        x = [float(c) for c in value_cols]
    else:
        axis_y = frame.index
        value_cols = numeric
        x = value_cols
    return go.Figure(go.Heatmap(z=frame[value_cols].to_numpy(), x=x, y=axis_y, colorscale="Viridis"))


def show_explorer(experiment: dict) -> None:
    lang = get_lang()
    st.subheader(t("exp.tab_explorer", lang))
    st.caption(t("view.explorer_intro", lang))
    eid = experiment["id"]
    all_entries = collect_entries(experiment)
    entries = [
        e for e in all_entries
        if e["table"].get("block", {}).get("kind") == "data"
        and any(m["kind"] in ("numeric", "range") and m["n_numeric"] > 0 for m in e["table"].get("column_meta", []))
    ]
    if not entries:
        st.info(t("view.explorer_empty_hint", lang))
        return
    stored = _load_effective_overrides(experiment)
    by_key = {e["key"]: e for e in entries}
    docs = sorted({e["document"]["name"] for e in entries})
    doc_filter = st.multiselect(t("view.docs_filter", lang), docs, default=docs, key=f"ex-docs-{eid}")
    pool = [e["key"] for e in entries if e["document"]["name"] in doc_filter]
    selected = st.multiselect(
        t("view.datasets_select", lang),
        pool,
        default=pool[:1],
        format_func=lambda k: _label(by_key[k], lang),
        key=f"ex-sel-{eid}",
    )
    if not selected:
        st.info(t("view.select_one_dataset", lang))
        return

    is_advanced = st.session_state.get("interaction_mode", "guided") == "advanced"
    prepared: list[dict[str, Any]] = []
    for key in selected:
        entry = by_key[key]
        with st.expander(f"⚙ {_label(entry, lang)}", expanded=is_advanced and len(selected) == 1):
            _show_flags(entry["table"], lang)
            st.markdown(f"**{t('view.available_fixes', lang)}**")
            override_editor(experiment, entry, stored)
            frame, meta = entry_frame(entry, all_entries, stored)
            derived_key = f"{key}-derived"
            derived = st.session_state.setdefault(derived_key, [])
            numeric_now = [c for c in frame.columns if pd.api.types.is_numeric_dtype(frame[c])]
            with st.expander(t("exp.derived_cols", lang)):
                d1, d2, d3, d4, d5 = st.columns([2, 2, 2, 1, 2])
                op = d1.selectbox(t("view.derived_op", lang), DERIVED_OPS, format_func=lambda o: _derived_label(o, lang), key=f"{key}-op")
                col_a = d2.selectbox("A", numeric_now, key=f"{key}-da") if numeric_now else None
                col_b = d3.selectbox("B", numeric_now, key=f"{key}-db") if numeric_now else None
                factor = d4.number_input("k", value=1.0, key=f"{key}-dk")
                new_name = d5.text_input(t("view.derived_name", lang), value=t("view.derived_default_name", lang), key=f"{key}-dn")
                b1, b2 = st.columns(2)
                if b1.button(t("view.derived_add", lang), key=f"{key}-dadd") and col_a:
                    derived.append({"op": op, "a": col_a, "b": col_b, "k": factor, "name": new_name})
                if derived and b2.button(t("view.derived_clear", lang), key=f"{key}-dclr"):
                    derived.clear()
            for spec in derived:
                try:
                    frame[spec["name"]] = derive_column(frame, spec["op"], spec["a"], spec["b"], spec["k"])
                except (KeyError, ValueError) as error:
                    st.warning(t("view.derived_ignored", lang, name=spec["name"], error=error))
            numeric = [c for c in frame.columns if pd.api.types.is_numeric_dtype(frame[c])]
            chart = suggest_chart(meta, len(frame), "data")
            st.caption(t("view.suggested_type", lang, kind=chart_label(chart["type"], lang)))
            x_default = numeric.index(chart["x"]) if chart.get("x") in numeric else 0
            x = st.selectbox(t("view.x_axis", lang), numeric, index=x_default, key=f"{key}-x")
            y_options = paired_y_columns(meta, x)
            y_default = [c for c in chart.get("y", []) if c in y_options][:1]
            if not y_default:
                y_default = y_options[:1]
            if f"{key}-y" in st.session_state:
                st.session_state[f"{key}-y"] = [y for y in st.session_state[f"{key}-y"] if y in y_options]
            ys = st.multiselect(t("view.y_axis", lang), y_options, default=y_default, key=f"{key}-y")
        prepared.append({"entry": entry, "frame": frame, "meta": meta, "x": x, "ys": ys, "chart": chart})

    first = prepared[0]
    st.markdown(f"#### {t('view.chart_header', lang)}")
    c1, c2, c3, c4 = st.columns(4)
    default_chart_key = _DEFAULT_CHART.get(first["chart"]["type"], "line")
    chart_key = c1.selectbox(
        t("view.chart_type", lang),
        CHART_KEYS,
        index=CHART_KEYS.index(default_chart_key),
        format_func=lambda ck: t(f"view.chart_type_{ck}", lang),
        key=f"ex-type-{eid}",
    )
    sort = c2.checkbox(t("view.sort_x", lang), value=True, key=f"ex-sort-{eid}")
    log_x = c3.checkbox(t("view.log_x", lang), key=f"ex-lx-{eid}")
    log_y = c4.checkbox(t("view.log_y", lang), key=f"ex-ly-{eid}")
    with st.expander(t("view.adv_adjust", lang)):
        t1, t2, t3, t4 = st.columns(4)
        baseline = t1.selectbox(t("view.baseline", lang), _BASELINE_KEYS, format_func=lambda k: t(_BASELINE_TRANS[k], lang), key=f"ex-bl-{eid}")
        normalize = t2.selectbox(t("view.normalize", lang), _NORM_KEYS, format_func=lambda k: t(_NORM_TRANS[k], lang), key=f"ex-nm-{eid}")
        smooth = t3.number_input(t("view.smooth", lang), min_value=0, max_value=501, value=0, key=f"ex-sm-{eid}")
        max_points = t4.number_input(t("view.max_points", lang), min_value=0, value=3000, step=500, key=f"ex-mp-{eid}")
        r1, r2, r3, r4 = st.columns(4)
        x_min_text = r1.text_input(t("view.x_min", lang), key=f"ex-xmin-{eid}")
        x_max_text = r2.text_input(t("view.x_max", lang), key=f"ex-xmax-{eid}")
        facet = r3.checkbox(t("view.facet", lang), key=f"ex-facet-{eid}")
        on_grid = r4.checkbox(t("view.on_grid", lang), key=f"ex-grid-{eid}", help=t("view.on_grid_help", lang))

    def to_float(text: str) -> float | None:
        try:
            return float(text.replace(",", ".")) if text.strip() else None
        except ValueError:
            return None

    x_min_val = to_float(x_min_text)
    x_max_val = to_float(x_max_text)
    params: dict[str, Any] = {
        "sort": sort,
        "x_min": x_min_val,
        "x_max": x_max_val,
        "baseline": baseline,
        "normalize": normalize,
        "smooth": int(smooth),
        "max_points": int(max_points),
    }
    series: dict[str, pd.DataFrame] = {}
    origin: dict[str, dict[str, Any]] = {}
    if chart_key not in {"heatmap", "xyc"} and not comparable_plot_axes(prepared):
        st.warning(t("view.incompatible_axes", lang))
        return
    multi_doc = len({p["entry"]["document"]["name"] for p in prepared}) > 1
    for item in prepared:
        for y in item["ys"]:
            s = prepare_series(
                item["frame"][item["x"]],
                item["frame"][y],
                sort=sort,
                x_min=x_min_val,
                x_max=x_max_val,
                baseline=baseline,
                normalize=normalize,
                smooth=int(smooth),
                max_points=int(max_points),
            )
            if s.empty:
                continue
            name = f"{item['entry']['table']['name']} · {y}"
            name += f" · {evidence_label(_series_kind(item['entry']['table'], y), lang)}"
            if multi_doc:
                name = f"{Path(item['entry']['document']['name']).stem} › {name}"
            series[name] = s
            origin[name] = item["entry"]
    if on_grid:
        series = common_grid(series)

    if chart_key == "heatmap":
        heat_fig = style_scientific_figure(_heatmap(first["frame"], first["meta"]), height=410)
        st.plotly_chart(heat_fig, use_container_width=True)
        from .guided_journeys import render_heatmap_explanation, render_term_help

        render_heatmap_explanation(first["entry"], experiment, lang)
        render_term_help(lang)
    elif chart_key == "xyc":
        numeric = [c for c in first["frame"].columns if pd.api.types.is_numeric_dtype(first["frame"][c])]
        if len(numeric) < 3 or not first["ys"]:
            st.info(t("view.need_3_cols", lang))
        else:
            color = st.selectbox(t("view.color_var", lang), [c for c in numeric if c not in (first["x"], first["ys"][0])], key=f"ex-color-{eid}")
            xyc_fig = style_scientific_figure(
                px.scatter(first["frame"], x=first["x"], y=first["ys"][0], color=color, template="plotly_white"),
                height=410,
            )
            st.plotly_chart(xyc_fig, use_container_width=True)
            from .guided_journeys import render_chart_explanation, render_term_help

            x_meta = next((m for m in first["meta"] if m["name"] == first["x"]), None)
            y_meta = next((m for m in first["meta"] if m["name"] == first["ys"][0]), {"name": first["ys"][0], "unit": "", "quantity": "unknown"})
            render_chart_explanation(first["entry"], first["x"], [first["ys"][0]], x_meta, [y_meta], None, experiment, lang)
            render_term_help(lang)
    elif not series:
        st.info(t("view.select_y_warning", lang))
    else:
        col_series = t("view.col_series", lang)
        col_dataset = t("view.col_dataset", lang)
        long = pd.concat([s.assign(**{col_series: name, col_dataset: origin[name]["table"]["name"]}) for name, s in series.items()], ignore_index=True)
        common: dict[str, Any] = dict(x="x", y="y", color=col_series, template="plotly_white", log_x=log_x, log_y=log_y)
        if facet:
            common["facet_col"] = col_dataset
        if chart_key == "scatter":
            fig = px.scatter(long, **common)
        elif chart_key == "bar":
            fig = px.bar(long, barmode="group", **common)
        else:
            fig = px.line(long, markers=(chart_key == "line_pts"), **common)
        x_meta = next((m for m in first["meta"] if m["name"] == first["x"]), None)
        y_meta = next((m for m in first["meta"] if first["ys"] and m["name"] == first["ys"][0]), None)
        fig.update_xaxes(title_text=axis_label(x_meta) if x_meta else first["x"])
        y_title = axis_label(y_meta) if y_meta and len(series) == 1 else t("view.value_axis", lang)
        if normalize != "nenhuma":
            y_title += " " + t("view.normalized_suffix", lang, mode=t(_NORM_TRANS[normalize], lang))
        fig.update_yaxes(title_text=y_title)
        style_scientific_figure(fig, height=420)
        st.plotly_chart(fig, use_container_width=True)
        from .guided_journeys import render_chart_explanation, render_term_help

        y_metas = [
            next((m for m in first["meta"] if m["name"] == y), {"name": y, "unit": "", "quantity": "unknown"})
            for y in first["ys"]
        ]
        render_chart_explanation(first["entry"], first["x"], first["ys"], x_meta, y_metas, params, experiment, lang)
        render_term_help(lang)
        _analysis_and_export(series, origin, prepared, params, stored, fig, long, eid)


def _analysis_and_export(series, origin, prepared, params, stored, fig, long, eid) -> None:
    lang = get_lang()
    with st.expander(t("view.series_analysis", lang)):
        st.caption(t("view.series_analysis_note", lang))
        controls = st.columns(3)
        include_fit = controls[0].checkbox(t("view.linear_fit", lang), value=True, key=f"an-fit-{eid}")
        include_peak = controls[1].checkbox(t("view.peak_width", lang), key=f"an-peak-{eid}")
        include_final = controls[2].checkbox(t("view.last_positive", lang), key=f"an-final-{eid}")

        lo = min(float(s["x"].min()) for s in series.values())
        hi = max(float(s["x"].max()) for s in series.values())
        start, end = lo, hi
        if include_fit:
            w1, w2 = st.columns(2)
            start = w1.number_input(t("view.fit_start", lang), value=lo, key=f"an-lo-{eid}", format="%.6g")
            end = w2.number_input(t("view.fit_end", lang), value=hi, key=f"an-hi-{eid}", format="%.6g")
            if end <= start:
                st.warning(t("view.fit_window_warn", lang))
                include_fit = False

        rows = []
        for name, series_frame in series.items():
            y = series_frame["y"].to_numpy()
            finite_y = y[pd.notna(y)]
            row: dict[str, Any] = {
                t("view.col_series", lang): name,
                "N": int(len(finite_y)),
                t("view.col_mean", lang): float(finite_y.mean()) if len(finite_y) else None,
                t("view.col_median", lang): float(pd.Series(finite_y).median()) if len(finite_y) else None,
                t("view.col_std", lang): float(pd.Series(finite_y).std(ddof=1)) if len(finite_y) > 1 else None,
                t("view.col_min", lang): float(finite_y.min()) if len(finite_y) else None,
                t("view.col_max", lang): float(finite_y.max()) if len(finite_y) else None,
            }
            if include_fit:
                window = series_frame[(series_frame["x"] >= start) & (series_frame["x"] <= end)]
                fit = fit_linear(window["x"].to_numpy(), window["y"].to_numpy())
                row.update({
                    t("view.fit_n", lang): fit["n"],
                    t("view.fit_slope", lang): fit["slope"],
                    t("view.fit_intercept", lang): fit["intercept"],
                    t("view.fit_r", lang): fit["r"],
                    t("view.fit_r2", lang): fit["r2"],
                })
            if include_peak:
                peak = peak_info(series_frame["x"].to_numpy(), series_frame["y"].to_numpy())
                row.update({
                    t("view.peak_x", lang): peak["x_peak"],
                    t("view.peak_y", lang): peak["y_peak"],
                    t("view.peak_fwhm", lang): peak["fwhm"],
                })
            if include_final:
                last = final_point(series_frame["x"].to_numpy(), series_frame["y"].to_numpy())
                row.update({t("view.last_x_pos", lang): last["x_final"], t("view.last_y_pos", lang): last["y_final"]})
            rows.append(row)
        results = pd.DataFrame(rows)
        st.dataframe(results, hide_index=True, use_container_width=True)
        st.download_button(t("view.dl_analysis", lang), results.to_csv(index=False).encode("utf-8-sig"), "series_analysis.csv", "text/csv", key=f"an-dl-{eid}")

    with st.expander(t("view.export_trace", lang)):
        provenance = [
            {
                "document": p["entry"]["document"]["name"],
                "sha256": p["entry"]["document"]["sha256"],
                "source_location": p["entry"]["table"].get("location"),
                "x": p["x"],
                "y": p["ys"],
                "overrides": stored.get(p["entry"]["key"], {}),
                "open_alerts": [f["message"] for f in p["entry"]["table"].get("flags", []) if f["level"] == "aviso"],
            }
            for p in prepared
        ]
        for item in provenance:
            st.caption(f"{item['document']} · {item['source_location']}")
        st.download_button(t("view.dl_plotted_csv", lang), long.to_csv(index=False).encode("utf-8-sig"), "plotted_data.csv", "text/csv", key=f"ex-csv-{eid}")
        st.download_button(
            t("view.dl_transforms_json", lang),
            json.dumps({"transforms": params, "series": provenance}, ensure_ascii=False, indent=2).encode("utf-8"),
            "transforms_provenance.json",
            "application/json",
            key=f"ex-json-{eid}",
        )
        st.download_button(t("view.dl_chart_html", lang), fig.to_html(include_plotlyjs="cdn").encode("utf-8"), "chart.html", "text/html", key=f"ex-html-{eid}")


# ----------------------------------------------------------------------------- tables


def show_tables(experiment: dict) -> None:
    lang = get_lang()
    st.subheader(t("view.tables_header", lang))
    entries = collect_entries(experiment)
    if not entries:
        st.info(t("view.no_tables", lang))
        return
    by_key = {e["key"]: e for e in entries}
    key = st.selectbox(t("view.select_table", lang), list(by_key), format_func=lambda k: _label(by_key[k], lang), key=f"tb-sel-{experiment['id']}")
    entry = by_key[key]
    table = entry["table"]
    block = table.get("block", {})
    stored = _load_effective_overrides(experiment)
    st.caption(t("view.source_origin", lang, doc=entry["document"]["name"], loc=table.get("location", "")))
    if block.get("sheet_titles"):
        st.caption(t("view.sheet_titles", lang, titles=" | ".join(block["sheet_titles"])))
    if table.get("params"):
        st.caption(t("view.label_params", lang, params=", ".join(f"{k}={v}" for k, v in table["params"].items())))
    _show_flags(table, lang)
    frame, meta = entry_frame(entry, entries, stored)
    if stored.get(key):
        st.info(t("view.overrides_active", lang))
    st.markdown(f"**{t('view.columns_heading', lang)}**")
    st.dataframe(
        pd.DataFrame([
            {
                t("view.columns_heading", lang): m["name"],
                t("view.col_unit", lang): m["unit"],
                t("view.col_qty", lang): quantity_label(m["quantity"], lang),
                t("view.col_kind", lang): m["kind"],
                t("view.col_num_values", lang): f"{m['n_numeric']}/{m['n_nonempty']}",
                t("view.col_min", lang): m["min"],
                t("view.col_max", lang): m["max"],
            }
            for m in meta
        ]),
        hide_index=True,
        use_container_width=True,
    )
    shown = frame.copy()
    rows = table.get("source_rows", [])
    if len(rows) == len(shown):
        shown.insert(0, t("view.col_source_row", lang), rows)
    st.download_button(
        t("view.export_csv", lang),
        shown.to_csv(index=False).encode("utf-8-sig"),
        f"{Path(entry['document']['name']).stem}_{table['name']}.csv".replace("/", "-"),
        "text/csv",
        key=f"tb-dl-{key}",
    )
    st.dataframe(shown, hide_index=True, use_container_width=True)
    if table.get("page") and entry["document"].get("extension") == ".pdf":
        if st.button(t("view.show_pdf_page", lang), key=f"tb-pg-{key}"):
            _show_pdf_page(experiment, entry["document"], table["page"])


# ----------------------------------------------------------------------------- PDF reader


def _show_pdf_page(experiment: dict, document: dict, page: int) -> None:
    lang = get_lang()
    try:
        st.image(
            render_pdf_page(storage.read_original(experiment, document), int(page), dpi=150),
            caption=t("vis.preview_caption", lang, name=document["name"], page=page),
            use_container_width=True,
        )
    except Exception as error:
        st.warning(t("view.no_pdf_page_err", lang, error=error))


def _open_pdf_page(experiment_id: str, document_id: str, page: int) -> None:
    """Callback updating selected PDF document and page before widgets build."""
    st.session_state[f"pdf-document-{experiment_id}"] = document_id
    st.session_state[f"pdf-page-{experiment_id}"] = int(page)


def show_search(experiment: dict) -> None:
    lang = get_lang()
    st.subheader(t("view.pdf_reader", lang))
    documents = [
        document for document in experiment.get("documents", [])
        if document.get("extension") == ".pdf" and document.get("status") != "erro"
    ]
    if not documents:
        st.info(t("view.no_pdfs", lang))
        return
    eid = experiment["id"]
    by_id = {document["id"]: document for document in documents}
    document_key = f"pdf-document-{eid}"
    page_key = f"pdf-page-{eid}"
    if st.session_state.get(document_key) not in by_id:
        st.session_state[document_key] = documents[0]["id"]

    st.caption(t("view.pdf_reader_note", lang))
    query = st.text_input(t("view.pdf_search_label", lang), placeholder=t("view.pdf_search_ph", lang), key=f"se-q-{eid}")
    if query.strip():
        results = search_content(documents, query, lambda d: cached_extraction(experiment, d), {"pdf", "legenda"})
        pages: dict[tuple[str, int], dict[str, Any]] = {}
        for result in results:
            if not result.get("page"):
                continue
            result_key = (result["document"]["id"], int(result["page"]))
            if result_key not in pages or result["score"] > pages[result_key]["score"]:
                pages[result_key] = result
        page_results = sorted(pages.values(), key=lambda item: (item["score"], item["coverage"]), reverse=True)
        if not page_results:
            st.warning(t("view.pdf_not_found", lang))
        else:
            st.caption(t("view.pdf_matches_count", lang, count=len(page_results)))
        for rank, result in enumerate(page_results[:60], start=1):
            left, right = st.columns([6, 1])
            left.write(t("view.pdf_page_line", lang, rank=rank, name=result["document"]["name"], page=result["page"]))
            left.caption(t("view.pdf_matched_terms", lang, terms=", ".join(result["matched_terms"])))
            right.button(
                t("view.open_page", lang),
                key=f"se-pg-{rank}-{result['document']['sha256'][:8]}",
                on_click=_open_pdf_page,
                args=(eid, result["document"]["id"], int(result["page"])),
                use_container_width=True,
            )

    st.markdown(f"### {t('view.pdf_page_heading', lang)}")
    selected_id = st.selectbox(
        t("view.pdf_open_select", lang),
        options=list(by_id),
        format_func=lambda identifier: by_id[identifier]["name"],
        key=document_key,
    )
    selected_document = by_id[selected_id]
    try:
        extraction = cached_extraction(experiment, selected_document)
        max_page = max(1, int(extraction.get("metadata", {}).get("page_count") or selected_document.get("page_count") or 1))
    except (OSError, ValueError, KeyError):
        max_page = 1
    requested_page = int(st.session_state.get(page_key, 1))
    if requested_page < 1 or requested_page > max_page:
        st.session_state[page_key] = 1
    page = st.number_input(t("view.pdf_page_num", lang), min_value=1, max_value=max_page, step=1, key=page_key)
    _show_pdf_page(experiment, selected_document, int(page))


# ----------------------------------------------------------------------------- ISA-Tab metadata


def show_metadata(experiment: dict) -> None:
    lang = get_lang()
    st.subheader(t("view.isa_heading", lang))
    found = False
    for document in experiment.get("documents", []):
        if document.get("status") == "erro":
            continue
        try:
            isa = cached_extraction(experiment, document).get("isa")
        except (OSError, ValueError, KeyError):
            continue
        if not isa:
            continue
        found = True
        study, comments = isa["study"], isa["comments"]
        with st.container(border=True):
            st.markdown(f"### {study['id']} — {study['title']}")
            st.caption(
                f"{document['name']} · {t('view.isa_submitted', lang, submitted=study['submitted'], released=study['released'])} · "
                f"{comments.get('Managing NASA Center', '')} · {comments.get('Project Type', '')} · {comments.get('SubResearch Area', '')}"
            )
            if comments.get("Investigation Start Date"):
                st.caption(t("view.isa_period", lang, start=comments["Investigation Start Date"], end=comments.get("Investigation End Date", "?")))
            if isa["design_types"]:
                st.markdown(f"**{t('view.isa_keywords', lang)}:** " + " · ".join(isa["design_types"]))
            for field in ("Objective", "Hypothesis", "Approach", "Research Impacts"):
                if comments.get(field):
                    with st.expander(field):
                        st.write(comments[field])
            if isa["publications"]:
                st.markdown(f"**{t('view.isa_publications', lang)}**")
                st.dataframe(pd.DataFrame(isa["publications"])[["year", "title", "authors", "doi", "link"]], hide_index=True, use_container_width=True)
            if isa["contacts"]:
                st.markdown(f"**{t('view.isa_contacts', lang)}**")
                st.dataframe(pd.DataFrame(isa["contacts"]), hide_index=True, use_container_width=True)
            if isa["empty_sections"]:
                st.warning(t("view.isa_empty_warn", lang, sections=", ".join(isa["empty_sections"])))
    if not found:
        st.info(t("view.no_isa", lang))
