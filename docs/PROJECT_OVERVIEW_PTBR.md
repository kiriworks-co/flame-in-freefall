# Visão Geral do Projeto — Flame in Freefall (`PSI Flame Microgravity`)

**Desafio:** NASA Space Apps Challenge 2026 — *Flame in Freefall*  
**Idioma da Interface:** Inglês (padrão) e Português Brasileiro (`PT-BR`)  
**Fonte Primária de Dados:** Repositório NASA Physical Sciences Informatics (`https://psi.nasa.gov/physci/repo/search?q=combustion`)

---

## 1. O que é o Flame in Freefall

O **Flame in Freefall** (`PSI Flame Microgravity`) é um ambiente web científico interativo desenvolvido em Python e Streamlit para explorar, auditar, comparar e consultar investigações reais da NASA sobre **combustão em microgravidade** e **segurança contra incêndio em espaçonaves**.

Em vez de tratar dados espaciais como uma caixa-preta ou gerar resumos artificiais sem fonte, o aplicativo preserva os arquivos originais públicos do repositório **NASA Physical Sciences Informatics (PSI)** com assinatura criptográfica (`SHA-256`), classifica rigorosamente cada coluna e trecho conforme sua natureza científica e transforma conjuntos heterogêneos em jornadas guiadas acessíveis, gráficos interativos, matrizes de compatibilidade e um assistente de pesquisa ancorado em evidências verificáveis.

---

## 2. Qual problema o aplicativo resolve

Os dados experimentais e computacionais públicos da NASA no repositório PSI são extraordinariamente valiosos, porém estão fragmentados em dezenas de planilhas CSV com codificações diversas (`utf-8-sig`, `cp1252`), arquivos XLSX com notas heterogêneas, relatórios científicos extensos em PDF, apresentações técnicas, arquivos de metadados ISA-Tab e documentos de requisitos de engenharia.

Sem uma camada rigorosa de engenharia de dados científicos, pesquisadores, estudantes e jurados enfrentam quatro obstáculos recorrentes:

1. **Mistura de categorias incompatíveis:** tabelas de **condições planejadas de ensaio** (concentração de O₂, pressão de câmara, combustível) são frequentemente confundidas com **medições de resultado**, **previsões de simulação CFD** ou **metadados bibliográficos**.
2. **Inconsistência dimensional e unidades ambíguas:** parâmetros aparecem em `psia`, `psig`, `mmHg`, `cm/s`, fração molar, `% by vol` ou com cabeçalhos incompletos (como `Burning rate; mm` no estudo `PSI-69`, que omite unidade temporal), tornando perigosa qualquer conversão automática cega.
3. **Barreira de acesso para não especialistas:** arquivos brutos do PSI exigem conhecimento prévio da física de microgravidade e dos acrônimos de missão (`BASS`, `FLEX`, `SAME`, `Saffire`, `ACME CFI-G`) para que o usuário entenda o que está observando.
4. **Risco de alucinação por IA genérica:** ferramentas convencionais de chat resumem PDFs ou misturam estudos distintos sem verificar se números, unidades ou citações correspondem de fato ao documento citado.

O **Flame in Freefall** resolve esses problemas ao reunir **12 investigações prioritárias do NASA PSI** e **2 guias oficiais da NASA** em um único sistema auditável onde toda visualização, comparação e resposta aponta para o arquivo original, página ou linha, DOI confirmado e hash `SHA-256`.

---

## 3. Relação com o NASA Space Apps Challenge 2026

O aplicativo endereça diretamente os objetivos do desafio **Flame in Freefall** do NASA Space Apps Challenge 2026, estruturando a experiência em torno das três competências centrais pedidas pelo desafio e expostas na página inicial (*Space Apps Challenge Hub*):

