# Uso de IA, Limites Científicos e Status do Provedor (`AI_USAGE.md`)

Em 15/11/2026, o desenvolvimento final do **Flame in Freefall (`PSI Flame Microgravity`)** preservou integralmente os arquivos e metadados científicos coletados diretamente da NASA (`psi.nasa.gov` / `nasa.gov`) e elevou interface, internacionalização, explicabilidade e camadas opcionais de IA com salvaguardas rígidas. Nenhuma medição científica foi gerada ou alterada por IA.

---

## 1. Busca Local e Fallback Sem Chave (Ativo por Padrão)

- **SQLite FTS5 + Vetores Locais**: Operam offline sem envio de dados externos.
  - Quando um modelo de embeddings local (`RAG_EMBEDDING_MODEL`, ex.: `paraphrase-multilingual-MiniLM-L12-v2`, licença registrada em [`data/embedding_model.json`](../data/embedding_model.json)) está configurado localmente, o índice utiliza **2.711 trechos em janela de tokens** (`local-semantic:...`).
  - Em containers limpos ou deploys públicos sem modelo pesado (`RAG_EMBEDDING_MODEL=""`), o sistema utiliza **1.517 segmentos estruturais determinísticos** com `lexical-vectors` bilíngues EN/PT.
- **Filtros Físicos Tipados**: Restrições numéricas (`O2`, pressão, velocidade de fluxo) cruzam somente observações estruturadas na mesma linha original, com preservação de unidades (`psia` vs. `psig`, `Burning rate; mm`).
- **Modo Offline (Sem LLM)**: Retorna passagens literais da NASA, documentos associados, DOIs, hashes SHA-256 e guias de leitura em linguagem simples, sem síntese especulativa.

---

## 2. Integração com Google Gemini API — Status Verificado

- **Status Atual neste Ambiente Local**: **`IMPLEMENTED BUT UNCONFIGURED`**.
  - O arquivo `.env` local não contém `GEMINI_API_KEY` nem `GOOGLE_API_KEY`. Nenhuma chamada externa real ao endpoint Gemini foi executada nesta máquina; todo o comportamento da integração foi validado em testes unitários e de integração com mocks HTTP ([`tests/test_gemini_and_challenge.py`](../tests/test_gemini_and_challenge.py)).
- **Arquitetura Implementada ([`src/gemini_provider.py`](../src/gemini_provider.py) + [`src/assistant.py`](../src/assistant.py))**:
  - **Modelo Padrão Configurável**: `GEMINI_MODEL=gemini-2.5-flash` (via `GEMINI_API_KEY` ou `GOOGLE_API_KEY` em `.env` ou Streamlit Cloud Secrets).
  - **Proteção de Dados Privados (`filter_public_nasa_evidence`)**: Bloqueia qualquer envio externo caso os trechos recuperados pertençam apenas a uploads locais privados (`local_upload`). Somente passagens públicas da NASA são elegíveis para síntese opcional.
  - **Controle de Cota e Resiliência**: Cache LRU em memória para consultas repetidas, limite deslizante de **10 requisições/minuto** e **40 requisições/sessão**, e fallback automático para citações offline verificáveis em caso de falha HTTP ou timeout.
  - **Validação Extrativa (`validate_claims`)**: Toda frase gerada exige correspondência com documento recuperado, trecho literal verificável, consistência numérica e fidelidade de categoria (`condition`, `sample`, `measurement`, `calculation`); afirmações livres são recusadas.

---

## 3. Revisão Visual Opcional (VLM) e Limites Científicos

- **Revisão Visual de PDFs (`src/visual_review.py` + `src/vlm_review.py`)**: Só envia a página selecionada após consentimento explícito do usuário (quando endpoint configurado). Todo retorno é isolado na tabela `analysis_results`, marcado como `inference` e `needs_human_review = True`, nunca alterando medições ou o índice de busca.
- **Prioridade de Leitura `0–100` (`src/relevance.py` + `src/challenge_engine.py`)**: Pontuação determinística transparente (até 50 aplicação + até 30 termos da consulta + até 20 cobertura local) para ajudar pesquisadores e iniciantes a decidir *qual estudo ler primeiro*. Nunca representa risco real de incêndio, inflamabilidade de material ou certificação espacial.
- **Segurança Aplicacional**: Prevenção contra path traversal, leitura inerte de texto/Markdown (`unsafe_allow_html=False` em citações e HTML escapado em cartões), verificação criptográfica SHA-256 dos arquivos NASA e modo somente leitura público automático (`is_public_readonly()`).
