"""Extrai parágrafos do PDF do PJe preservando o texto: junta linhas, reconstrói parágrafos por recuo/espaçamento,
descarta rodapés e cabeçalhos. Saída: lista de documentos {num, secoes:{RELATÓRIO:[...],VOTO:[...],...}}"""
import pymupdf, re, json, sys
def linhas(pdf):
    d=pymupdf.open(pdf); out=[]
    for pi,pg in enumerate(d):
        num=None
        for b in pg.get_text('dict')['blocks']:
            for l in b.get('lines',[]):
                t=''.join(s['text'] for s in l['spans'])
                m=re.match(r'Num\. (\d+) - Pág\. (\d+)',t.strip())
                if m: num=(m.group(1),int(m.group(2)))
        if not num: num=('SEM-NUM',pi+1)
        for b in pg.get_text('dict')['blocks']:
            for l in b.get('lines',[]):
                sp=[s for s in l['spans'] if s['text']]
                t=''.join(s['text'] for s in sp)
                if not t.strip(): continue
                size=max(round(s['size']) for s in sp)
                y=l['bbox'][1]
                if size<=9 and (y>800 or y<60): continue           # rodapé
                t=t.strip() if num[0]=='SEM-NUM' else t
                if re.match(r'Num\. \d+ - Pág\.',t.strip()): continue
                out.append(dict(p=pi,num=num,x=round(l['bbox'][0]),x1=round(l['bbox'][2]),y=y,size=size,
                                bold=all(s['flags']&16 for s in sp if s['text'].strip()),t=t.rstrip()))
    # funde fragmentos da mesma linha (justificação ampla gera várias "linhas" no mesmo y)
    fund=[]
    for l in out:
        f=fund[-1] if fund else None
        if f and f['p']==l['p'] and abs(f['y']-l['y'])<2 and l['x']>=f['x1']-1:
            f['t']=f['t']+' '+l['t'].strip(); f['x1']=l['x1']; f['bold']=f['bold'] and l['bold']
        else: fund.append(dict(l))
    for f in fund: f['t']=re.sub(r'\s{2,}',' ',f['t'])
    return fund
def juntar(a,b):
    if a.endswith('-') and not a.endswith(' -'): return a+b.lstrip()
    return a+' '+b.lstrip()
def paragrafos(L):
    """agrupa linhas consecutivas (mesmo documento) em parágrafos"""
    ps=[]; cur=None; prev=None
    for l in L:
        novo=False
        if prev is None or l['num'][0]!=prev['num'][0]: novo=True
        elif l['p']==prev['p']:
            gap=l['y']-prev['y']
            if gap>prev['size']*1.75: novo=True
            elif l['num'][0]!='SEM-NUM' and l['x']>prev['x']+20 and l['x']-81>30: novo=True       # recuo de 1ª linha
            elif l['num'][0]!='SEM-NUM' and prev['x1']<440 and not prev['t'].endswith('-'): novo=True  # linha anterior curta
            elif l['size']!=prev['size']: novo=True
        else:  # mudança de página
            if l['num'][0]=='SEM-NUM': pass
            elif l['x']>100 and l['x']>prev['x']+20: novo=True
            elif prev['x1']<440: novo=True
        if novo:
            if cur: ps.append(cur)
            cur=dict(num=l['num'][0],x=l['x'],size=l['size'],bold=l['bold'],t=l['t'].strip())
        else:
            cur['t']=juntar(cur['t'],l['t']); cur['bold']=cur['bold'] and l['bold']
        prev=l
    if cur: ps.append(cur)
    return ps
def documentos(pdf):
    ps=paragrafos(linhas(pdf)); docs={}
    for p in ps: docs.setdefault(p['num'],[]).append(p)
    return docs
if __name__=='__main__':
    docs=documentos(sys.argv[1])
    for n,ps in docs.items():
        print('#### DOC',n,len(ps))
        for p in ps: print(f"[x{p['x']}{' B' if p['bold'] else ''} s{p['size']}] {p['t'][:150]}")
