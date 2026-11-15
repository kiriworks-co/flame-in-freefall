# Revisão da interface — 15/11/2026

Escopo: novas áreas globais em `src/scientific_ui.py`, integradas ao Streamlit existente. Nenhum leitor, gráfico, upload ou análise anterior foi removido.

## Implementado e revisado

- Navegação global: visão geral, catálogo NASA, busca/assistente, comparação, ingestão/fontes e acesso aos arquivos do experimento.
- Catálogo usa IDs humanos PSI, DOI confirmado no manifesto NASA e contagem dos documentos realmente arquivados. DOI candidato continua explicitamente não confirmado quando não há evidência da fonte.
- Ranking recebe a cobertura real de documentos locais; score continua sendo relevância de investigação, nunca risco de material.
- Links externos usam o mesmo validador de referências do RAG: HTTPS, sem credenciais e sem parâmetros de URL assinada. Conteúdo de evidência é exibido como texto inerte.
- Resposta do assistente usa Markdown escapado pelo código de grounding, sem habilitar HTML externo. Os originais citados permanecem disponíveis para download e a página PDF pode ser renderizada.
- Avisos por campo publicados nos manifests são apresentados com o documento. A divergência entre associação PSI-69 e capa FLEX-2 do PDF de requisitos é explícita.
- A interface identifica o modo lexical ou o modo com embeddings semânticos locais. Pesos locais são reutilizados entre reruns, sem cache das respostas.
- Resultados da última pergunta mantêm consulta e escopo visíveis. Validação de intervalos aplica-se aos filtros habilitados.
- Monitor de jobs usa `progress` e `result_json`, correspondendo ao schema real do SQLite. Erros de leitura de originais são recuperáveis pela interface.
- Uso de controles nativos Streamlit com rótulos visíveis, texto de status, foco visível e áreas de ação de pelo menos 44 CSS px. Tabelas continuam usando o componente rolável nativo; não foi criada tabela de largura fixa.
- CSS estático para largura máxima, números tabulares, quebras de URLs e adaptação dos recuos em telas pequenas. Sem dados externos interpolados em HTML.

## Validação executada

`python -m pytest tests/test_ui_details.py tests/test_app.py -q`: **16 passed**, um aviso de depreciação de `fitz`. Inclui:

- carregamento das seis áreas globais;
- submissão da pergunta e renderização da seção de resposta/evidências;
- abertura real de PSI-69 pelo catálogo, preservando seleção de estudo e navegação para os leitores existentes;
- recusa de URLs executáveis, com credenciais, assinadas ou HTTP;
- cobertura real no catálogo e avisos de proveniência.

`python -m ruff check src/scientific_ui.py tests/test_ui_details.py --output-format concise`: **All checks passed**.

Índice global code-review-graph reconstruído para incluir os novos módulos: 32 arquivos, sem erro de parsing; consulta de impacto complementada por inspeção direta de app, pipeline e RAG.

Skills consultadas: ui-ux-pro-max (consulta específica para tabelas em telas pequenas), redesign-existing-projects, web-design-guidelines e playwright-cli. Fonte de revisão: [Web Interface Guidelines](https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md).

## Limites desta revisão

AppTest verifica o runtime Streamlit e as interações declaradas; não demonstra geometria real, contraste de todos os componentes, navegação completa por teclado ou comportamento de leitor de tela. A validação de navegador desktop/mobile pertence ao coordenador e deve ser registrada separadamente. Não houve alegação de auditoria WCAG completa. O tema atual é claro; modo escuro não foi validado.

## Complemento — revisão visual opcional

A seção **Revisão visual** permite selecionar um PDF original, conferir SHA-256 e página e renderizar a imagem localmente. O adaptador `src/visual_review.py` aceita provedor compatível com Chat Completions multimodal por `VLM_BASE_URL`, `VLM_MODEL` e `VLM_API_KEY`. Sem configuração, a inspeção local continua e o botão remoto fica indisponível. A página só é enviada após seleção explícita do usuário; não há chamada automática ao navegar.

O resultado é uma dataclass com hash, página, descrição qualitativa, regiões com caixas normalizadas, texto candidato, inferência e necessidade de revisão humana. Chaves de medições e números em descrições/inferências são rejeitados. Candidatos de rótulos podem conter números não verificados e são exibidos com esse aviso. Não se escrevem observações científicas, chunks ou resultados medidos. Somente a tabela `analysis_results`, com tipo `visual_review`, recebe o candidato e o comentário de revisão humana. Esse comentário não promove a interpretação a dado primário.

O schema rejeita citações a outro hash/página, regiões inválidas, NaN, HTML, controle de caracteres e conteúdo fora dos limites. Transporte usa HTTPS, exceto loopback HTTP local, e recusa redirecionamentos. Limites: PDF 25 MiB, PNG 6 MiB, resposta 128 KiB, página até 500, renderização até seis milhões de pixels; timeout de provedor 40 segundos. Credenciais nunca entram no prompt e mensagens de falha não incluem o corpo do provedor ou a string da exceção.

`python -m pytest tests/test_visual_review.py tests/test_ui_details.py -q`: **27 passed**, um aviso de depreciação de `fitz` (18 testes VLM e nove testes de detalhes UI). Respostas de provedor são **mocks sintéticos explicitamente rotulados**, não resultados de um VLM real. O teste local renderiza um PDF de fixture sintética, valida hash/página, verifica consentimento/modo indisponível, schema, redaction, transporte limitado, persistência separada e abertura da nova seção sem provedor.

`python -m ruff check src/visual_review.py src/scientific_ui.py tests/test_visual_review.py tests/test_ui_details.py --output-format concise`: **All checks passed**. `python -m mypy src/visual_review.py --ignore-missing-imports --follow-imports silent`: **Success: no issues found in 1 source file**.

**Limitação:** não houve chamada a provedor VLM real nem avaliação de acurácia de interpretação visual; faltam configuração/chave explícitas. Esta função não digitaliza séries nem lê valores exatos de gráficos. A revisão da imagem original pelo usuário continua necessária.

Complementos de acessibilidade: subseções globais usam títulos h2; cartões de investigação ficam sob título h2 pai. Os rótulos de evidência incluem resultado reportado e cálculo derivado. O modo exato do índice está visível na busca. Contraste calculado das cores básicas do tema: acento/branco 6,12:1, texto/fundo 13,68:1, acento/fundo 5,85:1; isso não representa auditoria de todos os componentes.