- **SUMMARIZE (Resumir):** sintetiza objetivos, cobertura documental, tipos de evidência e ressalvas documentadas de cada investigação NASA PSI a partir de arquivos reais preservados.
- **RANK (Ranqueamento de Prioridade de Leitura):** calcula um score determinístico e explicável (`0–100`) para orientar **qual estudo ler primeiro** em três frentes de segurança espacial (Prevenção em Habitat, Detecção de Fumaça e Supressão de Chamas) — deixando explícito que prioridade de leitura **não** é um índice de risco de incêndio ou de inflamabilidade de materiais.
- **INTERPRET (Interpretar):** separa de forma transparente o que os arquivos realmente contêm (condições, resultados reportados, simulações ou metadados), a implicação potencial para engenharia aeroespacial e as fronteiras científicas que impedem extrapolações indevidas.

---

## 4. Por que a combustão em microgravidade importa

Na Terra (`1g`), os gases quentes gerados por uma chama são menos densos que o ar frio ao redor. A gravidade puxa o ar frio para baixo e empurra os gases quentes para cima, criando o **empuxo (convecção natural)**. Esse fluxo ascendente alonga a chama no formato familiar de gota amarela, renova continuamente o oxigênio na base do fogo e leva a fumaça rapidamente até detectores instalados no teto.

Dentro de uma espaçonave em órbita (`~0g`, queda livre contínua), astronautas, equipamentos e o ar da cabine caem juntos ao redor da Terra — **o empuxo praticamente desaparece**. Como consequência:

- **Chamas esféricas:** sem direção "para cima", o calor e os reagentes difundem-se simetricamente ao redor do combustível, formando chamas esféricas azuladas e discretas.
- **Transporte lento por difusão e ventilação:** o oxigênio chega ao fogo apenas por difusão molecular ou pelo escoamento suave dos ventiladores de cabine, alterando drasticamente taxas de queima e limites de extinção.
- **Chamas frias (*cool flames*):** em ensaios com gotas e gases (como `FLEX` e `ACME CFI-G`), após a extinção da chama quente visível, reações químicas em baixa temperatura podem continuar ocorrendo e liberar calor residual ou risco de reignição.
- **Aerossóis de fumaça em suspensão:** sem corrente ascendente para o teto, partículas de fuligem permanecem em suspensão, coalescem em tamanhos diferentes dos observados em `1g` e acompanham o fluxo de ventilação, exigindo detectores calibrados especificamente para o ambiente espacial (`SAME` e `SAME-R`).

---

## 5. Público-alvo

A interface foi projetada com divulgação progressiva para atender dois perfis principais sem sacrificar o rigor técnico:

1. **Avaliadores, estudantes e público geral (Modo *Exploração Guiada* — padrão):** acessam imediatamente o diagrama visual `1g vs. 0g`, métricas verificadas do acervo, as duas Jornadas Guiadas de 4 passos estruturadas no modelo das **5 Perguntas Científicas** (*O que estou explorando? · Por que importa? · O que a evidência NASA mostra? · O que posso concluir? · Quais são as limitações?*) e o Hub `SUMMARIZE · RANK · INTERPRET`.
2. **Pesquisadores, engenheiros e analistas de dados (Modo *Pesquisa Avançada*):** exploram diretamente os 6 painéis do Explorador de Dados, tabelas originais com número de linha, ajustes reversíveis de coluna, análises de séries, leitor de PDF página a página, comparador de compatibilidade dimensional e filtros numéricos alinhados por linha no Assistente Científico.

---

## 6. Como o sistema funciona conceitualmente

O fluxo completo de dados segue sete etapas auditáveis:

