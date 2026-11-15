"""Telas de dados do dashboard: catálogo, explorador, tabelas, texto/PDF e metadados."""

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
from .crossref import build_crossref
from .extractors import render_pdf_page
from .frames import CHART_LABELS, axis_label, suggest_chart, table_to_frame
from .quantities import QUANTITY_LABELS
from .search import search_content

CHART_TYPES = ["Linha", "Linha com pontos", "Dispersão", "Barras", "Mapa de calor (matriz)", "Mapa X–Y–cor"]
_DEFAULT_CHART = {
    "time_series": "Linha", "spatial_profile": "Linha", "limit_curve": "Linha com pontos",
    "parametric": "Linha com pontos", "matrix": "Mapa de calor (matriz)", "distribution": "Dispersão",
}


# ----------------------------------------------------------------------------- acesso a dados

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


def _label(entry: dict[str, Any]) -> str:
    return f"{entry['document']['name'][:30]} › {entry['table']['name']} ({len(entry['table']['rows'])} linhas)"


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


def show_study_overview(experiment: dict) -> None:
    """Relatório científico resumido do experimento."""

    documents = experiment.get("documents", [])

    # ---------------------------------------------------------
    # Recuperação dos dados já extraídos

    entries = collect_entries(experiment)

    data_entries = [
        entry for entry in entries
        if entry["table"].get("block", {}).get("kind") == "data"
    ]

    overrides = storage.load_overrides(experiment)

    total_tables = len(data_entries)

    total_rows = sum(
        len(entry["table"].get("rows", []))
        for entry in data_entries
    )

    quantities = sorted({
        QUANTITY_LABELS.get(
            meta.get("quantity"),
            meta.get("quantity", "Não classificada")
        )
        for entry in data_entries
        for meta in entry["table"].get("column_meta", [])
        if meta.get("quantity") not in (None, "unknown")
        and meta.get("n_numeric", 0) > 0
    })

    # ---------------------------------------------------------
    # 1. RESUMO DO EXPERIMENTO

    st.subheader("Resumo do experimento")

    if experiment.get("description"):
        st.write(experiment["description"])
    else:
        st.info("Descrição do experimento ainda não informada.")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Documentos", len(documents))
    c2.metric("Conjuntos analisados", total_tables)
    c3.metric("Linhas de dados", total_rows)
    c4.metric("Grandezas físicas", len(quantities))

    if quantities:
        st.markdown("**Grandezas identificadas**")
        st.write(" · ".join(quantities))

    # ---------------------------------------------------------
    # 2. OBJETIVO DO EXPERIMENTO

    st.divider()
    st.subheader("Objetivo do experimento")

    isa_records = []

    for document in documents:
        if document.get("status") == "erro":
            continue

        try:
            extraction = cached_extraction(experiment, document)
            isa = extraction.get("isa")

            if isa:
                isa_records.append((document, isa))

        except (OSError, ValueError, KeyError):
            continue

    if isa_records:

        for document, isa in isa_records:

            study = isa.get("study", {})
            comments = isa.get("comments", {})

            title = (
                comments.get("Proposal Title")
                or study.get("title")
                or "Estudo sem título"
            )

            st.markdown(f"**{title}**")

            st.markdown("**Objetivo**")
            st.write(
                comments.get("Objective")
                or "Objetivo não declarado nos metadados."
            )

            st.markdown("**Hipótese**")
            st.write(
                comments.get("Hypothesis")
                or "Hipótese não declarada nos metadados."
            )

            if comments.get("Approach"):
                st.markdown("**Abordagem experimental**")
                st.write(comments["Approach"])

            if len(isa_records) > 1:
                st.caption(f"Fonte: {document['name']}")

    else:
        st.info(
            "Não foram encontrados objetivos ou hipóteses "
            "nos metadados ISA-Tab importados."
        )

    # ---------------------------------------------------------
    # 3. DADOS ANALISADOS

    st.divider()
    st.subheader("Dados analisados")

    statistical_rows = []

    for entry in data_entries:

        frame, meta = entry_frame(
            entry,
            entries,
            overrides
        )

        metadata_by_name = {
            item["name"]: item
            for item in meta
        }

        for column in frame.columns:

            values = pd.to_numeric(
                frame[column],
                errors="coerce"
            ).dropna()

            if values.empty:
                continue

            metadata = metadata_by_name.get(column, {})

            statistical_rows.append({
                "Documento": entry["document"]["name"],
                "Conjunto": entry["table"]["name"],
                "Variável": column,
                "Grandeza": QUANTITY_LABELS.get(
                    metadata.get("quantity"),
                    metadata.get("quantity", "Não classificada")
                ),
                "Unidade": metadata.get("unit") or "—",
                "Observações": len(values),
                "Média": values.mean(),
                "Mediana": values.median(),
                "Desvio padrão": values.std(ddof=1),
                "Mínimo": values.min(),
                "Máximo": values.max(),
            })

    if statistical_rows:

        statistical_frame = pd.DataFrame(statistical_rows)

        st.caption(
            "Resumo estatístico das variáveis numéricas "
            "extraídas dos conjuntos de dados do experimento."
        )

        st.dataframe(
            statistical_frame,
            hide_index=True,
            use_container_width=True
        )

        with st.expander("Visualizar dados por conjunto"):

            selected_table = st.selectbox(
                "Selecionar conjunto de dados",
                statistical_frame["Conjunto"].unique(),
                key=f"overview-table-{experiment['id']}"
            )

            selected_data = statistical_frame[
                statistical_frame["Conjunto"] == selected_table
            ]

            st.dataframe(
                selected_data,
                hide_index=True,
                use_container_width=True
            )

        st.download_button(
            "Exportar dados analisados (CSV)",
            statistical_frame.to_csv(
                index=False
            ).encode("utf-8-sig"),
            "dados_analisados.csv",
            "text/csv",
            key=f"overview-export-{experiment['id']}"
        )

    else:
        st.info(
            "Não foram encontrados dados numéricos "
            "suficientes para apresentar resultados estatísticos."
        )

    # ---------------------------------------------------------
    # 4. CONCLUSÃO DO EXPERIMENTO

    st.divider()
    st.subheader("Conclusão do experimento")

    if statistical_rows:

        variables = len(statistical_rows)
        datasets = total_tables

        st.markdown(
            f"Foram analisados **{datasets} conjuntos de dados**, "
            f"contendo **{total_rows} linhas**, com "
            f"**{variables} registros estatísticos de variáveis numéricas**."
        )

        st.markdown(
            "A análise descritiva apresenta os valores médios, "
            "medianos, desvios padrão e intervalos observados "
            "para as variáveis identificadas."
        )

        if quantities:
            st.markdown(
                "**Grandezas contempladas:** "
                + ", ".join(quantities)
                + "."
            )

        st.caption(
            "Esta síntese é descritiva e automática. "
            "A interpretação física dos resultados e a confirmação "
            "das hipóteses dependem da análise científica do experimento."
        )

    else:

        st.info(
            "Ainda não existem resultados numéricos suficientes "
            "para elaborar uma conclusão baseada nos dados."
        )


