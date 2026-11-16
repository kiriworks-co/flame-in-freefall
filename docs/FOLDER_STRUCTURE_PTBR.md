# Estrutura Real de Pastas e Fluxo de Dados (`FOLDER_STRUCTURE_PTBR.md`)

Este documento descreve a árvore real e inspecionada do repositório **Flame in Freefall (`PSI Flame Microgravity`)**, omitindo apenas ambientes virtuais (`.venv/`), caches de execução (`__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`, `.code-review-graph/`), artefatos temporários (`tmp/`, `.playwright-cli/`), internos do Git (`.git/`) e arquivos locais de credenciais (`.env`, `.streamlit/secrets.toml`).

---

## 1. Árvore Completa do Repositório

```text
PROJETO TESTE FLAME MICROGRAVITY/
├── .env.example                          # Modelo público de variáveis de ambiente (sem chaves)
├── .gitattributes                        # Preserva finais de linha dos originais científicos no Git
├── .gitignore                            # Ignora .venv, caches, .env, secrets.toml, *.sqlite3 e tmp/
├── .python-version                       # Fixa Python 3.11 para portabilidade e Streamlit Cloud
├── AGENTS.md                             # Instruções persistentes de engenharia e integridade científica
├── CODEX_MISSION.md                      # Especificação integral da missão e regras de execução
├── README.md                             # Guia principal de instalação, uso, verificação e publicação
├── app.py                                # Ponto de entrada Streamlit, barra contextual, sidebar e roteamento
├── pyproject.toml                        # Configurações de Ruff (lint) e Mypy (checagem estática)
├── pytest.ini                            # Configuração da suíte de testes Pytest e marcadores
├── requirements.txt                      # Dependências enxutas de execução e deploy público
├── requirements-dev.txt                  # Ferramentas de desenvolvimento (pytest, ruff, mypy)
├── requirements-models.txt               # Dependência opcional para embeddings locais (sentence-transformers)
├── requirements-tested.txt               # Snapshot exato de versões validadas localmente
│
├── .streamlit/
│   ├── config.toml                       # Tema Aerospace Daylight, toolbarMode = "minimal", showErrorDetails = "none"
│   └── secrets.toml.example              # Modelo TOML para Streamlit Community Cloud Secrets (sem segredos)
│
├── config/
│   └── quantity_rules.json               # Regras declarativas de identificação de grandezas físicas e unidades
│
├── data/
│   ├── embedding_model.json              # Metadados públicos e licença do modelo local de embeddings (384-d)
│   ├── experimentos/                     # Espelho estruturado por estudo (originais + extração JSON)
│   │   ├── nasa-context-guias-oficiais-nasa-cbd8a291/
│   │   ├── psi-25-bass-ii-2200f993/
│   │   ├── psi-26-bass-6cbbd60c/
│   │   ├── psi-62-psi-62-94ff5e48/
│   │   ├── psi-68-flex-2-511f3577/
│   │   ├── psi-69-flex-32da5589/
│   │   ├── psi-98-saffire-i-ba994cae/
│   │   ├── psi-99-saffire-ii-682a817e/
│   │   ├── psi-100-saffire-iii-64f649b6/
│   │   ├── psi-101-same-r-37c16a8a/
│   │   ├── psi-102-same-842fc416/
│   │   ├── psi-117-cool-flame-dynamics-cfd-flex-comparison-9fa7a556/
│   │   └── psi-159-acme-cfi-g-ed733501/
│   └── psi_downloads/                    # Arquivos originais imutáveis baixados da NASA + manifests JSON
│       ├── .gitkeep
│       ├── stage2_archive_audit.json     # Auditoria do pacote ZIP da Etapa 2 e anomalias vazias
│       ├── PSI-25/ ... PSI-26/ ... PSI-62/ ... PSI-68/ ... PSI-69/
│       ├── PSI-98/ ... PSI-99/ ... PSI-100/ ... PSI-101/ ... PSI-102/
│       ├── PSI-117/                      # Inclui archive_anomalies/ (2 ZIPs vazios) e metadata/ ISA
│       └── PSI-159/                      # Inclui metadata/ ISA, relatórios e tabelas experimentais
│
├── docs/                                 # Documentação técnica, auditorias, relatórios e entrega final
│   ├── ACTIVE_MISSION.md                 # Plano ativo de continuidade entre sessões
│   ├── AI_USAGE.md                       # Transparência sobre busca local, Gemini, VLM e limites
│   ├── ANTIGRAVITY_HANDOFF.md            # Registro histórico de handoff
│   ├── DATA_PROVENANCE.md                # Origens NASA, DOIs, versões, SHA-256 e lacunas científicas
│   ├── DEMO_SCRIPT.md                    # Roteiro de demonstração de 2–3 minutos (BASS, FLEX, SAME)
│   ├── DEPLOYMENT.md                     # Guia de execução local, Streamlit Community Cloud e GitHub Pages
│   ├── DESIGN_SYSTEM.md                  # Tokens de cor, tipografia, espaçamento e componentes reutilizáveis
│   ├── FEATURE_AUDIT.md                  # Auditoria de funcionalidades científicas e de UX
│   ├── FEATURES_AND_WORKFLOWS_PTBR.md    # [Doc B] Manual funcional completo em PT-BR
│   ├── FINAL_RELEASE_STATUS_PTBR.md      # [Doc E] Estado final de prontidão para submissão em PT-BR
│   ├── FOLDER_STRUCTURE_PTBR.md          # [Doc C] Este documento de arquitetura e diretórios em PT-BR
│   ├── LOCAL_ACCEPTANCE.md               # Roteiro de aceite local para o proprietário
│   ├── PLAN.md                           # Plano inicial de engenharia
│   ├── PROGRESS.md                       # Registro cronológico de retomada e entregas
│   ├── PROJECT_OVERVIEW_PTBR.md          # [Doc A] Visão geral completa do projeto em PT-BR
│   ├── QA_REVIEW.md                      # Parecer histórico de QA
│   ├── RELEASE_CHECKLIST.md              # Checklist de verificação antes da publicação pública
│   ├── RESOURCES_NASA.md                 # Referências dos 10 links oficiais do desafio
│   ├── SCIENTIFIC_REVIEW_CHECKLIST.md    # Checklist de revisão científica para o proprietário
│   ├── SEMANTIC_VALIDATION.md            # Registro de validação dos embeddings de 384 dimensões
│   ├── STAGE2_INTEGRATION.md             # Relatório técnico da integração de PSI-62, PSI-117 e PSI-159
│   ├── STAGE2_SOURCE_AUDIT.md            # Auditoria detalhada de originais, figuras e ressalvas da Etapa 2
│   ├── SUBMISSION_DESCRIPTION_EN.md      # [Doc D] Descrição oficial de submissão em inglês (curta e longa)
│   ├── TEST_REPORT.md                    # Relatório consolidado de testes automatizados e navegador
│   ├── UI_REVIEW.md                      # Revisão técnica de interface e acessibilidade
│   ├── UX_AUDIT.md                       # Auditoria de heurísticas de Nielsen e WCAG 2.2 AA
│   ├── index.html                        # Cartão estático bilíngue opcional para GitHub Pages
│   ├── junit.xml                         # Relatório XML histórico de testes
│   ├── qa-desktop.png                    # Captura histórica de QA desktop
│   ├── qa-mobile.png                     # Captura histórica de QA mobile
│   ├── qa-search-desktop.png             # Captura histórica da busca
│   └── qa-source-same-p13.png            # Captura histórica de página PDF SAME
│
├── resources/
│   ├── manifests/
│   │   ├── data_quality_profile.json     # Perfil de codificação, células vazias e dimensões das tabelas
│   │   ├── official_resources.json       # Catálogo dos 10 links oficiais do Space Apps
│   │   ├── priority_investigations.json  # Catálogo oficial das 12 investigações PSI, DOIs e ressalvas
│   │   └── resource_link_check.json      # Resultado da verificação HTTP dos links oficiais
│   └── official/
│       ├── README.md                     # Nota sobre os guias oficiais da NASA
│       ├── psi_database_guide.pdf        # Complete PSI Database Guide (NASA)
│       ├── psi_database_guide.provenance.json
│       ├── researchers_guide.pdf         # A Researcher's Guide to ISS Combustion Science (NASA)
│       └── researchers_guide.provenance.json
│
├── scripts/
│   ├── fetch_nasa_resources.py           # Coleta conservadora dos PDFs oficiais de contexto NASA
│   ├── fetch_psi_tables.py               # Coleta via API Geode NASA PSI (CSVs/PDFs e metadados)
│   ├── gemini_live_check.py              # Diagnóstico ao vivo (ou fallback offline) da integração Gemini
│   ├── import_stage2_archive.py          # Importador seguro e auditado do pacote ZIP Etapa 2
│   ├── ingest_nasa.py                    # CLI de ingestão idempotente e indexação em SQLite
│   ├── setup_embeddings.py               # Configuração explícita opcional de embeddings locais
│   └── setup_gemini.py                   # Assistente CLI seguro para gravar GEMINI_API_KEY em .env / secrets
│
├── src/
│   ├── __init__.py                       # Identificador do pacote Python
│   ├── analysis.py                       # Ajustes de série, baseline, normalização, ajuste linear e FWHM
│   ├── assistant.py                      # Orquestrador RAG PT/EN + validate_claims() programático
│   ├── blocks.py                         # Detecção de múltiplos blocos tabulares em planilhas e CSVs
│   ├── challenge_engine.py               # Motor SUMMARIZE · RANK · INTERPRET ancorado nos arquivos reais
│   ├── comparison.py                     # Verificação de compatibilidade dimensional/metodológica entre tabelas
│   ├── crossref.py                       # Referência cruzada entre tabelas-índice (Data ID) e blocos
│   ├── datasets.py                       # Enriquecimento de blocos (colunas tipadas, alertas e sugestão visual)
│   ├── design_system.py                  # Paleta, CSS responsivo, barra superior, hero SVG e padrão Plotly
│   ├── extractors.py                     # Extração local de CSV, XLSX, PDF (PyMuPDF), DOCX, imagens e TXT
│   ├── frames.py                         # Construção de DataFrames, rótulos de eixos e tipo de gráfico
│   ├── gemini_provider.py                # Adaptador REST Google Gemini com filtro privado e limites de taxa
│   ├── guided_journeys.py                # Jornadas Guiadas 1 e 2 (4 passos, 5 perguntas) e guias de gráfico
│   ├── i18n.py                           # Dicionário bilíngue EN/PT-BR, perfis das 12 investigações e tradutores
│   ├── isa.py                            # Leitor estruturado de metadados ISA-Tab (i_Investigation*.txt)
│   ├── local_jobs.py                     # Worker local de upload/reprocessamento sincronizado com SQLite
│   ├── pipeline.py                       # Cold-start idempotente (ensure_scientific_bootstrap), travas e jobs
│   ├── quality.py                        # Detecção não destrutiva de anomalias e alertas em tabelas
│   ├── quantities.py                     # Regras declarativas de classificação de grandezas físicas
│   ├── relevance.py                      # Score determinístico (0–100) de prioridade de leitura
│   ├── retrieval.py                      # Índice híbrido persistente (SQLite FTS5 + vetores 384D / lexicais)
│   ├── scientific_store.py               # Camada relacional SQLite (investigações, páginas, tabelas, observações)
│   ├── scientific_ui.py                  # Telas globais: Início, Hub, Catálogo, Comparar, Assistente, Visual, Fontes
│   ├── search.py                         # Tokenização, normalização textual e sinônimos científicos PT/EN
│   ├── storage.py                        # Persistência atômica por experimento, verificação SHA-256 e overrides
│   ├── units.py                          # Normalização dimensional conservadora via Pint (psia vs psig etc.)
│   ├── views.py                          # Explorador de Dados: síntese visual, gráficos, tabelas, leitor PDF e ISA
│   └── visual_review.py                  # Renderização local de páginas PDF e revisão qualitativa VLM isolada
│
├── submission_drafts/                    # Rascunhos históricos anteriores de texto (mantidos para referência)
│
└── tests/
    ├── test_app.py                       # Smoke test de navegação global e resposta do assistente
    ├── test_assistant.py                 # Grounding programático, rejeição de números inventados e sanitização
    ├── test_collectors.py                # Coleta NASA PSI, validação de endpoints Geode e links
    ├── test_comparison.py                # Guardrails de compatibilidade dimensional e ranking explicável
    ├── test_end_to_end.py                # Fluxo vertical completo (ingestão -> SQLite -> busca -> UI)
    ├── test_gemini_and_challenge.py      # Gemini REST/limites/explicações, Challenge Hub e barra única de idioma
    ├── test_guided_ux.py                 # Jornadas Guiadas 1 e 2, 5 perguntas, guias de gráfico e PT-BR
    ├── test_i18n_and_deployment.py       # Paridade de chaves EN/PT-BR, cold-start portátil e PSI_READONLY_MODE
    ├── test_ingestion.py                 # Extração CSV/PDF/ISA e idempotência de ingestão
    ├── test_local_jobs.py                # Jobs em segundo plano e isolamento de uploads locais
    ├── test_retrieval.py                 # Busca híbrida FTS5, filtros numéricos por linha e migração
    ├── test_security_regressions.py      # Proteções contra path traversal, fórmulas maliciosas e HTML/XSS
    ├── test_stage2_archive.py            # Auditoria e hashes dos 24 documentos da Etapa 2 e placeholders
    ├── test_stage2_ingestion.py          # Ingestão real, unidades conservadoras e concorrência no Windows
    ├── test_stage2_scientific_labels.py  # Classificação por coluna (simulação, reportado, condição, cálculo)
    ├── test_stage2_search_ui.py          # E2E em cópia isolada dos estudos PSI-62, PSI-117 e PSI-159
    ├── test_stage2_semantic_guard.py     # Limiar semântico conservador contra vizinhos irrelevantes
    ├── test_storage_atomic.py            # Escrita JSON atômica sob disputa simultânea
    ├── test_ui_details.py                # Validação de URLs seguras, DOIs, avisos de campo e abertura de estudo
    ├── test_units.py                     # Conversões Pint (atm/psia/m/s/°C) e preservação de ambiguidades
    └── test_visual_review.py             # Renderização PDF, consentimento VLM e isolamento em analysis_results
```

