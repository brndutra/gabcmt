"""Acumula acórdãos (JSON vindo do portal do TRF3) em acordaos.jsonl e regenera a tabela HTML.

Uso: python3 acumular.py lote.json   (lote = lista de objetos com processo, classe, orgao, julg, pub, ementa)
"""
import html
import sys
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))
JSONL = BASE / "acordaos.jsonl"
SAIDA = BASE / "tabela-acordaos-carlos-muta.html"


def secao(ementa, inicio, fim_padroes):
    m = re.search(inicio, ementa, re.I)
    if not m:
        return ""
    resto = ementa[m.end():]
    corte = len(resto)
    for p in fim_padroes:
        f = re.search(p, resto, re.I)
        if f:
            corte = min(corte, f.start())
    return resto[:corte].strip(" :\n")


def extrair_lista(texto, rotulo):
    """Captura 'Tema 629/STJ', 'Temas 550 e 1.102/STJ', 'Temas 1.075, 499 e 733' etc."""
    num = r"\d{1,4}(?:\.\d{3})?(?:/(?:STJ|STF|TNU|TFR|TRF3|TRF-3))?"
    achados = {}
    for m in re.finditer(rotulo + r"\s+(?:n[ºo°]\s*)?(" + num + r"(?:\s*(?:,|e)\s*" + num + r")*)", texto):
        itens = re.findall(num, m.group(1))
        sufixo = next((i.split("/")[1] for i in reversed(itens) if "/" in i), "")
        depois = texto[m.end():m.end() + 8]
        if not sufixo:
            s = re.match(r"\s*(?:do|da)?\s*/?\s*(STJ|STF|TNU)", depois)
            sufixo = s.group(1) if s else ""
        for i in itens:
            n = i.split("/")[0]
            suf = i.split("/")[1] if "/" in i else sufixo
            if suf or n not in achados:
                achados[n] = suf
    return [f"{n}/{s}" if s else n for n, s in sorted(achados.items(), key=lambda x: int(x[0].replace(".", "")))]


def derivar(r):
    e = r["ementa"]
    primeira = e.split("\n", 1)[0].strip()
    assunto = primeira
    dispositivos = secao(e, r"Dispositivos? relevantes? citados?:?", [r"\nJurisprud[êe]ncias? relevantes? citadas?", r"\n_{3,}"])
    jurisp = secao(e, r"Jurisprud[êe]ncias? relevantes? citadas?:?", [r"\nII\.\s*QUEST", r"\nDispositivos? relevantes?"])
    especificidades = secao(e, r"II\.\s*Quest(ão|ões) em discuss[ãa]o", [r"\nIII\.\s*Raz"])
    if not especificidades:
        especificidades = secao(e, r"I\.\s*Caso em exame", [r"\nII\."])
    temas, sumulas = extrair_lista(e, r"Temas?(?:\s+Repetitivos?)?"), extrair_lista(e, r"S[úu]mulas?(?:\s+Vinculantes?)?")
    temas_txt = "; ".join([f"Tema {t}" for t in temas] + [f"Súmula {s}" for s in sumulas])
    return {**r, "assunto": assunto, "temas": temas_txt, "especificidades": especificidades,
            "dispositivos": dispositivos, "jurisprudencia": jurisp}


def carregar():
    regs = {}
    if JSONL.exists():
        for linha in JSONL.read_text(encoding="utf-8").splitlines():
            if linha.strip():
                r = json.loads(linha)
                regs[(r["processo"], r.get("julg", ""))] = r
    return regs


PERIODO_BUSCA = "01/03 a 13/10/2026"