def _show_flags(table: dict[str, Any]) -> None:
    flags = table.get("flags", [])
    for flag in (f for f in flags if f["level"] == "aviso"):
        st.warning(flag["message"])
    notes = [f for f in flags if f["level"] != "aviso"]
    if notes:
        with st.expander(f"Observações automáticas ({len(notes)})"):
            for flag in notes:
                st.caption("• " + flag["message"])


# ----------------------------------------------------------------------------- correções (reversíveis)

def override_editor(experiment: dict, entry: dict[str, Any], stored: dict[str, Any]) -> dict[str, Any]:
    """Oferece as correções sugeridas pelos alertas como caixas de seleção; grava em correcoes.json."""
    table, key = entry["table"], entry["key"]
    current = stored.get(key, {})
    desired: dict[str, Any] = {}
    suggestions = [f for f in table.get("flags", []) if f.get("suggest")]
    swaps: list[list[str]] = []
    for i, flag in enumerate(suggestions):
        suggest = flag["suggest"]
        if "swap" in suggest:
            pair = suggest["swap"]
            if st.checkbox(f"Trocar os rótulos de '{pair[0]}' e '{pair[1]}'", value=pair in current.get("swap", []), key=f"{key}-sw{i}",
                           help=flag["message"]):
                swaps.append(pair)
        if "borrow_axis" in suggest:
            spec = suggest["borrow_axis"]
            if st.checkbox(f"Usar o eixo de '{spec['table']}' (suposição)", value=bool(current.get("borrow_axis")), key=f"{key}-bo{i}",
                           help=flag["message"]):
                desired["borrow_axis"] = spec
        if "divide_by_100" in suggest:
            cols = suggest["divide_by_100"]
            if st.checkbox(f"Converter {', '.join(cols)} de % para fração", value=bool(current.get("divide_by_100")), key=f"{key}-pc{i}"):
                desired["divide_by_100"] = cols
    columns = list(table.get("columns", []))
    if len(columns) >= 2:
        with st.container():
            c1, c2, c3 = st.columns([2, 2, 1])
            a = c1.selectbox("Trocar rótulos (manual): coluna A", columns, key=f"{key}-ma")
            b = c2.selectbox("coluna B", columns, index=1, key=f"{key}-mb")
            manual = [a, b] in current.get("swap", []) and [a, b] not in swaps
            if c3.checkbox("Aplicar", value=manual, key=f"{key}-mc") and a != b and [a, b] not in swaps:
                swaps.append([a, b])
    if swaps:
        desired["swap"] = swaps
    if desired != current:
        storage.save_overrides(experiment, key, desired)
        stored[key] = desired
        if not desired:
            stored.pop(key, None)
    if not suggestions and not desired:
        st.caption("Sem correções sugeridas para esta tabela.")
    return desired


