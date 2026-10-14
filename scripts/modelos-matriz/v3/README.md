# Modelos-matriz de 28,86% · v3

Cumprimento individual da ACP 0005019-15.1997.4.03.6000 (28,86%) · apelação. Dois modelos-matriz no formato do
workbench 38/41 (controvérsias incluídas uma a uma, com trechos e subtópicos vinculados por `cv`):

| id | modelo | votos-fonte |
|---|---|---|
| `par-matriz-2886-acp-cumprimento` | Abrangência territorial do título: provida (C1 “a”) ou acordo administrativo, desprovida (C1 “b”); prescrição (C2). Recurso adesivo do ente sobre a gratuidade: subtópico opcional e versão do dispositivo. A prova do acordo pelas fichas do SIAPE (parágrafo de aplicação e parágrafo das fichas) é opcional dentro do bloco do acordo | 5003454, 5003797, 5003544, 5007937, 5001115 |
| `par-matriz-2886-acp-sindicato` | Exclusão do título · servidor da categoria de sindicato com ação coletiva anterior (conhecimento parcial) | 5006675 |

`modelos-2886.json` é o arquivo de importação (Paradigmas → Modelos-matriz → Importar JSON). Os mesmos registros estão em
`data/paradigmas.json` (fonte canônica do app) e em `banco/modelos.json`.

Substituem os modelos anteriores (retirados): `par-matriz-2886-territorial-provida`,
`par-matriz-2886-acordo-administrativo-desprovida`, `par-matriz-2886-ilegitimidade-acao-sindical`,
`par-modelo-f04`, `par-modelo-f05`, `par-modelo-f12` e `par-modelo-m8-039`.

Por que dois modelos e não um:
- os cinco votos do primeiro modelo têm o mesmo bloco de abrangência territorial (22 parágrafos idênticos), e o resultado só muda com a prova do acordo administrativo;
- o voto do sindicato decide outra questão, a exclusão pelo próprio título. Ele conhece só em parte da apelação justamente para não examinar a abrangência territorial.

`conferir.py Votos_28_86.docx` compara palavra por palavra cada parágrafo dos votos com os modelos. O .docx não é versionado.

Extensões do workbench usadas pela matriz (opcionais) ficam em `scripts/workbench-controversias-*.js`, no pedido #1:
- frase numerada “A controvérsia envolve discutir: (1)…; e (2)…”;
- controvérsias no topo da Minuta;
- correção do redesenho.
