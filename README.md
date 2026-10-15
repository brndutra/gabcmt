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
  acervo.json          acervo geral de processos do gabinete (Painel Central), inclusive sigilosos
construtor.html        Construtor de Minutas
painel.html            Painel Central (acervo · seleção · pauta), ligado a banco/acervo.json
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

## Acervo geral (Painel Central)

`banco/acervo.json` (`schema: gabA.acervo`, formato 2) é o **espelho do Painel Central**: guarda o acervo como ele está no navegador, um processo por linha, identificado pelo número (`acv-<20 dígitos>`). Cada processo leva **todas as colunas do Acervo Central** — dados das planilhas e controles de trabalho (etiquetas atuais, Tema, Especificidades, Síntese Processual, complexidade, servidor, regularidade, voto, Seleção Prévia, pauta…) — e, no campo `_`, o estado interno da linha (triagem e escaninho, ordem da seleção, participações em pauta, histórico, intercorrências, etiquetas convertidas). Em `painel` fica o estado geral (sessões e marcos, equipe, calendário, escaninhos, configuração de colunas) e em `colunas`, a lista completa das colunas. `banco/acervo.csv` é a mesma base como planilha, com todas essas colunas (o GitHub a mostra como tabela). Quem alimenta os dois arquivos é o `painel.html` (publicado em `https://brndutra.github.io/gabcmt/painel.html`):

- **cada edição salva** no navegador carimba o processo alterado (`atualizado_em`); o estado geral também é carimbado;
- **ao clicar em SALVAR** e **após cada importação** (planilhas Gab A, PJe 2G ou arquivo do banco), com a opção ligada (padrão), o painel encaminha ao GitHub, num único commit, `acervo.json` e `acervo.csv` — basta informar um token com permissão *Contents: leitura e escrita*, que fica só na memória da aba. Antes de gravar, traz o que estiver mais recente no GitHub (outro computador);
- **ao abrir**, o painel lê o banco e aplica o que estiver mais recente que a cópia do navegador: processos e estado geral;
- a mescla é por processo (e, à parte, para o estado geral): prevalece a alteração mais recente, nada é apagado (há um botão à parte para substituir o banco inteiro);
- pelo diálogo **Banco do Acervo Geral** também se exporta o banco como `acervo.json`, `acervo.csv` ou `acervo.html` (tabela legível com o JSON embutido) e se importa `.json`/`.html`.

### Sessões, calendário e equipe (`banco/gabinete.json`)

`banco/gabinete.json` (`schema: gabA.gabinete`) é a **fonte única** das sessões de julgamento e seus marcos (`date`, `pautaDeadline`, `prepStart`, `minutasDeadline`, `releaseDeadline`, datas AAAA-MM-DD), do calendário de trabalho (`calendario.weekdays`, dias da semana de 0 = domingo a 6 = sábado, e `calendario.excluded`, feriados e folgas), dos servidores (atribuições em `functions`, especialidades, escopo das minutas e ausências) e do catálogo de atribuições (`equipe.catalog`). O painel **só lê** este arquivo: ao abrir e pelo botão **Atualizar conforme o repositório** da aba **Gabinete** das Configurações Globais (que reúne, em modo consulta, as antigas abas Calendário, Sessões, Servidores e Atribuições). Para mudar qualquer desses dados, edite o arquivo no repositório. A única exceção são **início da produção**, **entrega das minutas** e **liberação**: alterados na Seleção Prévia (na sessão escolhida), são gravados aqui na hora. Sem dados pessoais (repositório público): perfis, históricos e contatos dos servidores ficam só no navegador.

No repositório, o mesmo arquivo exportado entra por `python3 scripts/construir.py acervo.html` (ou `acervo.json`), com a mesma regra: prevalece a versão mais recente de cada processo.

**Saneamento** (o repositório é público): campos de celular, telefone, e-mail e CPF são removidos em qualquer nível (inclusive no estado interno e no estado geral) — no painel e de novo no `importar.py`; esses campos continuam só no navegador. Os processos **sigilosos entram** no banco (com `Consta_Acervo_Sigiloso` e `Nível_Sigilo`), porque a planilha Gab A - Sigilosos já mascara as informações sigilosas com `###`.

**Montagem do painel.** `painel.html` é gerado por `python3 scripts/painel/montar.py` a partir da versão baixada do app (guardada em `scripts/painel/original/painel-central.html`; para uma versão nova, passe o arquivo baixado como argumento). A montagem:

