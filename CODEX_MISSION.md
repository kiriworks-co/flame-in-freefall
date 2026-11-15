# CODEX — MISSÃO INTEGRAL: PSI Flame Microgravity (Space Apps 2026)

Você é o AGENTE IMPLEMENTADOR responsável por concluir o software existente de ponta a ponta. Não produza apenas um plano. Leia este arquivo, AGENTS.md, README.md, a árvore de código e o histórico Git, se disponível. Modifique arquivos reais, execute o programa e teste.

## Objetivo de produto
Criar um dashboard científico de microgravidade usando dados **originais** NASA Physical Sciences Informatics (PSI), capaz de catalogar investigações, importar PDFs/CSVs/XLSX, resumir/classificar/interpretar pesquisas, recuperar evidências com busca híbrida, comparar experimentos e responder com citações verificáveis, sem inventar medições ou conclusões de segurança.

Desafio: https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/
Leitura obrigatória: `resources/manifests/official_resources.json`, `resources/manifests/priority_investigations.json`, `docs/RESOURCES_NASA.md`.

## NORMAS DE EXECUÇÃO — não negocie com o escopo
1. CONTINUE o código já existente, Python + Streamlit; não substitua tudo por novo Next.js e não apague dados ou telas existentes. Sua base inclui `app.py`, `src/extractors.py`, `src/storage.py`, `src/search.py`, `src/quantities.py`, `src/frames.py`, `src/blocks.py`, `src/datasets.py`, `src/quality.py`, `src/views.py`, `src/crossref.py`.
2. Entre em modo de implementação: audite, planeje de maneira curta, codifique, teste, corrija, execute, apresente resultados. Crie `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/DATA_PROVENANCE.md`, `docs/TEST_REPORT.md`, `docs/AI_USAGE.md`.
3. Consulte e USE as **skills disponíveis e relevantes** no seu ambiente (listar/ler instruções das skills antes de aplicar). Prefira skills de Python, engenharia de software, dados, arquitetura, frontend/Streamlit, testes, qualidade, segurança e documentação, SE disponíveis. Não declare ter utilizado skills inexistentes. Se o ambiente permitir **subagentes**, delegue em paralelo tarefas independentes com responsabilidades delimitadas (ver abaixo); integre e teste você mesmo. Se não houver subagentes, faça sequencialmente.
4. Trabalhe com autonomia, sem pedir confirmações para decisões comuns. Se uma credencial paga, acesso restrito, autenticação, autorização destrutiva ou segredo estiver faltando, implemente adaptador funcional com modo degradado e informe bloqueio sem fingir sucesso.
5. Use ferramentas de terminal de código e testes; evite automação de navegador desnecessária, clique por clique, que gaste todo o limite do Codex. Se a sessão for interrompida, persista progresso granular em `docs/PROGRESS.md` e continue na próxima sessão.
6. Não use mock como se fosse dado NASA. Fixtures sintéticas apenas nos testes, rotuladas. Separe demonstração com dados reais de testes unitários.
7. Para o Space Apps, priorize um fluxo vertical funcional com dados verdadeiros, depois aperfeiçoe. Nunca minta dizendo que concluiu trabalho incompleto.

## Etapa zero: inspeção e inventário
- Confira Python, requirements, Streamlit, diretórios, segurança e eventuais testes existentes.
- Rode lint/smoke test atuais, registre bugs e funções reais.
- Confira documentos de recursos. Este kit NÃO contém PDFs/CSVs baixados; confirme o estado ao iniciar.
- Não confunda estudos OSDR/OSD com dados PSI de combustão; o namespace dos experimentos é PSI-XX.

