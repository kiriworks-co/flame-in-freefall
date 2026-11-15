"""Transforma blocos detectados em tabelas enriquecidas (colunas tipadas, parâmetros, gráfico sugerido, alertas)."""

from __future__ import annotations

import re
from typing import Any

from .blocks import make_table
from .frames import suggest_chart, table_to_frame
from .quality import check_sheet, check_table
from .quantities import parse_label_params, split_header


def _data_id(*texts: str | None) -> int | None:
    for text in texts:
        match = re.search(r"data\s*id\D{0,3}(\d+)", text or "", re.I)
        if match:
            return int(match.group(1))
    return None


def enrich_table(table: dict[str, Any]) -> tuple[Any, list[dict[str, Any]]]:
    frame, meta = table_to_frame(table)
    table["column_meta"] = meta
    table["chart"] = suggest_chart(meta, len(frame), table.get("block", {}).get("kind", "data"))
    table["flags"] = check_table(frame, meta, table)
    return frame, meta


def enrich_tables(tables: list[dict[str, Any]]) -> None:
    """Enriquece tabelas de uma mesma planilha/arquivo e roda as checagens entre blocos irmãos."""
    entries = []
    for table in tables:
        frame, meta = enrich_table(table)
        entries.append({"table": table, "frame": frame, "meta": meta})
    check_sheet(entries)


def tables_from_blocks(sheet_name: str, detected: dict[str, Any]) -> list[dict[str, Any]]:
    blocks = detected["blocks"]
    tables: list[dict[str, Any]] = []
    data_id = _data_id(sheet_name, *detected["sheet_titles"])
    for index, block in enumerate(blocks, start=1):
        label = block["label"]
        if label:
            name = f"{sheet_name} · {label}"
        elif len(blocks) > 1:
            name = f"{sheet_name} · bloco {index}"
        else:
            name = sheet_name
        location = f"planilha '{sheet_name}', intervalo {block['range']}" + (f", rótulo '{label}'" if label else "")
        table = make_table(name, location, block["headers"], block["rows"], block["header_row"], block["source_rows"])
        table["block"] = {
            "sheet": sheet_name,
            "range": block["range"],
            "label": label,
            "titles": block["titles"],
            "sheet_titles": detected["sheet_titles"],
            "kind": block["kind"],
            "has_header": block["has_header"],
        }
        table["params"] = parse_label_params(label)
        if data_id is not None:
            table["data_id"] = data_id
        tables.append(table)
    names = [t["name"] for t in tables]
    if len(set(names)) < len(names):  # nomes repetidos: diferencia TODOS os blocos pela grandeza medida
        for table in tables:
            if table["columns"]:
                base, _ = split_header(table["columns"][-1])
                table["name"] = f"{table['name']} · {base}"
    enrich_tables(tables)
    return tables

