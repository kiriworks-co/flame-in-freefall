# Etapa 2 — auditoria das fontes e complemento científico

Data de verificação: 2026-11-15. Escopo: PSI-62, PSI-117 e PSI-159; a Etapa 3 não foi iniciada.

O arquivo fornecido `experienciass.zip` tem SHA-256 `73cde2c18c4dafa63e96ebb372a6a3d530e3bddc94e19139e5e2e7bb92e016c0`. Cada original não vazio foi comparado byte a byte com novo download do endpoint público NASA PSI, utilizando a versão publicada no inventário oficial. Os três ZIPs ISA foram preservados e seus TXT extraídos sem transformação. Dois ZIPs internos de 22 bytes estão vazios: não foram ingeridos como ciência; seus bytes e caminhos estão registrados em `data/psi_downloads/stage2_archive_audit.json` e `archive_anomalies/`.

## Objetivos, métodos e limites

### PSI-62 — propagação concorrente e UFGM

Objetivo: desenvolver e validar manifolds gerados por flamelets não estacionários para propagação de chama sobre sólidos em microgravidade. Método declarado: modelagem acoplada fluido–sólido, PMMA e cera, comparação com BASS/BASS-II e reconstrução de fuligem/temperatura por tomografia de duas cores. Fonte: ISA `metadata/i_Investigation.txt`, campos `Comment[Objective]` e `Comment[Approach]`.

Disponibilidade: o inventário oficial da versão 1 expõe somente o ZIP ISA. Há contexto científico pesquisável, mas **não há séries numéricas, saída CFD, relatório ou novas medições** para importar. O arquivo `s_PSI-62.txt` contém apenas um exemplo `Do not use this`, que não representa amostras científicas. Não transformar objetivos/hipóteses em conclusões demonstradas.

### PSI-117 — dinâmica de chamas frias e comparação CFD/FLEX

Objetivo: estudar perturbações térmicas/convectivas em chamas frias de gotas por modelos multidimensionais, usando FLEX como referência experimental. A abordagem NASA descreve OpenFOAM 3D e química de baixa temperatura. Os arquivos publicados podem representar modelos específicos diferentes: a apresentação de oscilação descreve um modelo de gota na página 4; não atribuir automaticamente todas as séries a uma única configuração OpenFOAM.

Os nove CSVs foram preservados com grupos independentes. `Stable_Cool` e `Oscillatory_Cool_Flame` são trajetórias simuladas; a apresentação de oscilação, páginas 4–7, descreve o modelo e condições de comparação. Os outros sete CSVs contêm séries experimentais e simuladas com marcações `EXP`, `Expt`, `Experiment`, `Sim`, `Model` ou `Simulation`, separadas por índices de colunas. Campos repetidos não são combinados apenas pelo rótulo. Linhas de blocos diferentes não compartilham necessariamente o mesmo instante.

O ReadMe XLSX fornece arquivo, combustível, condições, publicação e figura: PROCI 2019 Stable/Oscillatory → `10.1016/j.proci.2018.05.151`, Fig. 1; Three Stage → `10.1016/j.proci.2018.09.015`, Fig. 7; PROCI 2023 Alkane → `10.1016/j.proci.2022.07.094`, Fig. 3; pressão/extinção C12 → mesma publicação, Fig. 7; MST 2024 → `10.1007/s12217-024-10115-x`, Figs. 1, 4, 5, 11. Esses identificadores foram extraídos do arquivo NASA, não são alegações de revisão independente dessas publicações.

Ressalvas: o ReadMe mistura `XO2=0.21`, `XN2=74/85` e `XO3=Balance`; as convenções são ambíguas e não foram corrigidas. Cabeçalhos sem unidade continuam sem unidade; barras de erro e zeros são valores publicados, não resultados negativos descartados. A apresentação Three Stage, páginas 15–16, descreve a observação FLEX 1268 e concordância qualitativa, o que não autoriza declarar previsão quantitativa universal.

### PSI-159 — ACME / CFI-G

Objetivo: chamas frias esféricas de combustíveis gasosos, normais e inversas, em queimadores porosos a bordo da ISS; comparação com modelos/CFD e mecanismos cinéticos. Métodos e objetivos estão no relatório final, páginas 3–6. Os dois CSVs Experimental Table estavam ausentes no ZIP e foram obtidos diretamente da NASA: contêm condições, cálculos tabulados (`Tad`, `Zst`) e resultados reportados (tempo de queima, temperatura máxima do queimador, ignição, extinção, comentários). Não são telemetria bruta; os papéis são registrados por coluna.

