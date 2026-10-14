"""Reconstrói cada voto-fonte a partir do modelo (escolhas da Minuta + campos preenchidos com os dados originais) e compara."""
import json, re, sys
from pathlib import Path
AQUI=Path(__file__).parent
V=json.load(open(AQUI/'votos.json'))
R={r['id']:r for r in json.load(open(AQUI.parents[2]/'banco'/'modelos.json'))['registros']}
SEL={
 '5003454':('par-matriz-2886-territorial-provida',['prelim-01a','prelim-02a','!contro-01','jurid-*','prescr-01b','prescr-02a','prescr-03a'],{}),
 '5003797':('par-matriz-2886-territorial-provida',['prelim-01a','prelim-02a','contro-01b','jurid-*','prescr-01a','prescr-02a','prescr-03a'],{}),
 '5003544':('par-matriz-2886-territorial-provida',['prelim-01a','prelim-02a','contro-01a','jurid-*','honor-01a'],{'@REU_DE':'da União'}),
 '5007937':('par-matriz-2886-acordo-administrativo-desprovida',['contro-01a','jurid-*','acordo-*','fatos-01a','fatos-02a','concl-01a','honor-01b','disp-01a'],{'@HONORARIOS_PERCENTUAL_ADICIONAL':'1%','{{ID das fichas financeiras}}':'388960832'}),
 '5001115':('par-matriz-2886-acordo-administrativo-desprovida',['contro-01b','jurid-*','acordo-*','fatos-01b','fatos-02a','concl-01b','mafe-*','gratuid-*','honor-01b','disp-01b'],{'@HONORARIOS_PERCENTUAL_ADICIONAL':'1%','{{IDs das fichas financeiras}}':'385140944, 385140957, 385140958, 385140959 e 385140960','@REU_DE':'da FUNASA'}),
 '5006675':('par-matriz-2886-ilegitimidade-acao-sindical',['admiss-*','contro-*','jurid-*','aplic-*','concl-*','honor-01b'],{'@HONORARIOS_PERCENTUAL_ADICIONAL':'1%','{{nome e sigla do sindicato}}':'Sindicato dos Trabalhadores Federais em Seguridade e Seguro Social no Estado do Rio de Janeiro (SINDSPREV/RJ)','{{nº da ação coletiva do sindicato}}':'0023278-37.1995.4.02.5101','{{sigla do sindicato}}':'SINDSPREV/RJ','{{data do ajuizamento da ação do sindicato}}':'25/09/1995','{{categoria e base territorial representadas pelo sindicato}}':'trabalhadores em instituições de saúde, trabalho e previdência social, com vínculo federal direto, indireto e funcional, lotados no Estado do Rio de Janeiro','@RECORRENTE_DE':'do apelante','{{ID e folha do documento}}':'376094580, f. 38'}),
}
def escolhidos(rid,sel):
    r=R[rid];P=json.loads(r['paragrafosModelo']);out=[]
    for i,p in enumerate(P):
        tid=p['posicao'];ps=[q for q in P if q['posicao']==tid]
        if f"{tid}-*" in sel or f"{tid}-{p['ordem']:02d}{p['versao']}" in sel: out.append(i);continue
        if f"!{tid}-{p['ordem']:02d}" in sel: continue
        if p['opcional'] is False and not any(f"{tid}-{q['ordem']:02d}{q['versao']}" in sel for q in ps if q['ordem']==p['ordem']): out.append(i)
    return out
def montar(rid,sel,subs):
    r=R[rid];e=json.loads(r['esqueletoModelo']);P=json.loads(r['paragrafosModelo'])
    out=[]
    for t in e['_topicos']:
        tid=t['id'];base=e[tid]['texto'] if e[tid]['ativo'] else ''
        ps=[p for p in P if p['posicao']==tid]
        def escolhido(p):
            if f"{tid}-*" in sel or f"{tid}-{p['ordem']:02d}{p['versao']}" in sel: return True
            irmaos=[q for q in ps if q['ordem']==p['ordem']]
            if f"!{tid}-{p['ordem']:02d}" in sel: return False
            return p['opcional'] is False and not any(f"{tid}-{q['ordem']:02d}{q['versao']}" in sel for q in irmaos)
        esc=[p for p in ps if escolhido(p)]
        if base.strip() and not ps: out.append(base)
        out+= [p['texto'] for p in sorted(esc,key=lambda p:(p['ordem'],p['versao']))]
    txt=[]
    for x in out:
        for a,b in subs.items(): x=x.replace(a,b)
        txt.append(x)
    return txt
N=lambda s:re.sub(r'\s+',' ',s.replace('\xa0',' ')).strip()
def orig(k):
    v=[x for x in V[k] if x not in ('O Desembargador Federal Carlos Muta (Relator):','Senhores Desembargadores,')]
    v=[x[len('Senhores Desembargadores, '):][:1].upper()+x[len('Senhores Desembargadores, ')+1:] if x.startswith('Senhores Desembargadores, ') else x for x in v]
    out=[]
    for x in v:
        if x.startswith('“É despicienda') and 'No tocante ao segundo grupo' in x:
            i=x.index('No tocante');out+=[x[:i].strip(),x[i:]]
        else: out.append(x)
    return out
if __name__=='__main__':
    for k,(rid,sel,subs) in SEL.items():
      a=[N(x) for x in montar(rid,sel,subs)];b=[N(x) for x in orig(k)]
      import difflib
      d=[x for x in difflib.unified_diff(b,a,lineterm='',n=0) if x[:1] in '+-' and not x.startswith(('+++','---'))]
      print(f'{k} × {rid.split("2886-")[1]}: {len(a)} × {len(b)} parágrafos · ' + ('IDÊNTICO' if not d else f'{len(d)//2} diferença(s)'))
      for x in d: print('    ',x[:230])
      pass
