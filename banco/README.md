# Banco do Construtor de Minutas

Exportações dos bancos do app, importadas por `scripts/banco/importar.py` (sem duplicatas: por id e por chave natural).

| Arquivo | Conteúdo | Registros | Versão |
|---|---|---:|---|
| [`acervo.json`](acervo.json) | Acervo geral de processos do gabinete (Painel Central), saneado: sem sigilosos, celulares e CPF | 0 | 2026-10-14 |
| [`assuntos.json`](assuntos.json) | Catálogo de assuntos (TPU/CNJ, seções e sinônimos) | 556 | 2026-10-13 |
| [`jurisprudencia.json`](jurisprudencia.json) | Jurisprudência de referência (temas, súmulas, precedentes qualificados) | 42 | 2026-10-13 |
| [`modelos.json`](modelos.json) | Modelos do Banco de Paradigmas, inclusive os antigos modelos-matriz (hoje unificados) | 202 | 2026-10-14 |
| [`normas.json`](normas.json) | Catálogo de normas (siglas, aliases e forma por extenso) | 56 | 2026-10-13 |
| [`paragrafos.json`](paragrafos.json) | Parágrafos-modelo do gestor de parágrafos | 120 | 2026-10-13 |
| [`precedentes.json`](precedentes.json) | Precedentes curados do Banco de Paradigmas | 64 | 2026-10-13 |
| [`redacao.json`](redacao.json) | Padrão de redação: conectivos, verbos, preferências, correções e alertas | 136 | 2026-10-13 |

Para atualizar: exporte cada banco no app e rode `python3 scripts/construir.py ARQUIVOS.json`.

O acervo (`acervo.json`) é atualizado pelo próprio Painel Central (`painel.html`): cada importação de planilha é encaminhada ao GitHub. Também aceita `python3 scripts/construir.py acervo.html` (ou `acervo.json`) exportado do painel. Saneamento: sem processos sigilosos, celulares, telefones, e-mails e CPF.
