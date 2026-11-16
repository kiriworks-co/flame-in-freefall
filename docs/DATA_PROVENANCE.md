# Proveniência dos dados NASA

## Investigações PSI-62, PSI-117 e PSI-159

Além das outras nove investigações do acervo, estas três fontes foram preservadas com seus metadados originais.
Os arquivos originais das três investigações, seus identificadores e os
metadados de integridade são preservados em `data/psi_downloads/`. A trilha
dos arquivos ISA e seus membros está em `data/psi_downloads/stage2_archive_audit.json`;
os manifests individuais registram versões, identificadores, URLs e hashes
SHA-256 para conferência com os registros oficiais da NASA. Os originais das demais investigações também permanecem
inalterados. A relação de arquivos mais abaixo registra o restante do acervo.

- **PSI-62**, versão 1, DOI `10.60555/e9xp-ex83`: metadados de uma investigação
  de modelagem UFGM e comparação com BASS/BASS-II. Não há resultados numéricos
  ou relatório público na seleção disponibilizada pela NASA.
- **PSI-117**, versão 2, DOI `10.60555/gz0q-b577`: nove CSVs analisados, quatro
  apresentações, ReadMe XLSX e dois TXT ISA. Séries CFD e resultados
  experimentais reportados são classificados separadamente por coluna/bloco.
  Unidades ausentes e convenções ambíguas do ReadMe permanecem sem correção.
- **PSI-159**, versão 1, DOI `10.60555/cyt1-kh64`: dois relatórios/PDFs, dois
  TXT ISA e duas tabelas pequenas obtidas diretamente da NASA para completar
  a pasta vazia do ZIP. As tabelas contêm condições, resultados reportados e
  cálculos tabulados, identificados separadamente; não são telemetria bruta.

Os três TXT `s_*.txt` são placeholders publicados pela NASA; foram preservados
e explicitamente excluídos da interpretação como amostras ou medições. Dois
ZIPs internos vazios foram ignorados pela ingestão científica e registrados
como anomalias. Documentos ou hipóteses teóricas não foram promovidos a
medições. Texto científico é conteúdo de fonte, nunca instrução do sistema.

Verificação independente: cada original não vazio fornecido foi comparado
com novo download NASA da versão indicada. Os metadados ISA extraídos
mantêm exatamente os bytes do ZIP verificado. As URLs S3 temporárias foram
usadas apenas para transporte; as referências persistidas são URLs NASA
permanentes. Não há licença específica inventada. Reexecução offline do
importador preservou o conteúdo de todos os arquivos.

O processamento de dados é realizado pelos scripts do diretório `scripts/`.
Arquivos preservados podem ser conferidos com os hashes registrados no acervo.

Coleta real em 2026-11-15. Os originais abaixo foram recebidos por HTTPS diretamente de NASA PSI ou NASA.gov; nenhum arquivo científico foi copiado de equipes externas. SHA-256 verificado novamente após a coleta. Links API são estáveis para solicitar o arquivo na versão registrada; URLs S3 assinadas foram usadas apenas em memória e não persistidas.

## Arquivos obtidos

