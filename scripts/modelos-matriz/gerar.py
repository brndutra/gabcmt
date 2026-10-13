"""Gera modelos-matriz.json (gabA.paradigmas · banco Modelo-matriz) a partir de defs.json."""
import json, re
POS=['admiss','prelim','trans','contro','jurid','fatos','provas','aplic','concl','consec','honor','complem','disp','fecho']
D=json.load(open('defs.json',encoding='utf-8'))
txt=lambda x: '\n\n'.join(x) if isinstance(x,list) else x
def registro(d):
    esq={p:{'texto':txt(d['esqueleto'].get(p,[])),'ativo':bool(d['esqueleto'].get(p))} for p in POS}
    pars=[{'posicao':x['posicao'],'titulo':x['titulo'],'texto':txt(x['texto'])} for x in d['paragrafos']]
    for x in pars: assert x['posicao'] in POS
    vars_=sorted(set(re.findall(r'\{\{([^}]*)\}\}',json.dumps([esq,pars],ensure_ascii=False))))
    for v in vars_: assert re.fullmatch(r'[A-Z_]+',v), v
    sit='; '.join(f"{x['posicao']}: {x['titulo']}" for x in pars) or 'nenhum (fonte única; ver relatório de conferência)'
    r={'id':d['id'],'processo':'MODELO-MATRIZ · '+d['nome'],'tipo':'Modelo','pronunciamento':'Voto','especie':d['especie'],
       'primeiroGrau':'','parteNotavel':'','papelNotavel':'',
       'assunto':'Índice de 28,86% Lei 8.622/1993 e 8.627/1993','temas':d['temas'],'causaPedir':'Cumprimento individual de sentença coletiva da ACP 0005019-15.1997.4.03.6000 (28,86%).',
       'tese':d['tese'],'fundamentacao':'Texto integral dos votos-fonte, sem alteração redacional, distribuído nas 14 posições do Modo Matriz.',
       'especificidades':('Variáveis do caso concreto: '+(', '.join('{{'+v+'}}' for v in vars_) or 'nenhuma')+'. Parágrafos situacionais (gestor): '+sit+'.'),
       'preliminares':'','honorarios':'','resultado':d['resultado'],'sessao':'05/10/2026',
       'fonte':'Votos do Des. Fed. Carlos Muta, Turma Regional de MS (TRF3), julgados em 05/10/2026: '+d['processosAssociados']+'. Modelo-matriz gerado em 13/10/2026.',
       'data':'2026-10-05','processosAssociados':d['processosAssociados'],'especificidadesTags':d['tags'],
       'formatoModelo':'Modelo-matriz','nomeModelo':d['nome'],'textoModelo':'',
       'esqueletoModelo':json.dumps(esq,ensure_ascii=False),'paragrafosModelo':json.dumps(pars,ensure_ascii=False)}
    assert re.fullmatch(r'[A-Za-z0-9._-]+',r['id'])
    for k,v in r.items(): assert isinstance(v,str), k
    return r
regs=[registro(d) for d in D['defs']]
assert len({r['id'] for r in regs})==len(regs)
out={'schema':'gabA.paradigmas','schema_versao':1,'versao':'1.0.0','atualizado_em':'2026-10-13','banco_tipo':'Modelo-matriz','registros':regs}
json.dump(out,open('modelos-matriz-2886.json','w',encoding='utf-8'),ensure_ascii=False,indent=2)
print(len(regs),'registros')
