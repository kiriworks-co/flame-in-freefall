# PSI Flame Microgravity

Dashboard científico local em Python e Streamlit. Continua o projeto original: preserva leitores, uploads, tabelas, correções, metadados ISA, gráficos e análises por experimento. Acrescenta catálogo NASA, ingestão rastreável, SQLite, busca híbrida, filtros físicos e assistente com evidências.

O acervo entregue contém **16 arquivos NASA reais**: nove CSVs PSI, cinco PDFs associados a estudos e dois guias oficiais. [URLs, versões, SHA-256 e limitações](docs/DATA_PROVENANCE.md). Fixtures sintéticas existem somente nos testes e são rotuladas.

## Iniciar no Windows

Abra PowerShell na pasta `PROJETO TESTE FLAME MICROGRAVITY`. Para nova instalação, Python 3.11 ou superior:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe scripts/ingest_nasa.py
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8501
```

Acesse [aplicação local](http://127.0.0.1:8501). A interface usa loopback; não há autenticação para exposição pública. Nesta máquina a `.venv` já foi criada com Python **3.12.14** do runtime Codex, pois não havia Python no PATH. Python 3.11 é alvo de compatibilidade, mas não foi executado nesta sessão. `requirements-tested.txt` registra as versões instaladas, inclusive modelos opcionais. Não é preciso ativar a venv; os comandos usam seu executável diretamente.

## Coleta e ingestão NASA

```powershell
.\.venv\Scripts\python.exe scripts/fetch_nasa_resources.py --guide --psi-manual
.\.venv\Scripts\python.exe scripts/fetch_psi_tables.py --ids PSI-25 PSI-26 PSI-68 PSI-69 PSI-98 PSI-99 PSI-100 PSI-101 PSI-102
.\.venv\Scripts\python.exe scripts/fetch_psi_tables.py --ids PSI-69 PSI-25 PSI-102 --pdfs
.\.venv\Scripts\python.exe scripts/ingest_nasa.py
```

Coletores consultam endpoints oficiais públicos, respeitam limites e arquivos restritos, preservam versão/DOI/hashes e não guardam URLs S3 temporárias. Reexecuções não sobrescrevem originais divergentes. Perfil de cobertura: `resources/manifests/data_quality_profile.json`.

A importação é idempotente e tolera falhas por arquivo. Também pode ser iniciada em **Ingestão e fontes**, por worker local com histórico SQLite. Extrações malsucedidas mantêm o original e tornam o job parcial. Jobs abandonados são marcados interrompidos na próxima submissão. Não há download automático ao abrir a interface.

## Interface

- **Visão geral:** cobertura, documentos e prevenção/detecção/supressão.
- **Investigações NASA:** catálogo, DOI confirmado, fonte e importação.
- **Busca e assistente:** consulta PT/EN, FTS5/vetores e filtros tipados por O₂, pressão, velocidade e combustível, com página/linha/hash e original citado.
- **Comparar estudos:** duas ou três tabelas, com bloqueio de comparação quantitativa sem dimensões, métodos e condições compatíveis; relevância explicável para leitura.
- **Arquivos do experimento:** todas as telas originais, uploads, integridade, PDFs, correções e análise exploratória.
- **Revisão visual:** inspeção local de página PDF e adaptador VLM opcional, com consentimento e revisão humana.

Condição, configuração, amostra e resultado reportado são categorias distintas. Uma tabela publicada não equivale a telemetria bruta validada. Não há série temporal completa de sensores nesta seleção. Gráficos e análises não constituem laudo de segurança.

## Embeddings locais

Sem configuração, a busca combina FTS5, vetores **lexicais** e sinônimos PT/EN. Esse modo não é descrito como semântico aprendido e funciona sem internet.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-models.txt
.\.venv\Scripts\python.exe scripts/setup_embeddings.py --configure
.\.venv\Scripts\python.exe scripts/ingest_nasa.py
```