def gerar_html(regs):
    import paradigma as P
    ordenados = sorted(regs.values(), key=lambda r: (r.get("julg_iso", ""), r["processo"]), reverse=True)
    recs = []
    usados = {}
    for r in sorted(ordenados, key=lambda r: (r.get("julg_iso", ""), r["processo"])):
        p = P.converter(r, PERIODO_BUSCA)
        if p["id"] in usados:  # mesmo processo julgado mais de uma vez (ex.: apelação e depois embargos)
            p["id"] = f"{p['id']}-{(p['especie'] or 'julg').lower()}-{r.get('julg_iso', '').replace('-', '')}"
        usados[p["id"]] = 1
        banco = P.no_banco(r["processo"], p["especie"])
        p["_noBanco"] = banco["tipo"] if banco else ""
        ids_banco = {b["id"] for lst in P._CURADOS.values() for b in lst}
        if not banco and p["id"] in ids_banco:  # outro julgamento do mesmo processo já curado com este id: não sobrescrever
            p["id"] = f"{p['id']}-{(p['especie'] or 'julg').lower()}-{r.get('julg_iso', '').replace('-', '')}"
        usados[p["id"]] = 1
        recs.append(p)
    recs.reverse()
    import similaridade as SIM
    SIM.agrupar(recs)
    # arquivo de importação direta no Banco de Paradigmas: só o que ainda não consta do banco
    novos = [{k: v for k, v in x.items() if not k.startswith("_")} for x in recs if not x["_noBanco"]]
    (BASE / "precedentes.json").write_text(json.dumps({
        "schema": "gabA.paradigmas", "schema_versao": 1, "versao": "1.0.0",
        "atualizado_em": __import__("datetime").date.today().isoformat(), "banco_tipo": "Precedente",
        "registros": novos}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (BASE / "catalogo-agrupado.json").write_text(json.dumps(recs, ensure_ascii=False), encoding="utf-8")
    datas = [r["julg_iso"] for r in regs.values() if r.get("julg_iso")]
    periodo = f"{fmt(min(datas))} a {fmt(max(datas))}" if datas else "—"
    dados = json.dumps(recs, ensure_ascii=False).replace("</", "<\\/")
    SAIDA.write_text(MODELO.replace("{{DADOS}}", dados).replace("{{TOTAL}}", str(len(recs)))
                     .replace("{{PERIODO}}", periodo).replace("{{BUSCA}}", PERIODO_BUSCA), encoding="utf-8")


def fmt(iso):
    a, m, d = iso.split("-")
    return f"{d}/{m}/{a}"


def iso(br):
    m = re.match(r"(\d{2})/(\d{2})/(\d{4})", br or "")
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else ""


MODELO = r"""<title>Acórdãos Carlos Muta</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* Catálogo de gabinete no formato do Banco de Paradigmas: barra de exportação, filtros, tabela larga com rolagem própria */
:root{--bg:#f3f4f2;--card:#ffffff;--fg:#1d2321;--mut:#5d6763;--line:#d6dbd8;--acc:#1f5f57;--acc-soft:#e1ecea;--warn:#8a5a00;--warn-soft:#f6ecd8;
--serif:'Source Serif 4',Georgia,'Times New Roman',serif;--sans:'IBM Plex Sans',system-ui,-apple-system,'Segoe UI',sans-serif;--mono:'IBM Plex Mono',ui-monospace,Consolas,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#121615;--card:#1a1f1e;--fg:#e4e8e6;--mut:#9aa4a0;--line:#2e3634;--acc:#7cc4b8;--acc-soft:#1f2f2c;--warn:#e3b45c;--warn-soft:#33291a;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#121615;--card:#1a1f1e;--fg:#e4e8e6;--mut:#9aa4a0;--line:#2e3634;--acc:#7cc4b8;--acc-soft:#1f2f2c;--warn:#e3b45c;--warn-soft:#33291a;color-scheme:dark}
body{background:var(--bg);color:var(--fg);font:14px/1.5 var(--sans);padding-inline:16px;padding-block:24px 40px}
.top{max-width:1500px;margin:0 auto;display:grid;gap:12px}
.eyebrow{font:500 12px var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--acc)}
h1{font:600 clamp(22px,3vw,30px)/1.15 var(--serif);margin:0;text-wrap:balance}
.meta{color:var(--mut);max-width:86ch;margin:0}
.export{display:flex;flex-wrap:wrap;gap:10px 16px;align-items:center;padding:12px 14px;border:1px solid var(--line);border-radius:8px;background:var(--card)}
.export b{font-weight:600}.export .grow{flex:1 1 260px;min-width:0;color:var(--mut)}
.btn{font:600 13px var(--sans);padding:8px 14px;border-radius:6px;border:1px solid var(--acc);background:var(--acc);color:var(--card);cursor:pointer}
.btn.sec{background:var(--card);color:var(--acc)}.btn:disabled{opacity:.5;cursor:default}
label.chk{display:flex;gap:6px;align-items:center;font-size:13px}
#msg{flex-basis:100%;font-size:13px;color:var(--acc);min-height:1em}#msg.err{color:var(--warn)}
#jsonBox{flex-basis:100%;width:100%;min-height:120px;font:12px var(--mono);border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg);padding:8px}
.ctl{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
#f{flex:1 1 280px;max-width:520px;padding:9px 12px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--fg);font:inherit}
select{padding:8px 10px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--fg);font:inherit}
#f:focus-visible,select:focus-visible,.chip:focus-visible,.btn:focus-visible,summary:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{font:500 12px var(--sans);padding:5px 10px;border-radius:999px;border:1px solid var(--line);background:var(--card);color:var(--fg);cursor:pointer}
.chip em{font-style:normal;color:var(--mut);font-variant-numeric:tabular-nums}
.chip[aria-pressed="true"]{background:var(--acc);border-color:var(--acc);color:var(--card)}.chip[aria-pressed="true"] em{color:var(--card)}
#cont{font:12px var(--mono);color:var(--mut)}
.wrap{max-width:1500px;margin:16px auto 0;overflow-x:auto;border:1px solid var(--line);border-radius:8px;background:var(--card)}
table{border-collapse:collapse;width:100%;min-width:1500px}
th{position:sticky;top:0;background:var(--acc-soft);color:var(--fg);text-align:left;padding:10px;font:600 11.5px var(--sans);letter-spacing:.03em;text-transform:uppercase;border-bottom:1px solid var(--line)}
td{border-top:1px solid var(--line);padding:10px;vertical-align:top;font-size:13px}
tbody tr:first-child td{border-top:0}
td.num{color:var(--mut);font:12px var(--mono);font-variant-numeric:tabular-nums;width:34px}
.proc{width:200px}.proc b{font:500 13px var(--mono);display:block;margin-bottom:2px}.proc span{display:block;color:var(--mut);font-size:12px}
.pill{display:inline-block;margin-top:4px;font:600 10.5px var(--sans);letter-spacing:.04em;text-transform:uppercase;padding:2px 7px;border-radius:999px;background:var(--acc-soft);color:var(--acc)}
.pill.banco{background:var(--warn-soft);color:var(--warn)}
.ass{width:220px}.ramo{display:block;font:600 10.5px var(--sans);letter-spacing:.05em;text-transform:uppercase;color:var(--mut);margin-bottom:3px}
.sug{display:block;font-size:11.5px;color:var(--warn);margin-top:2px}
.tema{width:150px;font:12px var(--mono)}.tese{width:260px}.res{width:150px}.ref{font-size:12.5px}
td i{color:var(--mut);font-style:normal}
summary{cursor:pointer;color:var(--acc);font-weight:500}
.ementa{margin-top:8px;font:14px/1.55 var(--serif);max-width:62ch;white-space:pre-line}
.views{display:inline-flex;border:1px solid var(--line);border-radius:7px;overflow:hidden}
.views button{font:600 13px var(--sans);padding:8px 14px;border:0;background:var(--card);color:var(--fg);cursor:pointer}
.views button[aria-pressed="true"]{background:var(--acc);color:var(--card)}
.tg{width:170px;font-size:12.5px}.tg b{font:600 12px var(--mono);color:var(--acc)}.tg span{display:block;color:var(--mut)}
#grp{max-width:1500px;margin:16px auto 0;display:grid;gap:22px}
.asec>h2{font:600 19px/1.25 var(--serif);margin:0 0 4px}.asec>.sub{color:var(--mut);font-size:13px;margin:0 0 10px}
.tcard{border:1px solid var(--line);border-radius:8px;background:var(--card);margin-bottom:8px}
.tcard>summary{list-style:none;display:grid;grid-template-columns:auto 1fr auto;gap:4px 12px;align-items:baseline;padding:12px 14px;color:var(--fg);font-weight:400}
.tcard>summary::-webkit-details-marker{display:none}
.tcard>summary .tid{font:600 12px var(--mono);color:var(--acc)}
.tcard>summary .rot{font:600 15px/1.35 var(--serif)}
.tcard>summary .n{font:600 13px var(--mono);font-variant-numeric:tabular-nums;color:var(--mut);white-space:nowrap}
.tcard>summary .rz{grid-column:2/4;display:flex;flex-wrap:wrap;gap:6px;width:auto}
.tag{font:500 11.5px var(--sans);padding:2px 8px;border-radius:999px;background:var(--acc-soft);color:var(--acc)}
.tag.w{background:var(--warn-soft);color:var(--warn)}
.tcard>summary .esp{grid-column:2/4;display:flex;flex-wrap:wrap;gap:4px 10px;font-size:12.5px;color:var(--mut)}
.tcard>summary .esp b{font:600 11px var(--sans);letter-spacing:.05em;text-transform:uppercase;color:var(--fg)}
.tcard>summary .esp span+span::before{content:'· ';color:var(--line)}.tcard>summary .esp em{font:500 11px var(--mono);font-style:normal}
.tcard[open]>summary{border-bottom:1px solid var(--line)}
.sent{font:600 11px var(--sans);letter-spacing:.05em;text-transform:uppercase;color:var(--mut);padding:10px 14px 2px}
.mb{display:grid;grid-template-columns:200px 120px 1fr;gap:4px 14px;padding:8px 14px;border-top:1px dashed var(--line);font-size:13px}
.mb:first-of-type{border-top:0}
.mb .pr b{font:500 12.5px var(--mono);display:block}.mb .pr span{color:var(--mut);font-size:12px}
.gr{font:600 11.5px var(--sans)}.gr i{display:block;font:500 11px var(--mono);color:var(--mut);font-style:normal}
.g-rep{color:var(--acc)}.g-ide{color:var(--acc)}.g-qua{color:var(--acc)}.g-sim{color:var(--fg)}.g-mes{color:var(--mut)}
.mb details summary{font-weight:400;color:var(--fg)}
@media (max-width:760px){.mb{grid-template-columns:1fr}.tcard>summary{grid-template-columns:1fr}.tcard>summary .rz,.tcard>summary .esp{grid-column:auto}}
@media (prefers-reduced-motion:no-preference){.chip,.btn{transition:background .15s,color .15s}}
</style>
<div class="top">
<div class="eyebrow">TRF3 · Turma Regional de Mato Grosso do Sul · formato Banco de Paradigmas</div>
<h1>Acórdãos do Desembargador Federal Carlos Muta</h1>
<p class="meta">{{TOTAL}} acórdãos julgados de {{PERIODO}}, organizados por assunto, por tema (mesma questão jurídica) e por igualdade de texto da ementa, colhidos na base de jurisprudência do TRF3 (publicação de {{BUSCA}}). Cada linha já está no padrão do Banco de Paradigmas: assunto do catálogo do gabinete, temas, marcadores, tese, resultado, sessão de julgamento e data de publicação. Todos os registros saem como <b>brutos</b>, para curadoria antes do uso.</p>
<div class="export" role="group" aria-label="Exportar para o Banco de Paradigmas">
 <span class="grow" id="expInfo"></span>
 <label class="chk"><input type="checkbox" id="incBanco"> Incluir os que já constam do banco</label>
 <button type="button" class="btn" id="btnExp">Exportar precedentes.json</button>
 <button type="button" class="btn sec" id="btnCopy">Copiar JSON</button>
 <div id="msg" role="status" aria-live="polite"></div>
 <textarea id="jsonBox" readonly hidden aria-label="JSON para importação"></textarea>
</div>
<div class="ctl"><div class="views" role="group" aria-label="Modo de exibição"><button type="button" data-v="grp" aria-pressed="true">Agrupado por assunto e tema</button><button type="button" data-v="tab" aria-pressed="false">Tabela</button></div>
 <select id="grau" aria-label="Grau de igualdade de texto"><option value="">Qualquer grau de semelhança</option><option value="igual">Só textos idênticos ou quase idênticos</option><option value="par">Só casos com par (temas com 2 ou mais)</option><option value="unico">Só casos sem par</option></select></div>
<div class="ctl"><input id="f" type="search" placeholder="Filtrar por processo, tema, palavra…" aria-label="Filtrar acórdãos">
 <select id="sit" aria-label="Situação no banco"><option value="">Todos</option><option value="novo">Ainda não estão no banco</option><option value="banco">Já constam do banco</option><option value="sem">Sem assunto definido</option><option value="sug">Assunto sugerido (conferir)</option></select>
 <span id="cont"></span></div>
<div class="chips" id="chips"></div>
</div>
<div id="grp" aria-live="polite"></div>
<div class="wrap" id="tabWrap" hidden><table><thead><tr><th>#</th><th>Processo</th><th>Assunto</th><th>Tema · texto</th><th>Tema(s)</th><th>Especificidades</th><th>Tese principal</th><th>Resultado</th><th>Dispositivos citados</th><th>Jurisprudência citada</th><th>Ementa</th></tr></thead>
<tbody id="t"></tbody></table></div>
<script type="application/json" id="dados">{{DADOS}}</script>
<script>
const R=JSON.parse(document.getElementById('dados').textContent);
const $=id=>document.getElementById(id);
const esc=s=>String(s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const vazio='<i>—</i>';
let filtro={q:'',ass:null,sit:'',grau:''};let vista='grp';
const contAss={};R.forEach(r=>{const k=r.assunto||'Sem assunto';contAss[k]=(contAss[k]||0)+1});
$('chips').innerHTML=Object.entries(contAss).sort((a,b)=>b[1]-a[1]).slice(0,14).map(([a,n])=>`<button type="button" class="chip" aria-pressed="false" data-a="${esc(a)}">${esc(a)} <em>${n}</em></button>`).join('');
const linha=(r,i)=>`<tr data-i="${i}"><td class="num">${i+1}</td>
<td class="proc"><b>${esc(r.processo)}</b><span>${esc(r.classeSigla)} · julgamento ${esc(r.sessao)}</span><span>publicação ${esc(r.data.split('-').reverse().join('/'))}</span><span class="pill${r._noBanco?' banco':''}">${r._noBanco?'já no banco ('+esc(r._noBanco)+')':'novo'}</span></td>
<td class="ass"><span class="ramo">${esc(r.ramoDireito)}</span>${esc(r.assunto)||vazio}${r.assuntoOrigem==='sugerido'?'<span class="sug">sugerido, conferir</span>':''}</td>
<td class="tg"><b>${esc(r.temaId)}</b> ${esc(r.temaRotulo)}<span>${esc(r.grauIgualdade)}${r.grauIgualdade!=='único'&&r.grauIgualdade!=='representante'?' · '+r.similaridadeTema+'%':''}${r.modeloTextoId?' · texto '+esc(r.modeloTextoId)+' ('+r.modeloTextoTamanho+')':''}</span></td>
<td class="tema">${esc(r.temas)||vazio}</td><td>${esc(r.especificidadesTags)||vazio}</td><td class="tese">${esc(r.tese)||vazio}</td>
<td class="res">${esc(r.resultado)||vazio}${r.honorarios?'<br><span style="color:var(--mut)">'+esc(r.honorarios)+'</span>':''}</td>
<td class="ref">${esc(r.dispositivosCitados)||vazio}</td><td class="ref">${esc(r.jurisprudenciaCitada)||vazio}</td>
<td><details><summary>Íntegra</summary><div class="ementa">${esc(r.ementaIntegral)}</div></details></td></tr>`;
$('t').innerHTML=R.map(linha).join('');
const trs=[...document.querySelectorAll('#t tr')];
const busca=R.map((r,i)=>[r.processo,r.assunto,r.temaId,r.temaRotulo,r.temas,r.especificidadesTags,r.tese,r.resultado,r.dispositivosCitados,r.jurisprudenciaCitada,r.ementaIntegral,r.modeloTextoId].join(' ').toLowerCase());
const IGUAL=new Set(['representante','idêntico','quase idêntico']);
const temIgual=new Set(R.filter(x=>x.grauIgualdade==='idêntico'||x.grauIgualdade==='quase idêntico').map(x=>x.temaId));
const passaGrau=r=>!filtro.grau||(filtro.grau==='igual'&&(r.grauIgualdade==='idêntico'||r.grauIgualdade==='quase idêntico'||(r.grauIgualdade==='representante'&&temIgual.has(r.temaId))))||(filtro.grau==='par'&&r.temaTamanho>1)||(filtro.grau==='unico'&&r.temaTamanho===1);
const passa=(r,tr)=>(!filtro.ass||(r.assunto||'Sem assunto')===filtro.ass)&&(!filtro.q||busca[+tr.dataset.i].includes(filtro.q))&&passaGrau(r)&&
 (!filtro.sit||(filtro.sit==='novo'&&!r._noBanco)||(filtro.sit==='banco'&&r._noBanco)||(filtro.sit==='sem'&&!r.assunto)||(filtro.sit==='sug'&&r.assuntoOrigem==='sugerido'));
function visiveis(){return trs.filter(tr=>!tr.hidden).map(tr=>R[+tr.dataset.i])}
function paraExportar(){const inc=$('incBanco').checked;return visiveis().filter(r=>inc||!r._noBanco)}
function aplicar(){let n=0;trs.forEach(tr=>{const ok=passa(R[+tr.dataset.i],tr);tr.hidden=!ok;if(ok)n++});$('cont').textContent=n+' de '+R.length;atualizaGrupos();
 const e=paraExportar(),fora=visiveis().length-e.length;
 $('expInfo').innerHTML=`<b>${e.length}</b> registro(s) visíveis prontos para importar no Banco de Paradigmas`+(fora?` · ${fora} já constam do banco e ficam de fora`:'');
 $('btnExp').disabled=$('btnCopy').disabled=!e.length;$('jsonBox').hidden=true}
function jsonExport(){const regs=paraExportar().map(r=>{const o={};for(const k in r)if(k[0]!=='_')o[k]=r[k];return o});
 return JSON.stringify({schema:'gabA.paradigmas',schema_versao:1,versao:'1.0.0',atualizado_em:new Date().toISOString().slice(0,10),banco_tipo:'Precedente',registros:regs},null,2)+'\n'}
function msg(t,err){const m=$('msg');m.textContent=t;m.classList.toggle('err',!!err)}
let dl=null;(async()=>{try{dl=await (window.claude&&window.claude.use?window.claude.use('downloads'):null)}catch(e){dl=null}})();
$('btnExp').addEventListener('click',async()=>{const txt=jsonExport(),n=JSON.parse(txt).registros.length;
 if(!dl){mostrarJson(txt);msg('O download não está disponível nesta visualização. Copie o JSON abaixo e salve como precedentes.json.',true);return}
 try{await dl.save({filename:'precedentes.json',data:txt});msg(`precedentes.json com ${n} registro(s). No app, abra o Banco de Paradigmas › Precedentes › Importar JSON.`)}
 catch(e){const c=e&&e.code;if(c==='declined')msg('Download cancelado.',true);else if(c==='rate_limited')msg('Já há uma confirmação de download aberta. Conclua-a e tente de novo.',true);else{mostrarJson(txt);msg('Não foi possível baixar aqui. Copie o JSON abaixo.',true)}}});
function mostrarJson(txt){const b=$('jsonBox');b.value=txt;b.hidden=false}
$('btnCopy').addEventListener('click',()=>{const txt=jsonExport();navigator.clipboard.writeText(txt).then(()=>msg('JSON copiado. Cole num arquivo precedentes.json para importar.')).catch(()=>{mostrarJson(txt);const b=$('jsonBox');b.focus();b.select();msg('A cópia automática foi bloqueada. O JSON está selecionado abaixo: use Ctrl+C.',true)})});
$('incBanco').addEventListener('change',aplicar);
$('f').addEventListener('input',e=>{filtro.q=e.target.value.toLowerCase().trim();aplicar()});
$('sit').addEventListener('change',e=>{filtro.sit=e.target.value;aplicar()});
$('chips').addEventListener('click',e=>{const b=e.target.closest('.chip');if(!b)return;filtro.ass=filtro.ass===b.dataset.a?null:b.dataset.a;document.querySelectorAll('.chip').forEach(c=>c.setAttribute('aria-pressed',String(c.dataset.a===filtro.ass)));aplicar()});
// ── visão agrupada: assunto › tema (mesma questão jurídica) › resultado › casos, do mais ao menos semelhante ao representante
const SENT=['provido','parcialmente provido','desprovido','não conhecido','rejeitados','acolhidos','prejudicado/extinto','outro'];
const CL={'representante':'g-rep','idêntico':'g-ide','quase idêntico':'g-qua','similar':'g-sim','mesma questão':'g-mes','único':'g-mes'};
const porTema={};R.forEach((r,i)=>{(porTema[r.temaId]=porTema[r.temaId]||[]).push(i)});
const porAss={};Object.keys(porTema).sort().forEach(t=>{const a=R[porTema[t][0]].assunto||'Sem assunto';(porAss[a]=porAss[a]||[]).push(t)});
const membro=i=>{const r=R[i];const pct=(r.grauIgualdade==='representante'||r.grauIgualdade==='único')?'':`<i>${r.similaridadeTema}% do texto</i>`;
 return `<div class="mb" data-i="${i}"><div class="pr"><b>${esc(r.processo)}</b><span>${esc(r.classeSigla)} · julg. ${esc(r.sessao)}${r._noBanco?' · já no banco':''}</span></div>
 <div class="gr ${CL[r.grauIgualdade]||''}">${esc(r.grauIgualdade)}${pct}${r.modeloTextoId?`<i>texto ${esc(r.modeloTextoId)} · ${r.modeloTextoTamanho} iguais</i>`:''}</div>
 <details data-e="${i}"><summary>${esc(r.ementaCabecalho||r.processo)}</summary><div class="ementa"></div></details></div>`};
function cartao(t){const idx=porTema[t],r0=R[idx[0]];const cont={};idx.forEach(i=>{const s=R[i].sentidoResultado;cont[s]=(cont[s]||0)+1});
 const iguais=idx.filter(i=>R[i].grauIgualdade==='idêntico'||R[i].grauIgualdade==='quase idêntico').length;
 const tc={};idx.forEach(i=>new Set(String(R[i].especificidadesTags||'').split(';').map(x=>x.trim()).filter(Boolean)).forEach(x=>{tc[x]=(tc[x]||0)+1}));
 const esp=Object.entries(tc).filter(([x,c])=>idx.length===1||c>=Math.max(2,idx.length*0.2)).sort((a,b)=>b[1]-a[1]).slice(0,8);
 const ord=[...idx].sort((a,b)=>SENT.indexOf(R[a].sentidoResultado)-SENT.indexOf(R[b].sentidoResultado)||R[b].similaridadeTema-R[a].similaridadeTema);
 let html='',cur=null;ord.forEach(i=>{const s=R[i].sentidoResultado;if(s!==cur&&Object.keys(cont).length>1){html+=`<div class="sent" data-s="${esc(s)}">${esc(s)}</div>`}cur=s;html+=membro(i)});
 return `<details class="tcard" data-t="${t}"${idx.length>1&&idx.length<=8?'':''}><summary><span class="tid">${t}</span><span class="rot">${esc(r0.temaRotulo)}</span><span class="n">${idx.length} ${idx.length>1?'casos':'caso'}</span>
 <span class="rz">${SENT.filter(s=>cont[s]).map(s=>`<span class="tag">${cont[s]} ${esc(s)}</span>`).join('')}${iguais?`<span class="tag w">${iguais} com texto igual ou quase igual ao representante</span>`:''}</span>${esp.length?`<span class="esp"><b>Especificidades</b> ${esp.map(([x,c])=>`<span>${esc(x)}${idx.length>1?` <em>${c}</em>`:''}</span>`).join('')}</span>`:''}</summary>${html}</details>`}
$('grp').innerHTML=Object.keys(porAss).sort((a,b)=>porAss[b].reduce((n,t)=>n+porTema[t].length,0)-porAss[a].reduce((n,t)=>n+porTema[t].length,0)).map(a=>{
 const ts=porAss[a],multi=ts.filter(t=>porTema[t].length>1),uni=ts.filter(t=>porTema[t].length===1);
 return `<section class="asec" data-a="${esc(a)}"><h2>${esc(a)}</h2><p class="sub"></p>${multi.map(cartao).join('')}${uni.length?`<details class="tcard" data-uni="1"><summary><span class="tid">—</span><span class="rot">Casos sem par neste assunto</span><span class="n"></span><span class="rz"><span class="tag">questões que aparecem uma só vez</span></span></summary>${uni.map(t=>membro(porTema[t][0])).join('')}</details>`:''}</section>`}).join('');
$('grp').addEventListener('toggle',e=>{const d=e.target;if(d.dataset&&d.dataset.e&&d.open){const b=d.querySelector('.ementa');if(!b.textContent)b.textContent=R[+d.dataset.e].ementaIntegral}},true);
const mbs=[...document.querySelectorAll('#grp .mb')];
function atualizaGrupos(){const vis=new Set(trs.filter(tr=>!tr.hidden).map(tr=>+tr.dataset.i));
 mbs.forEach(m=>m.hidden=!vis.has(+m.dataset.i));
 document.querySelectorAll('#grp .tcard').forEach(d=>{const ms=[...d.querySelectorAll(':scope>.mb')],v=ms.filter(m=>!m.hidden).length;d.hidden=!v;
  if(d.dataset.uni)d.querySelector('.n').textContent=v+(v>1?' casos':' caso');else d.querySelector('.n').textContent=v===ms.length?`${v} ${v>1?'casos':'caso'}`:`${v} de ${ms.length}`;
  d.querySelectorAll('.sent').forEach(h=>{let n=h.nextElementSibling,any=false;while(n&&!n.classList.contains('sent')){if(!n.hidden)any=true;n=n.nextElementSibling}h.hidden=!any})});
 document.querySelectorAll('#grp .asec').forEach(s=>{const ts=[...s.querySelectorAll('.tcard:not([data-uni])')].filter(d=>!d.hidden).length;const casos=[...s.querySelectorAll('.mb')].filter(m=>!m.hidden).length;
  s.hidden=!casos;s.querySelector('.sub').textContent=`${casos} acórdão(s) · ${ts} tema(s) com dois ou mais casos`})}
document.querySelectorAll('.views button').forEach(b=>b.addEventListener('click',()=>{vista=b.dataset.v;document.querySelectorAll('.views button').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));$('grp').hidden=vista!=='grp';$('tabWrap').hidden=vista!=='tab'}));
$('grau').addEventListener('change',e=>{filtro.grau=e.target.value;aplicar()});
aplicar();
</script>"""


if __name__ == "__main__":
    regs = carregar()
    novos = 0
    for arq in sys.argv[1:]:
        for r in json.loads(Path(arq).read_text(encoding="utf-8")):
            r["julg_iso"] = iso(r.get("julg"))
            chave = (r["processo"], r.get("julg", ""))
            if chave not in regs:
                novos += 1
            regs[chave] = derivar(r)
    regs = {k: derivar(v) for k, v in regs.items()}
    JSONL.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in regs.values()) + "\n", encoding="utf-8")
    gerar_html(regs)
    print(f"{novos} novos; total {len(regs)}; HTML em {SAIDA}")
