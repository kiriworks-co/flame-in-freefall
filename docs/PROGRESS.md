# PROGRESS — Retomada de sessões

## Publicação assistida — 2026-11-15 (em andamento)

- GitHub confirmado: https://github.com/kiriworks-co/flame-in-freefall . Remoto inicialmente vazio; main avançada por fast-forward até e8db878; push atômico de main e feat/spaceapps-public-release confirmado por ls-remote/fetch.
- 279 arquivos versionados (186.839.350 bytes); 353 blobs históricos verificados para padrões de credenciais, sem correspondências; nenhum blob acima de 95 MiB. .env e secrets.toml não versionados. Checagem focada, sem garantia de auditoria exaustiva.
- Índice code-review-graph atualizado para e8db878; documentos não são indexados, portanto impacto documental conferido por leitura direta.
- Arquivos de deploy presentes; Python 3.11 selecionado explicitamente no Streamlit. Implantação e URL pública ainda aguardam confirmação.
- Textos de submissão consolidados em SUBMISSION_TEXTS_EN.md a partir do rascunho existente e docs da Etapa 3. submission_drafts/ preservado localmente, fora dos commits desta publicação.
- Nenhuma chamada Gemini real executada; fallback sem chave é o modo de publicação. Suíte completa de 164 testes é resultado da Etapa 3, não reexecutada nesta sessão.

## Etapa 3 — Concluída e Validada (`2026-11-15`)

- **Checkpoint preservado:** `checkpoint/pre-stage3-final` em `e227b2f`; trabalho executado exclusivamente na branch `feat/spaceapps-public-release` sem reconstruir desnecessariamente `data/scientific.sqlite3` ou `data/search.sqlite3`.
- **Refinamento UX/UI & Navegação (`app.py`, `src/design_system.py`, `src/scientific_ui.py`, `src/i18n.py`, `.streamlit/config.toml`):**
  - `.streamlit/config.toml` atualizado para `toolbarMode = "minimal"` e `showErrorDetails = "none"`; chrome/menu do Streamlit ocultado preservando abertura da sidebar.
  - Adicionado `<meta name="google" content="notranslate">` e classe `notranslate` na barra superior e pílulas.
  - Removida duplicidade de idioma (`topbar-lang-toggle` removido): mantido **um único seletor segmentado `EN | PT-BR`** sincronizado na barra superior com alto contraste na opção ativa.
  - Criado hero em azul-marinho aeroespacial (`#0F1D2B`) com **diagrama visual comparativo HTML/CSS `Terra (1g) — Chama em gota` vs. `Órbita (~0g) — Chama esférica`** e selos `SUMMARIZE · RANK · INTERPRET`.
  - Os 3 cartões iniciais (*Discover the Science*, *Explore Fire Safety*, *Investigate NASA Data*) e as 4 métricas do acervo (`12` estudos, `40` arquivos, `117` tabelas, `15.524` segmentos) foram alinhados em linhas únicas em desktop (`1440×900`, altura idêntica `224,95 px`) com empilhamento limpo em mobile (`390×844`, `scrollWidth == 390 px`).
  - `_go_back()` tornado sensível às Jornadas Guiadas; opções técnicas (`Nível de experiência` na sidebar e sincronização/CLI em `Fontes`) recolhidas em expanders para visitantes comuns; título duplicado `PSI-69 · PSI-69 · FLEX` no Hub corrigido.
- **Google Gemini e Configuração (`src/gemini_provider.py`, `src/assistant.py`, `.env`, `.env.example`, `.streamlit/secrets.toml.example`, `scripts/setup_gemini.py`, `scripts/gemini_live_check.py`):**
  - Placeholders `GEMINI_API_KEY=` e `GEMINI_MODEL=gemini-2.5-flash` preparados no `.env` local (preservando `RAG_EMBEDDING_MODEL`, fora do Git) e em `.streamlit/secrets.toml.example`.
  - Limites separados por sessão (`40/sessão`) e servidor (`10/min`, `250/dia`), suporte a `explanation` curta opcional verificada contra números e limites da fonte em `validate_claims()`, e remoção de nomes de variáveis de ambiente das mensagens de interface.
  - Status local: `UNCONFIGURED` (aguarda chave pessoal opcional do proprietário; fallback offline e mocks validados).
