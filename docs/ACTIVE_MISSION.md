# ACTIVE MISSION — Continuidade e Plano de Execução (`Flame in Freefall`)

**Atualizado em:** `2026-11-15`  
**Branch ativa:** `feat/spaceapps-public-release`  
**Commit base recuperado:** `386ab9b` (`feat(ux-ai): finalize Aerospace Daylight UI, Challenge Hub, 5-question journeys, and Gemini integration`)  
**Checkpoint de segurança preservado:** `checkpoint/pre-final-engineering-refinement` (`386ab9b`)

## Estado após integração científica da Etapa 2

Base desta sessão: `5a2c487`, no repositório original e branch correta, sem
alterações iniciais a preservar. As 15 instruções fornecidas pelo proprietário
estão rastreadas em [STAGE2_INTEGRATION.md](STAGE2_INTEGRATION.md).

- 12 investigações PSI + registro NASA-CONTEXT; 40 documentos preservados
  (24 novos, dos quais 21 úteis e três placeholders ISA).
- PSI-62: somente metadados, sem séries numéricas públicas. PSI-117: dados
  experimentais reportados e CFD separados. PSI-159: relatórios, condições,
  cálculos e resultados reportados em dois CSVs complementados da NASA.
- SQLite: 117 tabelas extraídas, 10.114 linhas tabulares, 26.803 registros
  tipados; sem violações de chave estrangeira. Originais e blobs Git verificados.
- Busca persistente: 15.524 passagens FTS5/embeddings locais de 384 dimensões;
  recuperação real dos três estudos e resposta insuficiente verificadas.
- Ingestão idempotente, bloqueio entre processos, retomada de índice e
  preservação de bytes no Git corrigidos. UI EN/PT-BR, gráficos e tipos de
  evidência validados sem reformular o produto.
- Validação final: **161 testes aprovados em 243,83 s**, Ruff, Mypy em 15
  arquivos, compileall e pip check aprovados. Smoke com embeddings reais e
  navegador desktop/mobile concluídos. Etapa 2 encerrada no commit de mensagem
  `feat(science): integrate PSI-62 PSI-117 and PSI-159 sources`.

**Próxima etapa autorizável:** Etapa 3 — Final Engineering, Product Refinement
& Documentation. Ela não foi iniciada: nenhuma configuração Gemini, publicação
ou criação dos cinco documentos finais A–E nesta sessão.

---

## 1. Diagnóstico da Recuperação (Sessão Interrompida do Claude Opus 5.5)

- **Estado do Git recuperado sem perdas:**
  - `main`: `880145a` (`chore: baseline locally validated PSI Flame Microgravity prototype`)
  - `checkpoint/pre-ux-journey-redesign`: `51ddf8a`
  - `checkpoint/pre-final-product-overhaul`: `16acce4`
  - `checkpoint/pre-final-engineering-refinement`: `386ab9b` — criada pelo Claude Opus 5.5 em `2026-11-15 19:57:03` logo após iniciar a missão final de engenharia e antes da interrupção.
  - **Alterações não commitadas / stashes / objetos órfãos:** nenhum (`git status` limpo, `git stash list` vazio, `git fsck --lost-found` sem pendências).
- **O que foi executado pelo Claude Opus 5.5 antes do limite de uso (`429`):**
  - Verificou o estado do repositório e criou a branch `checkpoint/pre-final-engineering-refinement` em `386ab9b`.
  - Leu `app.py`, `src/i18n.py`, `src/scientific_ui.py` e `src/gemini_provider.py`, e gerou 24 miniaturas de inspeção (`tmp/img/rg_1.png` a `rg_24.png`, em pasta ignorada pelo Git) a partir de `resources/official/researchers_guide.pdf`.
  - Lançou o subagente `Gemini Integration Engineer` (que realizou apenas leitura de código e consultas à documentação oficial da API Gemini antes de encerrar por `RESOURCE_EXHAUSTED (code 429)` às `19:59:40`).
  - **Conclusão da auditoria:** nenhum arquivo de código-fonte, dado científico ou configuração foi alterado ou corrompido após `386ab9b`.
