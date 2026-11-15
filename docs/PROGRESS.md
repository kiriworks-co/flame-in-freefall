# PROGRESS — Retomada de sessões

## Estado atual
- **Repositório Git isolado (`feat/spaceapps-public-release`)**:
  - Branch principal `main` preservada + checkpoint seguro `checkpoint/pre-final-product-overhaul` em `16acce4` antes da reformulação final de produto e UX/UI.
- **Sistema de Design e Arquitetura UI (`src/design_system.py`, `docs/DESIGN_SYSTEM.md`, `docs/UX_AUDIT.md`, `.streamlit/config.toml`)**:
  - Direção visual **Aerospace Laboratory Daylight** com paleta de alto contraste (`#0F1D2B`, `#3E4C59`, `#B84A24`, `#1D5B86`), algarismos tabulares, cartões planos sem aninhamento excessivo e anéis de foco acessíveis (`3px solid #B84A24`).
  - `[client] toolbarMode = "viewer"` e `showErrorDetails = "none"` em `.streamlit/config.toml` removem botões de desenvolvedor (`Deploy`); `initial_sidebar_state="auto"` em `app.py` mantém o menu aberto no desktop e recolhido em telas estreitas/móveis.
  - CSS responsivo em `src/design_system.py` garante ausência de sobrecarga horizontal (`scrollWidth <= clientWidth` verificado em `1440×1000`, `768×1024`, `375×812` e zoom `200%`), quebra segura de abas `[role="tablist"]`, overlay de menu lateral em `<= 48rem` e espaçamento acima do cabeçalho fixo.
- **Navegação Contínua, Hub de Desafio e Descoberta Guiada (`src/scientific_ui.py`, `src/challenge_engine.py`, `src/guided_journeys.py`, `src/views.py`)**:
  - Barra superior fixa com *Onde você está*, controles **`← Back`** / **`🏠 Home`**, retorno contínuo às jornadas e alternador rápido **`Language: EN → PT-BR`** sincronizado com o seletor segmentado **`Language: [EN | PT-BR]`** da barra lateral sem traceback ao alternar idiomas repetidamente.
  - Página inicial com título *"Explore the Science of Fire in Space"*, 3 experiências de entrada e painel interativo **Space Apps Challenge Hub (`SUMMARIZE · RANK · INTERPRET`)**.
  - Todas as 4 etapas das Jornadas Guiadas 1 e 2 estruturadas com o quadro das **5 Perguntas Científicas** (*O que estou explorando · Por que importa · Evidência NASA · Conclusão · Limitações*), prévia de PDFs e gráficos Plotly padronizados (`style_scientific_figure`).
  - **Data Explorer Tab 0** atualizado com visualização gráfica imediata (**Visual First Look**) + painel **SUMMARIZE & INTERPRET** antes de tabelas estatísticas amplas.
- **Assistente Conversacional & Integração Opcional Google Gemini (`src/gemini_provider.py`, `src/assistant.py`)**:
  - Fluxo conversacional via `st.chat_message` com perguntas rápidas em 2 linhas, síntese **SUMMARIZE / INTERPRET** e suporte opcional ao Google Gemini (`GEMINI_API_KEY` / `GOOGLE_API_KEY`, padrão `gemini-2.5-flash`).
  - Bloqueio automático de envio de documentos privados (`local_upload`) via `filter_public_nasa_evidence`, teto deslizante de requisições (`10/min`, `40/sessão`), validação extrativa `validate_claims()` e fallback offline determinístico (`IMPLEMENTED BUT UNCONFIGURED` neste ambiente sem chave no `.env`, testado com mocks HTTP).
- **Documentação & QA Final**:
  - Documentação entregue em `docs/FEATURE_AUDIT.md`, `docs/LOCAL_ACCEPTANCE.md` (guia simples em português para aceite do responsável), `docs/SCIENTIFIC_REVIEW_CHECKLIST.md`, `docs/DESIGN_SYSTEM.md`, `docs/UX_AUDIT.md`, `docs/DEPLOYMENT.md`, `docs/TEST_REPORT.md`, `docs/AI_USAGE.md` e `README.md`.
- **Próxima ação manual do responsável**:
  - Validar localmente seguindo [`docs/LOCAL_ACCEPTANCE.md`](LOCAL_ACCEPTANCE.md) e, quando aprovado, publicar no GitHub + Streamlit Community Cloud seguindo [`docs/DEPLOYMENT.md`](DEPLOYMENT.md).
