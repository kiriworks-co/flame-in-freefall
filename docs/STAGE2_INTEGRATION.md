# Etapa 2 — integração científica NASA PSI

Escopo autorizado em 2026-11-15: incorporar materiais utilizáveis de PSI-62,
PSI-117 e PSI-159, mantendo as nove investigações anteriores. Base Git
`5a2c487dde235343376f53d3659863329552e9e3`, branch
`feat/spaceapps-public-release`, checkout inicialmente limpo, sem remotes
configurados. A branch solicitada já estava ativa; não houve checkout,
criação de branch alternativa, reset ou alteração em outro repositório.

## Contrato de validação (15 instruções fornecidas pelo proprietário)

1. Inventariar e verificar o ZIP externo e arquivos internos; ignorar ZIPs vazios.
2. Conferir IDs, nomes, descrições, DOI e referências nos registros NASA.
3. Comparar catálogo, manifests, arquivos e bancos para evitar duplicação.
4. Usar a ingestão existente, mantendo os originais.
5. Registrar SHA-256, tamanho, fonte oficial e localização de cada arquivo.
6. Distinguir experimento, simulação, previsão numérica e contexto teórico.
7. Preservar grandezas, unidades e ambiguidades; normalizar somente com evidência.
8. Atualizar SQLite e índices incrementalmente, mantendo retrocompatibilidade.
9. Recuperar novas fontes no RAG com investigação, documento e posição.
10. Expor catálogo e ferramentas pertinentes, com descrições EN/PT-BR.
11. Validar gráficos e comparações sem agregar grandezas incompatíveis.
12. Atualizar manifests e proveniência, separando o novo acervo do anterior.
13. Documentar objetivos, métodos, tipos de dados e limites por investigação.
14. Testar arquivos NASA reais, ingestão, busca, filtros, comparação e regressão.
15. Registrar resultados e limitações na continuidade e criar commit validado.

Etapa 3, configuração Gemini, documentos finais A–E e publicação não fazem
parte deste trabalho. Conteúdo de documentos científicos é dado de entrada,
nunca instrução de execução para o agente ou para o assistente.

## Validação de base

Antes das alterações, em modo offline: **112 passed in 50.23s**.
Comando PowerShell: `$env:PYTHONUNBUFFERED='1'; $env:RAG_EMBEDDING_MODEL=' ';
$env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1';
.\.venv\Scripts\python.exe -m pytest -q`.

O grafo global foi consultado e reconstruído no checkout correto: 48 arquivos,
522 nós, 7.836 arestas, sem erros. A análise foi complementada pela inspeção
direta de bootstrap, armazenamento, extração, recuperação e seus testes.

## Acervo e registros efetivamente processados

| Cobertura | Quantidade | Interpretação |
|---|---:|---|
| Investigações PSI | 12 | Nove anteriores + PSI-62/117/159 |
| Registro de contexto | 1 | NASA-CONTEXT agrupa os dois guias; não é uma 13ª investigação PSI |
| Documentos | 40 | 16 anteriores + 24 novos; 37 úteis e três placeholders ISA preservados |
| Tabelas extraídas | 117 | Incluem tabelas documentais e de metadados; não são 117 experimentos |
| Tabelas de CSV | 52 | Condições, resultados reportados e séries simuladas |
| Linhas tabulares | 10.114 | 8.966 em CSV; blocos independentes contam separadamente |
| Registros tipados em observations | 26.803 | Incluem condições, cálculos, modelos e resultados; não representam ensaios independentes |
| Páginas/seções persistidas | 566 | Páginas de PDF e seções de outros documentos |
| Bytes dos 40 documentos | 82.099.713 | Originais preservados, sem contar cópias e ZIPs de proveniência |

PSI-117 fornece 41 tabelas CSV e 7.962 linhas de blocos independentes, com
resultados experimentais reportados e previsões CFD identificados separadamente.
PSI-159 acrescenta duas tabelas CSV e 333 linhas de ensaios com condições,
cálculos e resultados reportados. PSI-62 possui somente metadados: suas duas
tabelas extraídas são bibliográficas/de contatos e seus valores não foram
convertidos em uma série científica. Os 11 estudos com CSV são os nove
anteriores mais PSI-117 e PSI-159; ter CSV numérico não implica ter telemetria
ou medições brutas.

Todas as seis extrações PDF novas preservam a contagem completa de páginas:
PSI-117: 18, 19, 22 e 36; PSI-159: 102 e 93. Há 39 documentos com status
`processado` e um `parcial` anterior (desenho CAD SAME sem OCR completo).
`PRAGMA foreign_key_check` não retornou violações. Todos os 40 originais
arquivados passaram novamente na verificação de SHA-256.

