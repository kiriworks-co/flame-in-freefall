"""Global NASA catalog, evidence retrieval, assistant and conservative comparison."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from . import storage, views
from .comparison import compare_tables
from .extractors import render_pdf_page
from .retrieval import safe_source_url

ROOT = Path(__file__).resolve().parents[1]
SECTIONS = ["Visão geral", "Investigações NASA", "Busca e assistente", "Comparar estudos", "Revisão visual",
            "Ingestão e fontes", "Arquivos do experimento"]
EVIDENCE_LABELS = {
    "condition": "Condição de ensaio", "sample": "Amostra",
    "measurement": "Resultado reportado", "calculation": "Cálculo derivado",
    "inference": "Inferência", "context": "Contexto documental",
    "document_context": "Contexto documental", "unclassified": "Não classificado",
    "mixed_conditions_and_reported_results": "Condições e resultados reportados",
    "engineering_or_publication": "Documento de engenharia ou publicação",
    "reported_result": "Resultado reportado (não validação independente)",
    "derived": "Cálculo derivado",
}


def _json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _study(experiment: dict) -> str:
    return str(experiment.get("psi_id") or experiment.get("study_id") or experiment.get("investigation_id") or experiment["id"])


def _safe_url(url: Any) -> str | None:
    return safe_source_url(url) or None


def _doi_url(value: Any) -> str | None:
    import re
    doi = str(value or "").removeprefix("https://doi.org/")
    return f"https://doi.org/{doi}" if re.fullmatch(r"10\.\d{4,9}/[^\s<>]+", doi) else None


def _document_notices(study_id: str, document: dict) -> list[str]:
    provenance = document.get("provenance") or document
    notices = []
    if provenance.get("classification_note"):
        notices.append(str(provenance["classification_note"]))
    for field in provenance.get("field_classification", []):
        if field.get("warning"):
            notices.append(f"{field.get('header', 'Campo')}: {field['warning']}")
    filename = document.get("name") or document.get("filename", "")
    if study_id == "PSI-69" and "FLEX Engineering Requirements Document" in filename:
        notices.append("O catálogo NASA associa este PDF a PSI-69, mas a capa identifica FLEX-2. "
                       "A associação de catálogo não demonstra que os requisitos se aplicam ao FLEX original.")
    return list(dict.fromkeys(notices))


@st.cache_resource(show_spinner=False)
def _retrieval_index(model_path: str):
    """Reuse local model weights between Streamlit reruns, without caching results."""
    from .retrieval import RetrievalIndex
    return RetrievalIndex()


def catalog(experiments: list[dict]) -> list[dict]:
    entries = _json(ROOT / "resources/manifests/priority_investigations.json", {}).get("investigations", [])
    by_id = {_study(exp): exp for exp in experiments}
    result = []
    for entry in entries:
        exp = by_id.get(entry["id"])
        downloaded = _json(ROOT / "data/psi_downloads" / entry["id"] / "source_manifest.json", {})
        result.append({**entry, "experiment": exp, "download_manifest": downloaded,
                       "documents": exp.get("documents", []) if exp else [],
                       "document_count": len(exp.get("documents", [])) if exp else 0})
    return result


def _open_experiment(identifier: str) -> None:
    st.session_state["active_experiment_id"] = identifier
    st.session_state["workspace_section"] = "Arquivos do experimento"


def _source_link(label: str, url: Any) -> None:
    safe = _safe_url(url)
    if safe:
        st.link_button(label, safe)


def show_overview(experiments: list[dict]) -> None:
    st.title("Combustão em microgravidade")
    st.write("Investigações NASA PSI, documentos originais e evidências rastreáveis para explorar perguntas científicas.")
    records = catalog(experiments)
    documents = [doc for exp in experiments for doc in exp.get("documents", [])]
    cols = st.columns(3)
    cols[0].metric("Investigações PSI importadas", sum(bool(row["experiment"]) for row in records))
    cols[1].metric("Originais preservados", len(documents))
    cols[2].metric("Tabelas extraídas", sum(doc.get("table_count", 0) for doc in documents))
    failures = sum(doc.get("status") == "erro" for doc in documents)
    partial = sum(doc.get("status") == "parcial" for doc in documents)
    st.caption(f"Extração: {len(documents) - failures - partial} processados · "
               f"{partial} parciais · {failures} com erro. Consulte Ingestão e fontes para detalhes.")
    st.warning("Tabelas experimentais podem descrever condições de ensaio. Elas não demonstram, por si, propagação de chama, eficácia de supressão ou risco de um material.")
    st.header("Cobertura por pergunta científica")
    categories = [("Prevenção", "BASS · BASS-II · Saffire"), ("Detecção", "SAME · SAME-R"),
                  ("Supressão", "FLEX · FLEX-2")]
    for category, names in categories:
        covered = [r for r in records if category.casefold() in r.get("category", "").casefold()]
        st.write(f"**{category}** — {names}")
        st.caption(f"{sum(bool(r['experiment']) for r in covered)} de {len(covered)} investigações prioritárias importadas")
    st.header("Comece pelos originais")
    st.write("Consulte Investigações NASA para abrir um estudo; use Busca e assistente para localizar trechos, páginas e linhas. Em Ingestão e fontes, importe os downloads e acompanhe o processamento.")
    if not documents:
        st.info("Ainda não há documentos importados. Os coletores e a ingestão funcionam separadamente; nenhum dado é criado para preencher o dashboard.")
    st.caption("Aplicativo local de pesquisa. Não é uma certificação de segurança de incêndio.")


def show_catalog(experiments: list[dict]) -> None:
    st.title("Investigações NASA")
    records = catalog(experiments)
    query = st.text_input("Pesquisar investigação", placeholder="Ex.: FLEX, BASS, SAME")
    category = st.selectbox("Área científica", ["Todas", "Prevenção", "Detecção", "Supressão"])
    st.header("Investigações disponíveis")
    shown = 0
    for row in records:
        if query.casefold() not in f"{row['id']} {row['name']} {row.get('category', '')}".casefold():
            continue
        if category != "Todas" and category.casefold() not in row.get("category", "").casefold():
            continue
        shown += 1
        exp = row["experiment"]
        with st.container(border=True):
            st.subheader(f"{row['id']} · {row['name']}")
            st.caption(row.get("category", ""))
            if exp and exp.get("description"):
                st.write(exp["description"])
            status = "Importado" if exp else "Baixado, aguardando ingestão" if row["download_manifest"].get("downloaded_csvs") else "Aguardando coleta"
            st.write(f"{status} · {row['document_count']} documento(s) no aplicativo")
            _source_link("Registro NASA PSI", row.get("nasa_record_url"))
            provenance = row["download_manifest"]
            doi = provenance.get("doi") or (exp or {}).get("doi")
            if _doi_url(doi):
                _source_link("DOI confirmado na fonte", _doi_url(doi))
            elif row.get("doi_candidate"):
                st.caption(f"DOI do catálogo (a confirmar): {row['doi_candidate']}")
            if exp:
                st.caption("Extração: " + ", ".join(
                    f"{doc.get('name', 'Documento')}: {doc.get('status', 'não processado')}"
                    for doc in exp.get("documents", [])))
                st.button("Abrir documentos e tabelas", key=f"nasa-open-{row['id']}",
                          on_click=_open_experiment, args=(exp["id"],))
            elif provenance.get("error"):
                st.caption(str(provenance["error"]))
    if not shown:
        st.info("Nenhuma investigação corresponde aos filtros. Altere o termo ou a área científica.")


def _original_for(evidence: dict, experiments: list[dict]) -> tuple[dict, dict] | None:
    digest = evidence.get("sha256") or evidence.get("document_sha256")
    study = evidence.get("study_id")
    for exp in experiments:
        if study and _study(exp) != study and exp["id"] != study:
            continue
        for doc in exp.get("documents", []):
            if doc.get("sha256") == digest:
                return exp, doc
    return None


def show_evidence(evidence: list[dict], experiments: list[dict]) -> None:
    for position, item in enumerate(evidence, 1):
        label = f"{position}. {item.get('study_id', '')} · {item.get('document_name', 'Documento')} · {item.get('location', '')}"
        with st.expander(label, expanded=position == 1):
            kind = item.get("evidence_kind", "unclassified")
            st.caption(f"Natureza: {EVIDENCE_LABELS.get(kind, kind)} · referência {item.get('id', '')}")
            st.text(item.get("text", ""))
            _source_link("Fonte permanente", item.get("source_url"))
            _source_link("DOI", _doi_url(item.get("doi")))
            st.code(item.get("sha256", ""), language=None)
            original = _original_for(item, experiments)
            if original:
                exp, doc = original
                for notice in _document_notices(_study(exp), doc):
                    st.warning(notice)
                try:
                    content = storage.read_original(exp, doc)
                except (OSError, ValueError) as error:
                    st.error(f"Original indisponível: {error}. Reimporte a cópia verificada em Ingestão e fontes.")
                    continue
                st.download_button("Baixar original citado", content, file_name=doc["name"],
                                   key=f"evidence-download-{position}-{item['id']}")
                if doc.get("extension") == ".pdf" and item.get("page"):
                    if st.button("Visualizar página citada", key=f"evidence-page-{position}-{item['id']}"):
                        try:
                            image = render_pdf_page(content, int(item["page"]))
                            st.image(image, caption=f"{doc['name']} · página {item['page']}")
                        except (OSError, ValueError, RuntimeError) as error:
                            st.error(f"Não foi possível renderizar a página: {error}")


def show_search(experiments: list[dict]) -> None:
    from .assistant import answer
    st.title("Busca e assistente científico")
    st.caption("PT / EN · Evidências locais disponíveis sem LLM · Filtros numéricos na mesma linha de origem")
    index = _retrieval_index(os.getenv("RAG_EMBEDDING_MODEL", "").strip())
    st.caption("Busca: FTS5 + embeddings semânticos locais" if index.model is not None
               else "Busca: FTS5 + vetores lexicais PT/EN. O modo lexical não usa embeddings semânticos.")
    st.caption(f"Modo do índice: {index.mode}")
    studies = sorted({_study(e) for e in experiments})
    selected = st.multiselect("Investigações consultadas (vazio = todas)", studies)
    with st.form("scientific-query"):
        question = st.text_area("Pergunta / Question", value="What are the experimental conditions for FLEX?",
                                help="Pergunte por condições, métodos ou documentos. Não use a ferramenta como laudo de segurança.")
        with st.expander("Filtros de valores documentados"):
            oxygen = st.checkbox("Filtrar fração de O₂")
            o2min = st.number_input("O₂ mínimo (fração, 0 a 1)", min_value=0.0, max_value=1.0, value=0.18, step=0.01)
            o2max = st.number_input("O₂ máximo (fração, 0 a 1)", min_value=0.0, max_value=1.0, value=0.25, step=0.01)
            pressure = st.checkbox("Filtrar pressão absoluta")
            pmin = st.number_input("Pressão mínima (psia)", min_value=0.0, value=0.0)
            pmax = st.number_input("Pressão máxima (psia)", min_value=0.0, value=30.0)
            velocity = st.checkbox("Filtrar velocidade")
            vmin = st.number_input("Velocidade mínima (cm/s)", value=0.0)
            vmax = st.number_input("Velocidade máxima (cm/s)", value=100.0)
            fuel = st.text_input("Combustível documentado", placeholder="Ex.: heptane")
            st.caption("Unidades e referência precisam ser explícitas na fonte. Pressão sem referência absoluta não será presumida psia.")
        language = st.selectbox("Idioma da resposta", ["pt", "en"])
        use_llm = st.checkbox("Usar LLM configurado no ambiente", value=False,
                               help="Envia somente pergunta e evidências selecionadas ao provedor configurado.")
        submitted = st.form_submit_button("Pesquisar evidências", type="primary")
    if submitted:
        if not question.strip():
            st.warning("Digite uma pergunta.")
            return
        if (oxygen and o2min > o2max) or (pressure and pmin > pmax) or (velocity and vmin > vmax):
            st.error("O limite mínimo deve ser menor ou igual ao máximo.")
            return
        filters = []
        if oxygen:
            filters.append({"field": "oxygen_fraction", "unit": "fraction", "min": o2min, "max": o2max})
        if pressure:
            filters.append({"field": "pressure", "unit": "psia", "reference": "absolute", "min": pmin, "max": pmax})
        if velocity:
            filters.append({"field": "velocity", "unit": "cm/s", "min": vmin, "max": vmax})
        if fuel.strip():
            filters.append({"field": "fuel", "value": fuel.strip()})
        with st.spinner("Recuperando evidências…"):
            result = answer(question, index, study_ids=selected or None, numeric_filters=filters or None,
                            language=language, use_llm=use_llm)
        st.session_state["scientific_answer"] = result
        st.session_state["scientific_query_context"] = {
            "question": question, "studies": ", ".join(selected) if selected else "Todas as investigações",
            "filters": filters,
        }
    result = st.session_state.get("scientific_answer")
    if result:
        st.header("Resposta e evidências")
        context = st.session_state.get("scientific_query_context", {})
        if context:
            st.caption(f"Última consulta · {context['studies']}")
            st.text(context["question"])
        # The assistant constructs this text and escapes source-authored Markdown.
        # Raw evidence remains inert st.text below; HTML is never enabled.
        st.markdown(result.get("text", ""), unsafe_allow_html=False)
        st.caption(f"Modo: {result.get('mode', 'evidências')}")
        for warning in result.get("warnings", []):
            st.warning(str(warning))
        show_evidence(result.get("evidence", []), experiments)


def show_comparison(experiments: list[dict]) -> None:
    from .relevance import rank_investigations

    st.title("Comparar estudos")
    st.write("Compare cobertura e proveniência de dois ou três estudos. Resultados físicos só são comparáveis com grandezas, métodos e condições compatíveis.")
    mapping = {_study(exp): exp for exp in experiments}
    selection = st.multiselect("Selecione dois ou três estudos", list(mapping), max_selections=3)
    if len(selection) >= 2:
        st.header("Tabelas selecionadas")
        entries = []
        for study in selection:
            exp = mapping[study]
            available = views.collect_entries(exp)
            st.subheader(study)
            if not available:
                st.info("Este estudo não tem tabela extraída.")
                continue
            chosen = st.selectbox("Tabela para comparar", range(len(available)),
                                  format_func=lambda n, a=available: a[n]["table"]["name"], key=f"compare-table-{study}")
            entry = available[chosen]
            entries.append({**entry, "study_id": study,
                            "evidence_kind": entry["document"].get("evidence_kind", "unknown"),
                            "source": entry["document"].get("source_url", "")})
        comparison = compare_tables(entries)
        if comparison["compatible"]:
            st.success("Dimensões, metodologia e condições declaradas coincidem. Inspecione os originais antes de interpretar diferenças.")
        else:
            st.warning("Comparação quantitativa conjunta não validada.")
            for reason in comparison["reasons"]:
                st.write(f"• {reason}")
        for profile in comparison["profiles"]:
            st.write(f"**{profile['study_id']}** · {profile['table']} · {profile['rows']} linhas")
            st.dataframe(pd.DataFrame(profile["columns"]), hide_index=True)
    else:
        st.info("Selecione ao menos dois estudos para inspecionar suas tabelas lado a lado.")
    st.divider()
    st.header("Relevância para uma pergunta de segurança")
    st.caption("Ordenação de investigações para orientar leitura. O score não mede risco, inflamabilidade nem eficácia.")
    application = st.selectbox("Aplicação", ["habitat", "detection", "suppression"])
    question = st.text_input("Pergunta para priorizar leitura", value="microgravity combustion")
    records = [{**r, "description": (r["experiment"] or {}).get("description", "")} for r in catalog(experiments)]
    ranked = rank_investigations(records, query=question, application=application)
    st.dataframe(pd.DataFrame([{"Estudo": r.get("id") or r.get("study_id"), "Nome": r.get("name"),
                               "Score": r.get("score"), "Fundamentos": "; ".join(r.get("reasons", []))}
                              for r in ranked]), hide_index=True)


@st.fragment(run_every=2)
def _job_monitor(job_id: str) -> None:
    from .pipeline import job_status
    job = job_status(job_id)
    if not job:
        st.info("Job não encontrado. Consulte os registros de ingestão.")
        return
    st.write(f"Processamento: {job.get('status', 'desconhecido')}")
    st.progress(min(1.0, max(0.0, float(job.get("progress") or 0))))
    if job.get("error"):
        st.error(str(job["error"]))
    result = job.get("result") or job.get("result_json")
    if result:
        try:
            st.json(json.loads(result) if isinstance(result, str) else result)
        except ValueError:
            st.text(str(result))
    if job.get("status") in {"completed", "complete", "succeeded", "partial", "failed", "interrupted"}:
        st.caption("Processamento encerrado. Atualize o catálogo para ler os novos documentos.")


def show_ingestion(experiments: list[dict]) -> None:
    from .pipeline import enqueue_ingestion
    from .scientific_store import ScientificStore

    st.title("Ingestão e fontes")
    st.write("Os downloads são explícitos, limitados e separados da interface. A importação roda em um worker local e preserva os originais.")
    with st.expander("Como obter ou atualizar os arquivos NASA"):
        st.code("python scripts/fetch_nasa_resources.py --guide --psi-manual\n"
                "python scripts/fetch_psi_tables.py --ids PSI-25 PSI-26 PSI-68 PSI-69 PSI-98 PSI-99 PSI-100 PSI-101 PSI-102\n"
                "python scripts/fetch_psi_tables.py --ids PSI-69 PSI-25 PSI-102 --pdfs\n"
                "python scripts/ingest_nasa.py", language="powershell")
    if st.button("Importar downloads e atualizar índice", type="primary"):
        st.session_state["ingestion_job_id"] = enqueue_ingestion()
    if st.session_state.get("ingestion_job_id"):
        _job_monitor(st.session_state["ingestion_job_id"])
    if st.button("Atualizar catálogo"):
        views.clear_cache()
        st.rerun()
    jobs = ScientificStore().jobs()
    if jobs:
        st.header("Histórico de processamento")
        st.dataframe(pd.DataFrame(jobs), hide_index=True)
    st.header("Documentos e proveniência")
    for exp in experiments:
        for doc in exp.get("documents", []):
            with st.expander(f"{_study(exp)} · {doc['name']}"):
                st.code(doc.get("sha256", ""), language=None)
                st.caption(f"{doc.get('size_bytes', 0)} bytes · {doc.get('status', '')}")
                for notice in _document_notices(_study(exp), doc):
                    st.warning(notice)
                st.json(doc.get("provenance") or doc.get("source") or {})
                try:
                    content = storage.read_original(exp, doc)
                    st.download_button("Baixar bytes originais", content, doc["name"],
                                       key=f"source-download-{exp['id']}-{doc['id']}")
                except (OSError, ValueError) as error:
                    st.error(f"Original indisponível: {error}. Execute novamente a ingestão da cópia verificada.")
    st.caption("Condições de uso, URLs permanentes, hashes e lacunas: docs/DATA_PROVENANCE.md. Nenhuma URL assinada temporária é uma citação permanente.")


def show_visual_review(experiments: list[dict]) -> None:
    from dataclasses import asdict

    from .visual_review import (
        configuration,
        provider_label,
        record_human_review,
        render_verified_page,
        review_pdf_page,
        save_review,
    )

    st.title("Revisão visual de páginas")
    st.write("Inspecione páginas complexas e gráficos no PDF original. Uma interpretação por IA, quando solicitada, "
             "é apenas um candidato qualitativo para revisão humana.")
    st.warning("A revisão visual não lê valores exatos de gráficos, não cria medições e não entra no índice de evidências científicas.")
    pdfs = [(exp, doc) for exp in experiments for doc in exp.get("documents", []) if doc.get("extension") == ".pdf"]
    if not pdfs:
        st.info("Não há PDF importado. Importe os documentos originais em Ingestão e fontes.")
        return
    selected = st.selectbox("PDF original", range(len(pdfs)),
                            format_func=lambda n: f"{_study(pdfs[n][0])} · {pdfs[n][1]['name']}",
                            key="visual-document")
    experiment, document = pdfs[selected]
    page_count = max(1, min(500, int(document.get("page_count") or 1)))
    page = int(st.number_input("Página original", min_value=1, max_value=page_count, value=1,
                               step=1, key=f"visual-page-{document['sha256']}"))
    digest = document["sha256"]
    st.caption(f"Documento SHA-256 {digest} · página {page} de {document.get('page_count', '?')}")
    for notice in _document_notices(_study(experiment), document):
        st.warning(notice)
    if st.button("Visualizar página localmente"):
        try:
            image = render_verified_page(storage.read_original(experiment, document), page, digest)
            st.session_state["visual_preview"] = (digest, page, image)
        except (OSError, ValueError, RuntimeError) as error:
            st.error(f"Prévia indisponível: {error}")
    preview = st.session_state.get("visual_preview")
    if preview and preview[:2] == (digest, page):
        st.image(preview[2], caption=f"{document['name']} · página {page}")
    st.header("Interpretação qualitativa opcional")
    st.caption(provider_label())
    try:
        configured = configuration() is not None
    except ValueError:
        configured = False
    if not configured:
        st.info("VLM não configurado. A visualização local funciona sem IA. "
                "Para habilitar um provedor, configure VLM_BASE_URL, VLM_MODEL e VLM_API_KEY no ambiente.")
    consent = st.checkbox("Enviar somente a imagem desta página ao provedor configurado",
                           value=False, disabled=not configured,
                           help="A imagem sai deste computador. O resultado não substitui os dados do documento.")
    if st.button("Solicitar candidato de revisão visual", disabled=not configured or not consent):
        with st.spinner("Solicitando interpretação qualitativa…"):
            try:
                content = storage.read_original(experiment, document)
                review = review_pdf_page(content, page, digest, consent=consent)
                save_review(review, _study(experiment))
                st.session_state["visual_review_result"] = review
            except (OSError, ValueError, RuntimeError) as error:
                st.error(f"Revisão não concluída: {type(error).__name__}. Nenhuma observação científica foi criada.")
    review = st.session_state.get("visual_review_result")
    if review and review.document_sha256 == digest and review.page == page:
        st.header("Candidato para revisão humana")
        for warning in review.warnings:
            st.warning(warning)
        st.caption(f"Estado: {review.status} · natureza: inferência · revisão humana necessária")
        if review.status == "candidate":
            st.text(review.description)
            st.text(review.inference)
            for index, region in enumerate(review.regions, 1):
                with st.expander(f"Região {index} · {region.kind}"):
                    st.caption("Coordenadas normalizadas de localização; não são valores físicos medidos.")
                    st.text(str(region.bbox))
                    st.text(region.description)
                    st.caption("Texto candidato não verificado")
                    st.text(region.text_candidate)
            st.download_button("Baixar candidato de revisão (JSON)",
                               json.dumps(asdict(review), ensure_ascii=False, indent=2).encode("utf-8"),
                               f"visual-review-{digest[:12]}-p{page}.json", "application/json")
            note = st.text_area("Comentário da revisão humana", max_chars=2000,
                                help="Registre o que conferiu no original. O comentário não promove inferências a medições.")
            if st.button("Registrar comentário de revisão"):
                try:
                    reviewed = record_human_review(review, note)
                    save_review(reviewed, _study(experiment))
                    st.session_state["visual_review_result"] = reviewed
                    st.success("Comentário registrado. O resultado permanece uma inferência separada dos dados primários.")
                except ValueError as error:
                    st.error(str(error))
            if review.human_review_note:
                st.caption(f"Comentário humano registrado em {review.human_reviewed_utc}")
                st.text(review.human_review_note)


def show_section(section: str, experiments: list[dict]) -> None:
    # Static CSS only. Do not interpolate external document strings into HTML.
    st.html("""<style>
        [data-testid="stMainBlockContainer"] { max-width: 90rem; }
        h1, h2, h3 { text-wrap: balance; }
        [data-testid="stMetricValue"], table { font-variant-numeric: tabular-nums; }
        [data-testid="stText"], [data-testid="stCaptionContainer"], p { overflow-wrap: anywhere; }
        button, [data-testid="stLinkButton"] a { min-height: 2.75rem; }
        :is(button, a, input, textarea):focus-visible { outline: 3px solid #A44426 !important; outline-offset: 3px; }
        @media (max-width: 40rem) {
            [data-testid="stMainBlockContainer"] { padding-inline: 1rem; }
        }
    </style>""")
    handlers = {"Visão geral": show_overview, "Investigações NASA": show_catalog,
                "Busca e assistente": show_search, "Comparar estudos": show_comparison,
                "Revisão visual": show_visual_review, "Ingestão e fontes": show_ingestion}
    handlers[section](experiments)
