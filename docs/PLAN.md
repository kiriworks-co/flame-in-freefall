# Plano de implementação — 15/11/2026

Continuar o Streamlit/Python existente e preservar seus leitores, tabelas, análises e originais.

1. Executar os coletores NASA, diagnosticar a API pública atual e registrar bytes, hash, versões e lacunas.
2. Integrar importação idempotente, SQLite e jobs locais à persistência JSON existente.
3. Indexar evidências estruturadas com FTS5 e vetores; filtrar números tipados e responder com citações verificadas.
4. Acrescentar visão global, catálogo NASA, busca/assistente e comparação conservadora sem remover as telas anteriores.
5. Validar unidades, segurança de arquivos, idempotência, recuperação, NASA real e Streamlit; registrar limitações.

## Coordenação

- NASA: scripts de coleta, resources, downloads e DATA_PROVENANCE.
- Ingestão: scientific_store, pipeline, units, storage/extractors e testes próprios.
- RAG: retrieval, assistant, relevance e testes próprios.
- Coordenador: app e interface científica, integração, dependências, E2E e documentação.
- QA adicional usará um slot liberado, sem editar arquivos dos agentes ainda ativos.

## Estado inicial verificado

O kit não contém dados NASA nem testes. Sem repositório Git próprio (o Git encontrado pertence a diretório ancestral e não será modificado). Criado índice local .code-review-graph; análise por dependências diretas complementa o grafo. Python 3.12.14 disponível no runtime Codex, criado ambiente local .venv. Não havia Python no PATH.