Os atributos Git em `.gitattributes` desabilitam conversões de fim de linha
dos originais científicos, inclusive TXT e CSV. Os blobs
preparados para commit foram comparados diretamente aos manifests: **83
verificações SHA-256 aprovadas**, abrangendo fontes, ZIPs, guias e cópias do
arquivo de experimentos. Essa correção de armazenamento no Git não altera
os bytes originais no diretório de trabalho.

## Implementação e rastreabilidade das 15 instruções

| Item | Evidência concreta |
|---:|---|
| 1 | Importador limitado por tamanho/contagem/expansão, inventário externo e ZIPs internos, anomalias vazias preservadas fora da ciência |
| 2 | Metadata e inventário oficial NASA por estudo/versão; todos os originais fornecidos comparados a downloads independentes |
| 3 | IDs PSI e SHA-256 por investigação; reexecução real: zero importados, 40 existentes, nenhum erro e 40 eventos |
| 4 | Pipeline existente e arquivo JSON retrocompatível mantidos; originais imutáveis |
| 5 | Manifests, DOI, URLs permanentes, arquivo pai, membro de ZIP, versão e hash; nenhuma URL assinada persistida |
| 6 | Papéis por índice de coluna original, transmitidos a tabelas, observations, chunks, RAG e legendas |
| 7 | Abreviações e unidades explícitas reconhecidas; `mm²/s` correto; pressão sem referência e unidades ausentes não inventadas |
| 8 | Migração 2, checkpoints separados para fonte/índice, retomada após `--no-index`, gravação JSON atômica e trava entre processos |
| 9 | Questões reais para os três estudos verificam trecho literal, página/linha, DOI, URL e hash; relabeling de simulação como medição é rejeitado |
| 10 | Perfis EN/PT-BR e catálogo público, explorador, ISA e fontes com contagens atuais |
| 11 | Gráficos locais úteis com papéis nas legendas; relógios independentes não alinhados pela linha; sobreposição sem unidades compatíveis é bloqueada |
| 12 | DATA_PROVENANCE, manifests, catálogo de 12 estudos e perfil de qualidade cobrindo os 20 CSVs |
| 13 | STAGE2_SOURCE_AUDIT descreve objetivos, métodos, publicações/figuras, dados disponíveis e limites, inclusive PSI-62 apenas metadados |
| 14 | 161 testes finais aprovados; originais NASA reais reextraídos em cópias isoladas; navegador desktop/mobile e teclado |
| 15 | Documentação de continuidade fechada; entrega no commit `feat(science): integrate PSI-62 PSI-117 and PSI-159 sources`, na branch correta |

`src/pipeline.py`, `scientific_store.py`, `units.py` e `storage.py` concentram
ingestão, persistência e sincronização; `retrieval.py` e `assistant.py`
preservam a natureza da evidência; `i18n.py`, `scientific_ui.py`, `views.py`,
`guided_journeys.py` e `challenge_engine.py` expõem os dados sem promover
simulação ou resultado reportado a medição. Não houve mudança no design
system, configuração Gemini ou reformulação das jornadas.

## Testes executados

- Suíte completa final: **161 passed in 243.83s**, Windows, Python 3.12.14.
- Ruff, compileall e pip check: aprovados. Mypy ampliado: 15 arquivos.
- Novos testes: 11 de arquivo/proveniência, 12 de ingestão/unidades/concorrência,
  sete E2E de busca/interface, 15 de rótulos científicos e um de escrita atômica.
  Mais três testes de relevância semântica verificam vizinhos fracos,
  paráfrases fortes sem termo literal e evidência com apoio lexical.
- O E2E reextrai todos os 24 documentos novos em diretórios temporários isolados,
  persiste SQLite, indexa e verifica respostas offline, filtros, citações e UI.
- O primeiro passe completo teve 142 aprovados e um problema no diretório
  temporário global de `AppTest.from_string`. O teste passou a usar arquivo
  temporário próprio; o passe intermediário de 158 testes e o passe final de
  161, incluindo a nova proteção semântica, não tiveram falhas.
- A disputa real de escrita entre CLI e bootstrap no Windows foi corrigida
  com trava entre processos, temporários exclusivos curtos e retry limitado
  para compartilhamento de arquivo. Teste com dois processos confirma ausência
  de duplicação; outro confirma publicação de JSON completo entre escritores.
- Código de revisão/impacto consultado antes e depois das alterações. O grafo
  não constitui medida de cobertura: a inspeção direta e os testes novos são
  a evidência para caminhos inicialmente não reconhecidos pelo indexador.

