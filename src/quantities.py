"""Números, unidades, rótulos de bloco e classificação de grandezas físicas.

Tudo aqui é independente de experimento: as regras de classificação são dados
(``DEFAULT_RULES``) e podem ser estendidas por ``config/quantity_rules.json``.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

_NUM = r"[-+]?(?:\d+[.,]?\d*|[.,]\d+)(?:[eE][-+]?\d+)?"


# ----------------------------------------------------------------------------- números

def parse_number(value: Any) -> float | None:
    """Converte número ou texto numérico (vírgula/ponto, '~', '%') em float; senão None."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value) if math.isfinite(value) else None
    text = str(value).strip().replace("\u2212", "-").replace("\xa0", " ")
    text = text.lstrip("~≈").strip()
    if text.endswith("%"):
        text = text[:-1].strip()
    text = text.replace(" ", "")
    if not text or not re.fullmatch(r"[-+]?[\d.,]+(?:[eE][-+]?\d+)?", text):
        return None
    if "," in text and "." in text:
        decimal = "," if text.rfind(",") > text.rfind(".") else "."
        thousands = "." if decimal == "," else ","
        text = text.replace(thousands, "").replace(decimal, ".")
    elif text.count(",") > 1:
        text = text.replace(",", "")
    elif text.count(".") > 1:
        text = text.replace(".", "")
    else:
        text = text.replace(",", ".")
    try:
        number = float(text)
    except ValueError:
        return None
    return number if math.isfinite(number) else None


_RANGE = re.compile(rf"^\s*~?\s*({_NUM})\s*(?:-|–|—|to|a|até)\s*({_NUM})\s*$", re.I)
_LIST = re.compile(rf"^\s*~?\s*{_NUM}(?:\s*(?:,|;|and|e|&)\s*{_NUM})+\s*$", re.I)


def parse_range(value: Any) -> dict[str, Any] | None:
    """'2.0 - 7.0' -> min/max; '0.5 and 5.0' -> lista; '~4.5' -> valor aproximado."""
    if value is None or isinstance(value, (int, float)):
        return None
    text = str(value).strip()
    match = _RANGE.match(text)
    if match:
        low, high = parse_number(match.group(1)), parse_number(match.group(2))
        if low is not None and high is not None:
            return {"min": min(low, high), "max": max(low, high), "values": [low, high], "kind": "intervalo"}
    if _LIST.match(text):
        values = [parse_number(item) for item in re.findall(_NUM, text)]
        values = [item for item in values if item is not None]
        if len(values) >= 2:
            return {"min": min(values), "max": max(values), "values": values, "kind": "lista"}
    if text.startswith(("~", "≈")):
        number = parse_number(text)
        if number is not None:
            return {"min": number, "max": number, "values": [number], "kind": "aproximado"}
    return None


# ----------------------------------------------------------------------------- cabeçalhos e rótulos

_UNIT_TAIL = re.compile(r"^(?P<name>.*?)\s*[\(\[](?P<unit>[^\)\]]*)[\)\]]\s*$")
_UNIT_ALIASES = {"mol.%": "mol%", "mol. %": "mol%", "mol %": "mol%", "um": "µm", "us": "µs"}


def normalize_unit(unit: str | None) -> str:
    if not unit:
        return ""
    cleaned = unit.strip()
    return _UNIT_ALIASES.get(cleaned.lower(), cleaned)


def split_header(text: str) -> tuple[str, str]:
    """'aCFE (1/s)' -> ('aCFE', '1/s'); 'distance [cm]' -> ('distance', 'cm')."""
    match = _UNIT_TAIL.match(text.strip())
    if match and match.group("name").strip():
        return match.group("name").strip(), normalize_unit(match.group("unit"))
    return text.strip(), ""


_KV = re.compile(
    rf"(?P<key>[A-Za-zϕφΦ_][\w\.]*)\s*=\s*(?P<val>{_NUM})\s*(?P<unit>mol\.?\s*%|%|[A-Za-zµ°][\w/²³\.]*)?"
)
_LEAD_NUM = re.compile(rf"^\s*(?P<num>{_NUM})\s*,\s*(?P<tag>.+?)\s*$")
_FUEL = re.compile(r"^n-?C(\d{1,2})$", re.I)


def parse_label_params(label: str | None) -> dict[str, Any]:
    """Extrai parâmetros de rótulos de bloco: 'Xf = 0.1', 'O3 = 4.1 mol.%', '550,O3', 'nC12'."""
    params: dict[str, Any] = {}
    if not label:
        return params
    text = str(label).strip()
    for match in _KV.finditer(text):
        value = parse_number(match.group("val"))
        if value is None:
            continue
        key = match.group("key")
        params[key] = value
        unit = normalize_unit(match.group("unit"))
        if unit:
            params[f"{key}_unidade"] = unit
    if params:
        return params
    lead = _LEAD_NUM.match(text)
    if lead:
        params["valor_rotulo"] = parse_number(lead.group("num"))
        tag = lead.group("tag").strip()
        negated = re.match(r"^(no|sem|without)\s+(.+)$", tag, re.I)
        if negated:
            params[negated.group(2).strip()] = False
        else:
            params[tag] = True
        return params
    fuel = _FUEL.match(text)
    if fuel:
        params["combustivel"] = f"nC{fuel.group(1)}"
    return params


_COND_UNITS = {"atm": "P", "K": "T"}


