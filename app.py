"""Dashboard local para organizar, indexar e explorar arquivos PSI."""

from __future__ import annotations

from datetime import datetime
from io import BytesIO
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src import scientific_ui, views
from src.extractors import SCHEMA_VERSION, SUPPORTED_EXTENSIONS
from src.local_jobs import enqueue_refresh_experiment, enqueue_uploads
from src.pipeline import job_status
from src.quantities import load_rules
from src.storage import (
    CONFIG_DIR,
    DATA_DIR,
    create_experiment,
    list_experiments,
    load_extraction,
    read_original,
    update_experiment,
    verify_original,
)

st.set_page_config(
    page_title="PSI Flame Microgravity",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)


load_dotenv(Path(__file__).resolve().parent / ".env", override=False)
load_rules(CONFIG_DIR / "quantity_rules.json")


def _date_label(value: str | None) -> str:
    if not value:
        return "—"
    try:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone(ZoneInfo("America/Sao_Paulo"))
        return parsed.strftime("%d/%m/%Y %H:%M")
    except (ValueError, TypeError):
        return str(value)


def _bytes_label(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{value:.1f} GB"


def _format_experiment(experiment_id: str, experiment_map: dict[str, dict]) -> str:
    return experiment_map[experiment_id]["name"] if experiment_id in experiment_map else "Selecionar experimento"


def _load_one(experiment: dict, document: dict) -> dict:
    return load_extraction(experiment, document)


def _activate_experiment(experiment_id: str) -> None:
    st.session_state["active_experiment_id"] = experiment_id


def _show_home(experiments: list[dict]) -> None:
    st.title("Experimentos")
    st.write(
        "Organize os arquivos dos experimentos de combustão em microgravidade. "
        "Cada experimento mantém seus documentos originais e extrações em uma pasta independente."
    )
    if not experiments:
        st.info("Ainda não há experimentos. Crie o primeiro pelo formulário na barra lateral.")
        return

    st.subheader("Experimentos cadastrados")
    for experiment in experiments:
        documents = experiment.get("documents", [])
        failed = sum(doc.get("status") == "erro" for doc in documents)
        partial = sum(doc.get("status") == "parcial" for doc in documents)
        status = "Com falhas" if failed else "Extração parcial" if partial else "Pronto" if documents else "Sem arquivos"
        with st.container(border=True):
            left, right = st.columns([5, 1])
            with left:
                st.markdown(f"### {experiment.get('name', 'Experimento sem nome')}")
                if experiment.get("description"):
                    st.write(experiment["description"])
                st.caption(
                    f"ID {experiment.get('id', '')[:8]} · Criado em {_date_label(experiment.get('created_at'))} · "
                    f"Atualizado em {_date_label(experiment.get('updated_at'))} · "
                    f"{len(documents)} documento(s) · Status: {status} · "
                    f"{sum(doc.get('table_count', 0) for doc in documents)} tabela(s)"
                )
            with right:
                st.button(
                    "Abrir",
                    key=f"open-{experiment['id']}",
                    type="primary",
                    use_container_width=True,
                    on_click=_activate_experiment,
                    args=(experiment["id"],),
                )


def _show_overview(experiment: dict) -> None:
    documents = experiment.get("documents", [])
    pdf_count = sum(doc.get("extension") == ".pdf" for doc in documents)
    table_count = sum(doc.get("table_count", 0) for doc in documents)
    processed_count = sum(doc.get("status") in {"processado", "parcial"} for doc in documents)
    partial_count = sum(doc.get("status") == "parcial" for doc in documents)
    failed_count = sum(doc.get("status") == "erro" for doc in documents)
    total_size = sum(int(doc.get("size_bytes", 0)) for doc in documents)

    st.subheader("Overview")
    st.caption(f"Criado em {_date_label(experiment.get('created_at'))} · Atualizado em {_date_label(experiment.get('updated_at'))}")
    if experiment.get("description"):
        st.write(experiment["description"])
    else:
        st.write("Adicione uma descrição para registrar o objetivo ou o contexto deste experimento.")

    metric_columns = st.columns(5)
    metric_columns[0].metric("Documentos", len(documents))
    metric_columns[1].metric("PDFs", pdf_count)
    metric_columns[2].metric("Tabelas", table_count)
    metric_columns[3].metric("Extraídos", processed_count)
    metric_columns[4].metric("Armazenamento", _bytes_label(total_size))

    if failed_count or partial_count:
        st.warning(
            f"{failed_count} arquivo(s) com falha total e {partial_count} com extração parcial. "
            "Os originais foram preservados para consulta."
        )
    elif documents:
        st.success("Os documentos importados foram indexados. Os arquivos originais permanecem preservados.")
    else:
        st.info("Importe arquivos na seção Documentos para começar a organizar os dados.")

    quality = views.quality_summary(experiment)
    if quality["tabelas"]:
        q1, q2, q3 = st.columns(3)
        q1.metric("Blocos de dados detectados", quality["dados"])
        q2.metric("Alertas de qualidade", quality.get("aviso", 0), help="Rótulos trocados, eixos ausentes, escalas misturadas etc. Veja Catálogo e Explorador.")
        q3.metric("Observações automáticas", quality.get("info", 0))

    views.show_study_overview(experiment)

    st.markdown("**Estrutura local**")
    st.code(str(DATA_DIR / experiment["folder"]), language=None)

    with st.expander("Editar nome e descrição do experimento"):
        with st.form(f"edit-{experiment['id']}"):
            name = st.text_input("Nome", value=experiment.get("name", ""))
            description = st.text_area("Descrição", value=experiment.get("description", ""), height=90)
            submitted = st.form_submit_button("Salvar alterações", type="primary")
        if submitted:
            try:
                update_experiment(experiment, name, description)
                st.rerun()
            except ValueError as error:
                st.error(str(error))

    if documents:
        st.markdown("**Arquivos mais recentes**")
        recent = sorted(documents, key=lambda doc: doc.get("uploaded_at", ""), reverse=True)[:6]
        st.dataframe(
            pd.DataFrame([
                {
                    "Arquivo": doc.get("name"),
                    "Formato": doc.get("extension", "").lstrip(".").upper(),
                    "Extração": doc.get("status", "—"),
                    "Tabelas": doc.get("table_count", 0),
                    "Importado em": _date_label(doc.get("uploaded_at")),
                }
                for doc in recent
            ]),
            hide_index=True,
            use_container_width=True,
        )


def _show_documents(experiment: dict) -> None:
    st.subheader("Documentos")
    st.write("Importe arquivos em lote. Cada original recebe um identificador SHA-256 e fica associado somente a este experimento.")
    uploads = st.file_uploader(
        "Selecionar arquivos",
        type=sorted(extension.lstrip(".") for extension in SUPPORTED_EXTENSIONS),
        accept_multiple_files=True,
        key=f"upload-{experiment['id']}",
        help="CSV, TSV, XLS, XLSX, PDF, imagens, DOCX e TXT (inclui ISA-Tab i_Investigation*.txt).",
    )
    if st.button("Importar e extrair", type="primary", disabled=not uploads, key=f"import-{experiment['id']}"):
        try:
            st.session_state[f"local-job-{experiment['id']}"] = enqueue_uploads(
                experiment, [(uploaded.name, uploaded.getvalue()) for uploaded in uploads or []])
        except ValueError as error:
            st.error(str(error))

    local_job = st.session_state.get(f"local-job-{experiment['id']}")
    if local_job:
        status = job_status(local_job)
        if status:
            if status["status"] in {"queued", "running"}:
                st.info("Importação ou reprocessamento em segundo plano. Os uploads locais mantêm origem local, inclusive em estudos PSI.")
                st.progress(float(status.get("progress", 0)))
                if st.button("Atualizar processamento", key=f"local-job-refresh-{experiment['id']}"):
                    views.clear_cache()
                    st.rerun()
            elif status["status"] == "completed":
                st.success("Processamento concluído: originais, extrações, registro científico e busca sincronizados.")
            elif status["status"] == "partial":
                st.warning("Processamento parcial. Consulte as falhas abaixo; os originais importados foram preservados.")
            else:
                st.error(f"Processamento {status['status']}: {status.get('error') or 'Consulte o histórico de tarefas.'}")
            if status.get("result_json"):
                with st.expander("Resultado do processamento local"):
                    st.json(status["result_json"])
        experiment = next((item for item in list_experiments() if item["id"] == experiment["id"]), experiment)

    documents = experiment.get("documents", [])
    if not documents:
        st.info("Nenhum documento associado a este experimento.")
        return

    outdated = [doc for doc in documents if doc.get("schema_version", 1) < SCHEMA_VERSION]
    if outdated:
        st.warning(
            f"{len(outdated)} documento(s) foram extraídos por uma versão anterior e não têm blocos, alertas nem legendas. "
            "Reprocessar refaz a extração a partir dos originais, que não são alterados."
        )
        if st.button("Reprocessar documentos desatualizados", key=f"reprocess-all-{experiment['id']}"):
            st.session_state[f"local-job-{experiment['id']}"] = enqueue_refresh_experiment(
                experiment, document_ids=[doc["id"] for doc in outdated], reextract=True)
            st.rerun()

    st.markdown("**Índice de documentos oficiais**")
    st.dataframe(
        pd.DataFrame([
            {
                "Arquivo": doc.get("name"),
                "Formato": doc.get("extension", "").lstrip(".").upper(),
                "Tamanho": _bytes_label(int(doc.get("size_bytes", 0))),
                "Status": doc.get("status", "—"),
                "Tabelas": doc.get("table_count", 0),
                "Páginas / trechos": doc.get("page_count", 0),
                "Importado em": _date_label(doc.get("uploaded_at")),
            }
            for doc in documents
        ]),
        hide_index=True,
        use_container_width=True,
    )

    st.markdown("**Detalhes e integridade**")
    selected_id = st.selectbox(
        "Documento",
        options=[doc["id"] for doc in documents],
        format_func=lambda identifier: next(doc["name"] for doc in documents if doc["id"] == identifier),
        key=f"document-detail-{experiment['id']}",
    )
    document = next(doc for doc in documents if doc["id"] == selected_id)
    col_a, col_b = st.columns([3, 1])
    with col_a:
        st.caption("SHA-256 do arquivo original")
        st.code(document.get("sha256", ""), language=None)
    with col_b:
        if st.button("Reprocessar este", key=f"reprocess-{selected_id}"):
            try:
                st.session_state[f"local-job-{experiment['id']}"] = enqueue_refresh_experiment(
                    experiment, document_ids=[selected_id], reextract=True)
                st.rerun()
            except (OSError, ValueError) as error:
                st.error(str(error))
        if st.button("Verificar integridade", key=f"verify-{selected_id}"):
            try:
                if verify_original(experiment, document):
                    st.success("O original corresponde ao SHA-256 registrado.")
                else:
                    st.error("O conteúdo do original não corresponde ao SHA-256 registrado.")
            except (OSError, ValueError) as error:
                st.error(f"Não foi possível ler o original: {error}")

    try:
        original = read_original(experiment, document)
        st.download_button(
            "Baixar original",
            data=original,
            file_name=document["name"],
            mime="application/octet-stream",
            key=f"download-{selected_id}",
        )
        extraction = _load_one(experiment, document)
    except (OSError, ValueError, KeyError) as error:
        st.error(f"Não foi possível abrir o documento: {error}")
        return

    if document.get("extension") in {".jpg", ".jpeg", ".png", ".tif", ".tiff"}:
        try:
            st.image(BytesIO(original), caption=document["name"], use_container_width=True)
        except Exception:
            st.caption("Pré-visualização indisponível para este arquivo.")
    if extraction.get("warnings"):
        for warning in extraction["warnings"]:
            st.warning(warning)
    metadata = extraction.get("metadata", {})
    if metadata:
        with st.expander("Metadados extraídos"):
            st.json(metadata)
    if extraction.get("formulas"):
        with st.expander(f"Fórmulas encontradas ({len(extraction['formulas'])})"):
            st.dataframe(pd.DataFrame(extraction["formulas"]), hide_index=True, use_container_width=True)
    preview = extraction.get("text", "")
    if preview:
        with st.expander("Prévia do texto extraído"):
            st.text(preview[:12000] + ("\n… conteúdo truncado na prévia" if len(preview) > 12000 else ""))


def main() -> None:
    experiments = list_experiments()
    experiment_map = {item["id"]: item for item in experiments}

    with st.sidebar:
        st.markdown("## PSI Flame")
        st.caption("Dados NASA · Evidências científicas")
        section = st.radio("Área de trabalho", scientific_ui.SECTIONS, key="workspace_section")
        st.divider()
        with st.form("create-experiment", clear_on_submit=True):
            new_name = st.text_input("Novo experimento", placeholder="Ex.: Ensaio de chama 01")
            new_description = st.text_area("Descrição", placeholder="Objetivo ou observações iniciais", height=75)
            create = st.form_submit_button("Criar experimento", type="primary", use_container_width=True)
        if create:
            try:
                created = create_experiment(new_name, new_description)
                st.session_state["active_experiment_id"] = created["id"]
                st.rerun()
            except ValueError as error:
                st.error(str(error))

        st.divider()
        search_experiments = st.text_input("Pesquisar experimento", placeholder="Nome ou descrição")
        if st.button("← Lista de experimentos", use_container_width=True):
            st.session_state["active_experiment_id"] = ""
        filtered = [
            item for item in experiments
            if search_experiments.casefold() in (item.get("name", "") + " " + item.get("description", "")).casefold()
        ]
        options = [""] + [item["id"] for item in filtered]
        if st.session_state.get("active_experiment_id", "") not in options:
            st.session_state["active_experiment_id"] = ""
        selected_id = st.selectbox(
            "Experimento aberto",
            options=options,
            format_func=lambda identifier: _format_experiment(identifier, experiment_map),
            key="active_experiment_id",
        )
        st.caption("Os arquivos ficam neste computador, dentro da pasta do projeto.")

    if section != "Arquivos do experimento":
        scientific_ui.show_section(section, experiments)
        return

    experiment = experiment_map.get(selected_id)
    if experiment is None:
        _show_home(experiments)
        return

    st.title(experiment.get("name", "Experimento"))
    st.caption("Ambiente isolado do experimento · os documentos de outros experimentos não aparecem nesta área")
    tabs = st.tabs(["Overview", "Documentos", "Catálogo", "Explorador", "Tabelas", "Leitor de PDFs"])
    with tabs[0]:
        _show_overview(experiment)
    with tabs[1]:
        _show_documents(experiment)
    with tabs[2]:
        views.show_catalog(experiment)
    with tabs[3]:
        views.show_explorer(experiment)
    with tabs[4]:
        views.show_tables(experiment)
    with tabs[5]:
        views.show_search(experiment)


if __name__ == "__main__":
    main()

