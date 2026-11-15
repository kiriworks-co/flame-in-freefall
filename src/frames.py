"""Colunas tipadas, sugestão de gráfico e construção de DataFrames a partir das tabelas extraídas.

As tabelas extraídas guardam valores brutos. Aqui eles viram colunas numéricas
(com unidade e grandeza física), sem descartar texto em silêncio: o que não
converte é contado e aparece como alerta. Correções do usuário (``overrides``)
são aplicadas aqui, sem tocar no original.
"""

from __future__ import annotations

from typing import Any, Callable

import numpy as np
import pandas as pd

from .quantities import classify_quantity, parse_number, parse_range, split_header

NUMERIC_THRESHOLD = 0.8
AXIS_KINDS = {"time", "length"}


# ----------------------------------------------------------------------------- metadados de colunas

def describe_columns(columns: list[str], rows: list[list[Any]]) -> list[dict[str, Any]]:
    meta: list[dict[str, Any]] = []
    for j, column in enumerate(columns):
        values = [row[j] if j < len(row) else None for row in rows]
        nonempty = [v for v in values if v is not None and str(v).strip() != ""]
        numbers = [parse_number(v) for v in nonempty]
        n_numeric = sum(n is not None for n in numbers)
        n_range = sum(1 for v, n in zip(nonempty, numbers) if n is None and parse_range(v) is not None)
        base, unit = split_header(column)
        if not nonempty:
            kind = "empty"
        elif n_numeric / len(nonempty) >= NUMERIC_THRESHOLD:
            kind = "numeric"
        elif n_range and (n_numeric + n_range) / len(nonempty) >= NUMERIC_THRESHOLD:
            kind = "range"
        else:
            kind = "text"
        finite = [n for n in numbers if n is not None]
        meta.append({
            "name": column,
            "base": base,
            "unit": unit,
            "kind": kind,
            "quantity": classify_quantity(base, unit) if kind in ("numeric", "range") else "unknown",
            "n_rows": len(values),
            "n_nonempty": len(nonempty),
            "n_numeric": n_numeric,
            "n_range": n_range,
            "numeric_ratio": round(n_numeric / len(nonempty), 3) if nonempty else 0.0,
            "min": min(finite) if finite else None,
            "max": max(finite) if finite else None,
        })
    return meta


def axis_label(meta: dict[str, Any]) -> str:
    return f"{meta['base']} [{meta['unit']}]" if meta.get("unit") else meta["name"]


# ----------------------------------------------------------------------------- sugestão de gráfico

_PREFERRED_Y = ["diameter", "intensity", "temperature", "strain_rate", "burning_rate", "length", "ratio"]


def suggest_chart(meta: list[dict[str, Any]], n_rows: int, block_kind: str = "data") -> dict[str, Any]:
    """Tipo de gráfico, X e Y sugeridos a partir das grandezas físicas das colunas."""
    if block_kind == "catalog":
        return {"type": "catalog", "x": None, "y": []}
    numeric = [m for m in meta if m["kind"] in ("numeric", "range") and m["n_numeric"] > 0]
    if not numeric:
        return {"type": "catalog", "x": None, "y": []}

    header_numbers = sum(parse_number(m["name"]) is not None for m in meta)
    if len(meta) >= 5 and header_numbers >= 0.7 * len(meta):
        return {"type": "matrix", "x": None, "y": [m["name"] for m in numeric]}

    def pick(kinds: set[str]) -> dict[str, Any] | None:
        return next((m for m in numeric if m["quantity"] in kinds), None)

    def others(x: dict[str, Any]) -> list[str]:
        rest = [m for m in numeric if m["name"] != x["name"]]
        rest.sort(key=lambda m: (_PREFERRED_Y.index(m["quantity"]) if m["quantity"] in _PREFERRED_Y else 99))
        return [m["name"] for m in rest]

    x = pick({"time"})
    if x:
        return {"type": "time_series", "x": x["name"], "y": others(x)}
    x = pick({"length"})
    if x:
        return {"type": "spatial_profile", "x": x["name"], "y": others(x)}
    fraction = pick({"fraction"})
    if fraction and pick({"strain_rate"}):
        return {"type": "limit_curve", "x": fraction["name"], "y": others(fraction)}
    if len(numeric) >= 3 and n_rows >= 6:
        return {"type": "parametric", "x": numeric[0]["name"], "y": others(numeric[0])}
    if len(numeric) >= 2:
        return {"type": "parametric", "x": numeric[0]["name"], "y": others(numeric[0])}
    return {"type": "distribution", "x": None, "y": [numeric[0]["name"]]}


