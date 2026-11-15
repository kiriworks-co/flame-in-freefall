"""Busca lexical (com sinônimos PT/EN) em texto, legendas, tabelas e metadados ISA. Não é busca semântica."""

from __future__ import annotations

import re
import unicodedata
from typing import Any

_STOPWORDS = {
    "a", "as", "o", "os", "um", "uma", "de", "da", "do", "das", "dos", "em", "no", "na", "nos", "nas", "por",
    "para", "com", "sem", "e", "ou", "que", "qual", "quais", "como", "foi", "sao", "ser",
    "the", "of", "in", "on", "and", "or", "to", "for", "with", "is", "are",
}

_SYNONYM_GROUPS = [
    {"extincao", "extinction", "quenching"}, {"chama", "flame", "flames"}, {"fria", "cool", "cold"},
    {"gota", "droplet", "goticula", "drop"}, {"ozonio", "ozone", "o3"}, {"temperatura", "temperature"},
    {"pressao", "pressure"}, {"combustivel", "fuel"}, {"diametro", "diameter"},
    {"queima", "burning", "combustao", "combustion"}, {"oscilacao", "oscillation", "oscillatory"},
    {"estiramento", "strain", "stretch"}, {"microgravidade", "microgravity"}, {"tabela", "table"},
    {"figura", "figure", "fig"}, {"atraso", "delay"}, {"ignicao", "ignition"}, {"radiacao", "radiation"},
    {"limite", "limit", "limits"}, {"distancia", "distance"}, {"sinal", "signal"}, {"oxigenio", "oxygen"},
    {"concentracao", "concentration"}, {"contrafluxo", "counterflow"},
]
_SYN = {term: group for group in _SYNONYM_GROUPS for term in group}


def normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def _tokens(text: str) -> list[str]:
    return [w for w in re.findall(r"[\w]+", normalize(text)) if w and w not in _STOPWORDS]


def _snippet(text: str, variants: list[set[str]], limit: int = 440) -> str:
    if len(text) <= limit:
        return text
    normalized = normalize(text)
    positions = [normalized.find(v) for group in variants for v in group if normalized.find(v) >= 0]
    center = min(positions) if positions else 0
    start = max(0, center - limit // 4)
    end = min(len(text), start + limit)
    return ("…" if start else "") + text[start:end].strip() + ("…" if end < len(text) else "")


def table_search_text(table: dict[str, Any]) -> str:
    block = table.get("block", {})
    parts = [table.get("name", ""), table.get("location", ""), block.get("label") or "", " ".join(block.get("titles", []))]
    parts.append(" ".join(table.get("columns", [])))
    parts.append(" ".join(f"{k} {v}" for k, v in table.get("params", {}).items()))
    seen: list[str] = []
    for row in table.get("rows", [])[:400]:
        for cell in row:
            if isinstance(cell, str) and cell.strip() and cell not in seen:
                seen.append(cell)
        if len(seen) >= 200:
            break
    parts.append(" ".join(seen))
    return "\n".join(p for p in parts if p)


def _items(document: dict[str, Any], extraction: dict[str, Any]):
    kind_page = "texto" if document.get("extension") != ".pdf" else "pdf"
    for page in extraction.get("pages", []):
        text = str(page.get("text", ""))
        if text.strip():
            yield {"kind": kind_page, "location": page.get("location", ""), "text": text, "page": page.get("page")}
    for caption in extraction.get("captions", []):
        cond = ", ".join(f"{c['symbol']}={c['value']:g}{c['unit']}" for c in caption.get("conditions", []))
        yield {
            "kind": "legenda", "location": f"página {caption['page']}, {caption['kind']} {caption['number']}",
            "text": caption["text"] + (f"  [condições: {cond}]" if cond else ""), "page": caption["page"],
        }
    for index, table in enumerate(extraction.get("tables", [])):
        yield {"kind": "tabela", "location": table.get("location", ""), "text": table_search_text(table), "table_index": index}


def search_content(documents: list[dict[str, Any]], query: str, load_extraction, kinds: set[str] | None = None) -> list[dict[str, Any]]:
    terms = list(dict.fromkeys(_tokens(query)))
    if not terms:
        return []
    variants = [_SYN.get(t, {t}) for t in terms]
    results: list[dict[str, Any]] = []
    for document in documents:
        if document.get("status") == "erro":
            continue
        try:
            extraction = load_extraction(document)
        except (OSError, ValueError, KeyError):
            continue
        for item in _items(document, extraction):
            if kinds and item["kind"] not in kinds:
                continue
            haystack = " ".join(_tokens(item["text"]))
            matched = [t for t, group in zip(terms, variants) if any(v in haystack for v in group)]
            if not matched:
                continue
            coverage = len(matched) / len(terms)
            phrase = len(terms) > 1 and " ".join(terms) in haystack
            results.append({
                **item, "document": document, "score": coverage + (0.8 if phrase else 0.0), "coverage": coverage,
                "matched_terms": matched, "snippet": _snippet(item["text"], variants),
            })
    return sorted(results, key=lambda r: (r["score"], r["coverage"]), reverse=True)