O relatório final de 2022 possui 93 páginas. A página 23 relata observações de chamas frias normais com n-butano, sob as condições descritas naquela página. As páginas 4/6 apresentam objetivos/propostas; a página 17 informa retirada de n-pentano e mudanças de teste. Os apêndices preservam relatos preliminares anteriores: a página 34 registra que ainda não se acreditava haver chamas frias autossustentadas nos três primeiros dias, não contradizendo os resultados posteriores. Não resumir toda hipótese da proposta como resultado alcançado. Documentos de engenharia e condições não equivalem a certificação contra incêndio.

## Inventário verificável

| Estudo | Versão | DOI NASA | Documentos processáveis | ZIP ISA preservado |
|---|---:|---|---:|---:|
| PSI-62 | 1 | 10.60555/e9xp-ex83 | 2 | 1 |
| PSI-117 | 2 | 10.60555/gz0q-b577 | 16 | 1 |
| PSI-159 | 1 | 10.60555/cyt1-kh64 | 6 | 1 |

Total: 24 documentos preservados/processáveis (6 PDFs, 11 CSVs, 1 XLSX, 6 TXT ISA), dos quais **21 têm conteúdo científico ou metadados úteis**. Os três `s_PSI-*.txt` são placeholders ISA de 56 bytes (`Do not use this`) e não são evidência científica nem dados de amostra. Permanecem preservados e identificados como metadados; sua existência não amplia a cobertura científica. Há ainda 3 ZIPs ISA e 2 ZIPs vazios preservados fora da ingestão científica. O maior PDF foi fornecido pelo usuário e tem 30.873.451 bytes, dentro do limite de 30 MiB do pipeline. Não foram baixados vídeos, arquivos de imagens ou coleções brutas de gigabytes.

A divergência de nome `PIS-117` na pasta do ZIP foi resolvida pelo identificador do arquivo e conferência NASA. O PDF de implementação ACME tem dois pontos antes de `pdf` no nome oficial; o fornecido tinha um. Os bytes são idênticos e o nome original do membro foi mantido na proveniência.