1. **Coleta e Verificação de Originais:** scripts dedicados consultam os endpoints públicos Geode da NASA PSI e documentos oficiais, registrando versão do estudo, DOI oficial, URL permanente, tamanho e `SHA-256` (sem persistir URLs assinadas S3 temporárias).
2. **Preservação Imutável:** os bytes originais ficam intactos em `data/psi_downloads/` e são espelhados por investigação em `data/experimentos/` com trava contra gravação concorrente e escrita atômica.
3. **Extração Estruturada e Classificação por Papel Científico:** CSVs, XLSX, PDFs e arquivos ISA-Tab (`i_Investigation*.txt`) são extraídos localmente (PyMuPDF, pandas/openpyxl). Cada coluna e tabela recebe classificação explícita (`condition`, `reported_result`, `simulation`, `derived`, `metadata`, `engineering_or_publication`, `context`, `identifier_or_unclassified`).
4. **Normalização Conservadora de Unidades:** o módulo `Pint` converte apenas unidades explícitas (`1 atm = 14,6959 psia`, `1 m/s = 100 cm/s`, `°C → K`, `% O₂ → fração molar`). Pressões em `psig`, `mmHg` ou `psi` sem referência absoluta explícita nunca são convertidas silenciosamente para `psia`, e `Burning rate; mm` permanece bruto com alerta.
5. **Persistência Relacional e Busca Híbrida:** metadados, páginas, tabelas e observações tipadas alimentam `data/scientific.sqlite3`. Trechos estruturais de texto e linhas tabulares formam o índice `data/search.sqlite3` combinando busca lexical **SQLite FTS5** com vetores semânticos locais de **384 dimensões** (`paraphrase-multilingual-MiniLM-L12-v2`) — com fallback 100% determinístico para vetores lexicais PT/EN caso nenhum modelo de embeddings esteja carregado.
6. **Grounding Programático e IA Opcional:** todas as perguntas de pesquisa recuperam primeiro evidências reais do índice híbrido. Se o proprietário ativar o provedor opcional Google Gemini (`gemini-2.5-flash`), o modelo atua apenas sobre passagens públicas da NASA e passa por validação em código (`validate_claims()`), que rejeita qualquer número, categoria ou citação não comprovada na fonte.
7. **Interface Bilíngue e Modo Público Seguro:** o app em Streamlit inicia automaticamente em modo somente leitura quando implantado em nuvem pública (`PSI_READONLY_MODE`), ocultando uploads/edições locais e mantendo a navegação entre Inglês (padrão) e Português Brasileiro (`PT-BR`).

---

## 7. Investigações NASA incluídas

O acervo reúne **12 investigações reais do NASA PSI** organizadas nos três pilares de segurança espacial, além de um registro dedicado para os **2 guias oficiais da NASA (`NASA-CONTEXT`)**:

| ID NASA | Título / Campanha | Pilar | DOI Confirmado | Natureza Principal dos Dados no Acervo |
|---|---|---|---|---|
| **PSI-25** | BASS-II (*Burning and Suppression of Solids II*) | Prevenção | `10.60555/4qc4-de67` | SRD (16 p.), CSV experimental (condições e gases finais reportados) e proofsheet em PDF |
| **PSI-26** | BASS (*Burning and Suppression of Solids*) | Prevenção | `10.60555/58h4-dy80` | CSV catálogo de ensaios/amostras de combustão de sólidos |
| **PSI-62** | UFGM (*Concurrent Flame Spread Modeling*) | Prevenção | `10.60555/e9xp-ex83` | **Somente metadados ISA-Tab** e referências bibliográficas (sem séries numéricas ou saídas CFD públicas) |
| **PSI-68** | FLEX-2 (*Flame Extinguishment Experiment 2*) | Supressão | `10.60555/byp8-h018` | CSV de condições experimentais e intervalos operacionais |
| **PSI-69** | FLEX (*Flame Extinguishment Experiment*) | Supressão | `10.60555/mbq8-0451` | CSV experimental (condições e diâmetros de extinção reportados, além do cabeçalho ambíguo `Burning rate; mm`) e PDF de requisitos (capa FLEX-2 sinalizada) |
| **PSI-98** | Saffire-I (*Spacecraft Fire Experiment I*) | Prevenção | `10.60555/0t15-1z43` | CSV resumo de 4 linhas em escala de nave Cygnus (com lacunas parciais de unidade) |
| **PSI-99** | Saffire-II (*Spacecraft Fire Experiment II*) | Prevenção | `10.60555/2chp-m469` | CSV resumo de 9 amostras de materiais em voo orbital |
| **PSI-100** | Saffire-III (*Spacecraft Fire Experiment III*) | Prevenção | `10.60555/040q-4h36` | CSV resumo de 2 linhas sob maior velocidade de ventilação (unidades ausentes preservadas) |
| **PSI-101** | SAME-R (*Smoke Aerosol Measurement Experiment - Reflight*) | Detecção | `10.60555/2np7-jv14` | CSV de configurações de amostra, fluxo, envelhecimento e taxa declarada de perda de massa |
| **PSI-102** | SAME (*Smoke Aerosol Measurement Experiment*) | Detecção | `10.60555/gd4k-8h62` | Relatório científico final (68 p.), CSV de ensaios e desenho CAD do ignitor (1 p. sem camada textual) |
| **PSI-117** | *Cool Flame Dynamics (CFD / FLEX comparison)* | Supressão | `10.60555/gz0q-b577` | 9 CSVs com séries CFD e experimentais de referência identificadas separadamente, 4 apresentações em PDF, ReadMe XLSX e metadados ISA |
| **PSI-159** | ACME CFI-G (*Cool Flames Investigation with Gases*) | Supressão | `10.60555/cyt1-kh64` | 2 relatórios/PDFs (engenharia e relatório final de 93 p.), 2 CSVs (*Normal* e *Inverse Flames* com condições, cálculos `Tad`/`Zst` e resultados reportados) e metadados ISA |
| **NASA-CONTEXT** | Guias Oficiais NASA | Contexto | — | *A Researcher's Guide to ISS Combustion Science* e *Complete PSI Database Guide* (contexto teórico/metodológico separado de dados empíricos) |