*(Nota: os bancos reconstruíveis `data/scientific.sqlite3` e `data/search.sqlite3` são gerados automaticamente na primeira execução a partir dos arquivos versionados acima e permanecem ignorados pelo Git conforme `.gitignore`.)*

---

## 2. Responsabilidades por Camada

| Camada | Arquivos / Diretórios Principais | Responsabilidade |
|---|---|---|
| **Frontend & Navegação** | `app.py`, `src/design_system.py`, `src/scientific_ui.py`, `src/guided_journeys.py`, `src/views.py`, `src/i18n.py` | Layout responsivo, barra contextual (`Onde você está`, `← Voltar`, `🏠 Início`, seletor único `EN \| PT-BR`), hero visual com esquema SVG `1g vs 0g`, Hub `SUMMARIZE · RANK · INTERPRET`, Jornadas Guiadas, Explorador de Dados em 6 abas e localização integral EN/PT-BR. |
| **Processamento Científico & Unidades** | `src/extractors.py`, `src/blocks.py`, `src/datasets.py`, `src/frames.py`, `src/quality.py`, `src/quantities.py`, `src/units.py`, `src/analysis.py`, `src/isa.py`, `src/crossref.py`, `config/quantity_rules.json` | Extrai tabelas e texto sem alterar os originais, detecta múltiplos blocos por planilha, aplica alertas de qualidade não destrutivos, analisa metadados ISA-Tab e converte apenas grandezas e escalas explicitamente documentadas via `Pint`. |
| **Motor Comparativo & Desafio** | `src/comparison.py`, `src/relevance.py`, `src/challenge_engine.py` | Verifica compatibilidade de grandezas/unidades/metodologias antes de comparar estudos, calcula prioridade de leitura `0–100` de forma determinística e gera resumos e interpretações ancoradas em arquivos reais. |
| **IA, Busca Híbrida & Grounding** | `src/retrieval.py`, `src/search.py`, `src/assistant.py`, `src/gemini_provider.py`, `src/visual_review.py` | Indexa passagens em SQLite `FTS5` + vetores (embeddings 384D ou lexicais), aplica filtros numéricos na mesma linha de origem, executa seleção opcional via Google Gemini com proteção de privacidade (`local_upload`) e valida citações/números em código (`validate_claims`). |
| **Armazenamento & Ingestão** | `src/storage.py`, `src/scientific_store.py`, `src/pipeline.py`, `src/local_jobs.py` | Mantém originais imutáveis por `SHA-256`, gerencia `data/experimentos/` e `data/scientific.sqlite3`, realiza *cold-start bootstrap* automático e coordena travas entre processos. |
| **Recursos NASA & Scripts** | `data/psi_downloads/`, `resources/manifests/`, `resources/official/`, `scripts/` | Armazena os 40 documentos autênticos da NASA com manifests/DOIs e fornece scripts de coleta Geode, auditoria ZIP, ingestão, configuração de embeddings e configuração/teste de Gemini. |
| **Configuração de Deploy & QA** | `.streamlit/config.toml`, `.streamlit/secrets.toml.example`, `.env.example`, `.python-version`, `requirements.txt`, `tests/`, `docs/` | Configura tema claro, `toolbarMode = "minimal"`, `showErrorDetails = "none"`, modo público `PSI_READONLY_MODE`, dependências enxutas e suíte com 164 testes automatizados. |

