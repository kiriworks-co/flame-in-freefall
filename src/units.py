"""Conservative dimensional normalization; a unit never supplies a missing reference."""
from __future__ import annotations

import math
import re
from functools import lru_cache
from typing import Any

from .quantities import parse_number, parse_range


@lru_cache(maxsize=1)
def registry():
    import pint
    return pint.UnitRegistry(autoconvert_offset_to_baseunit=True)


def normalize_quantity(value: Any, unit: str, quantity: str | None = None,
                       reference: str | None = None) -> dict[str, Any]:
    """Return a typed record. Unspecified psi is deliberately not converted to psia.

    Gauge pressure remains psig: conversion to absolute requires a separately
    sourced reference pressure, handled by ``gauge_to_absolute``.
    """
    result = {"value": parse_number(value), "unit": unit or "", "quantity": quantity,
              "normalized_value": None, "normalized_unit": None,
              "reference": reference, "status": "unresolved"}
    number = result["value"]
    if number is None:
        uncertainty = re.fullmatch(r"\s*([-+\d.,eE]+)\s*(?:±|\+/-)\s*([\d.,eE]+)\s*", str(value))
        if uncertainty:
            center = parse_number(uncertainty.group(1))
            spread = parse_number(uncertainty.group(2))
            if center is not None and spread is not None:
                normalized = normalize_quantity(center, unit, quantity, reference)
                normalized.update(uncertainty=spread, uncertainty_unit=unit, status="uncertain")
                return normalized
        interval = parse_range(value)
        if interval:
            result.update(value_min=interval["min"], value_max=interval["max"], status="range")
        else:
            result["status"] = "missing" if value is None or str(value).strip().lower() in {"", "n/a", "na", "null", "none"} else "qualitative"
        return result
    raw = (unit or "").strip()
    canonical = {"°C": "degC", "C": "degC", "°F": "degF", "F": "degF",
                 "cm/sec": "cm/s", "m/sec": "m/s", "sec": "s", "µm": "um",
                 "mol%": "%", "mol.%": "%", "vol%": "%", "mole fraction": "dimensionless",
                 "% by vol": "%", "% by volume": "%", "ppm": "ppm"}.get(raw, raw)
    # Scientific spreadsheets commonly omit the caret in an explicit area unit.
    # This expands the written unit; it never supplies a unit absent from source.
    canonical = re.sub(r"\b(mm|cm|m)(?:2|²)\b", r"\1**2", canonical)
    lowered = canonical.casefold()
    if lowered in {"psia", "psi (absolute)", "psi absolute"}:
        result.update(normalized_value=number, normalized_unit="psia", reference="absolute", status="normalized", quantity="pressure")
        return result
    if lowered in {"psig", "psi (gauge)", "psi gauge"}:
        result.update(normalized_value=number, normalized_unit="psig", reference="gauge", status="normalized", quantity="pressure")
        return result
    if quantity == "pressure" and reference not in {"absolute", "gauge"}:
        result.update(reference="unspecified", status="reference_required")
        return result
    if lowered == "psi" and reference not in {"absolute", "gauge"}:
        result.update(quantity="pressure", reference="unspecified", status="reference_required")
        return result
    targets = {"pressure": ("psi", "psig" if reference == "gauge" else "psia"),
               "velocity": ("cm/s", "cm/s"), "temperature": ("kelvin", "K"),
               "diameter": ("mm", "mm"), "length": ("mm", "mm"),
               "area_rate": ("mm**2/second", "mm²/s"),
               "time": ("second", "s"), "rate": ("1/second", "1/s"),
               "oxygen": ("dimensionless", "fraction"), "mass_rate": ("mg/min", "mg/min")}
    if not canonical:
        return result
    target, label = targets.get(quantity or "", (canonical, raw))
    from pint.errors import PintError
    try:
        converted = registry().Quantity(number, canonical).to(target).magnitude
        if math.isfinite(float(converted)):
            result.update(normalized_value=float(converted), normalized_unit=label, status="normalized")
    except (PintError, ValueError, TypeError, LookupError):
        result["status"] = "unit_unrecognized"
    return result


def gauge_to_absolute(value_psig: float, reference_psia: float) -> dict[str, Any]:
    if not all(math.isfinite(v) for v in (value_psig, reference_psia)) or reference_psia < 0:
        raise ValueError("Invalid gauge/reference pressure")
    return {"value": value_psig + reference_psia, "unit": "psia", "evidence_kind": "derived",
            "formula": "P_absolute = P_gauge + P_reference", "reference_psia": reference_psia}