O download explícito usa o cache do usuário fora do repositório, sem chave paga. Registra revisão/licença em `data/embedding_model.json` e caminho em `.env`. Modelo: [paraphrase-multilingual-MiniLM-L12-v2](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2), Apache-2.0. É multilíngue geral; sua precisão científica não foi calibrada. A aplicação só carrega modelos locais, com `trust_remote_code=False`. Chunks respeitam o tokenizer; falhas de modelo preservam a recuperação lexical e avisam sobre reindexação.

## LLM opcional e privacidade

Use `.env.example` como referência e preserve eventual caminho de embedding já configurado em `.env`. Defina `RAG_MODEL`, `RAG_BASE_URL` e, quando necessário, `RAG_API_KEY`. Aceita endpoint OpenAI-compatible HTTPS ou servidor local em loopback. Não há chave incluída nem chamada paga realizada nesta entrega.

O modo padrão recupera evidências e admite insuficiência. O LLM opcional seleciona **trechos literais**, cuja fonte, texto, números e categoria são verificados em código. Paráfrases científicas livres são recusadas; isso reduz a liberdade do resumo para manter verificabilidade. Fontes continuam no idioma original.

Perguntas e documentos são dados não confiáveis. O assistente não executa ferramentas. Somente pergunta e trechos selecionados seguem ao provedor quando o usuário habilita LLM; ambiente, arquivos arbitrários e segredos não entram no prompt.

Para o VLM opcional, configure `VLM_MODEL`, `VLM_BASE_URL` e `VLM_API_KEY`. A página é enviada somente após consentimento explícito. A saída tipada é candidata qualitativa para revisão humana, armazenada em análises separadas; não vira observação científica nem leitura numérica exata. Sem provedor, a prévia local funciona. Nenhuma chamada VLM real foi executada nesta sessão.

## Persistência e unidades

- `data/psi_downloads/`: originais NASA e manifests.
- `resources/official/`: guias oficiais e proveniência.
- `data/experimentos/`: arquivo original/extração JSON por experimento, retrocompatível.
- `data/scientific.sqlite3`: investigações/fontes/versões/páginas/regiões/tabelas/células/observações/jobs/análises.
- `data/search.sqlite3`: chunks, FTS5 e vetores persistentes.

Faça backup conjunto de `data/` e `resources/`. Índices são reconstruíveis; originais são a referência. SHA-256 detecta alteração, não é criptografia nem assinatura.

Pint normaliza apenas unidades documentadas. Pressão sem referência explícita não vira psia; psig exige referência independente para conversão absoluta. Pressão parcial de O₂ é derivação rotulada. Intervalos, incertezas, qualitativos e ausências não viram valores exatos em filtros.

## Testar

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check app.py src scripts tests
.\.venv\Scripts\python.exe -m mypy src/units.py src/scientific_store.py src/comparison.py
.\.venv\Scripts\python.exe -m compileall -q app.py src scripts tests
.\.venv\Scripts\python.exe -m pip check
```

Integrações usam originais NASA em diretórios temporários, sem alterar o acervo principal. [Relatório de testes](docs/TEST_REPORT.md), [roteiro de demonstração](docs/DEMO_SCRIPT.md), [progresso retomável](docs/PROGRESS.md).

## Limitações e licenças

- O PDF de requisitos associado pela NASA a PSI-69 identifica FLEX-2 na capa; há aviso na interface.
- `Burning rate; mm` no FLEX é dimensionalmente ambíguo e não é convertido como taxa.
- O desenho SAME não tem texto extraível. OCR depende do Tesseract e idiomas, não incluídos no Python.
- Apollo 1/13 falharam TLS; não foi desativada validação de certificados.
- Não foram baixados vídeos gigantes, todo o raw nem todas as publicações. Não se contornam acessos restritos.
- A API não declara licença específica por arquivo: preserve NASA/autores e verifique termos e direitos de terceiros antes de redistribuir. Não foi inventada licença para dados ou código original.
- [Uso de IA e limites de validação](docs/AI_USAGE.md).