- grava o painel **desempacotado** (React, runtime, planilhas e fontes embutidos direto): abre sem a etapa de descompactação e sem o logotipo gigante “Unpacking…”, com uma tela de carregamento discreta até o banco local terminar de carregar;
- aplica os ajustes de `scripts/painel/melhorias.py`: funções de normalização de colunas memorizadas e listas ocultas desenhadas só quando abertas (com 3.000 processos, a abertura caiu de 15–19 s para cerca de 3,5 s); na tela Acervo Central, Assuntos · Classes processuais · Tarefas atuais na primeira linha, em larguras iguais, e **Antiguidade do acervo** à esquerda de **Processos por seção**, na mesma altura fixa; e cards de processo que, abertos, mostram só os **controles de trabalho da planilha da Seleção Prévia**;
- refaz, na Seleção Prévia, o **planejamento da sessão** (`scripts/painel/planejamento.py`): *01 · Marcos da sessão* em uma só linha (sessão, cinco marcos com os dias úteis entre eles, dias de produção, capacidade × restantes, entrega ideal e tempo decorrido × entregue) e *02 · Simulador* em card de altura fixa, com a estatística da distribuição no cabeçalho e lista rolável de metas por servidor (meta/dia planejada = designados ÷ dias úteis do início à entrega; meta/dia para entregar = restantes ÷ dias úteis que faltam; andamento contra o esperado; término no ritmo habitual);
- cria a aba **Triagem Processual** (`scripts/painel/triagem.py`): no Acervo Central, o seletor de sessão destino ganha a opção “Triagem Processual” (botão ENCAMINHAR); na aba, a **bandeja da triagem** (fichas dos processos ainda sem pasta) fica ao lado do **móvel de escaninhos** — nichos com placa (título e subtítulo), pilha de autos, bilhete de observação e cor da pasta. Marcam-se as fichas e clica-se no escaninho (ou arrastam-se até ele); clicar num escaninho o abre logo abaixo, no próprio móvel, para editar a placa e o bilhete e ver ou devolver os processos guardados. Nada disso altera Seleção Prévia, sessão ou pauta. A triagem e os escaninhos são gravados no navegador e espelhados em `banco/acervo.json` com os demais controles de trabalho;
- reúne no diálogo **Banco do Acervo Geral** (`scripts/painel/banco_dialogo.py`) tudo o que era da página Importar / atualizar e do bloco Operações da barra lateral: sincronização com o GitHub, exportações (XLSX completo e acervo sem controles), importação da planilha principal, em lote e suplementares, registro dos arquivos e ocorrências de importação; abre pelo botão da barra lateral ou pelo botão flutuante ACERVO · GITHUB;
- injeta `scripts/painel/acervo-github.js` (banco do acervo no GitHub).

Cada ajuste é uma troca exata no código do painel: se uma versão nova do app mudar o trecho, a montagem para e diz qual ajuste revisar, em vez de gerar um painel quebrado.

## Catálogo de acórdãos do TRF3

`catalogo-trf3/` reúne 1.828 acórdãos do relator (julgados de 18/03 a 06/10/2026), colhidos no portal do TRF3 (`acordaos.jsonl`) e organizados por **assunto** e, dentro do assunto, por **tema** (mesma questão jurídica), com as especificidades mais frequentes. Comece por [`catalogo-trf3/INDICE.md`](catalogo-trf3/INDICE.md). O `index.html` mostra o mesmo catálogo com busca, filtros, visão agrupada ou em tabela e exportação para o app.

Sem duplicidade: o que já está em `banco/precedentes.json` (ou é citado em `banco/modelos.json`) não entra nos arquivos de importação do catálogo; aparece nos índices com a marca *(no banco)*. Quando o mesmo processo tem outro julgamento já curado (ex.: a apelação no banco e os embargos de declaração no catálogo), o do catálogo recebe id próprio (`par-<processo>-<espécie>-<data>`), para não sobrescrever o curado ao importar.

Campos acrescentados aos acórdãos do catálogo: `temaId`, `temaRotulo`, `temaTamanho`, `temaRepresentante`, `similaridadeTema`, `grauIgualdade` (idêntico, quase idêntico, similar, mesma questão, representante, único), `modeloTextoId`, `modeloTextoTamanho` e `sentidoResultado`. O agrupamento é automático; todos saem com `statusCuradoria: bruto`.

## Scripts

- `scripts/construir.py`: importa os bancos, refaz o catálogo, `catalogo-trf3/` e o `index.html`.
- `scripts/banco/importar.py`: só a importação dos bancos para `banco/`.
- `scripts/catalogo/`: geração do catálogo (`acumular.py`, `paradigma.py`, `similaridade.py`, `organizar.py`, `extrair.py`).
- `scripts/modelos-matriz/`: extração de votos dos PDFs do PJe (`extrair_pdf.py`, `estruturar.py`) e, em `v3/`, os dois modelos-matriz de 28,86% (abrangência territorial; exclusão por ação sindical), com a conferência literal com os votos-fonte.