## 1. Download NASA PSI — PRIORIDADE ZERO
- Confira os 10 links oficiais em `resources/manifests/official_resources.json`. A fonte empírica é **PSI Data Repository**, os demais contextualizam.
- Priorize PSI-25, PSI-26 (sólidos), PSI-68, PSI-69 (gotas/extinção), PSI-98/99/100 (Saffire), PSI-101/102 (fumaça).
- Execute `python scripts/fetch_nasa_resources.py --guide --psi-manual` para obter PDF NASA oficial e manual do repositório.
- Execute `python scripts/fetch_psi_tables.py --ids PSI-25 PSI-26 PSI-68 PSI-69 PSI-98 PSI-99 PSI-100 PSI-101 PSI-102`. Os scripts são ferramentas de partida, NÃO presumir que API funciona: teste, diagnostique e ajuste conformemente a resposta REAL da NASA, respeite rate limits, redirecionamentos e licenças.
- Se o API Geode exigir ajustes: inspeccione a aplicação pública e a documentação do PSI; use os endpoints descobertos (base `https://psi.nasa.gov/geode-py/ws`): GET `/studies/{ID}/metadata`, GET `/repo/investigations/{ID}/versions`, POST `/files/v2`, GET `/studies/{ID}/download?file=...&version=...&redirect=false`. São endpoints observados em documentação comunitária, podem mudar. Não falsifique respostas.
- Se a API não responder: adote a página oficial para baixar arquivos selecionados manualmente, ou registre URLs e instruções precisas; **não troque fonte primária por números inventados**. Retente o download de apenas 2-3 investigações essenciais antes de expandir.
- Baixe pequenos CSVs `Experimental table` e PDFs relevantes; não baixe terabytes, grandes vídeos ou todos os raw files. Preserve bytes, SHA-256, versão, DOI, URL, data de acesso, tipo de arquivo, unidades, licença e lacunas. Não publique URLs assinadas S3 expiradas como referências permanentes.
- Implemente importação em lote dos arquivos baixados na estrutura atual `data/experimentos` sem duplicação. IDs humanos PSI e IDs internos devem coexistir.
- Separe explicitamente registros contendo **condições de ensaio**, **amostras** e **medições reais**. Um CSV de condições não prova velocidade de propagação, eficácia de supressão nem risco de incêndio.

## 2. Banco de dados, ingestão e proveniência
- Preserve todos os originais imutáveis, atualizando o sistema de SHA-256 atual sem quebrar retrocompatibilidade.
- Introduza SQLite com migrações leves para investigação PSI, documentos, versões, páginas, regiões, tabelas, células/cabeçalhos, eventos, observações, fontes, chunks, jobs e resultados de análise; associe dados físicos à fonte e granularidade.
- Processamento idempotente e incremental: evitar duplicação, suportar falhas parciais e reexecução. Background jobs reais com status, não bloquear UI; uso de worker simples local é suficiente.
- PDFs: PyMuPDF com layout/blocos, seções e páginas, tabelas/figuras/equações/legendas, metadados e bounding boxes. OCR condicional. Integre VLM opcional para gráficos e páginas complexas, com saída tipada e revisão; nunca converta visualização de gráfico em leitura exata sem validação.
- CSV/XLSX: manter matriz bruta, cabeçalhos, fórmulas e linhas; inferir grandezas e unidades somente com evidência; suportar séries temporais, ranges, qualitativos, nulos e incertezas. Não misturar categorias heterogêneas.
- Normalizar pressão em psi **distinguindo psia/psig**, velocidades cm/s, temperaturas com escala declarada, diâmetro e taxa com unidades dimensionalmente corretas; usar Pint e testes. Pressão parcial de O₂ = fração x pressão absoluta, mas marcar isso como derivação, nunca medição.

## 3. Conhecimento, embeddings, busca e RAG
- Chunking estrutural/semântico: dividir por documento, seção, página, tabela e legenda; retenção de arquivo, posição, estudo, DOI e hash.
- Índice híbrido persistente: SQLite FTS5 + Chroma/FAISS ou equivalente simples, embeddings científicos/multilíngues (modelo local quando viável), busca lexical e vetorial. Filtros numéricos aplicados a campos tipados e comparáveis, NUNCA como similaridade de strings.
- Reranking com prioridade moderada para experimento ativo, porém comparações globais devem pesquisar múltiplos.
- Q&A com LLM configurável por ambiente (qualquer provedor coerente, não exigir gasto). Adicione modo sem LLM com recuperação e evidências clicáveis. Distinga medida, condição, cálculo e inferência. Estabeleça política de insuficiência de evidência para responder "não encontrei dados". Use links de DOI e localizações de documento, linha/linha tabela/página.
- Grounding programático: verificar se citações apontam para fontes retornadas e se valores numéricos afirmados estão apoiados em registros; prompt sozinho NÃO garante evidência.
- Defesa contra prompt injection em PDFs e strings de planilhas; limite tamanho de arquivo, impedir descompactação maliciosa/path traversal, sanitizar markdown/html e não enviar segredos ao LLM.

