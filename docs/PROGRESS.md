# Progresso

## Estado de criação do kit (2026-11-15)
- [x] Projeto original copiado sem `.git`, sem sobrescrever módulos existentes.
- [x] Links de dez recursos e IDs de nove investigações catalogados.
- [x] Scripts de tentativa de download preparados.
- [ ] Download real NASA (bloqueado pela rede do ambiente de preparação; executar no Codex).
- [ ] Normalização científica avançada, pipeline multimodal, índice híbrido, RAG e testes E2E (a serem desenvolvidos).

## Execuções e modificações subsequentes
Adicionar entradas com data, arquivos, comandos, resultado e próximo passo.

### 15/11/2026 — execução em andamento

- Leitura integral de AGENTS.md, CODEX_MISSION.md, RESOURCES_NASA.md e deste progresso; README e manifests inspecionados.
- Raiz efetiva: subpasta PROJETO TESTE FLAME MICROGRAVITY.
- Nenhum Git local; não alterar índice do Git ancestral. Índice .code-review-graph local criado e análise de impacto inicial executada.
- Python do runtime Codex 3.12.14 localizado; .venv criada; instalação das dependências em andamento.
- Skills consultadas: ui-ux-pro-max, redesign-existing-projects, awesome-design-skills (somente professional como inspiração), playwright-cli, web-design-guidelines, PDF e security-audit (orientação focada). React não se aplica à arquitetura Streamlit.
- Três subagentes ativos: NASA DATA, INGESTION e SEARCH/RAG, com arquivos exclusivos; coordenador integra interface e validação.
- Próximos passos: concluir coleta real, integrar manifests no pipeline, executar ingestão/indexação, testar UI e registrar resultados.

### 15/11/2026 — integração e validação

- [x] Coletores executados exatamente como solicitado; API Geode corrigida para key/sortingCategory e restrições.
- [x] Obtidos e verificados 16 originais NASA: nove CSVs, cinco PDFs PSI e dois guias; URLs/SHA completos em DATA_PROVENANCE.md.
- [x] SQLite e JSON integrados: 10 investigações (nove PSI + contexto), 16 documentos, 199 páginas, 31 tabelas, 9.967 células e 4.788 observações.
- [x] Reexecução NASA idempotente, zero duplicações/erros; jobs reais e detecção de falha parcial.
- [x] Índice FTS5 e vetores lexicais validado com 1.517 chunks.
- [x] Modelo multilíngue real baixado no cache externo, revisão e8f8c211226b894fcb81acc59f3b34ba3efd5f42; índice semântico com 2.709 chunks, 43 lotes, 82,8s, zero falhas.
- [x] Catálogo, visão global, busca PT/EN, filtros tipados, comparação conservadora e leitor de evidências integrados.
- [x] VLM opcional implementado com saída tipada e revisão humana, separado de observações; sem chave/provedor real, testes com mocks rotulados.
- [x] QA independente validou CSV/PDF NASA reais até pergunta/citação e PNG; corrigido job que antes poderia indicar concluído após erro de extração.
- [x] Ruff global e mypy seletivo passaram nesta etapa; suíte inicial 42 passed, expandida por QA/RAG/VLM (contagem final pendente).
- [x] Streamlit local funcionando em 127.0.0.1:8501; inspeção visual desktop realizada.
- [ ] Finalizar jobs de uploads locais e sua integração SQLite/índice (sem atribuir origem NASA a uploads do usuário).
- [ ] Concluir navegador mobile/teclado, suíte final, TEST_REPORT.md e DEMO_SCRIPT.md com páginas reais.

Lacunas externas confirmadas: Apollo1/13 TLS; OCR depende de Tesseract; LLM/VLM reais sem configuração/chave. Unidade Burning rate/mm ambígua e capa FLEX-2 em documento catalogado PSI-69 sinalizadas. Não há validação científica independente, série temporal completa nem certificação de segurança.

### 15/11/2026 — entrega local validada

- [x] Jobs de upload/reprocessamento integrados ao JSON, SQLite e índice; recarga após lock; provenance local_upload sem atribuição de fonte NASA.
- [x] Corrigidos recorte de subwords acima do limite e fechamento de conexões SQLite. Índice final **2.711 chunks**, todos com no máximo 128 tokens; 384 dimensões. Ver SEMANTIC_VALIDATION.md.
- [x] Rodada final do coordenador: **92 passed**, zero falhas, um FutureWarning do alias fitz, 57,80s. Ruff global, mypy em oito módulos, compileall e pip check passaram. JUnit em docs/junit.xml.
- [x] Browser desktop/mobile/paisagem, escala 200% em paisagem, navegação por teclado e foco sólido de 3px verificados; sem overflow de página nas larguras 375/812/1440 testadas.
- [x] Pergunta FLEX com filtro O2 retornou linhas do CSV real; download via UI confere byte a byte e SHA com NASA.
- [x] Job de ingestão acionado pela UI concluiu: 16 existentes, zero importados, errors=[], indexed=0, total=2711. Um job completed real está registrado.
- [x] Original PDF SAME página física 13 renderizado e inspecionado. Screenshots em docs/qa-*.png.
- [x] README, .env.example, PLAN, DATA_PROVENANCE, AI_USAGE, DEMO_SCRIPT e TEST_REPORT atualizados; RESOURCES_NASA registra que a lacuna histórica de coleta foi resolvida.
- [x] Grafo reconstruído integralmente: 41 arquivos, zero erros de parsing; impacto final inclui os workers, interface, RAG e revisão visual. Nenhum Git ancestral foi alterado.

**Estado para retomada:** aplicação rodando em http://127.0.0.1:8501, com nove estudos PSI reais e contexto. Iniciar na raiz efetiva com `.venv\Scripts\python.exe -m streamlit run app.py --server.port 8501`. Modelo opcional configurado em .env por caminho externo, sem segredos; proveniência do modelo em data/embedding_model.json.

**Pendências externas/limites:** configurar provedor e credencial se desejar homologar LLM/VLM reais; instalar Tesseract/idiomas se precisar OCR do desenho SAME; validar cientificamente interpretação, taxa ambígua e aplicabilidade do PDF FLEX-2. Não foi realizada auditoria WCAG completa, validação Python3.11, calibração de acurácia semântica, coleta de todo raw/vídeo ou publicação em produção. Não há implementação obrigatória pendente para o fluxo local com evidências sem LLM descrito na definição de pronto; esses limites não devem ser apresentados como resolvidos.
