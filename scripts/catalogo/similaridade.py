"""Organiza os acórdãos por similaridade/igualdade de assunto e texto, em três níveis:
  1. ASSUNTO  — o do catálogo do gabinete (ou "Sem assunto");
  2. TEMA     — mesma questão jurídica, dentro do assunto: cabeçalho da ementa (sem rótulos genéricos),
                "Questão em discussão" e "Tese de julgamento", TF-IDF + cosseno, ligação média;
  3. MODELO   — mesmo texto-base de ementa (cosseno ≥ 0,85 no corpo inteiro), em qualquer assunto.
Campos acrescentados a cada registro (todos simples, aceitos pelo importador do Banco de Paradigmas):
  temaId, temaRotulo, temaTamanho, temaRepresentante, similaridadeTema (0–100, texto integral × representante),
  grauIgualdade (representante | idêntico | quase idêntico | similar | mesma questão | único),
  modeloTextoId, modeloTextoTamanho."""
import re, collections
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AgglomerativeClustering

CORTES_TEMA=(0.80,0.72,0.65,0.58)  # distância (1 − cosseno); temas com mais de MAX_TEMA casos são subdivididos com corte mais estrito
MAX_TEMA=30
CORTE_MODELO=0.15  # distância para o mesmo texto-base
MAI='A-ZÁÀÂÃÉÊÍÓÔÕÚÜÇ'
GENERICO=re.compile(rf'^(DIREITO[{MAI} ,]*|ADMINISTRATIVO|PREVIDENCIÁRIO|TRIBUTÁRIO|CIVIL|PROCESSUAL CIVIL|CONSTITUCIONAL|AMBIENTAL|PENAL|ACIDENTÁRIO|'
    rf'APELAÇ(ÃO|ÕES)\b.*|RECURSOS? (DE APELAÇÃO|PROVIDOS?|DESPROVIDOS?|PARCIALMENTE PROVIDOS?|NÃO PROVIDOS?)\b.*|AGRAVO (DE INSTRUMENTO|INTERNO)\b.*|'
    rf'EMBARGOS DE DECLARAÇÃO\b.*|REMESSA (OFICIAL|NECESSÁRIA)\b.*|SENTENÇA (MANTIDA|REFORMADA|ANULADA)\b.*|HONORÁRIOS RECURSAIS|'
    rf'(PARCIAL )?PROVIMENTO\b.*|DESPROVIMENTO\b.*|[{MAI} ]*(PROVIDA|DESPROVIDA|PROVIDO|DESPROVIDO|PROVIDAS|DESPROVIDAS|REJEITADOS|ACOLHIDOS|PREJUDICADA)S?)$')

def normalizar(t):
    t=re.sub(r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}',' NPROC ',t or '')
    t=re.sub(r"\bID(?:'s|’s|s)?\s*[\d.,\se]+",' ID ',t)
    t=re.sub(r'\d{1,2}/\d{1,2}/\d{2,4}',' DATA ',t)
    t=re.sub(r'R\$\s*[\d.,]+',' VALOR ',t)
    return re.sub(r'\s+',' ',t.lower())

def corpo(e):  # ementa sem as listas finais de dispositivos e jurisprudência
    return re.split(r'\n\s*(?:Dispositivos? relevantes?|_{3,}|-{5,})',e or '')[0]

def segmentos(c):
    return [s.strip(' .') for s in re.split(rf'\.\s+(?=[{MAI}0-9])',c or '') if s.strip(' .')]

def secao(e,ini,fim):
    m=re.search(ini,e or '',re.I)
    if not m: return ''
    r=e[m.end():]; f=re.search(fim,r,re.I); return r[:f.start()] if f else r[:700]

def texto_tema(r):
    e=r.get('ementaIntegral','')
    cab=' . '.join(s for s in segmentos(r.get('ementaCabecalho','')) if not GENERICO.match(s))
    return normalizar(cab+' . '+cab+' . '+secao(e,r'II\.\s*Quest\w+ em discuss\w+',r'\n\s*III\.')+' . '+secao(e,r'Tese de julgamento',r'\n\s*(?:Dispositivos|_{3,}|-{3,})'))

def _segs(r): return set(s for s in segmentos(r.get('ementaCabecalho','')) if not GENERICO.match(s))
def rotulo(membros, contexto=None):
    """rótulo do tema: segmentos do cabeçalho mais frequentes no grupo e mais característicos dele
    em relação ao assunto (contexto) — evita rótulos iguais para temas diferentes"""
    import math
    cont=collections.Counter(); [cont.update(_segs(r)) for r in membros]
    n=len(membros)
    if n==1: esc=[s for s,_ in cont.most_common(4)]
    else:
        ctx=collections.Counter(); [ctx.update(_segs(r)) for r in (contexto or membros)]; N=len(contexto or membros)
        cand=[(s,c) for s,c in cont.items() if c>=max(2,0.25*n)]
        pont=sorted(cand,key=lambda x:-(x[1]/n)*math.log(1+(x[1]/n)/max(ctx[x[0]]/N,1e-9)))
        freq=sorted(cand,key=lambda x:-x[1])
        esc=[]
        for s,_ in freq[:1]+pont:          # o mais frequente + os mais característicos
            if s not in esc: esc.append(s)
            if len(esc)==4: break
        if not esc: esc=[s for s,_ in cont.most_common(3)]
    return '. '.join(frase(x) for x in esc) or '(sem cabeçalho)'