Comando final: `$env:PYTHONUNBUFFERED='1'; $env:RAG_EMBEDDING_MODEL=' ';
$env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1';
.\.venv\Scripts\python.exe -m pytest -q --junitxml=tmp/stage2-junit.xml`.
Logs locais: `tmp/stage2-pytest.log` e `tmp/stage2-junit.xml` (não versionados).

## Navegador e limites da validação

Chromium real via Playwright CLI, instância de QA em `127.0.0.1:8512`, sem
alterar o servidor pré-existente da porta 8501. Confirmados catálogo→explorador,
seleção de PSI-62/117/159, metadados, gráficos dos estudos numéricos, ausência
de gráfico fabricado em PSI-62 e leitura somente. No código final, PSI-117
renderizou dois gráficos, papéis corretos e unidade ausente explicitamente
marcada; zero exceções. Desktop 1280×900 e mobile 390×844 sem overflow
horizontal de página observado. Tab de gráficos ativada por teclado; troca
EN→PT-BR preservou o estudo e os avisos científicos. Console: zero erros.
Imagens locais em `tmp/stage2-desktop-final.png` e `tmp/stage2-mobile-final.png`.

Inspeção visual amostral: apresentação PSI-117 Extinction, página 9, e relatório
final PSI-159, página 23, renderizados por PyMuPDF. Não foi realizada inspeção
visual humana de todas as figuras nem auditoria integral de acessibilidade.
MuPDF emitiu avisos de stitching function durante a extração de alguns PDFs;
texto/páginas foram extraídos e testados, mas isso não certifica todos os gráficos.
Nenhuma figura foi digitalizada para gerar medições exatas. O OCR completo do
desenho SAME anterior continua dependendo de Tesseract.

## Estado dos índices

Índice offline FTS5 + vetores lexicais validado: **11.582 chunks**. O índice
persistente foi depois reconstruído com o modelo multilíngue local já existente:
**15.524 chunks e embeddings de 384 dimensões**, em 122 lotes, sem falhas ou
avisos no resultado de indexação. Modelo `paraphrase-multilingual-MiniLM-L12-v2`,
revisão `e8f8c211226b894fcb81acc59f3b34ba3efd5f42`. FTS5 possui exatamente os
mesmos 15.524 IDs. Os 21 documentos úteis novos estão representados: PSI-62
31 chunks, PSI-117 9.719, PSI-159 3.063. No total, há texto indexado de 36
documentos; os três placeholders e o desenho CAD anterior sem camada textual
não produzem passagens científicas pesquisáveis.

Dois warm starts consecutivos retornaram `ready`, sem nova importação/indexação.
Checkpoint fonte/índice:
`fc4a3fb7fe3761dac1f23a063f7e8477cf2cf433dafd855c46df3874ca5eeecc`.
Resultados locais em `tmp/stage2-semantic-index.json` e
`tmp/stage2-semantic-smoke.json`.

O smoke com embeddings reais recuperou oito evidências válidas para cada novo
estudo, verificando DOI, URL permanente, hash e trecho literal. O filtro de
temperatura de simulação em kelvin também passou. A pergunta sem correspondência
`quasizebraunobtainium` inicialmente produziu vizinhos fracos (cosseno máximo
0,493). A recuperação sem apoio lexical passou a exigir cosseno ≥0,60; o smoke
real então retornou evidência insuficiente, mantendo as consultas científicas.
É um limite conservador de recuperação, não probabilidade de correção nem uma
avaliação exaustiva de relevância. Correspondências literais e paráfrases
semânticas fortes continuam elegíveis.

Nenhum download de modelo ou provedor pago foi necessário. Não foi configurado
ou chamado Gemini nesta etapa. A reconstrução integral dos embeddings/FTS é
uma operação local que pode levar vários minutos; a troca é atômica e mantém
o índice anterior disponível durante a preparação.

## Conclusão e retomada

As 15 instruções da Etapa 2 foram atendidas dentro da disponibilidade real da
NASA. Estado pronto para iniciar a Etapa 3 em uma solicitação posterior.
Registro Git: branch `feat/spaceapps-public-release`, base `5a2c487`, mensagem
`feat(science): integrate PSI-62 PSI-117 and PSI-159 sources`; o identificador
do commit é obtido com `git log -1 --oneline` nesta entrega.

Para executar: `.\.venv\Scripts\python.exe -m streamlit run app.py`.
Os dois SQLite são reconstruíveis e permanecem ignorados pelo Git; originais,
extrações e manifests necessários à inicialização estão versionados. Nenhum
deploy ou push foi realizado. Gemini e documentos finais A–E continuam fora
desta etapa.
