# Manual Funcional Completo e Fluxos de Uso (`FEATURES_AND_WORKFLOWS_PTBR.md`)

Este manual descreve todas as funcionalidades efetivamente implementadas na versão final do **Flame in Freefall (`PSI Flame Microgravity`)**, com localização exata na interface, passos de operação, entradas, saídas, relevância científica, limitações, dependência do Gemini e exemplos reproduzíveis com os dados reais da NASA no acervo.

---

## Visão Geral da Navegação e Modos de Operação

Em qualquer tela do aplicativo, o usuário conta com:

- **Barra Contextual Superior (Topo da área principal):**
  - Pílula **Onde você está** (*Where you are*), exibindo a seção ativa e, quando aplicável, o passo atual da Jornada Guiada.
  - Botão **`← Voltar`**: retorna ao passo anterior da jornada, à jornada ativa ou à tela anterior do histórico.
  - Botão **`🏠 Início`**: retorna imediatamente à página inicial (`Home / Overview`) e encerra eventual jornada aberta.
  - **Seletor Único de Idioma (`EN` | `PT-BR`)**: alterna todo o aplicativo entre **Inglês (padrão)** e **Português Brasileiro (`PT-BR`)** preservando estudo selecionado, filtros e histórico sem duplicidade de controles.
  - Botão **`← Voltar à Jornada Guiada (Passo X de 4)`**: aparece automaticamente sempre que você salta de uma Jornada Guiada para o Explorador, Comparador ou Assistente.
- **Barra Lateral (`Navegação`):** dá acesso direto às **7 áreas** (`Início / Visão Geral`, `Investigações`, `Explorador de Dados`, `Comparar`, `Assistente Científico`, `Revisão Visual`, `Fontes e Metodologia`) e ao expander recolhido **Nível de experiência** (`Exploração Guiada` padrão vs. `Pesquisa Avançada`, que expande filtros, diagnósticos e controles avançados por padrão).
- **Modo Público Somente Leitura (`PSI_READONLY_MODE`):** quando implantado em nuvem pública (ex.: Streamlit Community Cloud) ou com `PSI_READONLY_MODE=1`, uploads, criação/edição de experimentos locais e reprocessamento ficam bloqueados automaticamente, mantendo intactos todos os gráficos, comparações, leitores e buscas.

---

## 1. Página Inicial (*Home / Overview*) e *Space Apps Challenge Hub*

- **Propósito:** Explicar em segundos por que o fogo muda em microgravidade, mostrar o escopo real do acervo NASA e oferecer três portas de entrada claras além dos módulos interativos `SUMMARIZE · RANK · INTERPRET`.
- **Localização na interface:** Seção **`Início / Visão Geral`** (`workspace_section = "home"`).
- **Como operar:**
  1. Leia o banner aeroespacial superior com o **diagrama comparativo `Terra (1g)` vs. `Órbita (~0g)`** e observe as **4 métricas reais do acervo** (`12 Estudos NASA PSI`, `40 Originais NASA`, `117 Tabelas Extraídas`, `15.524 Segmentos Pesquisáveis`).
  2. Escolha um dos **3 cartões de entrada principais** (altura uniforme):
     - **Descobrir a Ciência** (*Discover the Science*) → inicia a **Jornada Guiada 1**.
     - **Explorar Segurança contra Incêndio** (*Explore Fire Safety*) → inicia a **Jornada Guiada 2**.
     - **Investigar Dados da NASA** (*Investigate NASA Data*) → abre diretamente o **Explorador de Dados** (com `PSI-69 · FLEX` pré-selecionado).
  3. Logo abaixo, use os botões rápidos **`Ver Todas as 12 Investigações NASA`** ou **`Consultar Assistente Científico Baseado em Evidências`**.
  4. Interaja com as **3 abas do Hub Space Apps (`RESUMIR · RANQUEAR · INTERPRETAR`)**:
     - **Aba `1. RESUMIR Estudo`:** selecione qualquer estudo (ex.: `PSI-69`, `PSI-117`, `PSI-159`) para ver pilar, objetivo científico, quantidade de arquivos/tabelas, papéis de evidência, ressalvas e botão para abrir no Explorador.
     - **Aba `2. RANQUEAR Prioridade`:** escolha o foco (*Prevenção em Habitat*, *Detecção de Fumaça* ou *Supressão de Chamas*) e veja os 4 estudos prioritários com score `0–100` e justificativa explícita.
     - **Aba `3. INTERPRETAR Segurança`:** selecione um estudo para inspecionar três blocos separados: *O que os arquivos contêm*, *Relevância para engenharia espacial* e *Fronteira científica e ressalva*.
  5. Opcionalmente, abra os expanders inferiores (*Terra vs. Microgravidade*, *Termos Científicos*, *Diagnóstico técnico*).
