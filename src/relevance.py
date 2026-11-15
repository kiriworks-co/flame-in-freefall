"""Explainable investigation relevance, never a material/fire-risk estimate."""
from __future__ import annotations

from .search import _tokens, normalize

APPLICATION_TERMS = {
    "habitat": {"bass", "saffire", "solid", "spread", "flammability", "prevention", "prevencao", "material"},
    "detection": {"same", "smoke", "detector", "detection", "fumaca", "deteccao", "aerosol"},
    "suppression": {"flex", "extinction", "suppression", "droplet", "extincao", "supressao", "gota"},
}


def rank_investigations(investigations: list[dict], query: str = "", application: str = "habitat") -> list[dict]:
    """0..100 = application match (50), query terms (30), local evidence (20).

    These weights describe discoverability and coverage, not experimental
    quality, causality, fire risk or suppression efficacy.
    """
    if application not in APPLICATION_TERMS:
        raise ValueError("application must be habitat, detection or suppression")
    query_terms = set(_tokens(query))
    ranked = []
    for item in investigations:
        text = normalize(" ".join(str(item.get(k) or "") for k in ("name", "title", "description", "category")))
        application_hits = sorted(t for t in APPLICATION_TERMS[application] if t in text)
        query_hits = sorted(t for t in query_terms if t in text)
        documents = item.get("documents", [])
        count = len(documents) if documents else item.get("files_downloaded", 0)
        evidence = min(20, int(count or 0) * 5)
        query_score = 30 * len(query_hits) / len(query_terms) if query_terms else 0
        score = (50 if application_hits else 0) + query_score + evidence
        reasons = [f"Aplicação: {', '.join(application_hits)} (+50)" if application_hits else "Sem termo específico da aplicação (+0)",
                   f"Consulta: {len(query_hits)}/{len(query_terms)} termos (+{query_score:g})",
                   f"Arquivos locais: {count or 0} (+{evidence})"]
        ranked.append({**item, "score": round(score, 2), "reasons": reasons, "application": application})
    return sorted(ranked, key=lambda item: (-item["score"], str(item.get("id", item.get("psi_id", "")))))