## 4. Interface completa (Streamlit)
- Visão geral com cobertura, status da ingestão e categorização prevenção/detecção/supressão.
- Catálogo de investigações com links diretos NASA, documentos/DOI, descrição, filtros e estado de extração.
- Explorador de PDFs/tabelas com inspeção de original, unidades, missingness, gráficos, séries temporais e aviso quando dados são condições e não medições.
- Comparador de 2-3 estudos, fazendo comparação somente se dimensões/condições/metodologias forem compatíveis, caso contrário explicar limitações.
- Busca avançada textual + semântica + numérica (O₂, pressão, velocidade, combustível) com evidências.
- Assistente científico RAG em PT/EN com referências verificáveis e saída honesta.
- Ranking de **relevância da investigação para perguntas de segurança**, não ranking fictício de risco de materiais. Score interpretável, deterministicamente computado; separar para aplicação em habitat, detecção e supressão, com fundamentos documentados.
- UI profissional, clara e operacional; preservar recursos já existentes.

## 5. Testes, documentação e entrega
- Adicione pytest, lint/format se disponível, type checking seletivo, testes de integração, teste com ao menos um CSV NASA REAL e um PDF NASA REAL; smoke test Streamlit.
- Testes de unidades (1 atm absoluto = ~14,6959 psia; 1 m/s = 100 cm/s); idempotência; hashes; fontes; filtro numérico; chunk; ranking; mecanismo de resposta insuficiente; segurança de arquivos; modo offline.
- O teste E2E deve executar: baixar/importar estudo e PDF original → extrair → persistir → indexar → perguntar → obter evidências válidas e visualizá-las na UI. Teste sem LLM e, se houver chave válida, também com LLM. Não invente sucesso caso indisponível.
- `README.md`: setup Windows Python 3.11, .env.example sem segredos, instruções de ingestão, datasets, setup de modelos, teste, problemas conhecidos, licenças, AI disclosure e fontes.
- Gere `docs/DEMO_SCRIPT.md` com roteiro de 2-3 minutos demonstrando BASS, FLEX e SAME sem promessas científicas indevidas, com links de arquivo e paginação real.
- Faça revisão final de código, segurança, qualidade, acessibilidade e proveniência.

## Paralelismo / subagentes (se o ambiente suportar)
- **Agente A — NASA DATA**: download de PSI e PDF, manifests, DOI, fonte e classificação dos campos; trabalha apenas em scripts e resources/data.
- **Agente B — INGESTION**: armazenamento, extração e unidades; src pipeline e testes correspondentes.
- **Agente C — SEARCH/RAG**: chunks, embeddings, filtros, rerank, LLM, citadores e testes.
- **Agente D — UI/UX**: Streamlit e experiências guiadas; não altera pipeline central.
- **Agente E — QA/SECURITY**: testes de integração, revisão de segurança, documentação e relatório.
- **Você (agente coordenador)**: audita dependências de interfaces, atribui arquivos sem conflitos, integra PRs/branches e valida o E2E. Subagentes não substituem responsabilidade de integração.

## Definição de pronto
Um usuário consegue abrir o Streamlit, escolher PSI-69 ou outro estudo **real**, inspecionar CSV original e fonte NASA, comparar dados sem extrapolação, buscar por filtros numéricos, fazer uma pergunta, obter evidências e uma resposta com fontes quando o LLM estiver configurado, ou obter as evidências sem LLM.

A entrega final deve listar exatamente:
- arquivos reais NASA baixados, URL e SHA-256;
- dados indisponíveis e motivos;
- componentes implementados, pendências e bloqueios externos;
- testes executados e resultado;
- comando exato para rodar.

**EXECUTE A MISSÃO AGORA.** Antes de responder ao usuário, altere arquivos e realize o máximo de implementação real possível. Não se limite a fornecer sugestões. Priorize a cadeia vertical com fontes reais antes da VLM sofisticada. Se a janela de execução terminar, atualize `docs/PROGRESS.md` e registre os próximos passos atômicos.