def find_conditions(text: str) -> list[dict[str, Any]]:
    """Condições experimentais em legendas: 'Do = 2.771 mm', 'XO2=8%', '1 atm', '298 K'."""
    found: dict[str, dict[str, Any]] = {}
    for match in _KV.finditer(text):
        value = parse_number(match.group("val"))
        if value is None:
            continue
        symbol = match.group("key")
        found.setdefault(symbol, {"symbol": symbol, "value": value, "unit": normalize_unit(match.group("unit"))})
    for match in re.finditer(rf"(?<![\w.])({_NUM})\s*(atm|K)\b", text):
        value = parse_number(match.group(1))
        symbol = _COND_UNITS[match.group(2)]
        if value is not None and symbol not in found:
            found[symbol] = {"symbol": symbol, "value": value, "unit": match.group(2)}
    return list(found.values())


def infer_column_name(values: list[Any]) -> str:
    """Nome provisório para coluna sem cabeçalho, a partir do conteúdo."""
    texts = [str(v).strip() for v in values if v is not None and str(v).strip()]
    if not texts:
        return ""
    if sum(bool(re.match(r"^(https?://|doi:|10\.\d{4,})", t, re.I)) for t in texts) >= 0.6 * len(texts):
        return "Link / DOI"
    if sum(bool(re.match(r"^(fig(ure|ura)?\.?|table|tabela)\b", t, re.I)) for t in texts) >= 0.6 * len(texts):
        return "Figura / tabela"
    if sum(bool(re.fullmatch(r"[\w\-]+_[\w\-]+", t)) for t in texts) >= 0.6 * len(texts):
        return "Arquivo / identificador"
    return ""


# ----------------------------------------------------------------------------- classificação de grandezas

# Ordem importa: a primeira regra que casar vence. "name" casa o nome, "unit" casa a unidade.
DEFAULT_RULES: list[dict[str, Any]] = [
    {"kind": "strain_rate", "name": r"^a(_?(cfe|hfe|ext))?$|strain|estiramento", "unit": r"^(1/s|s\^?-1|s⁻¹)$"},
    {"kind": "temperature", "name": r"temperat|^t_?(max|min|avg|gas|flame|chama)$", "unit": r"^(k|°c|c)$"},
    {"kind": "pressure", "name": r"^p$|pressure|press[aã]o", "unit": r"^(atm|bar|pa|kpa|mpa|torr|psi)$"},
    {"kind": "equivalence_ratio", "name": r"^(ϕ|φ|Φ|phi)|equivalence|equival[eê]ncia", "unit": None},
    {"kind": "fraction", "name": r"^[XY][A-Za-z][A-Za-z0-9]*$|^[XY][0-9]$|fraction|fra[cç][aã]o",
     "unit": r"^(mol%|%|mass%|massa%)$", "case_sensitive": True},
    {"kind": "burning_rate", "name": r"^k(_?avg|_?b)?$|burning rate|taxa de queima", "unit": r"^mm(\^2|²)/s$"},
    {"kind": "time", "name": r"^(t|time|tempo)(\b|_)", "unit": r"^(s|ms|µs|min)$"},
    {"kind": "intensity", "name": r"signal|sinal|intensit|plif|chemi|radiance|luminesc", "unit": r"^(counts?|a\.?u\.?|arb\.?|cps)$"},
    {"kind": "diameter", "name": r"diameter|di[aâ]metro|^d(f|o|0|ext|_?ext)?$|\bdext\b", "unit": None},
    {"kind": "length", "name": r"distance|dist[aâ]ncia|location|position|posi[cç][aã]o|radius|raio|height|altura",
     "unit": r"^(m|cm|mm|µm|nm)$"},
    {"kind": "ratio", "name": r"fsr|ratio|raz[aã]o", "unit": None},
]

_RULES: list[dict[str, Any]] = list(DEFAULT_RULES)


def load_rules(path: Path) -> int:
    """Antepõe regras definidas pelo usuário (JSON) às regras padrão. Retorna quantas foram carregadas."""
    global _RULES
    _RULES = list(DEFAULT_RULES)
    if not path.is_file():
        return 0
    try:
        custom = json.loads(path.read_text(encoding="utf-8")).get("rules", [])
    except (OSError, json.JSONDecodeError):
        return 0
    valid = [r for r in custom if isinstance(r, dict) and r.get("kind") and (r.get("name") or r.get("unit"))]
    _RULES = valid + list(DEFAULT_RULES)
    return len(valid)


def classify_quantity(name: str, unit: str = "") -> str:
    """Tipo físico provável da coluna a partir de nome e unidade ('unknown' se nada casar)."""
    for rule in _RULES:
        flags = 0 if rule.get("case_sensitive") else re.I
        try:
            if rule.get("name") and re.search(rule["name"], name.strip(), flags):
                return rule["kind"]
            if rule.get("unit") and unit and re.search(rule["unit"], unit.strip(), re.I):
                return rule["kind"]
        except re.error:
            continue
    return "unknown"


QUANTITY_LABELS = {
    "time": "tempo", "length": "posição/distância", "diameter": "diâmetro", "temperature": "temperatura",
    "pressure": "pressão", "strain_rate": "taxa de estiramento", "fraction": "fração (molar/mássica)",
    "equivalence_ratio": "razão de equivalência", "intensity": "sinal/intensidade", "burning_rate": "taxa de queima",
    "ratio": "razão adimensional", "unknown": "não classificada",
}