- **Entradas exigidas:** Seleção opcional de estudo ou foco de segurança nas abas do Hub.
- **Saídas produzidas:** Cartões de resumo ancorados nos arquivos, ranking determinístico `0–100`, interpretação delimitada e atalhos com estado preservado.
- **Relevância científica:** Permite comparar imediatamente quais estudos tratam de condições, simulações, metadados ou resultados reportados antes de analisar dados numéricos.
- **Limitações:** O score `0–100` mede relevância documental e cobertura local no acervo — **nunca** representa risco de incêndio nem certificação de segurança.
- **Requer Gemini?** **Não.** Todo o fluxo da página inicial e do Challenge Hub funciona 100% offline.
- **Exemplo reproduzível:** Na aba `1. RESUMIR Estudo`, selecione `PSI-62` — o Hub informa o objetivo de modelagem UFGM e exibe a ressalva explícita de que apenas metadados ISA-Tab e referências bibliográficas estão disponíveis (zero séries numéricas inventadas). Na aba `2. RANQUEAR Prioridade`, escolha *Supressão de Chamas (FLEX / FLEX-2)* para ver `PSI-69` e `PSI-68` no topo com justificativa ponto a ponto.

---

## 2. Jornadas Guiadas 1 e 2 (Experiências em 4 Passos e 5 Perguntas)

- **Propósito:** Conduzir iniciantes, estudantes e jurados passo a passo pela física da combustão espacial e pelos pilares da NASA sem exigir conhecimento prévio.
- **Localização na interface:** Acionadas na Página Inicial pelos cartões **Descobrir a Ciência** (Jornada 1) e **Explorar Segurança contra Incêndio** (Jornada 2).
- **Como operar:**
  1. Navegue pelos **4 passos** usando **`← Voltar`** e **`Continuar →`** (no rodapé ou na barra superior), ou **`Reiniciar Jornada`** / **`Voltar ao Início`**.
  2. Em **cada passo**, consulte o quadro **Guia Estruturado de Descoberta (5 Perguntas-Chave)**: *1. O que estou explorando? · 2. Por que isso importa? · 3. O que a evidência NASA mostra? · 4. O que posso concluir? · 5. Quais são as limitações?*
  3. **Na Jornada 1 (*Entendendo o Fogo em Microgravidade*):**
     - *Passo 1:* alterne o rádio interativo entre 4 efeitos físicos (`Formato da Chama`, `Oxigênio`, `Chamas Quentes vs. Frias`, `Fumaça`).
     - *Passo 2:* observe a ficha do `PSI-69 · FLEX` ao lado da imagem real renderizada da página 36 do `researchers_guide.pdf`.
     - *Passo 3:* alterne o gráfico Plotly real do `PSI-69` entre *Concentração de O₂ vs. Diâmetro da Gota* e *O₂ vs. `'Burning rate; mm'`* (com alerta explícito de unidade) e leia 3 trechos citados da NASA.
     - *Passo 4:* revise descobertas vs. limitações e avance para a Jornada 2, Assistente ou Explorador.
  4. **Na Jornada 2 (*Segurança contra Incêndio em Espaçonaves*):**
     - *Passo 1:* revise os três riscos únicos de cabine orbital.
     - *Passo 2:* alterne entre **Prevenção** (`BASS`, `BASS-II`, `Saffire I–III`, `PSI-62`), **Detecção** (`SAME`, `SAME-R`) e **Supressão** (`FLEX`, `FLEX-2`, `PSI-117`, `PSI-159`), abrindo qualquer estudo no Explorador com retorno garantido.
     - *Passo 3:* examine evidências reais de `PSI-25 · BASS-II` (gráfico O₂% vs CO₂% por material), `PSI-102 · SAME` (página 13 do relatório final + tabela CSV) e o alerta metodológico contra misturar `PSI-25` com `PSI-69`.
     - *Passo 4:* consolide as implicações operacionais e salte para o Comparador, Assistente ou Explorador.
