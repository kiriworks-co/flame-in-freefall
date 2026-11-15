# Uso de IA e limites

Em 15/11/2026, Codex continuou o código original com subagentes de coleta NASA, ingestão, RAG, interface e QA. Código, testes e documentação tiveram assistência de IA. Os dados científicos vieram diretamente da NASA; nenhuma medição foi gerada para preencher lacunas.

Skills aplicadas segundo o escopo: ui-ux-pro-max, redesign-existing-projects, awesome-design-skills (professional apenas como inspiração), playwright-cli, web-design-guidelines, PDF para inspeção e security-audit em orientação focada. Não havia skill específica Python/RAG no catálogo. React não se aplica ao Streamlit. As regras científicas do projeto prevaleceram. O usuário autorizou instalar dependências e executar testes/aplicação; essa autorização prevaleceu sobre defaults genéricos das skills. Não houve pentest nem deploy público.

## Respostas e privacidade

- FTS5 e vetores lexicais funcionam localmente. Embeddings aprendidos usam pesos locais; modelo, revisão e licença estão em data/embedding_model.json.
- Semelhança vetorial não comprova relevância científica. Filtros físicos usam observações tipadas na mesma linha, com unidade e referência quando exigidas.
- O modo sem LLM mostra evidências e localizações sem concluir cientificamente.
- O LLM opcional recebe pergunta e trechos selecionados após ação do usuário. Não recebe ambiente, arquivos arbitrários ou segredos e não dispõe de ferramentas.
- As afirmações aceitas são extrativas: fonte recuperada, trecho literal, números e categoria correspondentes. Afirmações livres são recusadas. Isso não é garantia geral contra toda alucinação.
- LLM pago/chave real não foram utilizados. Fixtures validam o contrato do adaptador; não homologam um provedor real.
- VLM opcional envia somente a página selecionada após consentimento. Descrição qualitativa, regiões e texto candidato passam por schema tipado e revisão humana. Persistência restrita a analysis_results; não alimenta medições, observações ou RAG. Foi validado com mocks rotulados, sem provedor real.

## Ciência e segurança

Condição, amostra, resultado reportado, cálculo e inferência permanecem distintos. Regras por cabeçalho são inspecionáveis e conservadoras, mas exigem revisão de domínio antes do uso decisório. Resultado publicado não equivale a telemetria bruta validada.

O ranking prioriza investigações para leitura: aplicação até 50, termos da pergunta até 30, cobertura local até 20, conforme src/relevance.py. Não é ranking de materiais nem estimativa de risco.

Pressão sem referência não é presumida absoluta; a taxa de queima com unidade ambígua é preservada. O PDF FLEX-2 associado ao PSI-69 é sinalizado. Não se certifica material nem eficácia de supressão.

Arquivos e strings são entradas não confiáveis: há limites de tamanho/expansão, rejeição de traversal, conferência de hash e exibição inerte de evidências. Fórmulas não são executadas. Não houve auditoria completa de dependências, teste adversarial de provedores nem homologação de exposição pública.