# ----------------------------------------------------------------------------- catálogo

def show_catalog(experiment: dict) -> None:
    st.subheader("Catálogo de conjuntos de dados")
    entries = collect_entries(experiment)
    if not entries:
        st.info("Importe planilhas, CSV ou DOCX para listar os conjuntos de dados.")
        return
    rows = []
    for e in entries:
        t = e["table"]
        rows.append({
            "Documento": e["document"]["name"], "Conjunto": t["name"], "Rótulo": t.get("block", {}).get("label") or "",
            "Parâmetros": ", ".join(f"{k}={v}" for k, v in t.get("params", {}).items() if not k.endswith("_unidade")),
            "Data ID": t.get("data_id"), "Linhas": len(t["rows"]),
            "Tipo": CHART_LABELS.get(t.get("chart", {}).get("type", ""), ""),
            "Avisos": sum(f["level"] == "aviso" for f in t.get("flags", [])), "_key": e["key"],
        })
    frame = pd.DataFrame(rows)
    c1, c2, c3 = st.columns([3, 3, 2])
    text = c1.text_input("Filtrar por texto", key=f"cat-text-{experiment['id']}")
    kinds = c2.multiselect("Tipo", sorted(frame["Tipo"].unique()), key=f"cat-kind-{experiment['id']}")
    only_warn = c3.checkbox("Só com avisos", key=f"cat-warn-{experiment['id']}")
    if text:
        mask = frame.drop(columns="_key").astype(str).apply(lambda col: col.str.contains(text, case=False, regex=False)).any(axis=1)
        frame = frame[mask]
    if kinds:
        frame = frame[frame["Tipo"].isin(kinds)]
    if only_warn:
        frame = frame[frame["Avisos"] > 0]
    st.dataframe(frame.drop(columns="_key"), hide_index=True, use_container_width=True)

    st.markdown("#### Referência cruzada entre índices e dados")
    documents = experiment.get("documents", [])
    extractions = {}
    for d in documents:
        try:
            extractions[d["sha256"]] = cached_extraction(experiment, d)
        except (OSError, ValueError, KeyError):
            continue
    cross = build_crossref(documents, extractions)
    if not cross["entries"]:
        st.caption("Nenhuma tabela-índice com colunas 'Data ID' e 'descrição' foi encontrada.")
    for item in cross["entries"]:
        icon = "⚠️" if item["conflicts"] else "✅"
        with st.expander(f"{icon} Data ID {item['data_id']} · {len(item['sources'])} fonte(s) · {len(item['blocks'])} bloco(s) de dados"):
            for source in item["sources"]:
                st.markdown(f"**{source['document']}** — {source['description']}")
                st.caption(" · ".join(x for x in [source["journal"], f"figura {source['figure']}" if source["figure"] else "", source["doi"]] if x))
            for conflict in item["conflicts"]:
                st.warning(conflict)
            for block in item["blocks"]:
                st.caption(f"Dados: {block['document']} › {block['name']}")
    if cross["files"]:
        missing = sum(not f["imported"] for f in cross["files"])
        st.markdown(f"**Arquivos de dados citados em índices:** {len(cross['files'])} · não importados: {missing}")
        st.dataframe(pd.DataFrame(cross["files"]).rename(columns={"document": "Índice", "file": "Arquivo", "imported": "Importado"}),
                     hide_index=True, use_container_width=True)


