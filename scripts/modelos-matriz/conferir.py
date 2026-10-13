import json
F=json.load(open('src/fontes.json',encoding='utf-8')); D=json.load(open('defs.json',encoding='utf-8'))
O=json.load(open('modelos-matriz-2886.json',encoding='utf-8'))
POS=['admiss','prelim','trans','contro','jurid','fatos','provas','aplic','concl','consec','honor','complem','disp','fecho']
REV={s['substituido_por']:s['original'] for s in D['substituicoes'] if '(vocativo' not in s['substituido_por']}
def voto(reg, escolhas):
    esq=json.loads(reg['esqueletoModelo']); pars=json.loads(reg['paragrafosModelo']); out=[]
    for p in POS:
        if esq[p]['texto']: out+=esq[p]['texto'].split('\n\n')
        for t in escolhas.get(p,[]): out+=pars[t]['texto'].split('\n\n')
    return out
def desfaz(ps):
    r=[]
    for t in ps:
        for n,o in REV.items(): t=t.replace(n,o)
        r.append(t)
    return r
def orig(proc):
    v=[x for x in F[proc]['voto'] if x!='O Desembargador Federal Carlos Muta (Relator):']
    v=[x[len('Senhores Desembargadores, '):] if x.startswith('Senhores Desembargadores, ') else x for x in v]
    v=[x for x in v if x!='Senhores Desembargadores,']
    out=[]
    for x in v:  # separa a fusão conhecida do voto 01
        if x.startswith('“É despicienda') and '” No tocante' not in x and 'No tocante ao segundo grupo' in x:
            i=x.index('No tocante'); out+=[x[:i].strip(),x[i:]]
        else: out.append(x)
    return out
def cmp(nome,reg,escolhas,proc):
    a=desfaz(voto(reg,escolhas)); b=orig(proc)
    a=[x[0].lower()+x[1:] if False else x for x in a]
    norm=lambda s: s[0].lower()+s[1:]
    ok=len(a)==len(b) and all(x==y or norm(x)==norm(y) for x,y in zip(a,b))
    print(f'{nome} × {proc}: {"IDÊNTICO" if ok else "DIFERENTE"} ({len(a)} × {len(b)} parágrafos)')
    if not ok:
        import difflib
        for d in difflib.unified_diff([x[:120] for x in b],[x[:120] for x in a],lineterm='',n=0): print('   ',d)
R={r['id']:r for r in O['registros']}
h1,h2,h3=R['par-matriz-2886-territorial-provida'],R['par-matriz-2886-acordo-administrativo-desprovida'],R['par-matriz-2886-ilegitimidade-acao-sindical']
cmp('H1',h1,{'contro':[0],'honor':[2]},'5003544-88.2024.4.03.6000')
cmp('H1',h1,{'contro':[1],'complem':[3]},'5003797-42.2025.4.03.6000')
cmp('H1',h1,{'complem':[4]},'5003454-12.2026.4.03.6000')
cmp('H2',h2,{'contro':[0],'concl':[2],'disp':[6]},'5007937-56.2024.4.03.6000')
cmp('H2',h2,{'contro':[1],'concl':[3],'consec':[4,5],'disp':[7]},'5001115-51.2024.4.03.6000')
cmp('H3',h3,{},'5006675-71.2024.4.03.6000')
