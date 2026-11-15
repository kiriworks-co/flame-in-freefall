"""NASA Space Apps Challenge 2026 Synthesis Engine: SUMMARIZE · RANK · INTERPRET."""
from __future__ import annotations

from typing import Any

from .i18n import (
    evidence_label,
    investigation_profile,
    t,
    translate_relevance_reason,
)
from .relevance import rank_investigations


def _study_id(experiment: dict[str, Any]) -> str:
    return str(
        experiment.get("psi_id")
        or experiment.get("study_id")
        or experiment.get("id")
        or "NASA-PSI"
    )


def _known_caveats(study_id: str, documents: list[dict[str, Any]], lang: str) -> list[str]:
    is_pt = str(lang).lower().startswith("pt")
    caveats: list[str] = []
    profile_caveat = investigation_profile(study_id, lang).get("caveat")
    if profile_caveat:
        caveats.append(profile_caveat)

    for doc in documents:
        name = str(doc.get("name") or "")
        if study_id == "PSI-69" and "FLEX Engineering Requirements Document" in name:
            caveats.append(
                "O catálogo NASA associa este PDF a PSI-69, mas a capa identifica FLEX-2."
                if is_pt
                else "NASA catalog groups a FLEX-2 requirements PDF under PSI-69 (explicitly flagged)."
            )
        if study_id == "PSI-102" and "ignitor" in name.lower():
            caveats.append(
                "Desenho técnico de 1 página sem camada de texto nativa (OCR requer Tesseract)."
                if is_pt
                else "1-page technical drawing lacks an embedded text layer (full OCR requires Tesseract)."
            )
        if str(doc.get("status") or "") == "parcial":
            caveats.append(
                f"Extração parcial registrada em `{name}`; original preservado integralmente."
                if is_pt
                else f"Partial text/table extraction recorded for `{name}`; original bytes remain preserved."
            )
    return list(dict.fromkeys(caveats))


def build_study_summary(experiment: dict[str, Any], language: str = "en") -> dict[str, Any]:
    """Build a structured SUMMARIZE record anchored strictly to archived NASA study files."""
    is_pt = str(language).lower().startswith("pt")
    sid = _study_id(experiment)
    profile = investigation_profile(sid, language)
    docs = list(experiment.get("documents") or [])
    pdf_count = sum(1 for d in docs if str(d.get("extension") or "").lower() == ".pdf")
    csv_count = sum(1 for d in docs if str(d.get("extension") or "").lower() in {".csv", ".tsv", ".xls", ".xlsx"})
    total_tables = sum(int(d.get("table_count") or 0) for d in docs)

    evidence_roles = sorted({
        evidence_label(str(d.get("evidence_kind") or "document_context"), language)
        for d in docs
    })
    citations = [
        {
            "document": str(d.get("name") or ""),
            "sha256_prefix": str(d.get("sha256") or "")[:16],
            "source_url": str(d.get("source_url") or ""),
            "status": str(d.get("status") or "—"),
        }
        for d in docs[:4]
    ]

    return {
        "study_id": sid,
        "title": str(experiment.get("name") or sid),
        "pillar": profile.get("pillar") or ("Contexto" if is_pt else "Context"),
        "objective": profile.get("objective") or str(experiment.get("description") or ""),
        "archive_coverage": (
            f"{len(docs)} arquivo(s) preservado(s) ({csv_count} planilha(s)/CSV, {pdf_count} PDF(s)) · {total_tables} tabela(s) extraída(s)"
            if is_pt
            else f"{len(docs)} preserved NASA file(s) ({csv_count} spreadsheet/CSV, {pdf_count} PDF) · {total_tables} extracted table(s)"
        ),
        "evidence_roles": ", ".join(evidence_roles) if evidence_roles else t("nav.sources", language),
        "citations": citations,
        "caveats": _known_caveats(sid, docs, language),
    }


def build_priority_ranking(
    records: list[dict[str, Any]],
    *,
    application: str = "habitat",
    query: str = "microgravity combustion",
    language: str = "en",
) -> list[dict[str, Any]]:
    """Produce explainable 0–100 RANK rows clarifying research priority, never fire risk."""
    ranked = rank_investigations(records, query=query, application=application)
    out: list[dict[str, Any]] = []
    for pos, row in enumerate(ranked, start=1):
        sid = str(row.get("id") or row.get("study_id") or "")
        profile = investigation_profile(sid, language)
        reasons = [translate_relevance_reason(str(r), language) for r in row.get("reasons", [])]
        out.append({
            "rank": pos,
            "study_id": sid,
            "name": str(row.get("name") or sid),
            "pillar": profile.get("pillar") or str(row.get("category") or ""),
            "score": float(row.get("score") or 0.0),
            "reasons": reasons,
            "reasons_text": " · ".join(reasons),
            "application": application,
        })
    return out


def build_spacecraft_interpretation(experiment: dict[str, Any], language: str = "en") -> dict[str, Any]:
    """Build an INTERPRET card separating observations, implications, and boundaries."""
    is_pt = str(language).lower().startswith("pt")
    sid = _study_id(experiment)
    profile = investigation_profile(sid, language)
    docs = list(experiment.get("documents") or [])
    pillar = profile.get("pillar") or ("Contexto" if is_pt else "Context")
    relevance = profile.get("relevance") or ""

    has_conditions = any("condition" in str(d.get("evidence_kind") or "").lower() for d in docs)
    has_results = any(
        any(tok in str(d.get("evidence_kind") or "").lower() for tok in ("measurement", "result", "mixed"))
        for d in docs
    )
    if has_conditions and not has_results:
        obs_scope = (
            "As tabelas indexadas registram principalmente configurações de câmara, combustíveis e parâmetros de ensaio (`Test condition`)."
            if is_pt
            else "Indexed tables primarily document chamber setups, fuel samples, and run parameters (`Test condition`)."
        )
    elif has_results:
        obs_scope = (
            "O estudo contém resultados reportados combinados com condições experimentais e relatórios NASA verificados."
            if is_pt
            else "This study combines reported experimental outcomes with run conditions and verified NASA reports."
        )
    else:
        obs_scope = (
            "O acervo carregado oferece documentação técnica e contexto científico da NASA sem medições primárias tabeladas."
            if is_pt
            else "Archived records provide official NASA technical documentation and context without raw tabular measurements."
        )

    implication = relevance or (
        "Oferece referência científica verificada para orientar hipóteses de engenharia espacial."
        if is_pt
        else "Provides verified spaceflight evidence to inform engineering hypotheses rather than standalone qualification."
    )
    boundary = (
        "Não constitui certificação de segurança ou inflamabilidade de voo; consulte arquivos originais, página/linha e unidades antes de modelar ou extrapolar."
        if is_pt
        else "Never treat these datasets as flight flammability certification; verify original PDFs, units, and test geometry before extrapolating."
    )
    return {
        "study_id": sid,
        "pillar": pillar,
        "observation_scope": obs_scope,
        "engineering_implication": implication,
        "scientific_boundary": boundary,
        "caveats": _known_caveats(sid, docs, language),
    }