- **Entradas exigidas:** Seleções nos rádios de foco/pilar e botões de navegação.
- **Saídas produzidas:** Imagens reais de PDFs NASA, gráficos Plotly estilizados com caixa *"Como Ler Este Gráfico"*, cartões de trechos verificados com `SHA-256` e sínteses estruturadas.
- **Relevância científica:** Ensina os fundamentos físicos sem perder a distinção entre condições de ensaio, gotas líquidas e materiais sólidos de cabine.
- **Limitações:** As jornadas focam nos estudos introdutórios representativos (`PSI-69`, `PSI-25`, `PSI-102`); para séries CFD detalhadas do `PSI-117` ou relatórios do `PSI-159`, o usuário deve abrir o Explorador ou o Assistente.
- **Requer Gemini?** **Não.** 100% offline.
- **Exemplo reproduzível:** Inicie a Jornada 1 → avance até o Passo 3 → selecione *Verificação de Valor Bruto (`Burning rate; mm`)* → confirme no quadro *"Como Ler Este Gráfico"* o alerta informando que `'Burning rate; mm'` omite unidade de tempo.

---

## 3. Catálogo de Investigações NASA (`Investigations`)

- **Propósito:** Inventário completo e pesquisável das 12 investigações NASA PSI e dos 2 guias oficiais (`NASA-CONTEXT`), com links permanentes oficiais.
- **Localização na interface:** Menu lateral **`Investigações`**.
- **Como operar:**
  1. Digite termos no filtro por palavra-chave (ex.: `cool flame`, `CFI-G`, `smoke`, `UFGM`).
  2. Filtre pelo **Pilar de segurança** (`Todos`, `Prevenção`, `Detecção`, `Supressão`, `Contexto`).
  3. Em cada cartão, consulte o selo de pilar, status de importação, quantidade de documentos, objetivo, relevância, ressalvas documentadas e acesse **`Registro NASA PSI`**, **`DOI confirmado na fonte`** ou **`Abrir no Explorador de Dados`**.
- **Entradas exigidas:** Texto livre opcional e seleção de pilar.
- **Saídas produzidas:** Lista filtrada de cartões com metadados oficiais, links HTTPS validados e atalho direto para o Explorador.
- **Relevância científica:** Preserva nomes oficiais, DOIs e ressalvas de escopo (como `PSI-62` ser apenas metadados) sem alteração.
- **Limitações:** A contagem de documentos inclui arquivos auxiliares preservados (como placeholders ISA `s_PSI-*.txt`, devidamente sinalizados nos manifestos).
- **Requer Gemini?** **Não.**
- **Exemplo reproduzível:** Digite `PSI-117` na busca → veja o selo **Supressão**, DOI `10.60555/gz0q-b577`, 16 documentos e a ressalva sobre preservação separada entre séries `Expt/Sim/Model` → clique em **`Abrir no Explorador de Dados`**.

---

## 4. Explorador de Dados (`Data Explorer`) — 6 Abas

