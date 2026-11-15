# AGENTS.md — Instruções persistentes para Codex

Leia primeiro `CODEX_MISSION.md`, depois `docs/RESOURCES_NASA.md`, README e código. Objetivo: concluir o aplicativo existente em vez de recomeçar.

- Antes de editar, descubra skills presentes no ambiente de execução e leia as relevantes. Não fabrique a existência de skills.
- Se houver subagentes, delegue coleta NASA, ingestão, RAG, interface e QA com limites de arquivos claros; caso contrário, execute sequencialmente.
- Preserve código e originais. Dados reais NASA só a partir de fontes/arquivos verificáveis.
- Escreva testes e execute smoke/E2E, documentando limitações, sem afirmar conclusão não comprovada.
- Mantenha `docs/PROGRESS.md` atualizado para retomar sessões.
- Não inclua API keys, downloads assinados expirados, arquivos gigantes ou dados sintéticos como dados científicos.

**Fonte primária: `https://psi.nasa.gov/physci/repo/search?q=combustion`.**
