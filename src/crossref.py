"""Referência cruzada entre tabelas-índice (catálogos) e blocos de dados, com detecção de divergências."""

from __future__ import annotations

import re
from typing import Any

from .quantities import parse_number

_STOP = {"the", "a", "an", "and", "of", "o", "a", "os", "as", "um", "uma"}


def normalize_doi(value: str | None) -> str:
    if not value:
        return ""
    match = re.search(r"10\.\d{4,9}/[^\s]+", str(value))
    return match.group(0).rstrip(".,;)").lower() if match else ""


def qualifiers(text: str) -> dict[str, bool]:
    """'with ozone' -> {'ozone': True}; 'no ozone' / 'without ozone' / 'sem ozônio' -> {...: False}."""
    result: dict[str, bool] = {}
    for match in re.finditer(r"\b(with|without|no|sem|com)\s+([A-Za-zÀ-ÿ0-9]+)", text, re.I):
        noun = match.group(2).casefold()
        if noun in _STOP:
            continue
        result[noun] = match.group(1).casefold() in {"with", "com"}
    return result


def normalize_figure(value: str | None) -> str:
    if value is None:
        return ""
    number = parse_number(value)
    if number is not None:
        return str(int(number)) if float(number).is_integer() else str(number)
    return re.sub(r"^(fig(ure|ura)?\.?\s*)", "", str(value).strip(), flags=re.I).casefold()


def _find(columns: list[str], pattern: str) -> int | None:
    for i, name in enumerate(columns):
        if re.search(pattern, name, re.I):
            return i
    return None


def build_crossref(documents: list[dict[str, Any]], extractions: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """``documents``: registros do experimento; ``extractions``: sha256 -> extração."""
    entries: dict[int, dict[str, Any]] = {}

    def entry(data_id: int) -> dict[str, Any]:
        return entries.setdefault(data_id, {"data_id": data_id, "sources": [], "blocks": [], "conflicts": []})

    files: list[dict[str, Any]] = []
    names = [d["name"].casefold() for d in documents]
    for document in documents:
        extraction = extractions.get(document["sha256"])
        if not extraction:
            continue
        for index, table in enumerate(extraction.get("tables", [])):
            columns = table["columns"]
            id_col = _find(columns, r"data\s*id")
            desc_col = _find(columns, r"descri")
            if id_col is not None and desc_col is not None:
                doi_col = _find(columns, r"link|doi|refer")
                fig_col = _find(columns, r"fig")
                journal_col = _find(columns, r"journal|publica")
                for row in table["rows"]:
                    number = parse_number(row[id_col])
                    if number is None:
                        continue
                    entry(int(number))["sources"].append({
                        "document": document["name"],
                        "description": str(row[desc_col] or ""),
                        "doi": normalize_doi(row[doi_col]) if doi_col is not None else "",
                        "figure": normalize_figure(row[fig_col]) if fig_col is not None else "",
                        "journal": str(row[journal_col]) if journal_col is not None and row[journal_col] is not None else "",
                    })
            file_col = _find(columns, r"data\s*file|arquivo|identificador")
            if file_col is not None:
                for row in table["rows"]:
                    value = row[file_col]
                    if value:
                        files.append({
                            "document": document["name"], "file": str(value),
                            "imported": any(str(value).casefold() in n for n in names),
                        })
            if table.get("data_id") is not None:
                entry(int(table["data_id"]))["blocks"].append({
                    "document": document["name"], "table_index": index, "name": table["name"], "sha256": document["sha256"],
                })

    for item in entries.values():
        sources = item["sources"]
        for i, a in enumerate(sources):
            for b in sources[i + 1:]:
                if a["doi"] and b["doi"] and a["doi"] != b["doi"]:
                    item["conflicts"].append(f"DOI diferente entre '{a['document']}' ({a['doi']}) e '{b['document']}' ({b['doi']}).")
                if a["figure"] and b["figure"] and a["figure"].strip() != b["figure"].strip():
                    item["conflicts"].append(f"Figura diferente: '{a['figure']}' ({a['document']}) contra '{b['figure']}' ({b['document']}).")
                qa, qb = qualifiers(a["description"]), qualifiers(b["description"])
                for noun in set(qa) & set(qb):
                    if qa[noun] != qb[noun]:
                        item["conflicts"].append(
                            f"Descrições se contradizem sobre '{noun}': {a['document']} diz "
                            f"{'com' if qa[noun] else 'sem'}, {b['document']} diz {'com' if qb[noun] else 'sem'}."
                        )
        if sources and not item["blocks"]:
            item["conflicts"].append("Há descrição no índice, mas nenhum bloco de dados com este Data ID foi importado.")
    return {"entries": [entries[k] for k in sorted(entries)], "files": files}