- **Validação Técnica e em Navegador:**
  - `pytest` completo offline: **164 passed in 179.45s** (`0` falhas), seguido por revalidação dirigida UI/i18n/Gemini após o ajuste final de CSS/título do Hub.
  - `ruff`, `mypy` (19 arquivos), `compileall` e `pip check` aprovados; zero segredos ou caminhos privados em runtime.
  - Chromium real em `http://127.0.0.1:8511` (`1440×900` e `390×844`) validado com inspeção direta das capturas de tela. Servidor local mantido ativo na porta `8511`.
- **Documentação Final Obrigatória Gerada (A–E):**
  - `docs/PROJECT_OVERVIEW_PTBR.md`
  - `docs/FEATURES_AND_WORKFLOWS_PTBR.md`
  - `docs/FOLDER_STRUCTURE_PTBR.md`
  - `docs/SUBMISSION_DESCRIPTION_EN.md`
  - `docs/FINAL_RELEASE_STATUS_PTBR.md`
  - Atualizados `README.md`, `docs/DEPLOYMENT.md`, `docs/AI_USAGE.md`, `docs/TEST_REPORT.md`, `docs/ACTIVE_MISSION.md`, `docs/PROGRESS.md` e `docs/index.html`.
- **Próxima ação do proprietário:** Conduzir a **Revisão Científica Independente (`PENDENTE`)** em `http://127.0.0.1:8511`, opcionalmente configurar a chave do Gemini via `scripts/setup_gemini.py`, e realizar `git push` + deploy público no Streamlit Community Cloud.

---

## Etapa 2 — concluída e validada (2026-11-15)

- Repositório original confirmado, branch `feat/spaceapps-public-release`, base
  `5a2c487`, checkout inicialmente limpo; nenhum outro repositório alterado.
- As 15 instruções completas foram fornecidas pelo proprietário nesta sessão;
  contrato rastreável em [STAGE2_INTEGRATION.md](STAGE2_INTEGRATION.md).
- ZIP externo íntegro e originais não vazios conferidos contra novos downloads
  NASA. Três estudos adicionais: 24 documentos preservados (21 úteis e três
  placeholders ISA), três ZIPs ISA, dois ZIPs vazios fora da ingestão científica.
  Dois CSVs PSI-159 complementados pela fonte NASA. Auditoria e hashes em
  [STAGE2_SOURCE_AUDIT.md](STAGE2_SOURCE_AUDIT.md).
- Primeira ingestão real: 40 documentos no total, 12 PSI + referência
  NASA-CONTEXT; todas as páginas dos seis PDFs novos extraídas; originais
  verificados e `foreign_key_check` vazio. Extrações e classificações por
  coluna preservam simulações, resultados reportados, condições e cálculos.
- Validação final: **161 passed in 243.83s**, Ruff, Mypy em 15 arquivos,
  compileall e pip check aprovados. Suíte de base: 112 aprovados. Testes novos
  cobrem fontes reais, filtros, RAG, interface, concorrência e relevância semântica.
- SQLite: 117 tabelas, 10.114 linhas tabulares (8.966 de CSV), 26.803 registros
  tipados; não são contagens de ensaios ou medições independentes.
- Índice persistente: **15.524 chunks FTS5 + embeddings locais de 384 dimensões**,
  sem falhas/avisos, com 21 documentos úteis novos recuperáveis. Dois warm starts
  retornaram `ready` sem importar/indexar novamente. Modo lexical também validado
  com 11.582 chunks. Consultas reais dos três estudos e insuficiência passaram.
- `.gitattributes` preserva originais no Git; 83 verificações SHA-256 dos blobs
  preparados aprovadas. Originais no disco permaneceram inalterados.
- Registro Git da Etapa 2: commit `e227b2f` (`feat(science): integrate PSI-62 PSI-117 and PSI-159 sources`).