# ----------------------------------------------------------------------------- explorador

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
    st.subheader("Explorador de dados")
    st.caption("Selecione um conjunto, confirme os eixos sugeridos e escolha o tipo de gráfico. Transformações e filtros ficam recolhidos para não esconder o dado original.")
    eid = experiment["id"]
    all_entries = collect_entries(experiment)
    entries = [
        e for e in all_entries
        if e["table"].get("block", {}).get("kind") == "data"
        and any(m["kind"] in ("numeric", "range") and m["n_numeric"] > 0 for m in e["table"].get("column_meta", []))
    ]
    if not entries:
        st.info("Não há conjuntos de dados numéricos. Importe planilhas ou CSV com dados experimentais.")
        return
    stored = storage.load_overrides(experiment)
    by_key = {e["key"]: e for e in entries}
    docs = sorted({e["document"]["name"] for e in entries})
    doc_filter = st.multiselect("Documentos", docs, default=docs, key=f"ex-docs-{eid}")
    pool = [e["key"] for e in entries if e["document"]["name"] in doc_filter]
    selected = st.multiselect("Conjuntos de dados (selecione vários para sobrepor)", pool, default=pool[:1],
                              format_func=lambda k: _label(by_key[k]), key=f"ex-sel-{eid}")
    if not selected:
        st.info("Selecione ao menos um conjunto de dados.")
        return

    prepared: list[dict[str, Any]] = []
    for key in selected:
        entry = by_key[key]
        with st.expander(f"⚙ {_label(entry)}", expanded=len(selected) == 1):
            _show_flags(entry["table"])
            st.markdown("**Correções disponíveis** (reversíveis; o original não é alterado)")
            override_editor(experiment, entry, stored)
            frame, meta = entry_frame(entry, all_entries, stored)
            derived_key = f"{key}-derived"
            derived = st.session_state.setdefault(derived_key, [])
            numeric_now = [c for c in frame.columns if pd.api.types.is_numeric_dtype(frame[c])]
            with st.expander("Transformações derivadas (avançado)"):
                d1, d2, d3, d4, d5 = st.columns([2, 2, 2, 1, 2])
                op = d1.selectbox("Coluna derivada", DERIVED_OPS, key=f"{key}-op")
                col_a = d2.selectbox("A", numeric_now, key=f"{key}-da") if numeric_now else None
                col_b = d3.selectbox("B", numeric_now, key=f"{key}-db") if numeric_now else None
                factor = d4.number_input("k", value=1.0, key=f"{key}-dk")
                new_name = d5.text_input("Nome", value="derivada", key=f"{key}-dn")
                b1, b2 = st.columns(2)
                if b1.button("Adicionar coluna derivada", key=f"{key}-dadd") and col_a:
                    derived.append({"op": op, "a": col_a, "b": col_b, "k": factor, "name": new_name})
                if derived and b2.button("Limpar colunas derivadas", key=f"{key}-dclr"):
                    derived.clear()
            for spec in derived:
                try:
                    frame[spec["name"]] = derive_column(frame, spec["op"], spec["a"], spec["b"], spec["k"])
                except (KeyError, ValueError) as error:
                    st.warning(f"Coluna derivada '{spec['name']}' ignorada: {error}")
            numeric = [c for c in frame.columns if pd.api.types.is_numeric_dtype(frame[c])]
            chart = suggest_chart(meta, len(frame), "data")
            st.caption(f"Tipo sugerido: **{CHART_LABELS.get(chart['type'], chart['type'])}**")
            x_default = numeric.index(chart["x"]) if chart.get("x") in numeric else 0
            x = st.selectbox("Eixo X", numeric, index=x_default, key=f"{key}-x")
            y_default = [c for c in chart.get("y", []) if c in numeric and c != x][:1]
            if not y_default:
                y_default = [column for column in numeric if column != x][:1]
            ys = st.multiselect("Eixo(s) Y", [c for c in numeric if c != x], default=y_default, key=f"{key}-y")
        prepared.append({"entry": entry, "frame": frame, "meta": meta, "x": x, "ys": ys, "chart": chart})

    first = prepared[0]
    st.markdown("#### Gráfico")
    c1, c2, c3, c4 = st.columns(4)
    chart_type = c1.selectbox("Tipo", CHART_TYPES, index=CHART_TYPES.index(_DEFAULT_CHART.get(first["chart"]["type"], "Linha")), key=f"ex-type-{eid}")
    sort = c2.checkbox("Ordenar por X", value=True, key=f"ex-sort-{eid}")
    log_x = c3.checkbox("X logarítmico", key=f"ex-lx-{eid}")
    log_y = c4.checkbox("Y logarítmico", key=f"ex-ly-{eid}")
    with st.expander("Ajustes e filtros avançados"):
        t1, t2, t3, t4 = st.columns(4)
        baseline = t1.selectbox("Linha de base", ["nenhuma", "mínimo", "primeiros N"], key=f"ex-bl-{eid}")
        normalize = t2.selectbox("Normalização", ["nenhuma", "pico", "mín-máx"], key=f"ex-nm-{eid}")
        smooth = t3.number_input("Suavização (pontos)", min_value=0, max_value=501, value=0, key=f"ex-sm-{eid}")
        max_points = t4.number_input("Máx. pontos (0 = todos)", min_value=0, value=3000, step=500, key=f"ex-mp-{eid}")
        r1, r2, r3, r4 = st.columns(4)
        x_min_text = r1.text_input("X mínimo", key=f"ex-xmin-{eid}")
        x_max_text = r2.text_input("X máximo", key=f"ex-xmax-{eid}")
        facet = r3.checkbox("Um painel por conjunto", key=f"ex-facet-{eid}")
        on_grid = r4.checkbox("Interpolar em grade comum", key=f"ex-grid-{eid}", help="Útil para comparar perfis medidos em malhas diferentes.")

    def to_float(text: str) -> float | None:
        try:
            return float(text.replace(",", ".")) if text.strip() else None
        except ValueError:
            return None

    params = {
        "sort": sort, "x_min": to_float(x_min_text), "x_max": to_float(x_max_text), "baseline": baseline,
        "normalize": normalize, "smooth": int(smooth), "max_points": int(max_points),
    }
    series: dict[str, pd.DataFrame] = {}
    origin: dict[str, dict[str, Any]] = {}
    multi_doc = len({p["entry"]["document"]["name"] for p in prepared}) > 1
    for item in prepared:
        for y in item["ys"]:
            s = prepare_series(item["frame"][item["x"]], item["frame"][y], **params)
            if s.empty:
                continue
            name = f"{item['entry']['table']['name']} · {y}"
            if multi_doc:
                name = f"{item['entry']['document']['name'][:20]} › {name}"
            series[name] = s
            origin[name] = item["entry"]
    if on_grid:
        series = common_grid(series)

    if chart_type == "Mapa de calor (matriz)":
        st.plotly_chart(_heatmap(first["frame"], first["meta"]), use_container_width=True)
    elif chart_type == "Mapa X–Y–cor":
        numeric = [c for c in first["frame"].columns if pd.api.types.is_numeric_dtype(first["frame"][c])]
        if len(numeric) < 3 or not first["ys"]:
            st.info("O mapa X–Y–cor exige ao menos 3 colunas numéricas e um eixo Y selecionado.")
        else:
            color = st.selectbox("Variável de cor", [c for c in numeric if c not in (first["x"], first["ys"][0])], key=f"ex-color-{eid}")
            st.plotly_chart(px.scatter(first["frame"], x=first["x"], y=first["ys"][0], color=color, template="plotly_white"), use_container_width=True)
    elif not series:
        st.info("Selecione ao menos uma coluna Y com valores numéricos.")
    else:
        long = pd.concat([s.assign(Série=name, Conjunto=origin[name]["table"]["name"]) for name, s in series.items()], ignore_index=True)
        common = dict(x="x", y="y", color="Série", template="plotly_white", log_x=log_x, log_y=log_y)
        if facet:
            common["facet_col"] = "Conjunto"
        if chart_type == "Dispersão":
            fig = px.scatter(long, **common)
        elif chart_type == "Barras":
            fig = px.bar(long, barmode="group", **common)
        else:
            fig = px.line(long, markers=(chart_type == "Linha com pontos"), **common)
        x_meta = next((m for m in first["meta"] if m["name"] == first["x"]), None)
        y_meta = next((m for m in first["meta"] if first["ys"] and m["name"] == first["ys"][0]), None)
        fig.update_xaxes(title_text=axis_label(x_meta) if x_meta else first["x"])
        y_title = axis_label(y_meta) if y_meta and len(series) == 1 else "valor"
        if normalize != "nenhuma":
            y_title += f" (normalizado: {normalize})"
        fig.update_yaxes(title_text=y_title)
        fig.update_layout(margin={"l": 20, "r": 20, "t": 30, "b": 20}, legend={"orientation": "h", "y": -0.25})
        st.plotly_chart(fig, use_container_width=True)
        _analysis_and_export(series, origin, prepared, params, stored, fig, long, eid)