- **Propósito:** Bancada analítica completa para inspecionar estatísticas, gerar gráficos científicos, auditar linhas originais, verificar hashes `SHA-256`, pesquisar em PDFs e ler metadados ISA-Tab de qualquer estudo.
- **Localização na interface:** Menu lateral **`Explorador de Dados`** (estudo padrão inicial: `PSI-69 · FLEX`). Inclui um **Glossário de Variáveis e Unidades** recolhido no topo.
- **Como operar por aba:**
  - **Aba 1 (`Visão Geral e Variáveis`):** exibe contagens de documentos/tabelas/blocos, grandezas identificadas, o gráfico automático **`Visão Visual Inicial`** (com *"Como Ler Este Gráfico"*), **`RESUMO & INTERPRETAÇÃO`** e a tabela de estatísticas descritivas (média, mediana, mín, máx, desvio) exportável em CSV. No modo local (não somente leitura), permite editar descrição ou criar novo experimento local.
  - **Aba 2 (`Gráficos Interativos`):** filtre por documento de origem, selecione um ou mais conjuntos numéricos, confirme ou ajuste **Eixo X**, **Eixo(s) Y**, **Tipo de gráfico** (`Linha`, `Linha com pontos`, `Dispersão`, `Barras`, `Mapa de calor`, `Mapa X–Y–cor`), aplique correções reversíveis (*troca de rótulos*, *% → fração*, *colunas derivadas*), suavização/normalização/escala log, analise ajuste linear (`R²`, inclinação) ou pico/FWHM e exporte dados plotados (CSV), proveniência de transformações (JSON) ou gráfico (HTML).
  - **Aba 3 (`Tabelas e Linhas Originais`):** selecione qualquer bloco extraído, veja origem e papel por coluna, esquema de colunas/unidades, tabela completa com número de linha original e seção de **Referência cruzada** (`Data ID`).
  - **Aba 4 (`Documentos e Integridade`):** lista todos os arquivos do estudo com tamanho, páginas/tabelas e status (`processado` / `parcial`), permite conferir **`Verificar SHA-256`** em tempo real, **`Baixar original NASA/fonte`**, inspecionar metadados, fórmulas e prévia do texto extraído. (Uploads locais e reprocessamento ficam disponíveis apenas fora do modo público `PSI_READONLY_MODE`.)
  - **Aba 5 (`Leitor e Busca em PDFs`):** busque termos em português ou inglês dentro dos PDFs do estudo e clique em **`Abrir página`** para visualizar a renderização fiel da página física do PDF (ou navegue manualmente por número de página).
  - **Aba 6 (`Metadados ISA-Tab`):** exibe estudo, período, submissão, palavras-chave, objetivos, hipóteses, publicações e contatos extraídos de `i_Investigation*.txt` (quando presentes, como em `PSI-62`, `PSI-117` e `PSI-159`).
- **Entradas exigidas:** Seleção do estudo e escolha de dataset/eixos/tabela/página PDF.
- **Saídas produzidas:** Figuras Plotly padronizadas, DataFrames interativos, estatísticas, renderizações PNG de páginas PDF e exportações rastreáveis.
- **Relevância científica:** Bloqueia automaticamente sobreposição em eixo comum quando séries têm grandezas/unidades distintas ou não declaradas (`comparable_plot_axes`), mantendo bases temporais paralelas separadas (`paired_y_columns` em `PSI-117`).
- **Limitações:** `PSI-62` e `NASA-CONTEXT` não possuem séries tabulares numéricas para gráficos; arquivos CAD sem camada textual (`PSI-102` ignitor) dependem de Tesseract externo para busca textual completa.
- **Requer Gemini?** **Não.**
- **Exemplo reproduzível:** Selecione `PSI-117` → na aba **Gráficos Interativos**, escolha `PSI-117_Analyzed Data_MST_2024_Burning_history_Flame_diameter.csv` → confirme que o seletor mantém separados os pares de tempo/diâmetro sem interpolar e exibe o aviso de que previsões numéricas não são medições experimentais. Selecione `PSI-159` → aba **Leitor e Busca em PDFs** → pesquise `n-butane` para abrir páginas do relatório final de 93 páginas.

---

## 5. Comparador de Investigações e Prioridade de Leitura (`Compare`)

- **Propósito:** Auditar se tabelas de 2 ou 3 investigações podem ser comparadas quantitativamente e ranquear estudos por prioridade de leitura em segurança espacial.
- **Localização na interface:** Menu lateral **`Comparar`**.
- **Como operar:**
  1. Clique em um dos **3 atalhos** (*FLEX vs BASS-II*, *SAME vs SAME-R*, *Saffire-I vs Saffire-II*) ou selecione 2 a 3 estudos manualmente.
  2. Escolha qual tabela inspecionar em cada estudo selecionado.
  3. Leia o veredito de compatibilidade (`compare_tables`) e os perfis de colunas lado a lado.
  4. Na seção inferior **Prioridade de Leitura (Não é Ranking de Risco)**, selecione o foco (*Prevenção em Habitat*, *Detecção de Fumaça*, *Supressão de Chamas*), informe palavras-chave (ex.: `cool flame oxygen`) e inspecione os cartões Top 3 e a tabela completa com score `0–100` e justificativa transparente.
