# Verificação da publicação assistida — 2026-11-15

Aplicação: https://flame-in-freefall-kiriworks.streamlit.app/ . GitHub: https://github.com/kiriworks-co/flame-in-freefall . O repositório privado foi preservado; a aplicação foi configurada como pública e pesquisável e abriu em navegador separado sem login.

## Código e dados

- Remoto inicialmente vazio. `main` avançou por fast-forward de `880145a` para o commit validado `e8db878`; push atômico de `main` e `feat/spaceapps-public-release`, seguido de confirmação por `ls-remote` e `fetch`.
- A árvore remota inicial continha os mesmos 279 arquivos. Originais NASA, extrações e manifests foram preservados; nenhum índice científico local foi reconstruído. A nuvem inicializou seus próprios bancos SQLite a partir desses arquivos.
- Checagem focada de padrões de credenciais em 279 arquivos atuais e 353 blobs históricos: nenhuma correspondência; `.env` e `.streamlit/secrets.toml` fora do Git. Nenhum blob acima de 95 MiB. Isso não equivale a auditoria exaustiva de segurança ou privacidade.
- `54e518c`: textos de submissão, manual e ajustes documentais. `94b865a`: desempenho de inicialização e indicador visível de preparação.
- O primeiro arranque levou alguns minutos. Foram removidas varreduras repetidas de observações por linha e buscas FTS por IDs novos. A correção preserva categorias e posições da evidência e evita duplicatas FTS.

## Verificação ao vivo executada

| Fluxo | Resultado observado |
|---|---|
| Página inicial sem login | Abriu em navegador separado: 12 PSI, 40 arquivos, 117 tabelas, 11.582 segmentos lexicais; 39 documentos completos, 1 parcial, 0 falhas |
| Idiomas | EN para PT-BR aplicado a navegação e conteúdo; retorno a EN após recarga |
| Catálogo | 12 investigações PSI e um registro NASA-CONTEXT com dois guias; filtro PSI-62 funcional |
| PSI-62 | Explorador e metadados abriram, com avisos de ausência de séries numéricas; não apresenta medições inventadas |
| PSI-117 | 16 documentos, 48 tabelas; gráfico d² versus t renderizado, resultado reportado e simulação diferenciados |
| PSI-159 | 6 documentos, 36 tabelas; prévia gráfica Tad identificada como cálculo derivado |
| Comparador | Preset FLEX/BASS-II mostrou tabelas e bloqueio explícito de combinação quantitativa não validada |
| Busca / RAG sem Gemini | Exemplo FLEX 18–25% recuperou 8 evidências, com linha, categoria, DOI, URL NASA e SHA-256 |
| Página citada | Guia NASA, página física 50, renderizado pelo botão da citação |
| Celular | Viewport 390×844: assistente legível, menu lateral abre e permite navegação; scrollWidth=clientWidth=390 |

A consulta demonstrativa com termos não suportados e a palavra genérica “microgravity” ainda recupera contexto NASA relacionado; isso não estabelece suporte à alegação inventada. Não foi gerada conclusão científica. A precisão/recall do recuperador continua sem avaliação independente.

Durante atualização automática de arquivos Python ocorreu erro transitório de importação (`KeyError` de módulo). Uma recarga completa após a atualização restaurou a aplicação; os fluxos acima foram continuados na versão atualizada. Não foi observado erro crítico persistente nos fluxos verificados. Não foram testadas todas as combinações de gráficos, todos os documentos ou aparelhos físicos.

## Testes desta sessão

`pytest -q tests/test_retrieval.py tests/test_stage2_semantic_guard.py tests/test_assistant.py tests/test_gemini_and_challenge.py`: **33 passed in 12.33s**. Inclui duas regressões novas para alinhamento tabela/linha e ausência de duplicatas FTS em inserções repetidas e atualizações. Ruff dos arquivos alterados e Mypy de `src/retrieval.py` passaram. `git diff --check` passou.

Os **164 testes** são a validação completa registrada na Etapa 3; não foram reexecutados integralmente. A nuvem usa Python 3.11.18 e dependências resolvidas por `requirements.txt`, não uma reprodução integral do ambiente Windows.

## Limites e pendências

- Gemini e VLM reais não configurados nem testados com API; aplicação publicada usa evidências locais verificáveis.
- O arquivo CAD PSI-102 permanece parcial, sem camada de texto; o original está preservado e a limitação é anterior ao deploy.
- Revisão científica independente e submissão final no portal Space Apps não foram executadas pelo agente. O rascunho autoral foi excluído desta tarefa por instrução do proprietário.
- Nenhum arquivo LICENSE de software foi encontrado. Não foi atribuída licença nova ao código ou aos dados NASA; atribuições e ressalvas de terceiros permanecem em DATA_PROVENANCE.md.
- O código GitHub privado exige acesso concedido pelo proprietário para revisão; a URL da aplicação é pública. GitHub Pages não foi ativado.
