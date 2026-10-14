# Histórico do banco de modelos

## 2026-10-14 — matriz de 28,86% por questões selecionáveis

A matriz única de 28,86% deixa de ter hipóteses [A]/[B]/[C] escolhidas por cartões e passa a ser montada por **questões do caso** (`_questoes` no esqueleto), cada uma um item selecionável no painel “Questões do caso” do editor (workbench 31 + `scripts/workbench-questoes-do-caso.js`). Marcar uma questão a inclui, numerada, na frase da Controvérsia e liga os subtópicos e parágrafos a ela vinculados; desmarcar retira o que só ela usava.

- Controvérsias: limitação territorial (padrão) · prescrição da pretensão executória · habilitação de herdeiros (exige prescrição) · acordo administrativo (fichas SIAPE) · servidor representado por sindicato com ação própria.
- Questões incidentais: Tema 1.433/STJ · ilegitimidade ativa em contrarrazões · má-fé · gratuidade impugnada no recurso adesivo · honorários pedidos pelo ente.
- Preliminares sem texto-base: Tema 1.433 e ilegitimidade viraram cartões próprios. A abertura “O caso é peculiar…” virou o subtópico **Exceções da coisa julgada**.
- As frases compostas reproduzem as controvérsias originais (territorial; territorial + prescrição + herdeiros). **Redação nova**, a revisar: as frases das questões “acordo administrativo” e “sindicato”.

## 2026-10-14 — matriz única de 28,86%

As três matrizes de 28,86% foram unificadas em **MODELO-MATRIZ · 28,86% · ACP 0005019-15.1997.4.03.6000 · cumprimento individual · apelação**, com três hipóteses marcadas por letra: [A] limite territorial afastado · provida; [B] acordo administrativo (fichas SIAPE) · desprovida; [C] servidor representado por sindicato com ação anterior · desprovida. Blocos fixos por questão (limitação territorial, acordo administrativo, limites subjetivos da coisa julgada, servidor do sindicato); seções de uma só hipótese desligadas por padrão; versões por hipótese como cartões (controvérsia, fichas, conclusão, honorários, dispositivo). Cada hipótese reproduz exatamente o texto da matriz de origem. Processos associados: os seis processos-fonte das três matrizes. Saem do banco: par-matriz-2886-territorial-provida, par-matriz-2886-acordo-administrativo-desprovida e par-matriz-2886-ilegitimidade-acao-sindical.

## 2026-10-14 — matrizes de 28,86% no padrão atual

Reinseridas as três matrizes de voto da ACP 0005019-15.1997.4.03.6000 (28,86%), já convertidas ao padrão atual do app (parágrafos em versões, variáveis @ e campos {{ }}), com os processos-fonte como processos associados:

| Matriz | Processos associados | Parágrafos |
|---|---|---:|
| 28,86% · Limite territorial afastado · apelação da parte exequente provida | 5003454-12.2026.4.03.6000, 5003797-42.2025.4.03.6000, 5003544-88.2024.4.03.6000 | 31 |
| 28,86% · Legitimidade reconhecida, mas acordo administrativo (fichas SIAPE) · apelação desprovida | 5007937-56.2024.4.03.6000, 5001115-51.2024.4.03.6000 | 68 |
| 28,86% · Ilegitimidade ativa · categoria representada por sindicato com ação coletiva anterior · apelação desprovida | 5006675-71.2024.4.03.6000 | 20 |

**Estrutura (revisão no mesmo dia):** um bloco de texto fixo por questão abordada, sem separar parágrafos que dependem uns dos outros (citações dentro do bloco). Cartões só para versões alternativas (controvérsia, fichas, conclusão, honorários, dispositivo, prescrição) e situações específicas (ilegitimidade e honorários pedidos em contrarrazões); prescrição, litigância de má-fé e gratuidade são seções desligadas. Cartões: 31 → 6, 68 → 11 e 20 → 3; o texto que sai com as escolhas-padrão é idêntico ao da versão 2.3.0.

As três substituem as versões antigas retiradas na revisão anterior; os modelos F04, F05, F12 e M8-039 seguem fora do banco.

## 2026-10-14 — saneamento, unificação e processos associados

Total: **207 → 158** registros (161 após a reinserção das matrizes de 28,86%) (Decisão interlocutória: 40, Decisão monocrática terminativa: 42, Despacho: 25, Voto: 51).

### O que mudou

