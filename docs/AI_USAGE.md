# Uso de IA, Limites Científicos e Status do Provedor (`AI_USAGE.md`)

Em `2026-11-15` (Etapa 3), o **Flame in Freefall (`PSI Flame Microgravity`)** manteve integralmente os arquivos e metadados científicos coletados diretamente da NASA (`psi.nasa.gov` / `nasa.gov`) e concluiu a camada opcional do Google Gemini com salvaguardas programáticas, scripts de configuração e validação offline. Nenhuma medição científica foi gerada ou alterada por IA.

---

## 1. Busca Local e Fallback Sem Chave (Ativo por Padrão)

- **SQLite FTS5 + Vetores Locais:** operam offline sem envio de dados externos.
  - No índice persistente atual (`data/search.sqlite3`), com `paraphrase-multilingual-MiniLM-L12-v2` configurado localmente (`data/embedding_model.json`), o sistema indexa **15.524 passagens em 384 dimensões** (`local-semantic:e8f8c211226b894fcb81acc59f3b34ba3efd5f42`).
  - Em containers limpos ou deploys públicos sem modelo pesado (`RAG_EMBEDDING_MODEL=""`), o sistema utiliza segmentação determinística offline com vetores lexicais bilíngues EN/PT + SQLite `FTS5` (`11.582` segmentos no modo lexical de base).
- **Filtros Físicos Tipados:** restrições numéricas (`O₂`, pressão `psia`, velocidade `cm/s`, combustível) cruzam somente observações estruturadas na mesma linha original, preservando unidades (`psia` vs. `psig`, `Burning rate; mm`).
- **Modo Offline (Sem LLM):** retorna passagens literais da NASA, documentos associados, DOIs, hashes `SHA-256` e guias de leitura em linguagem simples, sem síntese especulativa.

---

## 2. Integração com Google Gemini API — Status Verificado

- **Status Atual neste Ambiente Local:** **`IMPLEMENTED AND READY, UNCONFIGURED LOCALLY`** *(aguarda apenas chave pessoal do proprietário).*
  - O arquivo `.env` local (ignorado pelo Git) contém `GEMINI_API_KEY=` e `GEMINI_MODEL=gemini-2.5-flash` prontos para preenchimento; `.env.example` e `.streamlit/secrets.toml.example` estão versionados sem credenciais.
  - Estão disponíveis `scripts/setup_gemini.py` (para gravação segura sem expor a chave no terminal) e `scripts/gemini_live_check.py` (para diagnóstico ao vivo ou confirmação de fallback offline).
  - Por não haver chave ativa configurada nesta máquina, chamadas HTTP ao vivo para `generativelanguage.googleapis.com` não foram executadas; toda a integração foi validada com mocks HTTP, testes de limite de taxa e validação de explicações ancoradas em [`tests/test_gemini_and_challenge.py`](../tests/test_gemini_and_challenge.py).
- **Arquitetura Implementada ([`src/gemini_provider.py`](../src/gemini_provider.py) + [`src/assistant.py`](../src/assistant.py)):**
  - **Modelo Padrão Configurável:** `GEMINI_MODEL=gemini-2.5-flash` (via `GEMINI_API_KEY` ou `GOOGLE_API_KEY` em `.env` ou Streamlit Cloud Secrets).
  - **Proteção de Dados Privados (`filter_public_nasa_evidence`):** bloqueia qualquer envio externo caso os trechos recuperados pertençam a uploads locais privados (`local_upload`). Apenas passagens públicas da NASA são elegíveis.
  - **Controle de Cota Separado por Sessão e Servidor:** cache LRU em memória (até 64 consultas) e limites deslizantes de **10 requisições/minuto**, **250 requisições/dia no servidor** e **40 requisições por sessão**, com fallback automático para evidências locais em caso de erro HTTP ou timeout.
  - **Validação Extrativa e Explicação Ancorada (`validate_claims`):** toda citação exige correspondência exata com documento recuperado, substring literal verificável, consistência numérica e fidelidade de categoria (`condition`, `simulation`, `reported_result`, `metadata`). Explicações curtas opcionais de 1 frase também têm números conferidos contra a fonte e são descartadas caso tentem reivindicar certificação de segurança ou promover condições/simulações a medições experimentais.

---

## 3. Revisão Visual Opcional (VLM) e Limites Científicos

- **Revisão Visual de PDFs (`src/visual_review.py`):** renderiza páginas localmente offline via PyMuPDF e só envia a página selecionada após consentimento explícito quando um provedor VLM está configurado. Todo retorno fica isolado na tabela `analysis_results`, marcado como `inference` e `needs_human_review = True`, nunca alterando medições ou o índice de busca.
- **Prioridade de Leitura `0–100` (`src/relevance.py` + `src/challenge_engine.py`):** pontuação determinística transparente (até 50 aplicação + até 30 termos da consulta + até 20 cobertura local) para decidir *qual estudo ler primeiro*. Nunca representa risco de incêndio, inflamabilidade ou certificação espacial.
- **Segurança Aplicacional:** defesa contra path traversal, sanitização de Markdown/HTML, verificação criptográfica `SHA-256` dos arquivos NASA e modo somente leitura público automático (`is_public_readonly()`).