SIGLAS={'STJ','STF','TNU','CF','CPC','CTN','INSS','LOAS','BPC','EC','ACP','MP','ADI','ADC','RE','RESP','OAB','SIAPE','CDA','FGTS','RMI','DIB','DER','DII','PIS','CNIS','CTPS','PPP','LTCAT','EPI','IRDR','IAC','SUS','FUNASA','IBGE','UFMS','IFMS','IN','CNH','IPI','ICMS','IRPF','CSLL','COFINS','PASEP','SFH','CEF','MCMV','FIES','ICMBIO','IBAMA','ANTT','DNIT','CREA','CRM','CRC','CRF','CORE','PRF','RFB','PGFN','LEF','ECA','CDC','JEF','TRF3','TRF','MS','SP','UF','LTDA','ME','EPP','DPU','MPF','PRR','ADCT','ICMS','TCU','AGU','UNIÃO'}
def frase(s):
    if re.search(r'[a-zà-ü]',s.replace('º','').replace('ª','')): return s
    t=s[0]+s[1:].lower()
    return re.sub(r'\b([a-zà-ü0-9]+)\b',lambda m:m.group(1).upper() if m.group(1).upper() in SIGLAS and m.group(1).upper()!='UNIÃO' else ('União' if m.group(1)=='união' else m.group(1)),t)

def sentido(t):
    t=(t or '').lower()
    if re.search(r'n[ãa]o conhec|inadmit',t): return 'não conhecido'
    if re.search(r'parcial',t): return 'parcialmente provido'
    if re.search(r'desprov|negad|improv|n[ãa]o provid|mantid',t): return 'desprovido'
    if re.search(r'rejeitad',t): return 'rejeitados'
    if re.search(r'acolhid',t): return 'acolhidos'
    if re.search(r'provid|provimento|reformad|anulad',t): return 'provido'
    if re.search(r'prejudicad|extint|homolog',t): return 'prejudicado/extinto'
    return 'outro'

def _clusters(D,corte):
    if D.shape[0]==1: return np.array([0])
    return AgglomerativeClustering(n_clusters=None,metric='precomputed',linkage='average',distance_threshold=corte).fit_predict(D)

def agrupar(recs):
    n=len(recs)
    Xc=TfidfVectorizer(ngram_range=(1,2),min_df=2,sublinear_tf=True).fit_transform([normalizar(corpo(r.get('ementaIntegral',''))) for r in recs])
    Sc=(Xc@Xc.T).toarray(); np.clip(Sc,0,1,out=Sc)
    Xt=TfidfVectorizer(ngram_range=(1,2),min_df=2,sublinear_tf=True).fit_transform([texto_tema(r) for r in recs])
    St=(Xt@Xt.T).toarray(); np.clip(St,0,1,out=St)
    # nível 3: modelos de texto (global)
    mod=_clusters(1-Sc,CORTE_MODELO); tamM=collections.Counter(mod)
    # nível 2: temas dentro de cada assunto
    porAss=collections.defaultdict(list)
    for i,r in enumerate(recs): porAss[(r.get('assunto') or 'Sem assunto', r.get('especie')=='EDcl')].append(i)
    temas=[]
    for (ass,edcl),idx in porAss.items():
        def dividir(v,nivel=0):
            lab=_clusters(1-St[np.ix_(v,v)],CORTES_TEMA[nivel])
            g=collections.defaultdict(list)
            for i,l in zip(v,lab): g[l].append(i)
            out=[]
            for w in g.values():
                out+= dividir(w,nivel+1) if len(w)>MAX_TEMA and nivel+1<len(CORTES_TEMA) else [w]
            return out
        for v in dividir(idx):
            sub=(Sc[np.ix_(v,v)]+St[np.ix_(v,v)])/2; rep=v[int(sub.mean(1).argmax())]
            temas.append((ass,edcl,v,rep))
    totAss=collections.Counter(r.get('assunto') or 'Sem assunto' for r in recs)
    temas.sort(key=lambda t:(-totAss[t[0]],t[0],t[1],len(t[2])==1,-len(t[2]),recs[t[3]]['processo']))
    for k,(ass,edcl,v,rep) in enumerate(temas,1):
        ctx=[recs[i] for i in porAss[(ass,edcl)]]
        rot=('Embargos de declaração · ' if edcl else '')+rotulo([recs[i] for i in v],ctx)
        for i in v:
            r=recs[i]; s=float(Sc[i,rep])
            r['temaId']=f'T{k:03d}'; r['temaRotulo']=rot; r['temaTamanho']=len(v); r['temaRepresentante']=recs[rep]['processo']
            r['similaridadeTema']=100 if i==rep else round(s*100)
            r['grauIgualdade']=('único' if len(v)==1 else 'representante' if i==rep else 'idêntico' if s>=0.95 else
                                'quase idêntico' if s>=0.85 else 'similar' if s>=0.6 else 'mesma questão')
    for r in recs: r['sentidoResultado']=sentido(r.get('resultado',''))
    # numera os modelos de texto pela ordem dos temas
    ren={}
    for r,mi in sorted(zip(recs,mod),key=lambda x:(x[0]['temaId'],-x[0]['similaridadeTema'])):
        if tamM[mi]>1: ren.setdefault(mi,f'M{len(ren)+1:03d}')
    for r,mi in zip(recs,mod):
        r['modeloTextoId']=ren.get(mi,''); r['modeloTextoTamanho']=int(tamM[mi])
    return recs