- **Entradas exigidas:** 2 ou 3 estudos + tabela por estudo; foco e palavras-chave para ranking.
- **Saídas produzidas:** Diagnóstico booleano de compatibilidade com motivos detalhados, perfil de colunas por tabela e ranking determinístico `0–100`.
- **Relevância científica:** Impede agrupamento indevido entre condições de ensaio, medições, escalas diferentes (gotas vs tecidos) ou pressões sem referência.
- **Limitações:** Mesmo quando grandezas coincidem, a comparação estatística final continua exigindo conferência dos relatórios originais pelo pesquisador.
- **Requer Gemini?** **Não.**
- **Exemplo reproduzível:** Clique no atalho **`FLEX (PSI-69) vs BASS-II (PSI-25)`** → o comparador rejeita a junção quantitativa conjunta e lista as diferenças de escala, condições e metodologia.

---

## 6. Assistente Científico Baseado em Evidências (`Scientific Assistant`)

- **Propósito:** Responder perguntas científicas em Português ou Inglês com passagens literais verificadas do acervo NASA, filtros físicos exatos na mesma linha e síntese opcional pelo Google Gemini com grounding programático.
- **Localização na interface:** Menu lateral **`Assistente Científico`**.
- **Como operar:**
  1. Clique em uma das **5 perguntas prontas** (execução automática imediata) ou digite sua pergunta na caixa de pesquisa.
  2. Opcionalmente, expanda **Filtros avançados, seleção de estudos...** para restringir por estudo (`PSI-XX`), ou expanda **Filtros numéricos e físicos** para filtrar **na mesma linha original**: fração molar de O₂ (`0–1`), pressão absoluta (`psia`), velocidade (`cm/s`) ou combustível.
  3. Se o Google Gemini estiver configurado (`.env` ou Streamlit Secrets), você pode marcar **`Usar LLM externo configurado para seleção literal de trechos`**; caso contrário, o sistema executa em **Modo Evidência Local Verificada**.
  4. Clique em **`Pesquisar Evidências NASA`**.
  5. Inspecione os turnos visuais de chat (`st.chat_message`), o **Guia em Linguagem Simples**, os cartões **RESUMO** e **INTERPRETAÇÃO**, avisos científicos (como presença de simulações ou limite de condições) e cada cartão expansível de evidência com link permanente NASA, DOI, download do original e renderização da página citada do PDF.
- **Entradas exigidas:** Texto da pergunta; filtros opcionais e checkbox opcional do LLM.
- **Saídas produzidas:** Até 8 evidências ranqueadas (SQLite FTS5 + vetores 384D ou lexicais), trechos literais verificados, explicação curta ancorada (quando Gemini ativo) ou mensagem explícita de dados insuficientes (*"Não encontrei dados suficientes nas fontes indexadas"*).
- **Relevância científica:** Toda afirmação exibida pelo LLM passa por `validate_claims()`, exigindo citação conhecida, substring exata na fonte, correspondência numérica e fidelidade de categoria (`condition`, `simulation`, `reported_result`, `metadata`). Uploads locais privados (`local_upload`) são bloqueados antes de qualquer chamada externa.
- **Limitações:** Sem chave Gemini configurada, exibe diretamente as evidências literais e guias locais sem síntese generativa; limiar semântico conservador (`cosseno >= 0,60` quando sem apoio lexical) evita vizinhos espúrios em consultas sem sentido.
- **Requer Gemini?** **Opcional.** O modo offline completo é padrão e preserva 100% da busca e citações; o Gemini acrescenta apenas seleção literal e explicação curta ancorada.
- **Exemplo reproduzível:**
  - Clique no botão **`Condições de O₂ no FLEX (18–25%)`** → confirma `PSI-69`, fração molar de O₂ entre `0.18` e `0.25` na mesma linha e cartões com `DOI`, URL NASA e `SHA-256`.
  - Clique no botão **`Teste de insuficiência de evidências`** (`quasizebraunobtainium unsupported microgravity claim`) → retorna resposta explícita de insuficiência sem inventar texto.
  - Em filtros, selecione apenas `PSI-117` e consulte `"Oscillatory Cool Flame"` → confirma aviso explícito distinguindo séries de simulação numérica de séries experimentais de referência.