- **Ambiente local observado:**
  - Python `3.12.14` no `.venv` local; bancos reconstruíveis `data/scientific.sqlite3` e `data/search.sqlite3` intactos.
  - Um servidor Streamlit anterior na porta `8501` (`PID 19756` / `19512`) encontrava-se em execução desde `15:42:29` e não foi modificado.

### Diagnóstico do Bloqueio de `pytest` no Windows PowerShell
- Durante a validação da Etapa 1, `$env:RAG_EMBEDDING_MODEL=""` no PowerShell remove a variável do bloco de ambiente do Windows.
- Com a variável ausente, `app.py` e `src/pipeline.py` executam `load_dotenv(..., override=False)` e recarregam `RAG_EMBEDDING_MODEL` do `.env`, fazendo as threads `ScriptRunner` do `AppTest` tentarem importar `sentence_transformers`/`torch` e entrarem em espera sem progresso (`task-72`).
- **Solução comprovada para testes offline em PowerShell:** definir `$env:PYTHONUNBUFFERED="1"; $env:RAG_EMBEDDING_MODEL=" "` (um espaço impede `load_dotenv(override=False)` de sobrescrever a variável, e `.strip()` em `src/retrieval.py` trata o valor como vazio, mantendo o modo lexical determinístico).
- **Resultado validado após recuperação (`task-106`):** `112 passed in 68.42s`, além de `ruff`, `mypy` (10 arquivos), `compileall` e `pip check` aprovados sem erros.

---

## 2. Inventário na recuperação (`386ab9b`, histórico anterior à Etapa 2)

### A. Concluídas e Validadas (`386ab9b`)
- **Acervo NASA autêntico e imutável:** 9 investigações PSI (`PSI-25`, `PSI-26`, `PSI-68`, `PSI-69`, `PSI-98`, `PSI-99`, `PSI-100`, `PSI-101`, `PSI-102`) + 2 guias oficiais NASA (`16` arquivos, `7.881.267` bytes, SHA-256 e DOIs conferidos em [DATA_PROVENANCE.md](DATA_PROVENANCE.md)).
- **Persistência e cold-start:** `data/scientific.sqlite3` e `data/search.sqlite3` reconstruídos por `ensure_scientific_bootstrap()` (`src/pipeline.py`, `src/scientific_store.py`, `src/storage.py`).
- **Normalização conservadora de unidades:** `src/units.py` (Pint) preserva `psig` vs. `psia`, mantém `Burning rate; mm` bruto com alerta e não inventa unidades ausentes (`Saffire`).
- **Busca híbrida e grounding:** `src/retrieval.py` (SQLite `FTS5` + vetores lexicais determinísticos de `1.517` trechos ou embeddings locais de `2.711` trechos + filtros numéricos alinhados na mesma linha) e `src/assistant.py` (`validate_claims()` com rejeição de afirmações sem evidência).
- **Comparação e prioridade de leitura:** `src/comparison.py`, `src/relevance.py` e `src/challenge_engine.py` (`SUMMARIZE · RANK · INTERPRET`, score determinístico `0–100` de prioridade de leitura, separado de risco de incêndio).
- **Interface bilíngue e descoberta guiada:** `src/i18n.py` (`679` chaves EN/PT-BR com EN padrão), `src/guided_journeys.py` (Jornadas 1 e 2 com as 5 Perguntas Científicas), `src/views.py` (`Data Explorer` com `Visual First Look` na `Tab 0`), `src/visual_review.py` (renderização local de PDFs e revisão visual isolada), e bloqueio público `PSI_READONLY_MODE` em `app.py`.

### B. Parcialmente Implementadas (Em Refinamento na Etapa 3)
1. **Integração Google Gemini (`src/gemini_provider.py`, `src/assistant.py`):**
   - *Já existe:* adaptador REST `generateContent` com `responseSchema`, `filter_public_nasa_evidence` (bloqueando `local_upload`), cache LRU, rate-limit de módulo e testes com mocks HTTP (`tests/test_gemini_and_challenge.py`).
   - *Falta concluir:* scripts `scripts/setup_gemini.py` e `scripts/gemini_live_check.py`, template `.streamlit/secrets.toml.example`, garantia de placeholders no `.env`, limites separados por sessão (`session_id`) e por servidor (RPM/RPD), explicações curtas ancoradas nos números da citação e remoção de nomes de variáveis de ambiente das mensagens exibidas ao usuário; validação real ao vivo caso haja chave configurada.