---

## 3. Fluxo Completo de Informação (Ponta a Ponta)

```text
[Fontes Oficiais NASA PSI + Guias PDF]
   │  (scripts/fetch_psi_tables.py, fetch_nasa_resources.py, import_stage2_archive.py)
   ▼
[data/psi_downloads/PSI-* + resources/official/]  (Originais imutáveis + SHA-256 + DOI + URL)
   │  (src/pipeline.py :: ensure_scientific_bootstrap / ingest_downloads)
   ▼
[src/extractors.py + blocks.py + isa.py + units.py]
   ├──► [data/experimentos/*/extraction.json]      (Cache JSON retrocompatível por documento)
   └──► [data/scientific.sqlite3]                  (13 investigações, 40 docs, 566 pág., 117 tabelas, 26.803 obs. tipadas)
          │
          ├──► [src/views.py / guided_journeys.py / comparison.py / challenge_engine.py]
          │       └─► Gráficos Plotly, Tabelas, Comparações e SUMMARIZE · RANK · INTERPRET
          │
          └──► [src/retrieval.py → data/search.sqlite3] (15.524 chunks FTS5 + vetores 384D / lexicais)
                  │
                  ▼
               [src/assistant.py :: answer()]
                  ├─ Modo Offline (padrão sem chave): citações literais verificáveis + linhas + SHA-256
                  └─ Modo Gemini Opcional (src/gemini_provider.py :: gemini-2.5-flash):
                        1. filter_public_nasa_evidence() bloqueia local_upload
                        2. Envia pergunta + até 6 passagens públicas NASA
                        3. validate_claims() confere citação, trecho literal, números e tipo
                        4. Interface Streamlit exibe resposta, explicação ancorada e originais clicáveis
```
