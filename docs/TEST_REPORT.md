# Relatório de validação — 15/11/2026

## Resultado verificado

**92 testes passaram**, zero falhas e um aviso de depreciação do alias `fitz` no PyMuPDF. Rodada final do coordenador: **57,80 s**. JUnit: [junit.xml](junit.xml). Ambiente Windows, Python **3.12.14**, Streamlit **1.67.0**; versões instaladas em requirements-tested.txt. Python 3.11 não foi executado.

| Verificação | Resultado |
|---|---|
| pytest completo | 92 passed, 1 FutureWarning |
| Ruff global (app, src, scripts, tests) | All checks passed |
| mypy seletivo em oito módulos | Success: no issues found |
| compileall (app, src, scripts, tests) | exit 0 |
| pip check | No broken requirements found |
| Hash/tamanho dos 16 downloads NASA | todos conferem |
| Hash dos 16 originais arquivados | todos conferem |
| SQLite foreign_key_check | zero violações |
| Streamlit HTTP e navegador Chromium | aplicação funcional no loopback |

Comando da rodada final:

```powershell
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
.venv/Scripts/python.exe -m pytest -q --junitxml=docs/junit.xml
.venv/Scripts/python.exe -m ruff check app.py src scripts tests
.venv/Scripts/python.exe -m mypy src/units.py src/scientific_store.py src/comparison.py src/visual_review.py src/local_jobs.py src/pipeline.py src/retrieval.py src/assistant.py
.venv/Scripts/python.exe -m compileall -q app.py src scripts tests
.venv/Scripts/python.exe -m pip check
```

## Dados reais e cadeia vertical

Os dois comandos de coleta exigidos pela missão foram executados, além da seleção `--pdfs` de PSI-69/25/102. Obtidos **16 arquivos, 7.881.267 bytes**: nove CSVs, cinco PDFs PSI e dois guias oficiais. Fontes, versões e SHA-256 estão em [DATA_PROVENANCE.md](DATA_PROVENANCE.md). Nenhum arquivo veio de outra equipe.

Estado científico persistido: dez investigações (nove PSI e contexto), 16 documentos, 199 páginas, 2.143 regiões, 31 tabelas, 9.967 células e 4.788 observações tipadas. Reexecução NASA: 16 existentes, nenhum novo duplicado e zero erros. Um PDF de desenho permanece com extração parcial, sem camada textual/OCR; não é contado como extração textual completa.

O E2E isolado usa CSV e PDF NASA PSI-69 reais: confere bytes/hash, importa, extrai layout, persiste SQLite, indexa, pergunta, aplica filtros e valida referência/página/linha e renderização PNG. Fixtures são identificadas como sintéticas nos demais testes, sem alimentar o acervo principal.

Uploads locais e reprocessamento também têm jobs reais: testes confirmam idempotência, recarga do manifesto após lock, preservação do original em falha e sincronização com SQLite/índice. Upload sob estudo PSI mantém origem local, sem herdar URL/DOI NASA como fonte.

## Busca, ciência e IA

- FTS5 e vetores lexicais persistentes, filtros AND na mesma linha e equivalência de unidade/referência.
- Unidades: 1 atm absoluto aproximadamente 14,6959 psia; 1 m/s = 100 cm/s; referência psig/psia e pressão parcial derivada; intervalos/qualitativos/ausências não são números exatos.
- Ranking determinístico de relevância, insuficiência de evidências e bloqueio de comparações sem contexto/método compatíveis.
- Grounding: citações externas ao conjunto, paráfrases livres, números e categorias divergentes são rejeitados.
- Modelos indisponíveis preservam busca lexical e avisam sobre reindexação; falha de lote não destrói índice anterior.
- VLM opcional: schema tipado, consentimento, revisão humana, limites e persistência separada; tests de transporte usam mocks sintéticos. Nenhuma chamada real de LLM/VLM foi executada.