def _analysis_and_export(series, origin, prepared, params, stored, fig, long, eid) -> None:
    with st.expander("Análises das séries plotadas"):
        st.caption(
            "As estatísticas usam exatamente os dados do gráfico, incluindo filtros e transformações selecionadas. "
            "Uma inclinação é apenas uma tendência linear; atribua significado físico somente após confirmar modelo, unidades e hipótese."
        )
        controls = st.columns(3)
        include_fit = controls[0].checkbox("Ajuste linear", value=True, key=f"an-fit-{eid}")
        include_peak = controls[1].checkbox("Pico e largura", key=f"an-peak-{eid}")
        include_final = controls[2].checkbox("Último ponto positivo", key=f"an-final-{eid}")

        lo = min(float(s["x"].min()) for s in series.values())
        hi = max(float(s["x"].max()) for s in series.values())
        start, end = lo, hi
        if include_fit:
            w1, w2 = st.columns(2)
            start = w1.number_input("Janela do ajuste linear: X inicial", value=lo, key=f"an-lo-{eid}", format="%.6g")
            end = w2.number_input("Janela do ajuste linear: X final", value=hi, key=f"an-hi-{eid}", format="%.6g")
            if end <= start:
                st.warning("O fim da janela precisa ser maior que o início. O ajuste linear foi omitido.")
                include_fit = False

        rows = []
        for name, series_frame in series.items():
            y = series_frame["y"].to_numpy()
            finite_y = y[pd.notna(y)]
            row: dict[str, Any] = {
                "Série": name,
                "N": int(len(finite_y)),
                "Média": float(finite_y.mean()) if len(finite_y) else None,
                "Mediana": float(pd.Series(finite_y).median()) if len(finite_y) else None,
                "Desvio padrão": float(pd.Series(finite_y).std(ddof=1)) if len(finite_y) > 1 else None,
                "Mínimo": float(finite_y.min()) if len(finite_y) else None,
                "Máximo": float(finite_y.max()) if len(finite_y) else None,
            }
            if include_fit:
                window = series_frame[(series_frame["x"] >= start) & (series_frame["x"] <= end)]
                fit = fit_linear(window["x"].to_numpy(), window["y"].to_numpy())
                row.update({
                    "Pontos no ajuste": fit["n"],
                    "Inclinação": fit["slope"],
                    "Intercepto": fit["intercept"],
                    "Correlação linear (r)": fit["r"],
                    "R²": fit["r2"],
                })
            if include_peak:
                peak = peak_info(series_frame["x"].to_numpy(), series_frame["y"].to_numpy())
                row.update({
                    "X do pico": peak["x_peak"],
                    "Y do pico": peak["y_peak"],
                    "Largura a meia altura": peak["fwhm"],
                })
            if include_final:
                last = final_point(series_frame["x"].to_numpy(), series_frame["y"].to_numpy())
                row.update({"Último X com Y > 0": last["x_final"], "Y nesse ponto": last["y_final"]})
            rows.append(row)
        results = pd.DataFrame(rows)
        st.dataframe(results, hide_index=True, use_container_width=True)
        st.download_button("Baixar análises (CSV)", results.to_csv(index=False).encode("utf-8-sig"), "analises.csv", "text/csv", key=f"an-dl-{eid}")

    with st.expander("Exportar e rastreabilidade"):
        provenance = [
            {"documento": p["entry"]["document"]["name"], "sha256": p["entry"]["document"]["sha256"],
             "origem": p["entry"]["table"].get("location"), "x": p["x"], "y": p["ys"],
             "correcoes": stored.get(p["entry"]["key"], {}),
             "alertas_abertos": [f["message"] for f in p["entry"]["table"].get("flags", []) if f["level"] == "aviso"]}
            for p in prepared
        ]
        for item in provenance:
            st.caption(f"{item['documento']} · {item['origem']}")
        st.download_button("Dados plotados (CSV)", long.to_csv(index=False).encode("utf-8-sig"), "dados_plotados.csv", "text/csv", key=f"ex-csv-{eid}")
        st.download_button("Transformações e origem (JSON)", json.dumps({"transformacoes": params, "series": provenance}, ensure_ascii=False, indent=2).encode("utf-8"),
                           "transformacoes.json", "application/json", key=f"ex-json-{eid}")
        st.download_button("Gráfico interativo (HTML)", fig.to_html(include_plotlyjs="cdn").encode("utf-8"), "grafico.html", "text/html", key=f"ex-html-{eid}")


