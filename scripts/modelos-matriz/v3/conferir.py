"""Confere, palavra por palavra, os modelos-matriz de 28,86% (data/paradigmas.json) com os votos-fonte.

Uso:  python scripts/modelos-matriz/v3/conferir.py Votos_28_86.docx
O .docx (seis votos com as questões marcadas por cor; não versionado, pois contém dados das partes) traz,
para cada processo, um título “Processo NNNNNNN-…” (Título 1) e a seção “Voto” (Título 2).
Cada parágrafo do voto é comparado com o parágrafo mais próximo dos modelos; o relatório lista só as diferenças.
Diferenças esperadas: dados do caso (→ variáveis @ e campos {{ }}), o vocativo inicial (cabeçalho fixo do app)
e artefatos do .docx (hífen seguido de espaço, parágrafos partidos ou emendados)."""
import json, re, sys, difflib, unicodedata
from pathlib import Path
from docx import Document

RAIZ = Path(__file__).resolve().parents[3]
IDS = ('par-matriz-2886-acp-cumprimento', 'par-matriz-2886-acp-sindicato')
N = lambda s: ' '.join(unicodedata.normalize('NFC', s).replace('\xa0', ' ').split())
TOK = lambda s: re.findall(r'\w+|[^\w\s]', s)


def paragrafos_dos_modelos():
    d = json.loads((RAIZ / 'data' / 'paradigmas.json').read_text(encoding='utf-8'))
    regs = {r['id']: r for r in d['bancos']['Modelo-matriz']['registros'] if r['id'] in IDS}
    assert set(regs) == set(IDS), f'modelos ausentes em data/paradigmas.json: {set(IDS) - set(regs)}'
    out = []
    for rid, r in regs.items():
        esq, pars = json.loads(r['esqueletoModelo']), json.loads(r['paragrafosModelo'])
        textos = [(k, v['texto']) for k, v in esq.items() if isinstance(v, dict)] + [(p['id'], p['texto']) for p in pars]
        for k, t in textos:
            out += [(f'{rid[18:]}:{k}', N(re.sub(r'^> ', '', x.strip()))) for x in t.split('\n\n') if x.strip()]
    return out


def votos(docx):
    atual, sec, V = None, None, {}
    for p in Document(docx).paragraphs:
        st, t = p.style.name, p.text.strip()
        if st == 'Heading 1' and t.startswith('Processo'):
            atual, sec = t.split()[-1], None; V[atual] = []; continue
        if st == 'Heading 2':
            sec = t; continue
        if atual and sec == 'Voto' and t and not t.startswith('O Desembargador Federal') and t != 'É como voto.':
            t = re.sub(r'^Senhores Desembargadores,\s*', '', N(t))
            if V[atual] and re.search(r'\d-$', V[atual][-1]):  # parágrafo partido no meio de um número (artefato do .docx)
                V[atual][-1] += t
            else:
                V[atual].append(t)
    return V


def main(docx):
    M, total, iguais = paragrafos_dos_modelos(), 0, 0
    for proc, L in votos(docx).items():
        print(f'\n## {proc}')
        for s in L:
            total += 1
            onde, t = max(M, key=lambda m: difflib.SequenceMatcher(None, s, m[1], autojunk=False).ratio())
            if s.lower() == t.lower() or TOK(s) == TOK(t):
                iguais += 1; continue
            a, b = TOK(s), TOK(t)
            for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
                if op != 'equal':
                    print(f'  [{onde}] {op}: voto «{" ".join(a[i1:i2])[:160]}» → modelo «{" ".join(b[j1:j2])[:160]}»')
    print(f'\n{iguais}/{total} parágrafos idênticos (inclusive pontuação); os demais estão listados acima.')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'Votos_28_86.docx')
