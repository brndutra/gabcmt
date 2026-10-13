import sys, os, re, json, glob
sys.path.insert(0,'/home/claude/matriz'); import extrair_pdf as X
FONTES='/home/claude/fontes2886'
HEAD={'RELATÓRIO':'relatorio','VOTO':'voto','EMENTA':'ementa','ACÓRDÃO':'acordao'}
def estrutura_padrao(ps):
    sec=None; out={'cab':[], 'relatorio':[],'voto':[],'ementa':[],'acordao':[]}
    for p in ps:
        if p['bold'] and p['size']>=14 and p['t'] in HEAD: sec=HEAD[p['t']]; continue
        out[sec or 'cab'].append(p['t'])
    return out
def estrutura_semnum(ps, inicios):
    # quebra parágrafos fundidos em inícios conhecidos de outros votos
    txts=[]
    for p in ps:
        t=p['t']
        if re.match(r'(PODER JUDICIÁRIO|Rua Ceará|APELAÇÃO CÍVEL \(198\))',t): continue
        cortes=sorted({m.start()+2 for s in inicios for m in re.finditer(r'[.:;]\s'+re.escape(s),t)})
        prev=0
        for c in cortes: txts.append(t[prev:c].strip()); prev=c
        txts.append(t[prev:].strip())
    out={'cab':[],'relatorio':[],'voto':[],'ementa':[],'acordao':[]}; sec='ementa'
    for t in txts:
        if t.startswith('Trata-se de apelação'): sec='relatorio'
        if t.startswith('O Desembargador Federal Carlos Muta'): sec='voto'
        out[sec].append(t)
        if t=='É o relatório.' : sec='voto_'  # próximo
        if sec=='voto_': sec='voto'
    return out
def limpar_sigiloso(e, conhecidos=frozenset()):
    for k in ('relatorio','voto','ementa','acordao','cab'):
        out=[]; cont=False
        for t in e[k]:
            if t.strip()=='SIGILOSO': cont=True; continue
            if t.startswith('SIGILOSO '): t=t[9:]; cont=True
            if cont and out and (not re.search(r'[.:;”"!?]$',out[-1]) or (out[-1]+' '+t) in conhecidos): out[-1]=out[-1]+' '+t
            else: out.append(t)
            cont=False
        e[k]=out
    return e
res={}
arqs=sorted(f for f in os.listdir(FONTES) if f.endswith('.pdf'))
padrao={}
for f in arqs:
    docs=X.documentos(os.path.join(FONTES,f))
    reais=[k for k in docs if k!='SEM-NUM']
    if not reais: continue
    first=docs[reais[0]]
    padrao[f]=estrutura_padrao(first)
inicios={p[:45] for e in padrao.values() for k in ('voto','relatorio') for p in e[k] if len(p)>60}
for f in arqs:
    if f in padrao: e=padrao[f]
    else:
        docs=X.documentos(os.path.join(FONTES,f)); e=estrutura_semnum(docs['SEM-NUM'],inicios)
    m=re.search(r'\d{7}-\d{2}\.\d{4}\.4\.03\.\d{4}',f); e['processo']=m.group(0); e['arquivo']=f
    res[e['processo']]=e
conhecidos=frozenset(p for e in res.values() if 'SIGILOSO' not in json.dumps(e,ensure_ascii=False) for k in ('voto','relatorio','ementa') for p in e[k])
for e in res.values():
    limpar_sigiloso(e, conhecidos)
    print(e['processo'], {k:len(v) for k,v in e.items() if isinstance(v,list)})
json.dump(res,open('/home/claude/matriz/src/fontes.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
