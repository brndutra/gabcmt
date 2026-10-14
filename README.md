# gabcmt · Gabinete do Des. Fed. Carlos Muta

Construtor de Minutas e bancos do gabinete do Desembargador Federal Carlos Muta (Turma Regional de Mato Grosso do Sul, TRF3).

## Estrutura

```
banco/                 um arquivo por banco (é daqui que o construtor.html lê e grava)
  precedentes.json     precedentes curados
  modelos.json         modelos, inclusive os antigos modelos-matriz (hoje unificados)
  assuntos.json        catálogo de assuntos (TPU/CNJ, seções, sinônimos)
  jurisprudencia.json  temas, súmulas e precedentes de referência
  redacao.json         padrão de redação: conectivos, verbos, preferências, correções, alertas
  paragrafos.json      parágrafos-modelo do gestor de parágrafos
  normas.json          normas: siglas, aliases e forma por extenso
construtor.html        Construtor de Minutas
index.html             catálogo de acórdãos do TRF3 (visualização)
catalogo-trf3/         base bruta de acórdãos colhida no portal do TRF3, à espera de curadoria (não é banco)
scripts/               rotinas de importação e de geração do catálogo
```

## Bancos

Cada banco é um único arquivo em `banco/`, no formato das exportações do app (`schema: gabA.<banco>`, lista `registros`). O `construtor.html` os lê a cada abertura; publicado no GitHub Pages, lê do próprio site (`https://brndutra.github.io/gabcmt/construtor.html`). Contagens em [`banco/README.md`](banco/README.md).

Para atualizar a partir do app, exporte os bancos e rode na raiz do repositório:

```
python3 scripts/construir.py precedentes.json modelos.json assuntos.json jurisprudencia.json redacao.json paragrafos.json normas.json
```

Os arquivos são reconhecidos pelo `schema`, não pelo nome; uma exportação conjunta `gabA.paradigmas` é separada em precedentes e modelos. A importação mescla por `id` (atualiza o que existe, acrescenta o que é novo, não apaga nada) e elimina duplicatas pela chave natural de cada banco: processo e espécie nos precedentes, sigla nas normas, referência na jurisprudência, nome nos assuntos, texto nos parágrafos. Com `--substituir`, a exportação vira a fotografia oficial do banco, e o que foi apagado no app sai também daqui. Requer `scikit-learn` e `numpy`.

## Catálogo de acórdãos do TRF3

`catalogo-trf3/` reúne 1.828 acórdãos do relator (julgados de 18/03 a 06/10/2026), colhidos no portal do TRF3 (`acordaos.jsonl`) e organizados por **assunto** e, dentro do assunto, por **tema** (mesma questão jurídica), com as especificidades mais frequentes. Comece por [`catalogo-trf3/INDICE.md`](catalogo-trf3/INDICE.md). O `index.html` mostra o mesmo catálogo com busca, filtros, visão agrupada ou em tabela e exportação para o app.

Sem duplicidade: o que já está em `banco/precedentes.json` (ou é citado em `banco/modelos.json`) não entra nos arquivos de importação do catálogo; aparece nos índices com a marca *(no banco)*. Quando o mesmo processo tem outro julgamento já curado (ex.: a apelação no banco e os embargos de declaração no catálogo), o do catálogo recebe id próprio (`par-<processo>-<espécie>-<data>`), para não sobrescrever o curado ao importar.

Campos acrescentados aos acórdãos do catálogo: `temaId`, `temaRotulo`, `temaTamanho`, `temaRepresentante`, `similaridadeTema`, `grauIgualdade` (idêntico, quase idêntico, similar, mesma questão, representante, único), `modeloTextoId`, `modeloTextoTamanho` e `sentidoResultado`. O agrupamento é automático; todos saem com `statusCuradoria: bruto`.

## Scripts

- `scripts/construir.py`: importa os bancos, refaz o catálogo, `catalogo-trf3/` e o `index.html`.
- `scripts/banco/importar.py`: só a importação dos bancos para `banco/`.
- `scripts/catalogo/`: geração do catálogo (`acumular.py`, `paradigma.py`, `similaridade.py`, `organizar.py`, `extrair.py`).
- `scripts/modelos-matriz/`: extração de votos dos PDFs do PJe (`extrair_pdf.py`, `estruturar.py`) e, em `v3/`, os dois modelos-matriz de 28,86% (abrangência territorial; exclusão por ação sindical), com a conferência literal com os votos-fonte.