2. **Refinamento de UX/UI, Navegação e Idioma (`app.py`, `src/design_system.py`, `src/scientific_ui.py`, `src/i18n.py`, `.streamlit/config.toml`):**
   - *Já existe:* tema *Aerospace Laboratory Daylight*, barra superior contextual, Challenge Hub e responsividade CSS básica.
   - *Falta corrigir (13 pontos da revisão do proprietário):* excesso de espaço em branco, identidade visual fraca no hero, grandes blocos de texto sem apoio visual/diagrama, alinhamento e altura inconsistentes nos 3 cartões iniciais (o 3º cartão quebra de linha), simplificação da navegação lateral para destinos principais claros, remoção de controles duplicados/desnecessários (`← Back`, duplicidade de seletor de idioma), garantia de sincronismo visual do seletor de idioma e bloqueio de tradução automática do navegador (rótulos como `"Lar"`), ajuste da barra nativa do Streamlit (`toolbarMode = "minimal"`) e ocultação de ferramentas de desenvolvedor/manutenção para visitantes comuns.

### C. Pendentes
1. **Incorporação das investigações NASA `PSI-62`, `PSI-117` e `PSI-159`:** nenhum registro ou arquivo presente até `386ab9b`.
2. **Documentação final de entrega (Documentos A–E):** `docs/PROJECT_OVERVIEW_PTBR.md`, `docs/FEATURES_AND_WORKFLOWS_PTBR.md`, `docs/FOLDER_STRUCTURE_PTBR.md`, `docs/SUBMISSION_DESCRIPTION_EN.md` e `docs/FINAL_RELEASE_STATUS_PTBR.md` (a serem gerados somente após concluir código e testes).

---

## 3. Próximas Três Etapas

### Etapa 1 — Continuidade e recuperação do trabalho anterior *(Concluída)*
- Auditoria do histórico Git e dos logs da execução interrompida do Claude Opus 5.5 (`386ab9b`).
- Diagnóstico do travamento de `pytest` no Windows PowerShell e revalidação integral (`112 passed` + `ruff`, `mypy`, `compileall`, `pip check`).
- Registro oficial do estado em `docs/ACTIVE_MISSION.md` e `docs/PROGRESS.md` com checkpoint seguro no Git.

### Etapa 2 — Incorporação dos materiais NASA `PSI-62`, `PSI-117` e `PSI-159` *(Concluída e validada)*
- Baixar/importar apenas arquivos verificáveis da NASA para `PSI-62`, `PSI-117` e `PSI-159` em `data/psi_downloads/`.
- Registrar versão, DOI, URLs permanentes, tamanho, SHA-256, classificação e ressalvas científicas em `resources/manifests/priority_investigations.json` e `docs/DATA_PROVENANCE.md`.
- Executar ingestão idempotente e atualização dos bancos/índices (`data/scientific.sqlite3` e `data/search.sqlite3`).
- Adicionar perfis bilíngues em `src/i18n.py` (sem alterar IDs, DOIs ou valores originais) e validar com testes automatizados.

### Etapa 3 — Finalização da missão de engenharia, UX/UI, integração Gemini e documentação
- Executar o refinamento UX/UI e de navegação/idioma (13 itens identificados na avaliação).
- Concluir configuração, limites, explicações ancoradas e scripts de verificação do Google Gemini.
- Validar arquitetura de deploy (`PSI_READONLY_MODE`, cold-start, ausência de segredos), executar suíte completa e auditoria em navegador real mantendo o servidor local ativo para aceite final do proprietário.
- Gerar os Documentos A, B, C, D e E e atualizar `README.md` e `docs/PROGRESS.md` com base no software finalizado.
