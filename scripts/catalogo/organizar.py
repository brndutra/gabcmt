"""Organiza o catálogo em pastas: precedentes/<assunto>/<tema>.json, com índice geral e um README por assunto.

Cada arquivo .json é um arquivo de importação válido do Banco de Paradigmas (gabA.paradigmas · Precedente)
e contém só os acórdãos que ainda NÃO constam do banco do gabinete (importar os demais sobrescreveria a curadoria).
Os que já constam aparecem nos índices, marcados.

Uso: python3 organizar.py <catalogo-agrupado.json> <pasta-destino>
"""
import collections
import json
import re
import shutil
import sys
import unicodedata
from datetime import date
from pathlib import Path

SENT = ['provido', 'parcialmente provido', 'desprovido', 'não conhecido', 'rejeitados', 'acolhidos', 'prejudicado/extinto', 'outro']


def slug(t, n=60):
    t = unicodedata.normalize('NFKD', t or '').encode('ascii', 'ignore').decode().lower()
    t = re.sub(r'[^a-z0-9]+', '-', t).strip('-')
    return (t[:n].rstrip('-')) or 'sem-nome'


def tags(r):
    return [x.strip() for x in (r.get('especificidadesTags') or '').split(';') if x.strip()]


def especificidades(membros, limite=8):
    c = collections.Counter()
    for r in membros:
        c.update(set(tags(r)))
    n = len(membros)
    return [(t, k) for t, k in sorted(c.items(), key=lambda x: (-x[1], x[0])) if n == 1 or k >= max(2, 0.2 * n)][:limite]


def resultados(membros):
    c = collections.Counter(r.get('sentidoResultado', 'outro') for r in membros)
    return ', '.join(f'{c[s]} {s}' for s in SENT if c[s])


def limpo(r):
    return {k: v for k, v in r.items() if not k.startswith('_')}


def arquivo_import(regs):
    return json.dumps({'schema': 'gabA.paradigmas', 'schema_versao': 1, 'versao': '1.0.0',
                       'atualizado_em': date.today().isoformat(), 'banco_tipo': 'Precedente',
                       'registros': [limpo(r) for r in regs]}, ensure_ascii=False, indent=2) + '\n'


def md(t):
    return str(t or '').replace('|', '\\|').replace('\n', ' ')


def main(origem, destino):
    R = json.loads(Path(origem).read_text(encoding='utf-8'))
    dest = Path(destino)
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)

    por_ass = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in R:
        por_ass[r.get('assunto') or 'Sem assunto'][r['temaId']].append(r)
    ordem = sorted(por_ass, key=lambda a: (-sum(len(v) for v in por_ass[a].values()), a))

    indice = [f'# Precedentes do Des. Fed. Carlos Muta por assunto e tema\n',
              f'{len(R)} acórdãos em {len(ordem)} assuntos. Dentro de cada assunto, os casos estão reunidos por **tema** '
              '(mesma questão jurídica), com as **especificidades** mais frequentes de cada tema.\n',
              'Cada arquivo `.json` importa no Banco de Paradigmas › Precedentes › Importar JSON e traz apenas os '
              'acórdãos que ainda não constam do banco; os que já constam aparecem nos índices com a marca *(no banco)*.\n',
              '| # | Assunto | Acórdãos | Temas com 2+ casos | Casos sem par | Pasta |', '|---:|---|---:|---:|---:|---|']
    totais = {'arquivos': 0, 'registros': 0}

    for n, ass in enumerate(ordem, 1):
        temas = por_ass[ass]
        pasta = dest / f'{n:02d}-{slug(ass, 50)}'
        pasta.mkdir()
        multi = sorted((t for t in temas if len(temas[t]) > 1), key=lambda t: (-len(temas[t]), t))
        unicos = sorted(t for t in temas if len(temas[t]) == 1)
        total = sum(len(v) for v in temas.values())
        indice.append(f'| {n} | {md(ass)} | {total} | {len(multi)} | {len(unicos)} | [{pasta.name}]({pasta.name}/README.md) |')

        leia = [f'# {ass}\n', f'{total} acórdãos · {len(multi)} temas com dois ou mais casos · {len(unicos)} {"caso" if len(unicos)==1 else "casos"} sem par.\n',
                '[← Índice geral](../INDICE.md)\n', '## Temas\n',
                '| Tema | Casos | Resultados | Especificidades | Arquivo |', '|---|---:|---|---|---|']
        detalhes = []

        def grava(nome, membros):
            novos = [r for r in membros if not r.get('_noBanco')]
            if not novos:
                return '*(todos já no banco)*'
            (pasta / nome).write_text(arquivo_import(novos), encoding='utf-8')
            totais['arquivos'] += 1
            totais['registros'] += len(novos)
            return f'[{nome}]({nome})' + (f' ({len(novos)} de {len(membros)})' if len(novos) < len(membros) else '')

        for t in multi:
            v = sorted(temas[t], key=lambda r: (SENT.index(r.get('sentidoResultado', 'outro')), -r.get('similaridadeTema', 0)))
            rot = v[0]['temaRotulo']
            nome = f'{t}-{slug(re.sub(r"^Embargos de declaração · ", "edcl ", rot), 55)}.json'
            link = grava(nome, v)
            esp = '; '.join(f'{x} ({k})' for x, k in especificidades(v))
            leia.append(f'| **{t}** · {md(rot)} | {len(v)} | {resultados(v)} | {md(esp)} | {link} |')
            linhas = '\n'.join(
                f'| {r["processo"]}{" *(no banco)*" if r.get("_noBanco") else ""} | {r.get("sessao", "")} | {r.get("sentidoResultado", "")} | '
                f'{r.get("grauIgualdade", "")}{"" if r.get("grauIgualdade") in ("representante", "único") else " · " + str(r.get("similaridadeTema", "")) + "%"} | '
                f'{md("; ".join(tags(r)))} |' for r in v)
            detalhes.append(f'<details><summary><b>{t}</b> · {md(rot)} — {len(v)} casos</summary>\n\n'
                            f'| Processo | Julgamento | Resultado | Semelhança com o representante | Especificidades |\n|---|---|---|---|---|\n{linhas}\n\n</details>\n')

        if unicos:
            v = [temas[t][0] for t in unicos]
            link = grava('casos-sem-par.json', v)
            leia.append(f'| Casos sem par | {len(v)} | {resultados(v)} | questões que aparecem uma só vez | {link} |')
            linhas = '\n'.join(f'| {r["processo"]}{" *(no banco)*" if r.get("_noBanco") else ""} | {r.get("sessao", "")} | '
                               f'{r.get("sentidoResultado", "")} | {md(r.get("temaRotulo"))} | {md("; ".join(tags(r)))} |' for r in v)
            detalhes.append(f'<details><summary><b>Casos sem par</b> — {len(v)} casos</summary>\n\n'
                            f'| Processo | Julgamento | Resultado | Questão | Especificidades |\n|---|---|---|---|---|\n{linhas}\n\n</details>\n')

        leia += ['', '## Casos de cada tema\n', *detalhes]
        (pasta / 'README.md').write_text('\n'.join(leia) + '\n', encoding='utf-8')

    indice += ['', f'Arquivos de importação: {totais["arquivos"]}, com {totais["registros"]} precedentes ainda fora do banco.']
    (dest / 'INDICE.md').write_text('\n'.join(indice) + '\n', encoding='utf-8')
    print(f'{len(ordem)} assuntos · {totais["arquivos"]} arquivos · {totais["registros"]} registros')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