| Estudo / arquivo | Bytes | SHA-256 | Fonte permanente |
|---|---:|---|---|
| PSI-62 / `metadata/i_Investigation.txt` | 9402 | `fbbe3e34f381692c62721f4d59a6e85121e90cac852a5846a885da8935edaa16` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-62/download?file=PSI-62_metadata_NEWID-7_Concurrent+Flame+Spr.zip&version=1&redirect=false) |
| PSI-62 / `metadata/s_PSI-62.txt` | 56 | `cb9374159b9b01a83bfe53a0b8ba1a602793df86f298e0ad222615c55d200135` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-62/download?file=PSI-62_metadata_NEWID-7_Concurrent+Flame+Spr.zip&version=1&redirect=false) |
| PSI-62 / `PSI-62_metadata_NEWID-7_Concurrent Flame Spr.zip` | 9694 | `e8f984349473da4763818a424719afcb212c4876e35961792aefc3604aa9ea7a` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-62/download?file=PSI-62_metadata_NEWID-7_Concurrent+Flame+Spr.zip&version=1&redirect=false) |
| PSI-117 / `PSI-117_Analyzed Data_MST_2024_Burning_history_Flame_diameter.csv` | 44107 | `81e6b16c355bc64a226cf638f51156758c6a259ed10bc372c1612a0984cc7bc9` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-117/download?file=PSI-117_Analyzed+Data_MST_2024_Burning_history_Flame_diameter.csv&version=1&redirect=false) |
| PSI-117 / `PSI-117_Analyzed Data_MST_2024_Dext.csv` | 372 | `2ed485fec6fad15c1409cd9b5c558ecf7bee262df29c832e9a54f3befc9c2e46` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-117/download?file=PSI-117_Analyzed+Data_MST_2024_Dext.csv&version=1&redirect=false) |
| PSI-117 / `PSI-117_Analyzed Data_MST_2024_Kavg.csv` | 518 | `a89e0639567f05f19a6d0dffa9b2f659048358dee1c603b6c65bfcebd1101796` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-117/download?file=PSI-117_Analyzed+Data_MST_2024_Kavg.csv&version=1&redirect=false) |
| PSI-117 / `PSI-117_Analyzed Data_MST_2024_Radiance_Flame_Diameter.csv` | 82277 | `277998f5c80c08907f2c05e362e7a13a507ce4ebc967418ca883db2811a84d0d` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-117/download?file=PSI-117_Analyzed+Data_MST_2024_Radiance_Flame_Diameter.csv&version=1&redirect=false) |
| PSI-117 / `PSI-117_Analyzed Data_PROCI_2019_Oscillatory_Cool_Flame.csv` | 37138 | `5d329362ea8b6ff78cded953b289b95c83c45956ae36d136bfd33750a80a5a11` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-117/download?file=PSI-117_Analyzed+Data_PROCI_2019_Oscillatory_Cool_Flame.csv&version=1&redirect=false) |
| PSI-117 / `PSI-117_Analyzed Data_PROCI_2019_Stable_Cool.csv` | 15477 | `c0713c4ad79d1d20832d5ab9582d1bef6d184cff1a86bc3565d059f44998ed6f` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-117/download?file=PSI-117_Analyzed+Data_PROCI_2019_Stable_Cool.csv&version=1&redirect=false) |
| PSI-117 / `PSI-117_Analyzed Data_PROCI_2023_Alkane_Extinction_Diameter_1atm.csv` | 745 | `2b3c8edcfbba8916da95d1e13200310b5a30fa2e62dc8d77145a6ac3c206deb3` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-117/download?file=PSI-117_Analyzed+Data_PROCI_2023_Alkane_Extinction_Diameter_1atm.csv&version=1&redirect=false) |
| PSI-117 / `PSI-117_Analyzed Data_PROCI_2023_C12_Extinction_Diameter_vs_pressure.csv` | 449 | `4ab6f8c19f40a3349096eab8bdceb0a62611020af15e63f816922b149cfa7001` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-117/download?file=PSI-117_Analyzed+Data_PROCI_2023_C12_Extinction_Diameter_vs_pressure.csv&version=1&redirect=false) |
| PSI-117 / `PSI-117_Analyzed Data_PROCI_C12_2019_Three_Stage.csv` | 89130 | `0e7c8c7e9ea35bd139ba52c9f2118724b8cc9f251d82b9222adf03cb67317809` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-117/download?file=PSI-117_Analyzed+Data_PROCI_C12_2019_Three_Stage.csv&version=1&redirect=false) |
| PSI-117 / `PSI-117_Presentations_Extinction_Characteristics_TFarouk.pdf` | 11802360 | `2fe2fc85aa8ee3ac99a07495d31c49704f32d42bb83ae2ba2481d47c14407c43` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-117/download?file=PSI-117_Presentations_Extinction_Characteristics_TFarouk.pdf&version=1&redirect=false) |
| PSI-117 / `PSI-117_Presentations_Oscillatory_Cool Flame_TFarouk.pdf` | 8994674 | `8e4625bb2b2a8b17bd19854765815a3dd877e5192a9b94bd001aea2e8cccb4b2` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-117/download?file=PSI-117_Presentations_Oscillatory_Cool+Flame_TFarouk.pdf&version=1&redirect=false) |
| PSI-117 / `PSI-117_Presentations_PSI_Users_Group_Cool_Flames_in_Space_03302026.pdf` | 10786102 | `9b69c81ba20b7a9af49ca899fb7520ae8e2034f9ceadf94fc6ef22910fc417aa` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-117/download?file=PSI-117_Presentations_PSI_Users_Group_Cool_Flames_in_Space_03302026.pdf&version=1&redirect=false) |
| PSI-117 / `PSI-117_Presentations_Three_Stage_Cool_Flame_TFarouk.pdf` | 30873451 | `99b341840ed423878c622478b3b7817729d0ccf4d772f407f860a91d66972917` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-117/download?file=PSI-117_Presentations_Three_Stage_Cool_Flame_TFarouk.pdf&version=1&redirect=false) |
| PSI-117 / `PSI-117_Analyzed Data_ReadMe_List_of_Data.xlsx` | 11059 | `a84c138d22545ba9f59c4aa336710741dd48cf3c27823124ed04ac8f91a5f4a0` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-117/download?file=PSI-117_Analyzed+Data_ReadMe_List_of_Data.xlsx&version=1&redirect=false) |
| PSI-117 / `metadata/i_Investigation.txt` | 10088 | `f86a1b97fa011cb02c8c52d1e05184840d4f020197cf60462a942654612fb27a` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-117/download?file=PSI-117_metadata_NEWID-13_Effect+of+External+T.zip&version=2&redirect=false) |
| PSI-117 / `metadata/s_PSI-117.txt` | 56 | `cb9374159b9b01a83bfe53a0b8ba1a602793df86f298e0ad222615c55d200135` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-117/download?file=PSI-117_metadata_NEWID-13_Effect+of+External+T.zip&version=2&redirect=false) |
| PSI-117 / `PSI-117_metadata_NEWID-13_Effect of External T.zip` | 10382 | `a9698dbe10629c226dc498610d62ab8c5c7f15e2668412e831164ab74df99222` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-117/download?file=PSI-117_metadata_NEWID-13_Effect+of+External+T.zip&version=2&redirect=false) |
| PSI-159 / `PSI-159_Experimental table_CFI-G_Normal Flames.csv` | 22166 | `d95a621c3fbd27d204dd32ed29fa17d68f2b779d6a523cde8479ed7ebaa5251a` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-159/download?file=PSI-159_Experimental+table_CFI-G_Normal+Flames.csv&version=1&redirect=false) |
| PSI-159 / `PSI-159_Experimental table_CFI-G_Inverse Flames.csv` | 39422 | `d4d44f8b9896936728748e34d1b6ad0812032a92fa5289599b708c138e3a9b39` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-159/download?file=PSI-159_Experimental+table_CFI-G_Inverse+Flames.csv&version=1&redirect=false) |
| PSI-159 / `PSI-159_Engineering Documents_ACME Engineering Implementation Rpt..pdf` | 7496324 | `393f3ebc6662b10f0fe55d87ceda3b6696d2cc9c91266b81132761de50078456` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-159/download?file=PSI-159_Engineering+Documents_ACME+Engineering+Implementation+Rpt..pdf&version=1&redirect=false) |
| PSI-159 / `PSI-159_Reports_FinalRpt_ACME.CFI-G.pdf` | 3894907 | `f6cce7cc08ca69c155994d7a8898e21cd4aba122f4e46d5e00708e4889a1ebab` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-159/download?file=PSI-159_Reports_FinalRpt_ACME.CFI-G.pdf&version=1&redirect=false) |
| PSI-159 / `metadata/i_Investigation.txt` | 8110 | `03092ce8efc68e1a8430098bf73da9b4e9ae2ef302c677c368c2c81ded355ac9` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-159/download?file=PSI-159_metadata_PSI-159-ISA.zip&version=1&redirect=false) |
| PSI-159 / `metadata/s_PSI-159.txt` | 56 | `cb9374159b9b01a83bfe53a0b8ba1a602793df86f298e0ad222615c55d200135` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-159/download?file=PSI-159_metadata_PSI-159-ISA.zip&version=1&redirect=false) |
| PSI-159 / `PSI-159_metadata_PSI-159-ISA.zip` | 8404 | `0ef60d1ee8d4d53bbe58139d56fa99e9500ca48dd7913b25ac85dc853d6710ab` | [NASA](https://psi.nasa.gov/geode-py/ws/studies/PSI-159/download?file=PSI-159_metadata_PSI-159-ISA.zip&version=1&redirect=false) |

## Reprodução e segurança da importação

Primeira verificação: `python scripts/import_stage2_archive.py C:/Users/kiriyama/Desktop/experienciass.zip --verify-online`. Reexecução offline: o mesmo comando sem `--verify-online`, exigindo o hash exato do ZIP e manifestos previamente verificados. O replay verifica hashes e não sobrescreve originais divergentes.

O importador limita quantidade/tamanho/razão de compressão, rejeita traversal, caminhos absolutos/ADS, nomes de dispositivos Windows, links simbólicos, entradas duplicadas e ZIPs cifrados. Não executa conteúdo dos arquivos nem retém URLs assinadas temporárias. Conteúdo documental não é instrução operacional. A classificação científica conserva incertezas; a confirmação final de ingestão, índices e interface depende dos testes registrados pelo coordenador.
