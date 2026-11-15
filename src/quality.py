"""Alertas de qualidade para dados científicos tabulares.

Nada é corrigido automaticamente. Cada alerta descreve o problema e, quando há
uma correção plausível, traz ``suggest`` (ex.: trocar rótulos de duas colunas),
que a interface oferece ao usuário como correção reversível.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .frames import AXIS_KINDS, numeric_columns
from .quantities import QUANTITY_LABELS

MIN_ROWS_FOR_AXIS_CHECKS = 15


def flag(level: str, code: str, message: str, columns: list[str] | None = None, suggest: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"level": level, "code": code, "message": message, "columns": columns or [], "suggest": suggest or {}}


def monotone_fraction(values: np.ndarray) -> float:
    v = values[~np.isnan(values)]
    if len(v) < 3:
        return 1.0
    d = np.diff(v)
    d = d[d != 0]
    if len(d) == 0:
        return 1.0
    return float(max((d > 0).mean(), (d < 0).mean()))


def _is_axis_like(values: np.ndarray) -> bool:
    v = values[~np.isnan(values)]
    return len(v) >= MIN_ROWS_FOR_AXIS_CHECKS and monotone_fraction(values) >= 0.98 and len(np.unique(v)) > 0.5 * len(v)


def check_table(frame: pd.DataFrame, meta: list[dict[str, Any]], table: dict[str, Any]) -> list[dict[str, Any]]:
    flags: list[dict[str, Any]] = []
    n_rows = len(frame)
    numeric = numeric_columns(meta)
    by_name = {m["name"]: m for m in meta}
    block = table.get("block", {})

    if block.get("has_header") is False:
        flags.append(flag("aviso", "sem_cabecalho", "Não foi encontrado cabeçalho; as colunas receberam nomes provisórios."))

    for column in numeric:
        m = by_name[column]
        missing = m["n_rows"] - m["n_nonempty"]
        if missing > 0:
            flags.append(flag("info", "valores_ausentes", f"'{column}': {missing} de {m['n_rows']} valores ausentes.", [column]))
        if m["kind"] == "numeric" and 0.5 <= m["numeric_ratio"] < 1.0:
            ignored = m["n_nonempty"] - m["n_numeric"]
            flags.append(flag("aviso", "texto_em_coluna_numerica", f"'{column}': {ignored} célula(s) de texto serão ignoradas na parte numérica.", [column]))
        if m["kind"] == "range":
            flags.append(flag("info", "intervalos_em_celulas", f"'{column}': contém intervalos/aproximações; foram criadas colunas mín/máx.", [column]))
        if m["quantity"] == "intensity" and m["min"] is not None and m["min"] < 0:
            flags.append(flag("info", "sinal_negativo", f"'{column}': mínimo {m['min']:.3g} (ruído de linha de base); evite escala logarítmica direta.", [column]))

    if n_rows >= MIN_ROWS_FOR_AXIS_CHECKS:
        arrays = {c: frame[c].to_numpy(dtype=float) for c in numeric if c in frame}
        for column, values in arrays.items():
            quantity = by_name[column]["quantity"]
            if quantity not in AXIS_KINDS or monotone_fraction(values) >= 0.9:
                continue
            alternatives = [c for c, v in arrays.items() if c != column and _is_axis_like(v)]
            if alternatives:
                other = alternatives[0]
                flags.append(flag(
                    "aviso", "rotulos_trocados",
                    f"'{column}' está rotulada como {QUANTITY_LABELS.get(quantity, quantity)}, mas não é monótona; "
                    f"'{other}' é monótona e parece ser o eixo. Os rótulos podem estar trocados.",
                    [column, other], {"swap": [column, other]},
                ))
            else:
                flags.append(flag(
                    "aviso", "eixo_ausente",
                    f"'{column}' está rotulada como {QUANTITY_LABELS.get(quantity, quantity)}, mas não é monótona e nenhuma outra "
                    "coluna serve de eixo. A coordenada espacial/temporal parece não estar no arquivo.",
                    [column],
                ))
        names = list(arrays)[:12]
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                both = ~np.isnan(arrays[a]) & ~np.isnan(arrays[b])
                if both.sum() < MIN_ROWS_FOR_AXIS_CHECKS:
                    continue
                diff = arrays[b][both] - arrays[a][both]
                scale = max(1.0, float(np.abs(diff).mean()))
                if float(diff.std()) <= 1e-9 * scale and abs(float(diff.mean())) > 0:
                    flags.append(flag(
                        "info", "deslocamento_constante",
                        f"'{b}' = '{a}' + {diff.mean():.6g} (constante): é a mesma série com linha de base somada.", [a, b],
                    ))

    chart = table.get("chart", {})
    x_name = chart.get("x")
    if x_name and x_name in frame and n_rows >= 3:
        x = frame[x_name].to_numpy(dtype=float)
        mf = monotone_fraction(x)
        valid = x[~np.isnan(x)]
        if mf < 0.9:
            flags.append(flag("info", "x_fora_de_ordem", f"'{x_name}' não está ordenada; o explorador ordena por X antes de ligar os pontos.", [x_name]))
        elif len(valid) > 2 and np.all(np.diff(valid) <= 0) and valid[0] != valid[-1]:
            flags.append(flag("info", "x_decrescente", f"'{x_name}' está em ordem decrescente.", [x_name]))
        if len(np.unique(valid)) < len(valid):
            flags.append(flag("info", "x_repetido", f"'{x_name}' tem valores repetidos.", [x_name]))
    return flags


def check_sheet(entries: list[dict[str, Any]]) -> None:
    """Checagens entre blocos da mesma planilha. ``entries``: {table, frame, meta}; altera table['flags']."""
    data_entries = [e for e in entries if e["table"].get("block", {}).get("kind") == "data"]

    # Eixo ausente: procura em blocos irmãos uma coluna-eixo com o mesmo número de linhas.
    for entry in data_entries:
        for f in entry["table"]["flags"]:
            if f["code"] != "eixo_ausente":
                continue
            n = len(entry["frame"])
            for other in data_entries:
                if other is entry or len(other["frame"]) != n:
                    continue
                for column in numeric_columns(other["meta"]):
                    if _is_axis_like(other["frame"][column].to_numpy(dtype=float)):
                        f["suggest"] = {"borrow_axis": {
                            "table": other["table"]["name"], "column": column,
                            "replaces": f["columns"][0], "name": f["columns"][0],
                        }}
                        f["message"] += (
                            f" Há um eixo candidato em '{other['table']['name']}' (coluna '{column}', mesmo nº de linhas); "
                            "usá-lo é uma suposição, confirme na publicação."
                        )
                        break
                if f["suggest"]:
                    break

    # % versus fração para a mesma grandeza em blocos irmãos.
    seen: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]] = {}
    for entry in data_entries + [e for e in entries if e not in data_entries]:
        for m in entry["meta"]:
            if m["quantity"] == "fraction" and m["max"] is not None:
                seen.setdefault(m["base"], []).append((entry, m))
    for base, items in seen.items():
        fractions = [m for _, m in items if m["max"] <= 1.0]
        percents = [(e, m) for e, m in items if m["min"] is not None and m["min"] > 1.0 and m["max"] <= 100.0]
        if fractions and percents:
            for entry, m in percents:
                entry["table"]["flags"].append(flag(
                    "aviso", "percentual_vs_fracao",
                    f"'{m['name']}' está em % (valores de {m['min']:g} a {m['max']:g}), enquanto outros blocos desta origem usam fração (0–1).",
                    [m["name"]], {"divide_by_100": [m["name"]]},
                ))

    # Blocos de mesmo formato com comprimentos ligeiramente diferentes.
    groups: dict[tuple[str, ...], list[dict[str, Any]]] = {}
    for entry in data_entries:
        groups.setdefault(tuple(entry["table"]["original_headers"]), []).append(entry)
    for group in groups.values():
        lengths = [len(e["frame"]) for e in group]
        if len(group) > 1 and min(lengths) >= 100 and max(lengths) != min(lengths) and (max(lengths) - min(lengths)) <= 0.05 * max(lengths):
            for entry in group:
                if len(entry["frame"]) != max(lengths):
                    entry["table"]["flags"].append(flag(
                        "info", "comprimento_diferente",
                        f"{len(entry['frame'])} linhas, enquanto blocos do mesmo formato têm até {max(lengths)}.",
                    ))

