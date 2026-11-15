"""Comparações de cobertura e compatibilidade; nunca um ranking de risco."""
from __future__ import annotations

from typing import Any

from .frames import describe_columns


def compare_tables(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Require explicit method, conditions and measured provenance before pooling."""
    if not 2 <= len(entries) <= 3:
        return {"compatible": False, "reasons": ["Selecione duas ou três tabelas."], "profiles": []}
    profiles = []
    reasons = []
    signatures = []
    for entry in entries:
        table = entry["table"]
        scientific = table.get("scientific", {})
        kind = table.get("evidence_kind") or scientific.get("evidence_kind") or entry.get("evidence_kind", "unknown")
        method = table.get("methodology") or scientific.get("methodology")
        conditions = table.get("conditions") or scientific.get("conditions")
        columns = describe_columns(table.get("columns", []), table.get("rows", []))
        measured = kind in {"measurement", "measured", "medição"}
        if not measured:
            reasons.append(f"{entry['study_id']}: condições, catálogo ou natureza não validada; não equivale a medições.")
        if not method or not conditions:
            reasons.append(f"{entry['study_id']}: metodologia e condições comparáveis não documentadas.")
        signature = [(c["quantity"], c["unit"]) for c in columns if c["kind"] == "numeric"]
        if not signature or any(q == "unknown" or not unit for q, unit in signature):
            reasons.append(f"{entry['study_id']}: dimensões/unidades insuficientes para comparação quantitativa.")
        signatures.append((signature, method, conditions))
        profiles.append({
            "study_id": entry["study_id"],
            "table": table.get("name", ""),
            "evidence_kind": kind,
            "rows": len(table.get("rows", [])),
            "columns": columns,
            "source": entry.get("source", ""),
        })
    if any(s != signatures[0] for s in signatures[1:]):
        reasons.append("Grandezas, unidades, condições ou metodologias diferem entre as tabelas.")
    return {"compatible": not reasons, "reasons": list(dict.fromkeys(reasons)), "profiles": profiles}