| Investigação | Arquivo local | Bytes | SHA-256 | Fonte permanente |
|---|---|---:|---|---|
| PSI-100 | [data/psi_downloads/PSI-100/PSI-100_Experimental table_SAFFIRE-3.csv](../data/psi_downloads/PSI-100/PSI-100_Experimental%20table_SAFFIRE-3.csv) | 239 | `4d3c717ec20dd0247db670b2784a9fd7d746788bc54a936f80693e48eb8cd117` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-100/download?file=PSI-100_Experimental+table_SAFFIRE-3.csv&version=1&redirect=false) |
| PSI-101 | [data/psi_downloads/PSI-101/PSI-101_Experimental table_SAME-R.csv](../data/psi_downloads/PSI-101/PSI-101_Experimental%20table_SAME-R.csv) | 5674 | `87164b7dc9168a4273c159f7a9f23699afbd06ad97b77974377e79b9bf8a3bef` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-101/download?file=PSI-101_Experimental+table_SAME-R.csv&version=1&redirect=false) |
| PSI-102 | [data/psi_downloads/PSI-102/PSI-102_Experimental table_SAME.csv](../data/psi_downloads/PSI-102/PSI-102_Experimental%20table_SAME.csv) | 331 | `268d1e121d2f211b124407dd32b9475617bd269ede2c2d1749441da3e949a2af` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-102/download?file=PSI-102_Experimental+table_SAME.csv&version=1&redirect=false) |
| PSI-102 | [data/psi_downloads/PSI-102/PSI-102_Engineering Documents_60089MFHA415 Ignitor Wire Coil Assembly (for 0 .250 OD samples).pdf](../data/psi_downloads/PSI-102/PSI-102_Engineering%20Documents_60089MFHA415%20Ignitor%20Wire%20Coil%20Assembly%20(for%200%20.250%20OD%20samples).pdf) | 98186 | `3bee2dea59501f5022769e0aa9e44275ea3bce8f6fdfd3c1f1051f260054ef51` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-102/download?file=PSI-102_Engineering+Documents_60089MFHA415+Ignitor+Wire+Coil+Assembly+%28for+0+.250+OD+samples%29.pdf&version=2&redirect=false) |
| PSI-102 | [data/psi_downloads/PSI-102/PSI-102_Reports_SAME_Final Science Report.pdf](../data/psi_downloads/PSI-102/PSI-102_Reports_SAME_Final%20Science%20Report.pdf) | 3712845 | `af91c96d22d93bbefbc0f2c5e1cc06e24813f532e5379b3fec9f121cccb22193` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-102/download?file=PSI-102_Reports_SAME_Final+Science+Report.pdf&version=2&redirect=false) |
| PSI-25 | [data/psi_downloads/PSI-25/PSI-25_Experimental table_BASS-II.csv](../data/psi_downloads/PSI-25/PSI-25_Experimental%20table_BASS-II.csv) | 16590 | `71e792bf6b5fb5ea620c5dd70fbbac05515992e12aefcf5dff47312caa48c042` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-25/download?file=PSI-25_Experimental+table_BASS-II.csv&version=1&redirect=false) |
| PSI-25 | [data/psi_downloads/PSI-25/PSI-25_Raw Data_GMT2014_202_BASS_S220M_TPO5b_ProofSheet.pdf](../data/psi_downloads/PSI-25/PSI-25_Raw%20Data_GMT2014_202_BASS_S220M_TPO5b_ProofSheet.pdf) | 27893 | `4487d085b6a99e4f74f8a95dbe697ced7ac799becd051c224d41d400e8789153` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-25/download?file=PSI-25_Raw+Data_GMT2014_202_BASS_S220M_TPO5b_ProofSheet.pdf&version=2&redirect=false) |
| PSI-25 | [data/psi_downloads/PSI-25/PSI-25_Science Documents_BASS-II_SRD.pdf](../data/psi_downloads/PSI-25/PSI-25_Science%20Documents_BASS-II_SRD.pdf) | 1108340 | `d00a763d60719bc14004264e216452b44c3c1bf4b0c629e9d307c8abf9568e75` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-25/download?file=PSI-25_Science+Documents_BASS-II_SRD.pdf&version=2&redirect=false) |
| PSI-26 | [data/psi_downloads/PSI-26/PSI-26_Experimental table_BASS.csv](../data/psi_downloads/PSI-26/PSI-26_Experimental%20table_BASS.csv) | 4726 | `ccfc3c54d948b64a1c5d2596a63c7c8019e51df0c91a1d62f039f48fa28c300f` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-26/download?file=PSI-26_Experimental+table_BASS.csv&version=1&redirect=false) |
| PSI-68 | [data/psi_downloads/PSI-68/PSI-68_Experimental table_Flex2.csv](../data/psi_downloads/PSI-68/PSI-68_Experimental%20table_Flex2.csv) | 1029 | `cc57ad1bd9977aa13e7ac6c3aa618303012686e232b36c052c6a9f1a74e5f528` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-68/download?file=PSI-68_Experimental+table_Flex2.csv&version=1&redirect=false) |
| PSI-69 | [data/psi_downloads/PSI-69/PSI-69_Experimental table_FLEX.csv](../data/psi_downloads/PSI-69/PSI-69_Experimental%20table_FLEX.csv) | 24776 | `37c88ce8ae9391b7544ff630a45ce87543d04d317cdbfbed104fe7d5c27e1b96` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-69/download?file=PSI-69_Experimental+table_FLEX.csv&version=1&redirect=false) |
| PSI-69 | [data/psi_downloads/PSI-69/PSI-69_Engineering Documents_FLEX Engineering Requirements Document.pdf](../data/psi_downloads/PSI-69/PSI-69_Engineering%20Documents_FLEX%20Engineering%20Requirements%20Document.pdf) | 237373 | `a96a47878d2d9e4451f3d889f742571aa2d89c48ba9e9d84b6c698a4cb39486c` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-69/download?file=PSI-69_Engineering+Documents_FLEX+Engineering+Requirements+Document.pdf&version=1&redirect=false) |
| PSI-98 | [data/psi_downloads/PSI-98/PSI-98_Experimental table_SAFFIRE-1.csv](../data/psi_downloads/PSI-98/PSI-98_Experimental%20table_SAFFIRE-1.csv) | 469 | `c01f29c62455f0a3b512290ab85e5687ecded326733189f002f580368402308d` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-98/download?file=PSI-98_Experimental+table_SAFFIRE-1.csv&version=1&redirect=false) |
| PSI-99 | [data/psi_downloads/PSI-99/PSI-99_Experimental table_SAFFIRE-2.csv](../data/psi_downloads/PSI-99/PSI-99_Experimental%20table_SAFFIRE-2.csv) | 1973 | `3c24390b9ef86f3d1ebaab911a1a3cc95a8759aebf42062371370e6d4b31b8ac` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-99/download?file=PSI-99_Experimental+table_SAFFIRE-2.csv&version=1&redirect=false) |
| NASA context | [resources/official/psi_database_guide.pdf](../resources/official/psi_database_guide.pdf) | 1139998 | `9237b173f349028014ce69a2beae8c590a8483e7009978f178ecb6eac55fe7b1` | [NASA](https://assets.science.nasa.gov/content/dam/science/bps/bps-general/bps-data_osdr_psi/Complete_PSI_Database_Guide.pdf) |
| NASA context | [resources/official/researchers_guide.pdf](../resources/official/researchers_guide.pdf) | 1500825 | `5fe046efe4e35e506023e27a9784d041e893026f19c9987591483614aea5d6b6` | [NASA](https://www.nasa.gov/wp-content/uploads/2016/05/np-2015-10-034-jsc_combustion_in_reduced_gravity-iss-mini-book-011116-508.pdf) |

## Versões e DOI confirmados na NASA

| PSI | Versão do estudo | DOI oficial |
|---|---:|---|
| PSI-100 | 4 | [10.60555/040q-4h36](https://doi.org/10.60555/040q-4h36) |
| PSI-101 | 4 | [10.60555/2np7-jv14](https://doi.org/10.60555/2np7-jv14) |
| PSI-102 | 4 | [10.60555/gd4k-8h62](https://doi.org/10.60555/gd4k-8h62) |
| PSI-25 | 4 | [10.60555/4qc4-de67](https://doi.org/10.60555/4qc4-de67) |
| PSI-26 | 4 | [10.60555/58h4-dy80](https://doi.org/10.60555/58h4-dy80) |
| PSI-68 | 6 | [10.60555/byp8-h018](https://doi.org/10.60555/byp8-h018) |
| PSI-69 | 5 | [10.60555/mbq8-0451](https://doi.org/10.60555/mbq8-0451) |
| PSI-98 | 4 | [10.60555/0t15-1z43](https://doi.org/10.60555/0t15-1z43) |
| PSI-99 | 5 | [10.60555/2chp-m469](https://doi.org/10.60555/2chp-m469) |

Cada `data/psi_downloads/PSI-*/source_manifest.json` contém versão do estudo e do arquivo, data UTC de acesso, URL API, landing page, hash, tamanho, metadados originais selecionados e classificação. `metadata.json` preserva a resposta oficial de metadados; `resources/manifests/priority_investigations.json` conserva candidatos históricos e acrescenta DOI confirmado.

## Cobertura e interpretação científica

| PSI | Linhas não vazias | Colunas | Codificação | Linhas com largura irregular | Células vazias |
|---|---:|---:|---|---:|---:|
| PSI-100 | 2 | 9 | utf-8-sig | 0 | 0 |
| PSI-101 | 109 | 10 | utf-8-sig | 0 | 125 |
| PSI-102 | 8 | 5 | utf-8-sig | 0 | 12 |
| PSI-25 | 129 | 17 | utf-8-sig | 0 | 19 |
| PSI-26 | 122 | 6 | utf-8-sig | 0 | 3 |
| PSI-68 | 8 | 7 | utf-8-sig | 0 | 0 |
| PSI-69 | 274 | 15 | cp1252 | 0 | 78 |
| PSI-98 | 4 | 13 | utf-8-sig | 0 | 22 |
| PSI-99 | 15 | 17 | utf-8-sig | 0 | 97 |

Perfil inspecionável em `resources/manifests/data_quality_profile.json`. Unidade de análise: linha original da tabela experimental; algumas linhas representam amostras/configurações e outras ensaios. Não juntar estudos por número de amostra sem chave/metodologia validada. Ausências, valores qualitativos, intervalos e notas são preservados. Não há série temporal completa de sensores nesta seleção.

- FLEX (PSI-69) contém condições **e resultados reportados**: diâmetro de extinção, tempo de queima e fim do ensaio. O cabeçalho original `Burning rate; mm` é dimensionalmente ambíguo; não tratá-lo como mm/s ou mm²/s e não comparar taxas sem documentação adicional. Cabeçalhos `O`, `N`, `CO` não têm subscrito no arquivo; qualquer interpretação molecular precisa contexto e revisão. O arquivo usa Windows-1252, não UTF-8 puro.
- BASS-II (PSI-25) inclui gases iniciais/finais reportados; são resultados de ensaios específicos, não certificação de segurança. BASS (PSI-26) é principalmente catálogo de ensaios e material. FLEX-2 (PSI-68) traz condições e intervalos, não a matriz completa de resultados.
- Saffire-I/II têm colunas de tempo de queima e propagação, com unidades ausentes/heterogêneas em parte da tabela; Saffire-III não declara unidades em vários cabeçalhos. Não completar unidades por suposição.
- SAME/SAME-R descrevem amostras, fluxo, envelhecimento e taxa declarada de perda de massa; não equivalem a séries temporais nem a uma avaliação quantitativa da eficácia dos detectores.
- **Divergência documental:** o PDF `PSI-69_Engineering Documents_FLEX Engineering Requirements Document.pdf`, obtido na árvore oficial PSI-69, declara **FLEX-2 Engineering Requirements** na capa. A associação é de catálogo; os requisitos não devem ser atribuídos automaticamente ao FLEX original.
- PDFs: SAME relatório científico final 68 páginas; BASS-II requisitos científicos 16 páginas; FLEX-2 requisitos 37 páginas. Desenho SAME de uma página não tem camada textual. OCR depende de Tesseract. Proofsheet BASS-II é imagem documental, não medição numérica de chama.
- Guias NASA gerais são contexto e devem ficar separados dos estudos empíricos. Não inferir dados de um estudo a partir de recomendações gerais.

## Aquisição e compatibilidade API

Comandos executados (Python local `.venv/Scripts/python.exe`):

```powershell
.venv/Scripts/python.exe scripts/fetch_nasa_resources.py --guide --psi-manual
.venv/Scripts/python.exe scripts/fetch_psi_tables.py --ids PSI-25 PSI-26 PSI-68 PSI-69 PSI-98 PSI-99 PSI-100 PSI-101 PSI-102
.venv/Scripts/python.exe scripts/fetch_psi_tables.py --ids PSI-69 PSI-25 PSI-102 --pdfs
```

API validada: GET `/studies/{PSI-ID}/metadata` informa versão no topo e DOI em `studies[0].comments` com `name=DOI`; POST `/files/v2` retorna árvore `files`, nomes em `key`, categorias em `sortingCategory`. O script inicial procurava `fileName`, por isso detectava zero CSV. Download GET `/studies/{ID}/download?file=...&version=...&redirect=false` retorna URL S3 temporária. Preservado o endpoint permanente com a versão do arquivo. Apenas arquivos públicos pequenos, sem vídeos nem download massivo; limite 25 MiB, PDF selecionado até 5 MiB, backoff em 429/5xx, sem desativar TLS.

## Licença e lacunas

A resposta por arquivo não declara licença específica. Preservar crédito NASA e autores e verificar termos PSI e conteúdo de terceiros antes de redistribuir. Não foi atribuída licença inventada aos dados. Os manifests declaram a ausência.

Os dez links fornecidos foram testados, resultado em `resources/manifests/resource_link_check.json`: oito HTTP 200; Apollo 1 e Apollo 13 falharam com `CERTIFICATE_VERIFY_FAILED` (cadeia de certificado apresentada ao cliente). Não foi desativada a verificação TLS. HTTP 200 de YouTube/SPA confirma somente resposta HTTP, não reprodução do vídeo ou conteúdo renderizado.

A seleção não inclui os arquivos gigantes de imagem/vídeo e telemetria bruta; eles permanecem no catálogo NASA. Os CSVs não constituem todo o acervo experimental. Nenhuma conclusão de segurança de material ou supressão foi calculada a partir desta coleta.