CHART_LABELS = {
    "time_series": "Série temporal", "spatial_profile": "Perfil espacial", "limit_curve": "Curva de limite",
    "parametric": "Paramétrico (X–Y)", "matrix": "Matriz / campo", "distribution": "Distribuição", "catalog": "Catálogo (texto)",
}


# ----------------------------------------------------------------------------- DataFrame

def _unique(name: str, existing: set[str]) -> str:
    candidate, k = name, 2
    while candidate in existing:
        candidate = f"{name}_{k}"
        k += 1
    return candidate


def apply_overrides(
    frame: pd.DataFrame,
    overrides: dict[str, Any] | None,
    resolve_axis: Callable[[dict[str, Any]], pd.Series | None] | None = None,
) -> pd.DataFrame:
    """Trocas de rótulo, renomeação, exclusão e eixo emprestado. Os valores originais não mudam."""
    if not overrides:
        return frame
    frame = frame.copy()
    for first, second in overrides.get("swap", []):
        if first in frame.columns and second in frame.columns:
            mapping = {first: second, second: first}
            frame = frame.rename(columns=mapping)
    rename = {old: new for old, new in overrides.get("rename", {}).items() if old in frame.columns and new}
    if rename:
        frame = frame.rename(columns=rename)
    drop = [c for c in overrides.get("ignore", []) if c in frame.columns]
    if drop:
        frame = frame.drop(columns=drop)
    borrow = overrides.get("borrow_axis")
    if borrow and resolve_axis is not None:
        series = resolve_axis(borrow)
        if series is not None and len(series) == len(frame):
            name = borrow.get("name") or "eixo emprestado"
            replaced = borrow.get("replaces")
            if replaced in frame.columns:  # a coluna mal rotulada deixa de se passar pelo eixo
                frame = frame.rename(columns={replaced: f"{replaced} (rótulo original; não é eixo)"})
            frame.insert(0, _unique(name, set(frame.columns)), series.to_numpy())
    return frame


def table_to_frame(
    table: dict[str, Any],
    overrides: dict[str, Any] | None = None,
    resolve_axis: Callable[[dict[str, Any]], pd.Series | None] | None = None,
) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    """Retorna (DataFrame tipado, metadados das colunas). Texto não numérico vira NaN apenas em colunas numéricas."""
    raw = pd.DataFrame(table.get("rows", []), columns=table.get("columns", []), dtype=object)
    raw = apply_overrides(raw, overrides, resolve_axis)
    meta = describe_columns(list(raw.columns), raw.values.tolist())
    data: dict[str, Any] = {}
    out_meta: list[dict[str, Any]] = []
    for m in meta:
        column = raw[m["name"]]
        if m["kind"] in ("numeric", "range"):
            data[m["name"]] = column.map(parse_number).astype(float)
            out_meta.append(m)
            if m["kind"] == "range":
                spans = column.map(lambda v: parse_range(v) or ({"min": parse_number(v), "max": parse_number(v)} if parse_number(v) is not None else None))
                for suffix, key in (("mín", "min"), ("máx", "max")):
                    name = _unique(f"{m['name']} ({suffix})", set(data))
                    data[name] = spans.map(lambda s, k=key: s[k] if s else np.nan).astype(float)
                    values = data[name].dropna()
                    out_meta.append({
                        **m, "name": name, "kind": "numeric", "base": f"{m['base']} ({suffix})",
                        "n_nonempty": int(len(values)), "n_numeric": int(len(values)), "n_range": 0, "numeric_ratio": 1.0,
                        "min": float(values.min()) if len(values) else None, "max": float(values.max()) if len(values) else None,
                    })
        elif m["kind"] == "empty":
            continue
        else:
            data[m["name"]] = column.map(lambda v: None if v is None else str(v))
            out_meta.append(m)
    frame = pd.DataFrame(data)
    divide = [c for c in (overrides or {}).get("divide_by_100", []) if c in frame.columns]
    for column in divide:
        frame[column] = frame[column] / 100.0
        for m in out_meta:
            if m["name"] == column:
                m["note"] = "convertido de % para fração"
    return frame, out_meta


def numeric_columns(meta: list[dict[str, Any]]) -> list[str]:
    return [m["name"] for m in meta if m["kind"] in ("numeric", "range") and m["n_numeric"] > 0]