# ----------------------------------------------------------------------------- tabelas

def show_tables(experiment: dict) -> None:
    st.subheader("Tabelas")
    entries = collect_entries(experiment)
    if not entries:
        st.info("Nenhuma tabela foi extraída.")
        return
    by_key = {e["key"]: e for e in entries}
    key = st.selectbox("Tabela / bloco", list(by_key), format_func=lambda k: _label(by_key[k]), key=f"tb-sel-{experiment['id']}")
    entry = by_key[key]
    table = entry["table"]
    block = table.get("block", {})
    stored = storage.load_overrides(experiment)
    st.caption(f"Origem: {entry['document']['name']} · {table.get('location', '')}")
    if block.get("sheet_titles"):
        st.caption("Título(s) da planilha: " + " | ".join(block["sheet_titles"]))
    if table.get("params"):
        st.caption("Parâmetros do rótulo: " + ", ".join(f"{k}={v}" for k, v in table["params"].items()))
    _show_flags(table)
    frame, meta = entry_frame(entry, entries, stored)
    if stored.get(key):
        st.info("Esta visualização aplica correções do usuário (veja o Explorador). O arquivo original não foi alterado.")
    st.markdown("**Colunas**")
    st.dataframe(pd.DataFrame([{
        "Coluna": m["name"], "Unidade": m["unit"], "Grandeza": QUANTITY_LABELS.get(m["quantity"], m["quantity"]),
        "Tipo": m["kind"], "Valores numéricos": f"{m['n_numeric']}/{m['n_nonempty']}", "Mín": m["min"], "Máx": m["max"],
    } for m in meta]), hide_index=True, use_container_width=True)
    shown = frame.copy()
    rows = table.get("source_rows", [])
    if len(rows) == len(shown):
        shown.insert(0, "Linha original", rows)
    st.download_button("Exportar CSV", shown.to_csv(index=False).encode("utf-8-sig"),
                       f"{Path(entry['document']['name']).stem}_{table['name']}.csv".replace("/", "-"), "text/csv", key=f"tb-dl-{key}")
    st.dataframe(shown, hide_index=True, use_container_width=True)
    if table.get("page") and entry["document"].get("extension") == ".pdf":
        if st.button("Ver a página do PDF", key=f"tb-pg-{key}"):
            _show_pdf_page(experiment, entry["document"], table["page"])


