# KIT — NASA Space Apps 2026 / Flame in Freefall

**O que este arquivo contém:** cópia limpa do SEU projeto original Streamlit/Python, catálogo de 10 fontes oficiais, manifesto de 9 investigações prioritárias, dois scripts de download e instruções de continuidade do Codex. O código original foi preservado; as novidades estão em `resources/`, `scripts/`, `docs/`, `AGENTS.md`.

**Atualização de execução (2026-11-15):** a coleta NASA foi realizada neste ambiente. Há nove CSVs PSI, cinco PDFs associados e dois guias oficiais, com importação real no dashboard. A lista completa, URLs, versões, hashes e lacunas está em [DATA_PROVENANCE.md](DATA_PROVENANCE.md). O kit inicial não continha esses arquivos; esse bloqueio histórico foi resolvido. Nenhum dado experimental foi fabricado.

## Como usar — Windows

1. Descompacte este ZIP. Abra a pasta `PROJETO TESTE FLAME MICROGRAVITY` com Codex/VS Code.
2. Envie ao Codex: **"Leia `CODEX_MISSION.md` e `AGENTS.md` e EXECUTE a missão integralmente, sem reconstruir o projeto e sem inventar dados."**
3. Se preferir tentar os downloads você mesmo: `py scripts/fetch_nasa_resources.py --guide --psi-manual` e `py scripts/fetch_psi_tables.py --ids PSI-25 PSI-26 PSI-68 PSI-69 PSI-98 PSI-99 PSI-100 PSI-101 PSI-102`.
4. Os endpoints Geode foram testados e os scripts corrigidos para os campos atuais `key` e `sortingCategory`. Mudanças futuras da API ainda podem exigir diagnóstico; falhas não são preenchidas por dados inventados.
5. Os CSVs do PSI são muitas vezes tabelas de condições de ensaio, não matrizes de resultados medidos. Não os trate como equivalentes a telemetria ou séries temporais.

## Fonte original dos 10 recursos

https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/

A réplica do texto e links da aba Resources consultada em 2026-11-15: https://hackathlone.com/challenges/flame-in-freefall

## Referências úteis

- PSI: https://psi.nasa.gov/physci/repo/search?q=combustion
- Exemplo PSI-69: https://psi.nasa.gov/physci/repo/data/investigations/PSI-69
- NASA PDF de combustão: https://www.nasa.gov/missions/station/a-researchers-guide-to-combustion-science/
- Tutorial PSI de download: https://assets.science.nasa.gov/content/dam/science/bps/bps-general/bps-data_osdr_psi/Complete_PSI_Database_Guide.pdf
- Documentação comunitária sobre os endpoints PSI (não oficial; revalidar): https://github.com/Krypton-N/NASA-SPACE-APPS-8/blob/main/research/docs/psi_ingestion.md

## Fontes, licença e citações

Registre DOI e URL por investigação. Todos os dados baixados devem ser auditados contra a página PSI, identificando versão, arquivo, tamanho e SHA-256. Não presuma que repositórios de outras equipes sejam fontes primárias NASA. Evite cópias de obras não autorizadas.
