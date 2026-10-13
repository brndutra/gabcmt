# gabcmt · Acórdãos e modelos do Des. Fed. Carlos Muta

Material de apoio do gabinete do Desembargador Federal Carlos Muta (Turma Regional de Mato Grosso do Sul, TRF3), no formato do **Banco de Paradigmas** do Construtor de Minutas (`schema: gabA.paradigmas`).

## Conteúdo

| Caminho | O que é |
|---|---|
| `construtor.html` | **Construtor de Minutas (Gabinete CMT)**. Lê precedentes, modelos, parágrafos e citações de `banco/` a cada abertura; publicado no GitHub Pages, lê do próprio site (`https://brndutra.github.io/gabcmt/construtor.html`). |
| `index.html` | Catálogo de 1.828 acórdãos (julgados de 18/03 a 06/10/2026), organizados por **assunto › tema › igualdade de texto**, com as especificidades de cada tema, alternância para a visão em tabela, filtros e exportação de `precedentes.json`. Arquivo único, sem dependências. |
| `precedentes/` | Os mesmos precedentes em pastas: **uma pasta por assunto** e, dentro dela, **um arquivo por tema**, com as especificidades mais frequentes. Comece pelo [`precedentes/INDICE.md`](precedentes/INDICE.md); cada pasta tem um `README.md` com os temas, resultados, especificidades e a lista de processos. |
| `data/precedentes-parte1.json` | 845 precedentes julgados de 06/07 a 06/10/2026, prontos para importar. |
| `data/precedentes-parte2.json` | 845 precedentes julgados de 18/03 a 06/07/2026, prontos para importar. |
| `data/acordaos.jsonl` | Base bruta colhida na pesquisa de jurisprudência do TRF3 (um acórdão por linha). |
| `banco/` | **Bancos do app**, como exportados pelo Construtor de Minutas: precedentes curados, modelos, parágrafos, normas, jurisprudência, assuntos e padrão de redação. Veja [`banco/README.md`](banco/README.md). |
| `modelos-matriz/modelos-matriz-2886.json` | Três Modelos-matriz de voto sobre o índice de 28,86% (ACP 0005019-15.1997.4.03.6000), com gestor de parágrafos. |
| `scripts/` | Rotinas em Python que geram o catálogo, o agrupamento e os modelos-matriz. |

## Como visualizar

Ative o GitHub Pages em **Settings › Pages**, origem **Deploy from a branch**, branch `main`, pasta `/ (root)`. O endereço publicado abre o `index.html`. O arquivo também funciona aberto direto do computador.

## Como importar no Construtor de Minutas

- **Precedentes:** Banco de Paradigmas › Precedentes › **Importar JSON**, uma parte de cada vez (cada uma fica abaixo do limite de 10 MB do servidor). A importação casa por `id` e não apaga registros ausentes do arquivo. Os 138 processos que já constavam do banco ficaram de fora das partes; no `index.html`, marque "Incluir os que já constam do banco" para exportá-los também.
- **Por assunto ou tema:** cada `.json` dentro de `precedentes/<assunto>/` é um arquivo de importação completo, com só os acórdãos ainda fora do banco. Importe apenas os temas que interessam.
- **Modelos-matriz:** Banco de Paradigmas › Modelos-matriz › **Importar JSON**, com `modelos-matriz-2886.json`.

## Organização por similaridade

Cada precedente traz, além dos campos do banco:

- `temaId`, `temaRotulo`, `temaTamanho`, `temaRepresentante`: o **tema** reúne, dentro do mesmo assunto, os casos que discutem a mesma questão jurídica (cabeçalho da ementa, "Questão em discussão" e "Tese de julgamento", comparados por TF-IDF e cosseno). Embargos de declaração formam temas próprios.
- `similaridadeTema` (0–100) e `grauIgualdade`: quanto o texto integral da ementa coincide com o do caso representante do tema: `idêntico` (≥ 95%), `quase idêntico` (≥ 85%), `similar` (≥ 60%), `mesma questão` (abaixo disso), `representante` ou `único`.
- `modeloTextoId`, `modeloTextoTamanho`: ementas com o mesmo texto-base (≥ 85%), em qualquer assunto.
- `sentidoResultado`: provido, parcialmente provido, desprovido, não conhecido, rejeitados, acolhidos, prejudicado/extinto.

