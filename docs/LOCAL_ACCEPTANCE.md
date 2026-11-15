# Guia de Aceitação Local (`LOCAL_ACCEPTANCE.md`) — Em Português Simples

Este guia permite que você mesmo(a) abra, navegue e aprove a versão final do **Flame in Freefall (`PSI Flame Microgravity`)** no seu computador **antes** de enviar para o GitHub ou publicar no Streamlit Community Cloud.

---

## 1. Como abrir o aplicativo no seu computador

Abra o terminal (PowerShell) dentro da pasta do projeto e execute:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8511 --server.address 127.0.0.1
```

Depois abra no navegador o endereço: `http://127.0.0.1:8511`

> *(Dica: o próprio terminal também mostra o link local assim que o servidor iniciar. Para encerrar depois de testar, pressione `Ctrl + C` no terminal.)*

---

## 2. Roteiro rápido de conferência (5 a 10 minutos)

### A. Primeira impressão e barra superior (10 segundos)
1. Confirme que a página abre em **inglês por padrão** com o título **`Explore the Science of Fire in Space`** e o subtítulo explicando fogo em microgravidade.
2. Observe a barra superior de contexto:
   - Mostra **Onde você está** (`Where you are: Home / Overview`)
   - Botões claros **`← Back`** e **`🏠 Home`**
   - Botão rápido **`Language: EN → PT-BR`**
3. No menu lateral à esquerda, confira que o seletor segmentado **`Language: [EN | PT-BR]`** também funciona sem reiniciar seus filtros e sem mostrar menu de desenvolvedor (`Deploy`).
4. Clique para trocar **EN → PT-BR → EN** e confirme que toda a interface alterna suavemente sem mensagens de erro vermelhas.

### B. Os 3 caminhos iniciais + Hub do Desafio (`SUMMARIZE · RANK · INTERPRET`)
1. Na tela inicial, confira os **3 cartões principais**:
   - **Discover Fire in Microgravity** (Jornada Guiada 1 — iniciantes)
   - **Explore Spacecraft Fire Safety** (Jornada Guiada 2 — prevenção, detecção e supressão)
   - **Scientific Research Tools** (acesso direto aos módulos avançados)
2. Role logo abaixo até o painel interativo **`SUMMARIZE · RANK · INTERPRET`**:
   - Na aba **Summarize**, escolha estudos (ex.: `PSI-69 · FLEX`) e veja o resumo estruturado + aviso científico preservado (`FLEX-2` / `Burning rate; mm`).
   - Na aba **Rank**, alterne entre *Crew Habitat & Materials*, *Smoke & Fire Detection* e *Fire Suppression* e verifique o placar explicável `0–100` (deixando claro que é prioridade de leitura, não risco real de incêndio).
   - Na aba **Interpret**, confira a leitura aplicada para espaçonaves e limites científicos.

### C. Jornadas Guiadas com as 5 Perguntas Científicas
1. Clique em **Start Guided Journey** no primeiro cartão.
2. Em cada passo (**Step 1 of 4** até **Step 4 of 4**), verifique se aparece o quadro com as **5 Perguntas Científicas**:
   - *O que estou explorando?* (*What am I exploring?*)
   - *Por que isso importa?* (*Why does it matter?*)
   - *O que as evidências da NASA mostram?* (*What does the NASA evidence show?*)
   - *O que posso concluir?* (*What can I conclude?*)
   - *Quais são as limitações?* (*What are the limitations?*)
3. Avance até o gráfico interativo (Passo 3) e confirme a prévia da página PDF da NASA, os gráficos Plotly e o texto explicativo **"How to Read This Chart"**.
4. Clique em um atalho avançado e confirme que o botão **`← Return to Guided Journey`** aparece para trazê-lo de volta onde parou.

### D. Explorador de Dados, Comparador e Assistente Científico
1. Abra **Data Explorer**: confirme que na própria aba **Overview & Variables** já existe uma visualização gráfica imediata (**Visual First Look**) + painel **SUMMARIZE & INTERPRET** antes de tabelas densas.
2. Abra **Compare Studies**: confira o guia metodológico e a tabela/gráfico de prioridade `0–100`.
3. Abra **Scientific Assistant**:
   - Clique em uma das perguntas prontas para ver a execução imediata no formato conversacional (balão de pergunta + resposta com guia em linguagem simples + citações verificáveis NASA).
   - Confira o selo do **Google Gemini**: se nenhuma chave `GEMINI_API_KEY` estiver configurada no `.env`, o sistema informará de forma transparente que está operando no modo **somente citações locais offline** (sem inventar respostas).

### E. Celular e acessibilidade visual
1. Reduza a janela do navegador para largura estreita (ou use `F12` no navegador em modo celular `375px`):
   - Confira que o menu lateral recolhe automaticamente para não cobrir o título inicial.
   - Confira que cartões, botões e gráficos empilham verticalmente sem cortes nem barra de rolagem horizontal.

---

## 3. Como ativar o Google Gemini (opcional)

O aplicativo funciona 100% gratuitamente **sem nenhuma chave de API** usando busca híbrida local e respostas por evidências diretas da NASA.  
Se quiser testar síntese assistida por IA via Gemini localmente (mantendo validação rigorosa palavra-por-palavra):
1. Crie/edite o arquivo `.env` na raiz do projeto (nunca envie esse arquivo ao Git!):
   ```env
   GEMINI_API_KEY=sua_chave_aqui
   GEMINI_MODEL=gemini-2.5-flash
   ```
2. Reinicie o aplicativo no terminal e marque a opção de síntese com IA na tela **Scientific Assistant**.
3. Lembrete de segurança: documentos privados enviados localmente nunca são enviados para a API externa do Gemini.
