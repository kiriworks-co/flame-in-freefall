# Demonstração — 2 a 3 minutos

Pré-requisitos: ambiente instalado, coletores concluídos, ingestão sem erros e índice atualizado. Abrir http://127.0.0.1:8501. Os arquivos abaixo são originais NASA, com hashes e URLs em DATA_PROVENANCE.md. A numeração PDF é a posição física da página, usada pelo leitor; pode diferir da numeração impressa.

## 0:00–0:25 — cobertura e limites

Abrir **Visão geral**: nove investigações PSI, 16 originais, cobertura de prevenção, detecção e supressão. Explicar que condições de ensaio e resultados reportados não equivalem a prova de segurança de materiais. Não mostrar ranking de risco.

## 0:25–1:00 — BASS

Em **Investigações NASA**, pesquisar BASS e abrir PSI-25. Em **Documentos/Tabelas**, inspecionar [CSV BASS-II original](../data/psi_downloads/PSI-25/PSI-25_Experimental%20table_BASS-II.csv), cabeçalhos, células vazias e linhas de origem. A opção de baixar o original entrega os mesmos bytes verificados por SHA-256.

Em **Revisão visual**, selecionar [BASS-II Science Requirements](../data/psi_downloads/PSI-25/PSI-25_Science%20Documents_BASS-II_SRD.pdf), página **2**, e renderizar localmente. O documento descreve requisitos de medição de concentrações e operação; apresentar como requisito documental, não como resultado medido de um ensaio.

Fonte do estudo: https://psi.nasa.gov/physci/repo/data/investigations/PSI-25

## 1:00–1:45 — FLEX

Em **Busca e assistente**, selecionar PSI-69, perguntar `FLEX oxygen`, abrir os filtros e habilitar O₂ com faixa **0,18 a 0,25 de fração**. Essa faixa é uma escolha de consulta, não um resultado anunciado. Pesquisar e abrir um resultado de tabela: conferir linha, combustível, unidade, hash e original.

Arquivo: [CSV FLEX](../data/psi_downloads/PSI-69/PSI-69_Experimental%20table_FLEX.csv). Não interpretar `Burning rate; mm` como uma taxa dimensionalmente validada. Explicar que o filtro de pressão psia exclui fontes que não declaram referência absoluta.

Para contexto científico, **Revisão visual** → [Researchers Guide NASA](../resources/official/researchers_guide.pdf), página **36**, seção Droplet Combustion. O texto distingue as motivações de FLEX e FLEX-2. O PDF de requisitos catalogado em PSI-69 tem FLEX-2 na capa; mostrar o aviso se esse documento for aberto e não atribuir seus requisitos ao FLEX original.

Fonte: https://psi.nasa.gov/physci/repo/data/investigations/PSI-69

## 1:45–2:20 — SAME

Em **Investigações NASA**, abrir PSI-102 e conferir [CSV SAME](../data/psi_downloads/PSI-102/PSI-102_Experimental%20table_SAME.csv). Destacar a diferença entre configurações/catálogo e resultados reportados.

Em **Revisão visual**, abrir [SAME Final Science Report](../data/psi_downloads/PSI-102/PSI-102_Reports_SAME_Final%20Science%20Report.pdf), página **13** (impressa 3): há texto e uma figura do detector. A página física **24** contém a seção Flight Tests. Ler o original, sem inferir desempenho de detecção a partir de uma única imagem.

Fonte: https://psi.nasa.gov/physci/repo/data/investigations/PSI-102

## 2:20–2:50 — comparação e honestidade

Em **Comparar estudos**, selecionar BASS e FLEX. Mostrar as unidades e o aviso de incompatibilidade quando não há condições/metodologias equivalentes; não juntar curvas heterogêneas.

Voltar ao assistente, consultar termo sem correspondência, como `quasar-zebra-unsupported-xyz`, e mostrar insuficiência de evidências. O modo sem LLM segue operacional sem chave. Se houver LLM configurado, demonstrar apenas seleção de trechos verificáveis, sem afirmar que o provedor foi homologado nesta entrega.

A revisão VLM remota é opcional, requer configuração e consentimento; sem chave, demonstrar somente a inspeção local. Nenhuma inferência visual vira medição.