# ----------------------------------------------------------------------------- texto, legendas e PDFs

def _show_pdf_page(experiment: dict, document: dict, page: int) -> None:
    try:
        st.image(
            render_pdf_page(storage.read_original(experiment, document), int(page), dpi=150),
            caption=f"{document['name']} · página {page}",
            use_container_width=True,
        )
    except Exception as error:
        st.warning(f"Não foi possível renderizar a página (PyMuPDF instalado?): {error}")


def _open_pdf_page(experiment_id: str, document_id: str, page: int) -> None:
    """Callback: atualiza o leitor antes que seus widgets sejam construídos."""
    st.session_state[f"pdf-document-{experiment_id}"] = document_id
    st.session_state[f"pdf-page-{experiment_id}"] = int(page)


def show_search(experiment: dict) -> None:
    st.subheader("Leitor de PDFs")
    documents = [
        document for document in experiment.get("documents", [])
        if document.get("extension") == ".pdf" and document.get("status") != "erro"
    ]
    if not documents:
        st.info("Importe um PDF para pesquisar e navegar por páginas no leitor.")
        return
    eid = experiment["id"]
    by_id = {document["id"]: document for document in documents}
    document_key = f"pdf-document-{eid}"
    page_key = f"pdf-page-{eid}"
    if st.session_state.get(document_key) not in by_id:
        st.session_state[document_key] = documents[0]["id"]

    st.caption(
        "A pesquisa localiza páginas por termos e sinônimos em português e inglês. "
        "Os resultados abrem a página correspondente; o leitor não apresenta o texto extraído como se fosse o documento original."
    )
    query = st.text_input("Pesquisar nos PDFs", placeholder="Ex.: extinção chama fria ozônio", key=f"se-q-{eid}")
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
            st.warning("Nada encontrado. PDFs digitalizados sem OCR podem não ter texto pesquisável.")
        else:
            st.caption(f"{len(page_results)} página(s) localizada(s). Selecione uma para abrir no leitor.")
        for rank, result in enumerate(page_results[:60], start=1):
            left, right = st.columns([6, 1])
            left.write(f"{rank}. {result['document']['name']} · página {result['page']}")
            left.caption("Termos localizados: " + ", ".join(result["matched_terms"]))
            right.button(
                "Abrir página",
                key=f"se-pg-{rank}-{result['document']['sha256'][:8]}",
                on_click=_open_pdf_page,
                args=(eid, result["document"]["id"], int(result["page"])),
                use_container_width=True,
            )

    st.markdown("### Página do documento")
    selected_id = st.selectbox(
        "PDF aberto",
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
    page = st.number_input("Página", min_value=1, max_value=max_page, step=1, key=page_key)
    _show_pdf_page(experiment, selected_document, int(page))


# ----------------------------------------------------------------------------- metadados ISA

def show_metadata(experiment: dict) -> None:
    st.subheader("Metadados dos estudos (ISA-Tab)")
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
            st.caption(f"{document['name']} · enviado {study['submitted']} · liberação pública {study['released']} · "
                       f"{comments.get('Managing NASA Center', '')} · {comments.get('Project Type', '')} · {comments.get('SubResearch Area', '')}")
            if comments.get("Investigation Start Date"):
                st.caption(f"Período da investigação: {comments['Investigation Start Date']} a {comments.get('Investigation End Date', '?')}")
            if isa["design_types"]:
                st.markdown("**Palavras-chave:** " + " · ".join(isa["design_types"]))
            for field in ("Objective", "Hypothesis", "Approach", "Research Impacts"):
                if comments.get(field):
                    with st.expander(field):
                        st.write(comments[field])
            if isa["publications"]:
                st.markdown("**Publicações**")
                st.dataframe(pd.DataFrame(isa["publications"])[["year", "title", "authors", "doi", "link"]], hide_index=True, use_container_width=True)
            if isa["contacts"]:
                st.markdown("**Contatos**")
                st.dataframe(pd.DataFrame(isa["contacts"]), hide_index=True, use_container_width=True)
            if isa["empty_sections"]:
                st.warning("Sem fatores, ensaios ou protocolos descritos no ISA: " + ", ".join(isa["empty_sections"]) + ".")
    if not found:
        st.info("Nenhum arquivo ISA-Tab (i_Investigation*.txt) foi importado neste experimento.")