---

## 7. Revisão Visual de Páginas (`Visual Page Review`)

- **Propósito:** Inspecionar visualmente diagramas, desenhos de engenharia e gráficos em páginas originais de PDF com renderização local fiel (`PyMuPDF`) e apoio qualitativo VLM opcional estritamente isolado.
- **Localização na interface:** Menu lateral **`Revisão Visual`**.
- **Como operar:**
  1. Use um dos **3 atalhos recomendados** (*SAME Relatório Final · p. 13*, *BASS-II SRD · p. 2*, *Guia de Pesquisa NASA · p. 36*) ou escolha qualquer PDF e número de página física.
  2. Clique em **`Renderizar Página Localmente`** para visualizar a imagem em PNG.
  3. *(Opcional, apenas se um provedor VLM estiver configurado)* Marque o consentimento explícito para enviar **somente aquela página** e solicite candidato de revisão qualitativa, podendo registrar nota de revisão humana.
- **Entradas exigidas:** Seleção de PDF e número de página; consentimento explícito apenas para VLM remoto.
- **Saídas produzidas:** Imagem PNG renderizada localmente; se VLM acionado, candidato JSON marcado como `inference` (`needs_human_review = True`) salvo isoladamente na tabela `analysis_results`.
- **Relevância científica:** Nunca digitaliza valores numéricos exatos de gráficos e nunca escreve observações ou trechos no índice de busca científica.
- **Limitações:** Provedor VLM vem desativado por padrão; a renderização local depende apenas do PyMuPDF embutido.
- **Requer Gemini?** **Não** (usa renderização local; VLM opcional é configurável à parte via `VLM_MODEL`/`VLM_BASE_URL`).
- **Exemplo reproduzível:** Clique em **`Relatório Final SAME · p. 13 (Detector de Fumaça)`** → observe imediatamente a página original renderizada com diagramas do experimento de aerossol de fumaça.

---

## 8. Fontes e Metodologia (`Sources & Methodology`)

- **Propósito:** Documentar a proveniência integral dos dados NASA, regras de normalização dimensional, arquitetura de busca/IA, limitações conhecidas e fornecer inventário completo para conferência e download de todos os 40 documentos.
- **Localização na interface:** Menu lateral **`Fontes e Metodologia`**.
- **Como operar:**
  1. Leia os quatro blocos estruturados (*Origens NASA PSI*, *Extração e Unidades*, *Busca Híbrida e IA*, *Limitações Conhecidas*).
  2. Role até **`Inventário de Arquivos NASA Verificados e Downloads`** para abrir qualquer um dos 40 arquivos, conferir `SHA-256`, JSON completo de proveniência, avisos documentais (como `FLEX-2` sob `PSI-69`) e baixar os bytes originais.
  3. Em execução local (`PSI_READONLY_MODE=0`), o expander **`Sincronização do Acervo e Tarefas em Segundo Plano`** permite reindexar downloads locais sem bloquear a UI; em deploy público (`PSI_READONLY_MODE=1`), exibe apenas aviso de modo somente leitura.
- **Entradas exigidas:** Expansão dos itens de arquivo para auditoria/download.
- **Saídas produzidas:** Metadados completos, hashes `SHA-256`, histórico de jobs SQLite e download dos originais preservados.
- **Relevância científica:** Garante reprodutibilidade completa e transparência de proveniência exigida para revisão científica e julgamento técnico.
- **Limitações:** Em nuvem pública, sincronizações manuais ficam desabilitadas para proteger o acervo inicializado no arranque (*cold-start*).
- **Requer Gemini?** **Não.**
- **Exemplo reproduzível:** Expanda `PSI-69 · PSI-69_Engineering Documents_FLEX Engineering Requirements Document.pdf` para observar o `SHA-256`, o aviso amarelo explicando a divergência de capa (`FLEX-2`) e o botão de download do PDF original.