**Embedding real validado independentemente:** modelo multilíngue local, 384 dimensões, **2.711 chunks**; todos dentro de 128 tokens incluindo especiais. Seis consultas PT/EN retornaram evidências de PSI-69/25/102; 135 resultados foram conferidos contra quatro originais, sem problemas. Filtro O₂ real e fallback sem modelo funcionaram; clone idempotente alterou zero chunks. Esses checks verificam funcionamento/grounding, não precisão científica geral. Detalhes: [SEMANTIC_VALIDATION.md](SEMANTIC_VALIDATION.md).

## Navegador e acessibilidade

Usado Playwright CLI com Chromium local, sem publicação:

- Abertura do dashboard e das áreas globais; AppTest cobre sete seções e abertura real PSI-69 no catálogo.
- Pergunta `FLEX oxygen` com O₂ entre 0,18 e 0,25 retornou oito linhas reais do CSV PSI-69, com fonte permanente e SHA.
- Download pelo botão da evidência: arquivo `PSI-69_Experimental table_FLEX.csv` idêntico ao original. SHA `37c88ce8ae9391b7544ff630a45ce87543d04d317cdbfbed104fe7d5c27e1b96`.
- Job NASA iniciado pelo botão da interface e acompanhado até `completed`: zero importados, 16 existentes, zero erros, índice semântico com 2.711 chunks e zero recodificações. O histórico real permaneceu no SQLite.
- Teclado: seta no grupo de navegação mudou Busca para Comparar; foco visível confirmado com outline sólido de 3 px após ajuste de especificidade do CSS.
- Desktop 1440 × 1000: largura de página 1440; mobile 375 × 812: largura 375; paisagem 812 × 375: largura 812. Sem overflow horizontal da página nesses checks.
- Escala de fonte raiz a 200% no modo paisagem: largura continuou 812. Redução de movimento habilitada no check mobile.
- Prévia PDF real SAME página física 13 renderizada e inspecionada visualmente, com texto e figura preservados.

Evidências: [desktop](qa-desktop.png), [mobile](qa-mobile.png), [busca](qa-search-desktop.png), [página NASA](qa-source-same-p13.png). Não houve auditoria WCAG completa, leitor de tela, avaliação de todos os gráficos por teclado ou teste de todos os navegadores.

## Correções encontradas na validação

1. API PSI atual usa key/sortingCategory; conector inicial retornava zero CSV.
2. Nomes longos do Windows impediam cópia de alguns originais; arquivos internos compactos preservam nomes completos nos manifests.
3. Cabeçalhos sem unidade válida levantavam exceção Pint; agora ficam explicitamente não resolvidos.
4. Erro de extração podia produzir job concluído; agora preserva original e registra estado parcial.
5. Recorte de subwords podia produzir 129 tokens; agora comprimento é conferido após recorte.
6. Contexto SQLite fazia commit sem fechar conexão; fechamento explícito evita retenção no Windows.
7. Uploads sob PSI poderiam herdar fonte NASA; proveniência local agora impede atribuição.
8. API restrictedAccess também é respeitada, além de restricted/visible.

## Limitações materiais

OCR completo depende do Tesseract e idiomas, ausentes. LLM/VLM reais dependem de configuração/chave e não estão homologados por testes de mocks. Não foram adquiridos todos os vídeos/raw, todas as publicações ou séries temporais completas. Apollo1/13 falharam verificação TLS. Os avisos de Burning rate/mm e PDF FLEX-2 associado a PSI-69 permanecem. Não há validação independente de resultados científicos, certificação de segurança, auditoria completa de dependências nem homologação de exposição pública.

O grafo global foi reconstruído para este checkout (41 arquivos, zero erros de parsing) e usado para impacto. Não há .git próprio; não foi alterado o Git ancestral. Resolução estática de imports do grafo tem limitações no checkout Windows e foi complementada por inspeção direta, type checking e testes de execução.