def partial_oxygen_pressure(fraction: float, pressure_psia: float) -> dict[str, Any]:
    if not (0 <= fraction <= 1) or pressure_psia < 0 or not math.isfinite(pressure_psia):
        raise ValueError("Oxygen fraction must be 0..1 and pressure must be absolute and nonnegative")
    return {"value": fraction * pressure_psia, "unit": "psia", "evidence_kind": "derived",
            "formula": "p_O2 = oxygen_fraction * absolute_pressure", "oxygen_fraction": fraction,
            "absolute_pressure_psia": pressure_psia}


def field_definition(header: str) -> tuple[str | None, str, str | None]:
    """Recognize field and explicit unit, without guessing units from values."""
    text = header.strip()
    lower = text.casefold()
    quantity = None
    if re.search(r"oxygen|\bo[₂2]\b|oxig[eê]nio|^o initial ambient composition", lower):
        quantity = "oxygen"
    elif "pressure" in lower or "pressão" in lower or "pressao" in lower or re.search(r"\bp\s*\((?:atm|bar|pa|kpa)\)", lower):
        quantity = "pressure"
    elif re.search(r"velocity|speed|velocidade|air flow", lower):
        quantity = "velocity"
    elif re.search(r"diameter|diâmetro|^(?:dflame|dext[_\w]*|df|do|d)\s*\(", lower):
        quantity = "diameter"
    elif re.search(r"temperature|temperatura|\btemp\b|\bt_?max\s*\(|\btad\s*\(|\bt\s*\([kc° ]+\)", lower):
        quantity = "temperature"
    elif re.search(r"\btime\b|tempo|duration|^t\s*\(", lower):
        quantity = "time"
    elif re.match(r"^(?:k|kb)\s*\(", lower):
        quantity = "area_rate"
    elif re.search(r"fuel|combust[ií]vel", lower):
        quantity = "fuel"
    elif "burning rate" in lower:
        quantity = "rate"
    elif "weight loss rate" in lower:
        quantity = "mass_rate"
    explicit = re.findall(r"[\[(]([^\])]+)[\])]", text)
    unit = text.rsplit(";", 1)[-1].strip() if ";" in text else explicit[-1].strip() if explicit else ""
    if "% by vol" in lower:
        unit = "%"
    if quantity == "oxygen" and "mole fraction" in lower:
        unit = "mole fraction"
    elif quantity == "oxygen" and "percent" in lower:
        unit = "%"
    # Units embedded in prose are accepted only from a short explicit vocabulary.
    if not unit:
        match = re.search(r"(?<![\w/])(psia|psig|psi|kPa|MPa|Pa|atm|torr|mmHg|cm/s|m/s|mm|cm|°C|°F|K|%)(?![\w/])", text)
        unit = match.group(1) if match else ""
    reference = "absolute" if re.search(r"absolute|psia", lower) else "gauge" if re.search(r"gauge|psig", lower) else None
    return quantity, unit, reference


def observations_from_tables(tables: list[dict[str, Any]], evidence_kind: str = "unclassified") -> list[dict[str, Any]]:
    observations = []
    for table_index, table in enumerate(tables):
        for column_index, header in enumerate(table.get("columns", [])):
            quantity, unit, reference = field_definition(str(header))
            role: dict[str, Any] = next((item for item in table.get("field_classification", [])
                         if item.get("column_index") == column_index), {})
            quantity = role.get("quantity", quantity)
            unit = role.get("unit", unit)
            reference = role.get("reference", reference)
            if quantity is None and not unit:
                continue
            for row_index, row in enumerate(table.get("rows", [])):
                raw = row[column_index] if column_index < len(row) else None
                source_rows = table.get("source_rows", [])
                row_number = source_rows[row_index] if row_index < len(source_rows) else row_index + 2
                kind = role.get("role", table.get("evidence_kind", evidence_kind))
                if kind == "mixed_conditions_and_reported_results":
                    kind = classify_field(str(header))
                normalized = normalize_quantity(raw, unit, quantity, reference)
                observation = {**normalized, "field": str(header), "raw_value": raw,
                                     "table_index": table_index, "row_number": row_number,
                                     "column_index": column_index, "evidence_kind": kind,
                                     "source_column_index": role.get("source_column_index", column_index)}
                if role.get("warning"):
                    observation.update(warning=role["warning"], normalized_value=None,
                                       normalized_unit=None, status="source_unit_ambiguous")
                observations.append(observation)
    return observations


def classify_field(header: str) -> str:
    """Reported output is not equivalent to independent measurement validation."""
    lower = header.casefold()
    if re.search(r"extinction diameter|burning rate|burn time|test end|calibrated|final (o2|co2|co)\b|weight loss rate", lower):
        return "reported_result"
    if re.search(r"sample|identifier|test #|test number|^fuel$|material", lower):
        return "sample"
    return "condition"
