# PROGRESS — Retomada de sessões

## Estado atual (Recuperado pós-interrupção do Claude Opus 5.5 — `2026-11-15`)
- **Branch e checkpoints Git (`feat/spaceapps-public-release`)**:
  - Branch principal `main` em `880145a`.
  - Checkpoints preservados: `checkpoint/pre-ux-journey-redesign` (`51ddf8a`), `checkpoint/pre-final-product-overhaul` (`16acce4`) e `checkpoint/pre-final-engineering-refinement` (`386ab9b`).
  - Auditoria confirmou que a sessão interrompida do Claude Opus 5.5 (erro `429 RESOURCE_EXHAUSTED` no subagente Gemini) não deixou alterações não commitadas no repositório — apenas miniaturas temporárias em `tmp/img/rg_*.png` (ignoradas pelo Git).
- **Verificações executadas na recuperação (`386ab9b`)**:
  - `.\.venv\Scripts\python.exe -m ruff check app.py src scripts tests` → **All checks passed!**
  - `.\.venv\Scripts\python.exe -m mypy app.py src/design_system.py src/gemini_provider.py src/challenge_engine.py src/assistant.py src/scientific_ui.py src/guided_journeys.py src/views.py src/i18n.py tests/test_gemini_and_challenge.py` → **Success: no issues found in 10 source files**
  - `.\.venv\Scripts\python.exe -m compileall -q app.py src scripts tests` → **exit 0**
  - `.\.venv\Scripts\python.exe -m pip check` → **No broken requirements found.**
  - `$env:PYTHONUNBUFFERED="1"; $env:RAG_EMBEDDING_MODEL=" "; $env:HF_HUB_OFFLINE="1"; $env:TRANSFORMERS_OFFLINE="1"; .\.venv\Scripts\python.exe -m pytest -v` → **112 passed in 68.42s**
  - *Nota técnica para Windows PowerShell:* usar `$env:RAG_EMBEDDING_MODEL=" "` (espaço) em vez de `""`, pois string vazia remove a variável do ambiente Windows e faz `load_dotenv(override=False)` recarregar o modelo do `.env`, travando threads do `AppTest`.
- **O que já funciona integralmente**:
  - Catálogo e acervo verificado de 9 investigações NASA PSI (`PSI-25`, `PSI-26`, `PSI-68`, `PSI-69`, `PSI-98`, `PSI-99`, `PSI-100`, `PSI-101`, `PSI-102`) + 2 guias oficiais (`16` arquivos, `7.881.267` bytes, SHA-256 e DOIs verificados).
  - Persistência SQLite (`data/scientific.sqlite3` e `data/search.sqlite3`) com cold-start idempotente (`ensure_scientific_bootstrap()`), normalização conservadora Pint (`src/units.py`), busca híbrida `FTS5` + vetores + filtros físicos (`src/retrieval.py`), validação extrativa (`src/assistant.py`), comparação e ranking determinístico `0–100` (`src/comparison.py`, `src/relevance.py`, `src/challenge_engine.py`), bilíngue EN/PT-BR com `679` chaves (`src/i18n.py`), Jornadas Guiadas 1 e 2 (`src/guided_journeys.py`), Revisão Visual Offline (`src/visual_review.py`) e modo `PSI_READONLY_MODE`.
- **O que está parcial ou pendente**:
  - *Parcial:* finalização dos scripts/limites/explicações ancoradas do Google Gemini (`scripts/setup_gemini.py`, `scripts/gemini_live_check.py`, `.streamlit/secrets.toml.example`) e refinamento UX/UI/navegação/idioma (13 pontos apontados na avaliação visual).
  - *Pendente:* incorporação das investigações NASA `PSI-62`, `PSI-117` e `PSI-159`, validação em navegador após refinamento e geração dos Documentos A–E (`PROJECT_OVERVIEW_PTBR.md`, `FEATURES_AND_WORKFLOWS_PTBR.md`, `FOLDER_STRUCTURE_PTBR.md`, `SUBMISSION_DESCRIPTION_EN.md`, `FINAL_RELEASE_STATUS_PTBR.md`).

---

## Próximos Passos (Plano Registrado em [ACTIVE_MISSION.md](ACTIVE_MISSION.md))
1. **Etapa 1 — Continuidade e recuperação do trabalho anterior** *(Concluída)*: auditoria Git, diagnóstico do travamento de testes no PowerShell, validação dos 112 testes e criação de `docs/ACTIVE_MISSION.md`.
2. **Etapa 2 — Incorporação dos materiais NASA `PSI-62`, `PSI-117` e `PSI-159`** *(Próxima etapa imediata)*: coleta/verificação de arquivos originais NASA, atualização de manifests e `docs/DATA_PROVENANCE.md`, ingestão/indexação SQLite idempotente, perfis bilíngues em `src/i18n.py` e testes.
3. **Etapa 3 — Finalização da missão de engenharia, UX/UI, integração Gemini e documentação**: aplicar melhorias visuais e de navegação, finalizar scripts/proteções Gemini, validar em navegador real e produzir os Documentos A–E antes da publicação via [DEPLOYMENT.md](DEPLOYMENT.md).