- **Processos associados** preenchidos em todos os modelos M8: o processo de referência e os demais processos de onde o texto foi extraído (origem, ação conexa, execução, AI anterior), na ordem referência → demais. Os votos rurais trazem o processo do voto e as ações citadas na narrativa; os modelos unificados reúnem os processos de todos os modelos absorvidos.
- **Estrutura em fases** (Relatório › Fundamentação › Caso › Dispositivo › Determinações › Fecho) aplicada a todo o MODELOS 8; despachos ganharam o tópico *Relatório › Narrativa* e o relato saiu de *Determinações › Ordem*.
- **Unificação**: 28 modelos absorvidos em 15 famílias, com versões alternativas por hipótese (`paragrafosModelo`, mesma letra em todos os tópicos). Modelos com parágrafos alternativos/opcionais: 23.
- **Correções de conteúdo**: Tema 988/STJ (taxatividade mitigada) citado como “Tema 998” em M8-028/029/030/031; precedente restaurado no M8-010 (AI 5014100-44.2023.4.03.0000); fragmentos partidos (M8-029, M8-030); “(ID----)” no M8-058; assinatura perdida no meio do M8-129; versões coladas separadas como alternativas (M8-062, M8-106, M8-111, M8-123); M8-062 reclassificado como decisão interlocutória; tipografia (espaço rígido) normalizada.
- **Votos rurais (RURAL-001 a 036)** reconstruídos com o texto integral do caso (Compêndio Rural), dados pessoais substituídos por `{{CAMPOS}}`, ementa do acórdão, resultado, dispositivo, temas e dispositivos citados.
- **Nova matriz**: *MODELO-MATRIZ · Apelação · Aposentadoria por idade rural* — 17 parágrafos opcionais de análise e 5 conclusões alternativas extraídos dos votos.
- **Compêndio genérico**: itens só com orientação removidos quando há modelo com texto real; 5 (causa acidentária) e 7.2 (digitalização) reescritos nas fases-padrão; 4.3 virou parágrafo opcional do M8-001.

### Registros removidos

| Registro | Motivo |
|---|---|
| MODELO F04 | índice de 28,86% (matéria retirada do banco a pedido) |
| MODELO F05 | índice de 28,86% (matéria retirada do banco a pedido) |
| MODELO F12 | índice de 28,86% (matéria retirada do banco a pedido) |
| M8-039 | índice de 28,86% (matéria retirada do banco a pedido) |
| M8-063 | fragmento (“São Paulo, 06 de fevereiro de 2024”) da 2ª versão do sobrestamento — hoje alternativa “b” do M8-062 |
| M8-124 | 2ª versão colada do despacho de juntada de mídias — hoje alternativa “c” do M8-125 |
| 1.1.1 | compêndio sem texto — substituído por M8-084 |
| 1.1.2 | compêndio sem texto — substituído por M8-052 |
| 1.1.3 | compêndio sem texto — substituído por M8-084 |
| 1.2 | compêndio sem texto — substituído por M8-098 |
| 2.1 | compêndio sem texto — substituído por M8-006 |
| 3 | compêndio sem texto — substituído por M8-024 |
| 4.1 | compêndio sem texto — substituído por M8-001 |
| 4.2 | compêndio sem texto — substituído por M8-001 |
| 4.3 | compêndio sem texto — substituído por M8-001 (parágrafo opcional) |
| 6.1 | compêndio sem texto — substituído por M8-137 / M8-037 |
| 7.1 | compêndio sem texto — substituído por M8-116 |
| 7.3 | compêndio sem texto — substituído por M8-113 |
| M8-002 | absorvido em modelo unificado |
| M8-003 | absorvido em modelo unificado |
| M8-007 | absorvido em modelo unificado |
| M8-009 | absorvido em modelo unificado |
| M8-028 | absorvido em modelo unificado |
| M8-030 | absorvido em modelo unificado |
| M8-031 | absorvido em modelo unificado |
| M8-041 | absorvido em modelo unificado |
| M8-051 | absorvido em modelo unificado |
| M8-059 | absorvido em modelo unificado |
| M8-088 | absorvido em modelo unificado |
| M8-105 | absorvido em modelo unificado |
| M8-107 | absorvido em modelo unificado |
| M8-109 | absorvido em modelo unificado |
| M8-111 | absorvido em modelo unificado |
| M8-114 | absorvido em modelo unificado |
| M8-115 | absorvido em modelo unificado |
| M8-118 | absorvido em modelo unificado |
| M8-123 | absorvido em modelo unificado |
| M8-126 | absorvido em modelo unificado |
| M8-127 | absorvido em modelo unificado |
| M8-128 | absorvido em modelo unificado |
| M8-129 | absorvido em modelo unificado |
| M8-136 | absorvido em modelo unificado |
| M8-138 | absorvido em modelo unificado |
| M8-139 | absorvido em modelo unificado |
| M8-146 | absorvido em modelo unificado |
| M8-147 | absorvido em modelo unificado |
| RURAL-037 | voto rural sem texto-fonte (aguarda PDF) |
| RURAL-038 | voto rural sem texto-fonte (aguarda PDF) |
| RURAL-039 | voto rural sem texto-fonte (aguarda PDF) |
| RURAL-040 | voto rural sem texto-fonte (aguarda PDF) |

### Pendências

Votos rurais sem texto-fonte no compêndio (“A informar com o PDF”), retirados até a juntada do PDF:

- RURAL-037 — 5105717-56.2026.4.03.9999 (EDcl)
- RURAL-038 — 5204226-56.2025.4.03.9999 ()
- RURAL-039 — 5151731-98.2026.4.03.9999 ()
- RURAL-040 — 0025947-82.2026.4.03.8000 (EDcl)

> A importação do app não exclui registros: para que as remoções valham, use este `modelos.json` como banco (ou exclua manualmente os registros listados).