O agrupamento é automático; os rótulos dos temas vêm das próprias ementas e devem ser conferidos antes de servir como classificação oficial. Todos os registros saem com `statusCuradoria: bruto`.

## Modelos-matriz de 28,86%

Construídos a partir do texto integral de seis votos julgados em 05/10/2026, sem alteração redacional. Só os dados do caso concreto viraram variáveis `{{TIPO_DA_INFORMACAO}}`.

| Modelo-matriz | Votos de origem |
|---|---|
| Limite territorial afastado · apelação provida | 5003454-12.2026, 5003797-42.2025, 5003544-88.2024 |
| Acordo administrativo (fichas SIAPE) · apelação desprovida | 5007937-56.2024, 5001115-51.2024 |
| Ilegitimidade ativa · ação coletiva anterior de sindicato · apelação desprovida | 5006675-71.2024 |

Os parágrafos presentes em todos os votos de uma hipótese formam o texto-base; os que aparecem só em parte deles ficam no gestor de parágrafos como opções situacionais.

## Sem duplicidade

Cada precedente aparece uma única vez como arquivo de importação:

- se já está no banco do app, fica só em `banco/precedentes.json` (ou é citado em `banco/modelos.json`) e sai de `precedentes/` e de `data/precedentes-parte*.json`;
- se ainda não está, fica só no catálogo (`precedentes/` e `data/`), com `statusCuradoria: bruto`.

Quando o mesmo processo tem outro julgamento já curado (por exemplo, a apelação no banco e os embargos de declaração no catálogo), o do catálogo recebe id próprio (`par-<processo>-<espécie>-<data>`), para que importá-lo não sobrescreva o registro curado.

## Como atualizar

Exporte os bancos no app e rode, na raiz do repositório:

```
python3 scripts/construir.py normas.json paragrafos.json precedentes.json modelos.json assuntos.json jurisprudencia.json redacao.json
```

Os arquivos são reconhecidos pelo `schema`, não pelo nome. A importação mescla por `id` (atualiza o que existe, acrescenta o que é novo, não apaga nada) e elimina duplicatas pela chave natural de cada banco: processo e espécie nos precedentes, sigla nas normas, referência na jurisprudência, nome nos assuntos, texto nos parágrafos. Com `--substituir`, a exportação passa a ser a fotografia oficial do banco, e registros apagados no app saem também daqui. Em seguida o script refaz o catálogo, a pasta `precedentes/`, as duas partes de `data/` e o `index.html`. Requer `scikit-learn` e `numpy`.

## Scripts

- `scripts/construir.py`: executa todas as etapas acima.
- `scripts/banco/importar.py`: só a importação dos bancos para `banco/`, sem refazer o catálogo.

- `scripts/catalogo/`: `acumular.py` regenera o catálogo a partir de `acordaos.jsonl` (copie o arquivo de `data/` para a pasta do script); `paradigma.py` converte cada acórdão para o formato do banco; `similaridade.py` faz o agrupamento; `organizar.py` monta a pasta `precedentes/` a partir de `catalogo-agrupado.json` (gerado pelo `acumular.py`); `extrair.py` lê os lotes colhidos no portal. Requer `scikit-learn` e `numpy`.
- `scripts/modelos-matriz/`: extração dos votos dos PDFs do PJe (`extrair_pdf.py`, `estruturar.py`, requer `pymupdf`), montagem (`montar.py`), geração do JSON (`gerar.py`) e conferência de fidelidade ao texto original (`conferir.py`). Os PDFs de origem não estão no repositório.
