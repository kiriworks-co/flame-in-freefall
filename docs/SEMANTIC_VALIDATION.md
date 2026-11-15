# Validação independente do índice semântico

Execução: 2026-11-15T18:41:28.974172+00:00. Após a correção descrita abaixo, revisão somente leitura do índice principal; idempotência executada em cópia SQLite temporária.

Modelo local: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`; revisão `e8f8c211226b894fcb81acc59f3b34ba3efd5f42`. `HF_HUB_OFFLINE=1` e `TRANSFORMERS_OFFLINE=1`; nenhuma chamada a provedor LLM.

## Bugs encontrados e corrigidos

- A primeira validação encontrou segmentos com 129 tokens para um limite de 128: recortar tokens de um subword pode aumentar a contagem ao retokenizar. O segmentador agora retokeniza cada substring e reduz o trecho até caber no limite, preservando sobreposição e posição da fonte.
- O contexto sqlite3 realiza commit/rollback, mas não fecha a conexão por si. Isso bloqueou a remoção do clone no Windows. O gerenciador agora fecha explicitamente as conexões em finally.
- As regressões foram reproduzidas em testes sintéticos identificados como tal. Testes focados: 18 passaram; Ruff dos arquivos alterados passou.
- Reindexação corretiva real: 368 chunks escritos, 6 lotes, total final 2711, 15.755s, falhas=[].

## Integridade e limites de token

- 2711 chunks; dimensões dos vetores: [384].
- Limite do modelo: 128 tokens, incluindo especiais; máximo observado em TODOS os chunks: 128; acima do limite: 0.
- Impressão digital lógica do índice principal antes/depois da etapa somente leitura: `6063f4f69cd93397e5a8648506e17b3f69108630def3cc32868db2620a0fad1b`; inalterada: True.
- 135 evidências distintas verificadas contra 4 documentos originais: 0 problemas de hash, documento, página/linha ou URL permanente.

## Consultas PT/EN

| Estudo | Idioma | Consulta | Evidências | Tempo | Primeiro documento / localização |
|---|---|---|---:|---:|---|
| PSI-69 | pt | Quais condições de oxigênio e pressão foram usadas no FLEX? | 8 | 0.770s | PSI-69_Engineering Documents_FLEX Engineering Requirements Document.pdf / página 22 |
| PSI-69 | en | FLEX oxygen concentration pressure droplet experimental conditions | 8 | 0.763s | PSI-69_Engineering Documents_FLEX Engineering Requirements Document.pdf / página 22 |
| PSI-25 | pt | BASS-II velocidade do escoamento e oxigênio | 8 | 0.466s | PSI-25_Science Documents_BASS-II_SRD.pdf / página 2 |
| PSI-25 | en | BASS-II oxygen flow velocity experimental conditions | 8 | 0.461s | PSI-25_Science Documents_BASS-II_SRD.pdf / página 9 |
| PSI-102 | pt | SAME fumaça aerossol detecção | 8 | 0.582s | PSI-102_Reports_SAME_Final Science Report.pdf / página 41 |
| PSI-102 | en | SAME smoke aerosol detection | 8 | 0.577s | PSI-102_Reports_SAME_Final Science Report.pdf / página 61 |

## Filtro numérico e fallback

Filtro PSI-69: fração O₂ entre 0,20 e 0,22, consulta `FLEX oxygen`. Retornou 100 evidências (limite solicitado: 100); todas satisfazem o filtro por observação tipada na mesma linha: True.

- `PSI-69_Experimental table_FLEX.csv`, linha 256: frações O₂ normalizadas [0.21].
- `PSI-69_Experimental table_FLEX.csv`, linha 258: frações O₂ normalizadas [0.21].
- `PSI-69_Experimental table_FLEX.csv`, linha 17: frações O₂ normalizadas [0.21].
- `PSI-69_Experimental table_FLEX.csv`, linha 49: frações O₂ normalizadas [0.21].
- `PSI-69_Experimental table_FLEX.csv`, linha 223: frações O₂ normalizadas [0.2].

Sem modelo carregado, consulta `FLEX oxygen` manteve 8 evidências: modos ['lexical-fallback:reindex-required']. Aviso exibido: Índice criado com outro modelo: reindexação necessária; evidências preservadas em busca lexical..

## Idempotência

Em cópia temporária do índice, `index_experiments` retornou `indexed=0`, `batches_encoded=0`, `total=2711`, falhas=[]; execução em 2.634s. O índice principal não foi regravado nessa etapa.

## Limitações

- Esta é validação de execução, proveniência e invariantes. Não há perguntas com relevância anotada por especialistas; não se calculou nem se afirma acurácia, recall ou qualidade científica do ranking.
- Resultados trazem contexto e condições; não estabelecem causalidade, segurança de materiais ou eficácia de supressão.
- O modelo é multilíngue de uso geral; não foi ajustado ao domínio de combustão e pode ordenar trechos pouco relevantes.
- Rótulos de estudo e nomes de arquivos preservam a associação fornecida pelo PSI. Divergências entre FLEX/FLEX-2 exigem conferir os registros e não são resolvidas por embeddings.
- Não houve teste com LLM pago, nem validação humana de conclusões. O fallback lexical é explicitamente identificado.
- Os tempos são observações locais; não constituem benchmark geral de hardware.