---

## 8. Inventário verificado dos dados processados

Os números abaixo foram auditados diretamente no banco `data/scientific.sqlite3` e no índice `data/search.sqlite3` do repositório:

- **13 registros de investigação no banco:** 12 estudos `PSI-XX` + 1 registro `NASA-CONTEXT`.
- **40 documentos preservados (82.099.713 bytes originais):** 37 documentos com conteúdo científico ou documental útil e **3 arquivos placeholders ISA-Tab** (`s_PSI-62.txt`, `s_PSI-117.txt`, `s_PSI-159.txt`, de 56 bytes com o texto `"Do not use this"`), preservados apenas como metadados de arquivo e explicitamente excluídos de interpretações científicas. Dos 40 documentos, 39 possuem status `processado` e 1 possui status `parcial` (desenho CAD do `PSI-102` sem camada OCR).
- **566 páginas/seções** persistidas no banco relacional.
- **117 tabelas extraídas** (incluindo tabelas de CSV, planilhas, blocos de PDF e tabelas bibliográficas/de contato ISA) somando **10.114 linhas tabulares** (das quais 8.966 vêm de CSVs).
- **26.803 registros tipados na tabela `observations`:**
  - `simulation`: 16.081 registros
  - `reported_result`: 5.302 registros
  - `condition`: 3.472 registros
  - `identifier_or_unclassified`: 1.088 registros
  - `engineering_or_publication`: 495 registros
  - `derived`: 333 registros
  - `metadata`: 27 registros
  - `context`: 5 registros
  - **Nota científica essencial:** esses **26.803 registros tipados não equivalem a 26.803 experimentos independentes**, pois representam células e valores individuais extraídos de linhas tabulares, simulações CFD, parâmetros de configuração e metadados.
- **15.524 passagens pesquisáveis** no índice persistente (`chunks` e `chunks_fts`) com embeddings locais de **384 dimensões** (`paraphrase-multilingual-MiniLM-L12-v2`). Em instalações enxutas na nuvem sem pesos semânticos, o sistema reconstrói automaticamente o índice offline determinístico com vetores lexicais PT/EN.

---

## 9. O que o diferencia de um arquivo científico tradicional

