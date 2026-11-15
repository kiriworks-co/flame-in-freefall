# Validação independente de integração e segurança — 15/11/2026

Revisão focada das fronteiras de arquivo, proveniência e resposta científica, em complemento aos testes unitários e à validação da interface do coordenador. Não constitui auditoria completa de segurança ou validação científica dos resultados NASA.

## Execução

Comandos na raiz efetiva do aplicativo:

```powershell
.venv/Scripts/python.exe -m pytest tests/test_end_to_end.py tests/test_security_regressions.py -q
.venv/Scripts/python.exe -m ruff check tests/test_end_to_end.py tests/test_security_regressions.py --output-format concise
```

Resultado: **18 testes passaram**; Ruff passou. Testes executados com Python 3.12.14 no Windows. O PyMuPDF instalado emite um aviso de depreciação para o alias `fitz`; a extração e a renderização testadas funcionam.

## Cadeia validada com dados NASA reais

O E2E usa cópias temporárias dos bytes originais de dois arquivos associados a PSI-69:

- `PSI-69_Experimental table_FLEX.csv`, SHA-256 `37c88ce8ae9391b7544ff630a45ce87543d04d317cdbfbed104fe7d5c27e1b96`.
- `PSI-69_Engineering Documents_FLEX Engineering Requirements Document.pdf`, SHA-256 `a96a47878d2d9e4451f3d889f742571aa2d89c48ba9e9d84b6c698a4cb39486c`.

Manifest original NASA, CSV e PDF são copiados para um projeto temporário. O teste substitui `storage.DATA_DIR` por um arquivo temporário e usa bancos SQLite temporários. Não altera o acervo principal nem faz download durante o teste. Chamadas a `urllib.request.urlopen` são bloqueadas nesse fluxo.

Validado:

1. Importação verifica SHA-256 e preserva os bytes originais.
2. CSV e PDF são extraídos; SQLite contém documentos, fontes/DOI, células, regiões e observações com integridade referencial.
3. Chunks retêm estudo PSI, hash, página ou linha, DOI e URL permanente.
4. Pergunta sobre metanol com filtro O₂ = 0,21 recupera linhas correspondentes do CSV real.
5. Pressão `mmHg` sem referência absoluta explícita não satisfaz filtro em `psia`.
6. Pergunta sobre requisitos recupera páginas do PDF real, verifica o trecho contra a página e renderiza PNG da página citada.
7. Citação exata recuperada passa no verificador programático; consulta sem correspondência informa insuficiência.
8. Reexecução da ingestão e do índice não duplica documentos, eventos ou chunks e não muda os originais.

Um segundo teste verificou o SHA-256 e o tamanho registrado dos **16 arquivos NASA baixados** (9 CSVs PSI, 5 PDFs associados e 2 guias oficiais). Não equivale a verificar manualmente o conteúdo científico de todas as páginas desses arquivos.

## Fronteiras verificadas com fixtures sintéticas

As fixtures abaixo estão confinadas aos testes e não aparecem como dados NASA:

- Caminhos relativos com `..`, absolutos, de unidade Windows e UNC dentro de XLSX/DOCX são recusados.
- Limites de upload e expansão do arquivo são verificados antes da interpretação.
- Manifest e caminhos de documentos não podem escapar da pasta definida.
- URLs executáveis, HTTP, com credenciais ou assinaturas/tokens temporários não são aceitas como citações.
- Texto de instrução maliciosa em CSV permanece texto de evidência. Não gera execução, ferramentas ou conclusões livres.
- Afirmação de segurança fabricada é rejeitada mesmo que reutilize um número da fonte.
- HTML/Markdown de origem são escapados para renderização inerte.
- Ausência de LLM mantém recuperação offline sem chamada de rede.
- PDF inválido com hash correto preserva o original, registra erro de extração e finaliza o job como `partial`.

## Correção derivada da revisão

Foi identificado que uma extração que retornasse `status="erro"` poderia ser contada apenas como arquivo importado, deixando o job como `completed`. O coordenador corrigiu o pipeline para acrescentar erro após preservar o original. A regressão cobre tanto o resultado direto quanto o estado `partial` do worker.

## Limitações

- O PDF associado ao registro PSI-69 contém **FLEX-2** na capa. O E2E confirma essa divergência; a associação oficial ao catálogo não comprova que os requisitos sejam de FLEX.
- `Burning rate; mm` é mantido bruto e não normalizado como taxa. A correção dimensional exige consulta ao responsável pela fonte.
- O verificador LLM foi exercitado com respostas sintéticas e modo sem credencial; nenhum provedor pago ou modelo generativo foi chamado por estes testes.
- Embeddings semânticos e navegação real de navegador são validados separadamente pelo coordenador; estes testes usam o fallback vetorial lexical declarado.
- OCR/VLM, hardware, produção e auditoria completa de dependências não foram certificados por esta revisão.
