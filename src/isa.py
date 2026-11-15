"""Leitura de arquivos ISA-Tab (i_Investigation*.txt) do PSI.

Formato: TSV em que cada linha é um campo (rótulo na 1ª coluna, valores nas
seguintes) e linhas só com texto em maiúsculas iniciam seções. Campos longos
(Approach, Objective) vêm entre aspas e podem ter quebras de linha, então a
leitura usa ``csv`` e não ``splitlines``.
"""

from __future__ import annotations

import csv
import io
import re
from datetime import datetime
from typing import Any


def looks_like_isa(text: str) -> bool:
    head = text[:4000]
    return "ONTOLOGY SOURCE REFERENCE" in head or (
        re.search(r"^STUDY\s*$", text, re.M) is not None and "Study Identifier" in text
    )


def is_placeholder(text: str) -> bool:
    """Arquivos s_*.txt do PSI trazem apenas 'Do not use this'."""
    lines = [line for line in text.splitlines() if line.strip()]
    return len(lines) <= 3 and "do not use this" in text.casefold()


def normalize_date(value: str) -> str:
    for fmt in ("%d-%b-%Y", "%m-%d-%Y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(value.strip(), fmt).date().isoformat()
        except ValueError:
            continue
    return value


def _read_rows(text: str) -> list[list[str]]:
    rows = list(csv.reader(io.StringIO(text, newline=""), delimiter="\t", quotechar='"'))
    # Aspas desbalanceadas fariam o resto do arquivo virar um único campo: cai para leitura simples.
    if len(rows) < max(5, len([line for line in text.splitlines() if line.strip()]) // 4):
        rows = [line.split("\t") for line in text.splitlines()]
    return rows


def _trim(values: list[str]) -> list[str]:
    values = [v.strip() for v in values]
    while values and not values[-1]:
        values.pop()
    return values


def _aligned(section: dict[str, list[str]], fields: dict[str, str]) -> list[dict[str, str]]:
    """Listas paralelas (publicações, contatos): registro i = i-ésimo valor de cada campo."""
    count = max((len(section.get(label, [])) for label in fields), default=0)
    records = []
    for i in range(count):
        record = {key: (section.get(label, [])[i] if i < len(section.get(label, [])) else "") for label, key in fields.items()}
        if any(record.values()):
            records.append(record)
    return records


def parse_isa(text: str) -> dict[str, Any]:
    sections: dict[str, dict[str, list[str]]] = {}
    current = ""
    for row in _read_rows(text):
        cells = [c for c in row]
        if not any(c.strip() for c in cells):
            continue
        label = cells[0].strip()
        rest = [c for c in cells[1:] if c.strip()]
        if label and label.upper() == label and re.fullmatch(r"[A-Z ]+", label) and not rest:
            current = label
            sections.setdefault(current, {})
            continue
        sections.setdefault(current, {})[label] = _trim(cells[1:])

    study = sections.get("STUDY", {})

    def first(label: str) -> str:
        values = study.get(label, [])
        return values[0] if values else ""

    comments = {}
    for label, values in study.items():
        match = re.fullmatch(r"Comment\[(.+)\]", label)
        if match and values:
            comments[match.group(1)] = values[0] if len(values) == 1 else "; ".join(v for v in values if v)

    for key in ("Investigation Start Date", "Investigation End Date"):
        if key in comments:
            comments[key] = normalize_date(comments[key])

    publications = _aligned(
        sections.get("STUDY PUBLICATIONS", {}),
        {
            "Study PubMed ID": "pubmed",
            "Study Publication DOI": "doi",
            "Study Publication Author List": "authors",
            "Study Publication Title": "title",
            "Study Publication Status": "status",
            "Comment[Study Publication Link]": "link",
        },
    )
    for record in publications:
        year = re.search(r"\((\d{4})\)\s*$", record.get("title", ""))
        record["year"] = year.group(1) if year else ""
        record["title"] = re.sub(r"\s*\(\d{4}\)\s*$", "", record.get("title", "")).strip()
        record["title"] = re.sub(r"\s+", " ", record["title"])

    contacts = _aligned(
        sections.get("STUDY CONTACTS", {}),
        {
            "Study Person Last Name": "sobrenome",
            "Study Person First Name": "nome",
            "Study Person Email": "email",
            "Study Person Affiliation": "afiliacao",
            "Study Person Roles": "funcao",
            "Comment[orcidIdentifier]": "orcid",
        },
    )

    design = [v for v in sections.get("STUDY DESIGN DESCRIPTORS", {}).get("Study Design Type", []) if v]
    empty_sections = [
        name for name in ("STUDY FACTORS", "STUDY ASSAYS", "STUDY PROTOCOLS")
        if not any(values for values in sections.get(name, {}).values())
    ]
    return {
        "study": {
            "id": first("Study Identifier"),
            "title": first("Study Title"),
            "description": first("Study Description"),
            "submitted": normalize_date(first("Study Submission Date")),
            "released": normalize_date(first("Study Public Release Date")),
            "file": first("Study File Name"),
        },
        "comments": comments,
        "design_types": design,
        "publications": publications,
        "contacts": contacts,
        "empty_sections": empty_sections,
    }


def isa_pages(parsed: dict[str, Any]) -> list[dict[str, Any]]:
    """Cada campo textual vira um 'trecho' pesquisável com origem identificada."""
    pages: list[dict[str, Any]] = []

    def add(location: str, text: str) -> None:
        if text and text.strip():
            pages.append({"page": len(pages) + 1, "location": location, "text": text.strip()})

    study = parsed["study"]
    add("ISA > Estudo > Título", f"{study['id']} {study['title']}".strip())
    for key, value in parsed["comments"].items():
        add(f"ISA > Estudo > {key}", value)
    add("ISA > Estudo > Palavras-chave", ", ".join(parsed["design_types"]))
    for i, pub in enumerate(parsed["publications"], start=1):
        add(f"ISA > Publicação {i}", " ".join(filter(None, [pub["title"], pub["authors"], pub["year"], pub["doi"]])))
    return pages