| Aspecto | Repositório Científico Tradicional | Flame in Freefall |
|---|---|---|
| **Formato de consumo** | Download manual de dezenas de CSVs, XLSX e PDFs isolados | Explorador unificado, gráficos Plotly, leitor de PDF integrado e busca transversal |
| **Rastreabilidade** | Arquivos soltos após o download | `SHA-256`, DOI confirmado, URL permanente e número exato de página/linha em toda exibição |
| **Rigor de categorias** | Usuário precisa deduzir se uma coluna é entrada ou medição | Colunas e passagens rotuladas em código (`condition`, `reported_result`, `simulation`, `derived`, `metadata`) |
| **Tratamento de unidades** | Conversões manuais propensas a erro (`psig` vs `psia`, `%` vs fração) | Conversão conservadora via `Pint` que recusa inferir referências ou unidades ausentes |
| **Comparação entre estudos** | Risco de sobrepor séries incompatíveis no mesmo gráfico | Bloqueio programático de eixos/unidades incompatíveis e auditoria prévia de compatibilidade |
| **Acessibilidade** | Jargão técnico imediato | Jornadas Guiadas de 4 passos, modelo das 5 Perguntas, glossário e interface bilíngue EN/PT-BR |

---

## 10. O que a Inteligência Artificial realmente faz (e não faz)

- **Recuperação Offline (sem LLM externo):** a busca híbrida (`FTS5` + embeddings locais de 384 dimensões ou vetores lexicais) e os filtros numéricos por linha operam **100% localmente** e produzem citações verificáveis mesmo sem nenhuma chave de API.
- **Google Gemini Opcional (`gemini-2.5-flash`):** quando configurado pelo proprietário, recebe exclusivamente passagens públicas da NASA (uploads privados locais marcados como `local_upload` são bloqueados por código via `filter_public_nasa_evidence`) e atua apenas para selecionar trechos literais relevantes e redigir uma explicação curta de uma frase ancorada nos números da fonte.
- **Grounding Programático (`validate_claims`):** toda saída do LLM é verificada em Python antes de chegar à tela. Trechos que não aparecem palavra por palavra no documento recuperado, números não encontrados na fonte, paráfrases livres ou tentativas de promover uma condição/simulação a medição ou certificação de segurança são automaticamente rejeitados.
- **Revisão Visual Opcional (VLM):** ao inspecionar páginas de PDF, um usuário pode opcionalmente enviar apenas a página escolhida (mediante consentimento explícito e provedor configurado); qualquer retorno fica isolado na tabela `analysis_results` como `inference` (`needs_human_review = True`) e **nunca** cria medições numéricas nem entra no índice de busca.

---

## 11. Limitações importantes

1. **Não substitui validação científica independente nem certificação aeroespacial:** nenhum gráfico, cálculo derivado, score de prioridade de leitura (`0–100`) ou resumo do sistema atesta segurança contra incêndio ou inflamabilidade de materiais em voo.
2. **Escopo do acervo coletado:** não foram baixados vídeos experimentais brutos, arquivos de telemetria de alta frequência em escala de gigabytes ou imagens brutas completas; o acervo contém tabelas experimentais/analisadas, apresentações, documentos de engenharia, relatórios finais e metadados disponíveis publicamente no NASA PSI.
3. **Lacunas documentadas nos originais da NASA:**
   - `PSI-62` possui somente metadados ISA-Tab públicos nesta coleta (nenhuma série numérica).
   - `PSI-69` traz a coluna `Burning rate; mm` sem unidade temporal e associa um PDF cuja capa identifica `FLEX-2` — ambos sinalizados na interface.
   - `PSI-102` inclui um desenho CAD de 1 página sem camada textual extraível (OCR completo depende de Tesseract externo).
   - `PSI-117` contém convenções ambíguas no `ReadMe` e gráficos em apresentações que não são digitalizados automaticamente como valores exatos.
   - Os arquivos `s_PSI-62.txt`, `s_PSI-117.txt` e `s_PSI-159.txt` são placeholders ISA sem dados experimentais.
4. **Provedores externos opcionais:** o Google Gemini está implementado, protegido e validado em código e testes unitários/integrados com mocks HTTP, mas permanece **não configurado localmente** enquanto o proprietário não inserir sua chave pessoal da Google AI Studio em `.env` ou nos Secrets do Streamlit Community Cloud.
5. **Revisão científica independente pendente:** a revisão científica humana pelo proprietário ocorrerá após esta entrega de engenharia.
