"""Planejamento da sessão (Seleção Prévia › "Marcos da sessão e simulador de designação").

A página vive como texto dentro da página da Seleção Prévia, que por sua vez vai compactada (gzip+base64) dentro do
painel. melhorias.py abre essas camadas e chama aplicar() com o HTML da página de planejamento.

01 · Marcos da sessão — uma só linha compacta: sessão, os cinco marcos com os dias úteis entre eles (preparação,
     produção, revisão, antecedência) e os números que orientam o prazo: dias úteis de produção, capacidade da equipe
     no ritmo habitual contra as minutas restantes, entrega sugerida pela capacidade, tempo decorrido × entregue.
02 · Simulador — card de altura fixa: cabeçalho com a estatística da distribuição entre servidores e lista rolável
     com metas dinâmicas por servidor (meta/dia planejada = designados ÷ dias úteis do início à entrega; meta/dia
     para entregar = restantes ÷ dias úteis que faltam; andamento contra o esperado até hoje; término no ritmo).
"""

CSS = r"""<style id="planejamento-compacto">
.mk-line{display:flex;align-items:stretch;border:1px solid #dce4ed;border-radius:12px;background:#fbfcfe;padding:8px 10px;overflow-x:auto;scrollbar-width:thin}
.mk-session{flex:0 0 150px;display:flex;flex-direction:column;gap:4px;min-width:0;padding-right:8px;margin-right:4px;border-right:1px solid #e6edf4}
.mk-session .session-combined{position:relative}
.mk-session summary{display:flex;justify-content:space-between;gap:6px;align-items:center;cursor:pointer;list-style:none;border:1px solid #d6e0ea;border-radius:8px;background:#fff;padding:5px 8px;font-size:11.5px;font-weight:800;color:#253d56;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.mk-session summary::-webkit-details-marker{display:none}
.mk-session summary span:first-child{display:block;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;line-height:16px}
.mk-session .session-combined-popup{position:absolute;z-index:20;top:calc(100% + 4px);left:0;width:300px;background:#fff;border:1px solid #d6e0ea;border-radius:10px;box-shadow:0 12px 30px #203a5822;padding:10px}
.mk-session .mk-sub{display:flex;align-items:center;gap:5px}
.mk-session .mk-sub button{padding:1px 6px;font-size:11px;border-radius:6px}
.mk{flex:1 1 100px;display:flex;flex-direction:column;gap:3px;min-width:96px;padding:0 1px}
.mk input{padding:4px 5px;font-size:11.5px;font-weight:750;border-radius:7px;background:#fff;min-width:0}
.mk input::-webkit-calendar-picker-indicator{margin:0 0 0 2px;padding:0;width:11px;height:11px;cursor:pointer}
.mk-lbl{display:flex;align-items:center;justify-content:space-between;gap:3px;font-size:8.5px;font-weight:850;letter-spacing:.06em;color:#57708a;white-space:nowrap}
.mk-lbl button{padding:0 5px;font-size:9px;border-radius:5px;line-height:15px}
.mk-sub{font-size:10px;color:#748499;white-space:nowrap}
.mk.passed .mk-sub{color:#9aa8b6}
.mk.is-chronology-error input{border-color:#e0a46b;background:#fff6ed;color:#8d541d}
.mk-final input{border-color:#b9a3d9;background:#f8f4fd}
.mk-gap{flex:0 0 50px;min-width:0;position:relative;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:0 2px}
.mk-gap::before{content:"";position:absolute;left:4px;right:4px;top:50%;border-top:2px dashed #d3dde8;z-index:0}
.mk-gap b{position:relative;z-index:1;background:#fff;border:1px solid #d6e0ea;border-radius:99px;padding:1px 7px;font-size:10px;color:#29435f;white-space:nowrap}
.mk-gap span{position:relative;z-index:1;margin-top:3px;white-space:nowrap;background:#fbfcfe;padding:0 2px;font-size:9px;font-weight:700;color:#8092a4}
.mk-gap.prod b{background:#21466f;border-color:#21466f;color:#fff}
.mk-gap.bad b{background:#fff6ed;border-color:#f1dabb;color:#a64f35}
.mk-kpis{flex:0 0 auto;display:grid;grid-template-columns:repeat(2,auto);gap:4px 12px;margin-left:6px;padding-left:10px;border-left:1px solid #e6edf4;align-content:center}
.mk-kpis>div{display:flex;flex-direction:column;min-width:0}
.mk-kpis span{font-size:8.5px;font-weight:850;letter-spacing:.06em;color:#698099;text-transform:uppercase;white-space:nowrap}
.mk-kpis b{font-size:12.5px;color:#223c5b;white-space:nowrap}
.mk-kpis b.ok{color:#25714e}.mk-kpis b.bad{color:#a64f35}
.mk-kpis .mk-sug{display:flex;align-items:center;gap:5px}
.mk-kpis .mk-sug button{padding:1px 6px;font-size:9.5px;border-radius:6px}
.mk-warn{margin-top:6px;font-size:10.5px;color:#8d541d}
.mk-warn:empty{display:none}

.sim-card{height:560px;display:flex;flex-direction:column;border:1px solid #dce4ed;border-radius:12px;background:#fff;overflow:hidden}
.sim-head{flex:0 0 auto;padding:10px 12px 8px;border-bottom:1px solid #e6edf4;background:#f9fbfd}
.sim-kpis.k9{display:grid;grid-template-columns:repeat(9,minmax(0,1fr));gap:6px}
.sim-kpis.k9 .sim-kpi{padding:6px 8px;border-radius:9px}
.sim-kpis.k9 .sim-kpi span{font-size:8.5px;letter-spacing:.04em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sim-kpis.k9 .sim-kpi b{font-size:16px;line-height:1.35;white-space:nowrap}
.sim-kpis.k9 .sim-kpi small{display:block;font-size:9px;color:#8092a4;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.dist-bar{display:flex;height:20px;margin-top:8px;border-radius:7px;overflow:hidden;background:#edf1f5}
.dist-bar i{display:flex;align-items:center;justify-content:center;min-width:2px;font-style:normal;font-size:9.5px;font-weight:800;color:#fff;white-space:nowrap;overflow:hidden;border-right:1px solid #fff}
.dist-bar i.free{background:repeating-linear-gradient(45deg,#dfe6ee 0 6px,#eef2f6 6px 12px);color:#57708a}
.dist-bar i.over{background:#a64f35}
.sim-head #simWarnings .note{margin-top:6px;padding:5px 9px;font-size:10.5px;line-height:1.4}
.sim-list{flex:1 1 auto;min-height:0;overflow:auto}
.sim-list table.simtable{min-width:960px;border-collapse:separate;border-spacing:0}
.sim-list thead th{position:sticky;top:0;z-index:2;background:#f4f7fa;border-bottom:1px solid #e3e9f0;font-size:8.5px;letter-spacing:.04em;line-height:1.25;vertical-align:bottom;white-space:normal}
.sim-list tfoot td{position:sticky;bottom:0;z-index:2;background:#eef3f8;border-top:1px solid #d6e0ea;font-weight:800}
.sim-list td{padding:6px 8px;border-bottom:1px solid #eef2f6;font-size:11px;vertical-align:middle}
.sim-list td small{display:block;font-size:9px;color:#8092a4;font-weight:600;white-space:nowrap}
.sim-list .c-name{display:flex;align-items:center;gap:6px;min-width:170px}
.sim-list .c-name input[type=text]{width:118px;padding:4px 6px;font-size:11.5px;font-weight:750}
.sim-list .c-name .toggleline{display:flex;flex-direction:row;align-items:center;gap:3px;font-size:9px;font-weight:700;color:#8092a4;margin:0}
.sim-list .c-name .toggleline input{width:12px;height:12px}
.sim-list .dot{flex:0 0 auto;width:9px;height:9px;border-radius:50%}
.sim-list input.in-n{width:58px;padding:4px 6px;font-size:11.5px;font-weight:750}
.sim-list .share{height:4px;width:58px;margin-top:3px;border-radius:9px;background:#edf1f5;overflow:hidden}.sim-list .share i{display:block;height:100%}
.sim-list .meta b{font-size:13px;color:#21466f;white-space:nowrap}
.sim-list .meta.now b{font-size:14px}
.sim-list .meta.now.ok b{color:#25714e}.sim-list .meta.now.warn b{color:#a5730f}.sim-list .meta.now.bad b{color:#a64f35}
.sim-list .adv{color:#25714e;font-weight:800}.sim-list .late{color:#a64f35;font-weight:800}.sim-list .even{color:#57708a;font-weight:800}
.st-pill{display:inline-block;padding:3px 8px;border-radius:99px;font-size:9.5px;font-weight:850;white-space:nowrap}
.st-pill.ok{background:#e6f2ea;color:#25714e}.st-pill.warn{background:#fdf2dc;color:#8a5a00}.st-pill.bad{background:#fbe9e3;color:#a64f35}.st-pill.muted{background:#eef1f5;color:#8092a4}
.sim-list .chipbtn{padding:3px 7px;font-size:11px}
.sim-list tr.absences td{background:#f9fbfd}
.sim-note{font-size:10.5px;line-height:1.5;color:#698099;margin-top:6px}
@media(max-width:1060px){.mk-line{padding:7px 8px}.mk-session{flex-basis:116px}.mk{min-width:86px;flex-basis:86px}.mk input{font-size:10.5px;padding:3px 3px}.mk-gap{flex-basis:40px}.mk-kpis{gap:3px 8px;padding-left:8px;margin-left:4px}.mk-kpis b{font-size:12px}}
@media(max-width:900px){.mk-line{flex-wrap:wrap;row-gap:8px}.mk-kpis{margin-left:0;border-left:0;padding-left:0;grid-template-columns:repeat(4,auto);flex-basis:100%}}
@media(max-width:1100px){.sim-kpis.k9{grid-template-columns:repeat(5,minmax(0,1fr))}.sim-card{height:620px}.sim-list td{padding:6px 6px}.sim-list .c-name{min-width:140px}.sim-list .c-name input[type=text]{width:100px}.sim-list input.in-n{width:52px}.sim-list table.simtable{min-width:900px}.sim-list td small{white-space:normal}.st-pill{white-space:normal}}
@media(max-width:700px){.sim-kpis.k9{grid-template-columns:repeat(3,minmax(0,1fr))}}
</style>"""

INICIO_MARCOS = '<div class="section-caption"><div><h2>01 · Marcos da sessão</h2>'
FIM_SIMULADOR = '<details class="calendar-section" id="calendarDetails">'

MARCOS = r"""<div class="section-caption"><div><h2>01 · Marcos da sessão</h2><div class="sub">Prazos da sessão e os dias úteis entre eles · capacidade da equipe para fixar a entrega</div></div></div>
<div class="mk-line" id="mkLine">
 <div class="mk-session">
  <div class="mk-lbl">SESSÃO</div>
  <details class="session-combined" id="sessionCombined"><summary aria-label="Escolher sessão de julgamento"><span id="sessionCombinedLabel">Escolher sessão</span><span aria-hidden="true">▾</span></summary><div class="session-combined-popup"><label>Sessão e data de julgamento<select id="sessionChoice" aria-label="Sessão e data de julgamento"></select></label></div></details>
  <div class="mk-sub"><b id="procCount">0</b> processos <button id="openProcesses" title="Ver processos da sessão">✎</button><button id="clearProcesses" aria-label="Limpar seleção" title="Limpar seleção desta sessão">♻</button></div>
 </div>
 <div class="mk" data-field="pauta"><div class="mk-lbl">PAUTAR ATÉ</div><input id="pauta" type="date" lang="pt-BR" aria-label="Prazo para pautar"><div class="mk-sub" data-meta="pauta">—</div></div>
 <div class="mk-gap" data-gap="start"></div>
 <div class="mk" data-field="start"><div class="mk-lbl">INÍCIO PRODUÇÃO</div><input id="start" type="date" lang="pt-BR" aria-label="Início da preparação"><div class="mk-sub" data-meta="start">—</div></div>
 <div class="mk-gap prod" data-gap="deadline"></div>
 <div class="mk" data-field="deadline"><div class="mk-lbl">ENTREGA MINUTAS</div><input id="deadline" type="date" lang="pt-BR" aria-label="Entrega das minutas"><div class="mk-sub" data-meta="deadline">—</div></div>
 <div class="mk-gap" data-gap="release"></div>
 <div class="mk" data-field="release"><div class="mk-lbl">LIBERAÇÃO <button id="suggestRelease" title="Sugerir liberação 5 dias úteis antes da sessão">−5 út.</button></div><input id="release" type="date" lang="pt-BR" aria-label="Liberação dos votos"><div class="mk-sub" data-meta="release">—</div></div>
 <div class="mk-gap" data-gap="session"></div>
 <div class="mk mk-final" data-field="session"><div class="mk-lbl">JULGAMENTO</div><input id="session" type="date" lang="pt-BR" aria-label="Data da sessão"><div class="mk-sub" data-meta="session">—</div></div>
 <div class="mk-kpis">
  <div title="Dias úteis entre o início da produção e a entrega das minutas (feriados e dias sem expediente excluídos)"><span>Produção</span><b id="kProd">—</b></div>
  <div id="kCapBox"><span>Capac. · restam</span><b id="kCap">—</b></div>
  <div title="Primeiro dia em que a equipe, no ritmo habitual de cada servidor, conclui todas as minutas"><span>Entrega ideal</span><div class="mk-sug"><b id="suggestedDate">—</b><button id="applySuggested" title="Aplicar como entrega das minutas">aplicar</button></div></div>
  <div title="Tempo de produção já decorrido × minutas já concluídas"><span>Tempo · entregue</span><b><span id="elapsedPct">—%</span> · <span id="kDone">—%</span></b></div>
 </div>
</div>
<div class="mk-warn" id="mkWarn"></div>
<span id="suggestionExplanation" hidden></span>
<div class="process-editor" hidden="" id="processEditor"><label>Processos da sessão (um número por linha)<textarea readonly id="processList" placeholder="5000000-00.2026.4.03.6000"></textarea></label><div class="actions"><button hidden class="primary" id="saveProcesses">Salvar lista</button><button id="closeProcesses">Fechar</button></div><p class="help">Lista vinculada aos processos selecionados da sessão.</p></div>
<div class="rule"></div>
<div class="section-caption"><div><h2>02 · Simulador de Designação de Processos</h2><div class="sub">Metas diárias por servidor, do início da produção à entrega das minutas</div></div><div class="actions"><span class="helper-badge" id="simStatus">—</span><button class="primary" id="add">+ Servidor</button></div></div>
<div class="sim-card">
 <div class="sim-head">
  <div class="sim-kpis k9">
   <div class="sim-kpi"><span>Total da sessão</span><b id="totalProcesses">0</b><small>processos</small></div>
   <div class="sim-kpi"><span>Designados</span><b id="designated">0</b><small id="kDesigPct">—</small></div>
   <div class="sim-kpi"><span>Sem designação</span><b id="undesignated">0</b><small id="kFreeHint">—</small></div>
   <div class="sim-kpi"><span>Minutas feitas</span><b id="kDoneN">0</b><small id="kDonePct">—</small></div>
   <div class="sim-kpi"><span>Restantes</span><b id="kRemain">0</b><small>a entregar</small></div>
   <div class="sim-kpi"><span>Dias úteis</span><b id="availableDays">—</b><small id="kDaysHint">até a entrega</small></div>
   <div class="sim-kpi"><span>Meta da equipe</span><b id="kTeamDay">—</b><small>restantes ÷ dias</small></div>
   <div class="sim-kpi"><span>Meta por servidor</span><b id="kPerServer">—</b><small id="kActive">—</small></div>
   <div class="sim-kpi"><span>Equilíbrio</span><b id="kBalance">—</b><small id="kBalanceHint">menor–maior carga</small></div>
  </div>
  <div class="dist-bar" id="distBar" aria-label="Distribuição dos processos por servidor"></div>
  <div class="sim-bar" hidden><div id="distributionProgress"></div></div><input id="manualTotal" type="number" hidden value="0">
  <div id="simWarnings"></div>
 </div>
 <div class="sim-list"><table class="simtable"><thead><tr>
  <th>Servidor</th><th>Designados<br>· parcela</th><th>Feitas<br>· restantes</th><th>Dias úteis<br>plano · faltam</th><th title="Designados ÷ dias úteis do início da produção à entrega">Meta/dia<br>planejada</th><th title="Restantes ÷ dias úteis que faltam até a entrega">Meta/dia<br>para entregar</th><th title="Média habitual de minutas por dia útil (editável)">Ritmo<br>habitual</th><th title="Feitas comparadas ao esperado até ontem, pela meta planejada">Andamento</th><th title="Data em que conclui as restantes no ritmo habitual">Término<br>no ritmo</th><th>Situação</th><th></th>
 </tr></thead><tbody id="staffBody"></tbody><tfoot id="staffFoot"></tfoot></table></div>
</div>
<div class="sim-note">Meta/dia planejada = designados ÷ dias úteis do início da produção à entrega. Meta/dia para entregar = restantes ÷ dias úteis que faltam (a partir de hoje ou do início, o que vier depois). Minutas feitas = processos com data de minuta (MINUTADO). Dias úteis descontam fins de semana, feriados do calendário e ausências de cada servidor. A designação aqui é simulação: alterar quantidades não muda o SERVIDOR dos processos.</div>
"""

READHOST_ANTIGO = "actualAssigned:assigned,"
READHOST_NOVO = r"actualAssigned:assigned,done:rows.filter(x=>x.r.SERVIDOR===name&&/^\d{4}-\d\d-\d\d/.test(String(x.r.MINUTADO||''))).length,"

RENDER = r"""const MK_GAPS={start:'preparo',deadline:'produção',release:'revisão',session:'anteced.'};
const PAL=['#2f6690','#4a8f74','#b4763a','#7a5ba6','#3d8b9c','#a6545e','#6b7d2f','#5b6f8f','#c0843d','#46708a'];
function perDay(x){if(x===null||x===undefined||Number.isNaN(x))return '—';if(x===Infinity)return 'sem dias';if(x===0)return '0';if(x<1){const n=Math.round(1/x);return n<=1?'1/dia':'1 a cada '+n+' d';}const v=Math.round(x*10)/10;return String(v).replace('.',',')+'/dia'}
function finishDate(n,from,s){if(!(n>0)||!(s.rate>0))return '';let acc=0;for(let d=from,i=0;i<3660;d=add(d,1),i++){if(working(d,s.excluded||[],s.name)){acc+=s.rate;if(acc>=n)return d}}return ''}
function firstName(n){return String(n||'').trim().split(/\s+/)[0]||'—'}
function renderTimeline(){
 const keys=['pauta','start','deadline','release','session'],issues=milestoneConflicts(state),today=now();
 keys.forEach((k,i)=>{
  const card=document.querySelector('.mk[data-field="'+k+'"]');if(!card)return;
  const err=issues[k]||[],d=state[k];card.classList.toggle('is-chronology-error',!!err.length);card.setAttribute('aria-invalid',err.length?'true':'false');card.title=err.length?'Corrija a data: '+err.join(' '):'';card.classList.toggle('passed',!!d&&d<today);
  const meta=card.querySelector('[data-meta]'),diff=d?Math.round((at(d)-at(today))/86400000):null;
  if(meta)meta.textContent=diff===null?'sem data':diff<0?'há '+(-diff)+' dias':diff===0?'hoje':'em '+diff+' dias';
  if(i){const g=document.querySelector('[data-gap="'+k+'"]'),p=state[keys[i-1]];if(g){const bad=!!(p&&d&&d<p);const n=p&&d&&!bad?days(add(p,1),d):null;g.innerHTML='<b>'+(bad?'corrigir':n===null?'—':n+' út.')+'</b><span>'+MK_GAPS[k]+'</span>';g.classList.toggle('bad',bad);g.title={start:'Preparação',deadline:'Produção das minutas',release:'Revisão',session:'Antecedência da liberação'}[k]+': dias úteis entre os dois marcos';}}
 });
 const prod=state.start&&state.deadline&&state.start<=state.deadline?days(state.start,state.deadline):null;
 $('kProd').textContent=prod===null?'—':prod+' út.';
 const total=totalCount(),done=state.staff.reduce((a,s)=>a+(+s.done||0),0),remain=Math.max(0,total-done),from=state.start&&state.start>today?state.start:today;
 const active=state.staff.filter(s=>s.included!==false&&s.rate>0);
 const cap=state.deadline?active.reduce((a,s)=>a+(days(from,state.deadline,s.excluded||[],s.name)||0)*s.rate,0):null;
 const kc=$('kCap');kc.textContent=cap===null?'—':Math.round(cap)+' · '+remain;kc.className=cap===null?'':cap>=remain?'ok':'bad';
 $('kCapBox').title=cap===null?'Informe a entrega das minutas':'No ritmo habitual, a equipe produz cerca de '+Math.round(cap)+' minuta(s) até a entrega; restam '+remain+'. '+(cap>=remain?'Folga de '+Math.round(cap-remain)+'.':'Faltam '+Math.round(remain-cap)+': adiante o início, amplie a equipe ou adie a entrega.');
 let tp='—%';if(prod){const el=state.start<today?Math.min(prod,days(state.start,add(today,-1))||0):0;tp=Math.round(el/prod*100)+'%';}
 $('elapsedPct').textContent=tp;$('kDone').textContent=total?Math.round(done/total*100)+'%':'—%';
 $('sessionCombinedLabel').textContent=readOnly?'Escolher sessão':sessionKey;
 const msgs=Object.values(issues).flat();$('mkWarn').textContent=msgs.length?'Ordem dos marcos: '+[...new Set(msgs)].slice(0,2).join(' '):'';
}

function renderStaff(){
 const today=now(),from=state.start&&state.start>today?state.start:today,end=state.deadline,count=totalCount();
 const assigned=state.staff.reduce((a,s)=>a+(+s.assigned||0),0),unassigned=count-assigned;
 const done=state.staff.reduce((a,s)=>a+(+s.done||0),0),remain=Math.max(0,count-done);
 const overall=end?days(from,end):null,plan=state.start&&end?days(state.start,end):null;
 const active=state.staff.filter(s=>s.included!==false);
 $('totalProcesses').textContent=count;$('procCount').textContent=count;$('designated').textContent=assigned;$('undesignated').textContent=unassigned;
 $('kDesigPct').textContent=count?Math.round(assigned/count*100)+'% da sessão':'—';
 $('kFreeHint').textContent=unassigned>0&&active.length?'+'+Math.ceil(unassigned/active.length)+' p/ cada um':unassigned<0?'designação excedente':'tudo designado';
 $('kDoneN').textContent=done;$('kDonePct').textContent=count?Math.round(done/count*100)+'% concluído':'—';$('kRemain').textContent=remain;
 $('availableDays').textContent=overall===null?'—':overall;$('kDaysHint').textContent=plan===null?'até a entrega':'de '+plan+' no plano';
 $('kTeamDay').textContent=overall?perDay(remain/overall):'—';
 $('kPerServer').textContent=overall&&active.length?perDay(remain/overall/active.length):'—';$('kActive').textContent=active.length+' servidor(es) ativo(s)';
 const loads=active.map(s=>+s.assigned||0);
 $('kBalance').textContent=loads.length?Math.min(...loads)+'–'+Math.max(...loads):'—';
 $('kBalanceHint').textContent=loads.length?'média '+String(Math.round(loads.reduce((a,b)=>a+b,0)/loads.length*10)/10).replace('.',',')+' por servidor':'menor–maior carga';
 $('daysbadge').textContent=overall===null?'— dias úteis':overall+' dias úteis';
 $('distributionProgress').style.width=(count?Math.min(100,assigned/count*100):0)+'%';
 $('simStatus').textContent=count?Math.round(assigned/count*100)+'% distribuídos · '+Math.round(done/count*100)+'% feitos':'Sem processos';
 const base=Math.max(count,assigned)||1;
 $('distBar').innerHTML=state.staff.map((s,i)=>{const a=+s.assigned||0;if(!a)return '';const w=a/base*100;return '<i style="width:'+w+'%;background:'+PAL[i%PAL.length]+(s.included===false?';opacity:.45':'')+'" title="'+esc(s.name)+': '+a+' processo(s) · '+Math.round(a/(count||1)*100)+'%">'+(w>7?esc(firstName(s.name))+' '+a:w>3?a:'')+'</i>'}).join('')+(unassigned>0?'<i class="free" style="width:'+unassigned/base*100+'%" title="Sem designação: '+unassigned+'">'+(unassigned/base>.06?'livres '+unassigned:'')+'</i>':'');
 let tA=0,tF=0,tR=0,tRate=0,tExp=0;
 $('staffBody').innerHTML=state.staff.map((s,i)=>{
  const abs=s.excluded||[],a=+s.assigned||0,f=Math.min(a,+s.done||0),r=Math.max(0,a-f),cor=PAL[i%PAL.length],on=s.included!==false;
  const dPlan=state.start&&end&&state.start<=end?days(state.start,end,abs,s.name):null,dLeft=end?days(from,end,abs,s.name):null;
  const mPlan=dPlan>0?a/dPlan:dPlan===0&&a?Infinity:null,mNow=dLeft>0?r/dLeft:dLeft===0?(r?Infinity:0):null;
  const el=dPlan&&state.start<today?Math.min(dPlan,days(state.start,add(today,-1),abs,s.name)||0):0,exp=dPlan?Math.round(a*el/dPlan):0,delta=f-exp;
  const fin=r?finishDate(r,from,s):'',slack=fin&&end?(fin<=end?days(add(fin,1),end,abs,s.name):-days(add(end,1),fin,abs,s.name)):null;
  let st,cls;if(!on){st='Fora da simulação';cls='muted'}else if(!end){st='Defina a entrega';cls='muted'}else if(!a){st='Sem designação';cls='muted'}else if(!r){st='Concluído';cls='ok'}else if(!dLeft){st='Prazo esgotado';cls='bad'}else if(mNow<=s.rate){st='No ritmo';cls='ok'}else if(mNow<=s.rate*1.25){st='Atenção';cls='warn'}else{st='Acima da capacidade';cls='bad'}
  if(on){tA+=a;tF+=f;tR+=r;tRate+=+s.rate||0;tExp+=exp;}
  const and=!dPlan||!a?'<span class="even">—</span>':state.start>=today?'<span class="even">não iniciou</span>':delta>0?'<span class="adv">+'+delta+' adiantado</span>':delta<0?'<span class="late">'+delta+' atrasado</span>':'<span class="even">em dia</span>';
  return '<tr data-id="'+esc(s.id)+'"><td><div class="c-name"><span class="dot" style="background:'+cor+'"></span><div><input type="text" data-key="name" value="'+esc(s.name)+'"><label class="toggleline"><input type="checkbox" data-key="included" '+(on?'checked':'')+'> participa</label></div></div></td>'
  +'<td><input class="in-n" type="number" min="0" data-key="assigned" value="'+a+'"><div class="share"><i style="width:'+(count?Math.min(100,a/count*100):0)+'%;background:'+cor+'"></i></div><small>'+(count?Math.round(a/count*100):0)+'% da sessão</small></td>'
  +'<td><b>'+f+'</b> · '+r+'<small>feitas · restantes</small></td>'
  +'<td>'+(dPlan===null?'—':dPlan)+' · '+(dLeft===null?'—':dLeft)+'<small>'+(abs.length?abs.length+' ausência(s)':'sem ausências')+'</small></td>'
  +'<td class="meta"><b>'+perDay(mPlan)+'</b><small>'+(mPlan&&isFinite(mPlan)?'≈ '+String(Math.round(mPlan*5*10)/10).replace('.',',')+' por semana':'')+'</small></td>'
  +'<td class="meta now '+(on&&a?cls:'')+'"><b>'+perDay(mNow)+'</b><small>'+(mNow&&isFinite(mNow)&&s.rate?Math.round(mNow/s.rate*100)+'% do ritmo':'')+'</small></td>'
  +'<td><input class="in-n" type="number" min="0" step="0.5" data-key="rate" value="'+s.rate+'"><small>minutas/dia</small></td>'
  +'<td>'+and+'<small>'+(dPlan&&a&&state.start<today?'esperado '+exp+' · feitas '+f:'')+'</small></td>'
  +'<td>'+(r?(fin?fmt(fin):'—'):a?'concluído':'—')+'<small>'+(slack===null?'':slack>=0?slack+' út. de folga':(-slack)+' út. após a entrega')+'</small></td>'
  +'<td><span class="st-pill '+cls+'">'+st+'</span></td>'
  +'<td style="white-space:nowrap"><button class="chipbtn" data-action="expand" title="Ausências">'+(s.expanded?'▾':'▸')+'</button><button class="chipbtn" data-action="remove" title="Remover servidor">×</button></td></tr>'
  +(s.expanded?'<tr class="absences" data-id="'+esc(s.id)+'"><td colspan="11"><label>Ausências individuais de '+esc(s.name)+' (dd/mm/aaaa, uma por linha)<textarea data-key="excluded" rows="2">'+abs.map(fmt).join('\n')+'</textarea></label></td></tr>':'');
 }).join('')||'<tr><td colspan="11" class="muted">Adicione servidores para simular a designação.</td></tr>';
 const capDate=capacityDate(),tDelta=tF-tExp;
 $('staffFoot').innerHTML=state.staff.length?'<tr><td>Equipe ('+active.length+')</td><td>'+tA+'</td><td>'+tF+' · '+tR+'</td><td>'+(plan===null?'—':plan)+' · '+(overall===null?'—':overall)+'</td><td>'+(plan?perDay(tA/plan):'—')+'</td><td>'+(overall?perDay(tR/overall):'—')+'</td><td>'+String(tRate).replace('.',',')+'/dia</td><td>'+(state.start&&state.start<today&&plan?(tDelta>0?'+'+tDelta:tDelta)+' no total':'—')+'</td><td>'+(capDate?fmt(capDate):'—')+'</td><td colspan="2"></td></tr>':'';
 const alerts=[];if(unassigned<0)alerts.push('A soma das designações supera o total da sessão em '+(-unassigned)+' processo(s).');else if(unassigned>0)alerts.push(unassigned+' processo(s) sem designação'+(active.length?' — cerca de '+Math.ceil(unassigned/active.length)+' para cada servidor ativo.':'.'));if(count&&!state.start)alerts.push('Informe o início da produção para calcular metas e a entrega sugerida.');if(!state.deadline)alerts.push('Informe ou aplique a entrega das minutas para calcular as metas diárias.');
 $('simWarnings').innerHTML=alerts.map(s=>'<div class="note '+(unassigned<0?'warn':'')+'">'+esc(s)+'</div>').join('');
}
"""

UPDATE_ANTIGO = "$('suggestionExplanation').textContent=`${totalCount()} processos · ${active} servidor(es) ativo(s) · ritmo inicial de 3 processos/servidor/dia, ajustável na tabela · excluídos dias sem expediente e ausências.`;"
UPDATE_NOVO = "$('suggestionExplanation').textContent=`${totalCount()} processos · ${active} servidor(es) ativo(s) · ritmo habitual de cada servidor · excluídos dias sem expediente e ausências.`;"


# entrega sugerida: a partir de hoje (ou do início, se ainda não começou) e só com as minutas que faltam
CAPACIDADE_ANTIGA = "function capacityDate(){const total=totalCount();if(!state.start||total===0)return '';let remaining=total;const active=state.staff.filter(s=>s.included!==false&&s.rate>0);if(!active.length)return '';for(let d=state.start,i=0;i<3660;d=add(d,1),i++){"
CAPACIDADE_NOVA = "function capacityDate(){const total=totalCount();if(!state.start||total===0)return '';let remaining=total-state.staff.reduce((a,s)=>a+(+s.done||0),0);if(remaining<=0)return '';const active=state.staff.filter(s=>s.included!==false&&s.rate>0);if(!active.length)return '';for(let d=state.start>now()?state.start:now(),i=0;i<3660;d=add(d,1),i++){"


def aplicar(html: str) -> str:
    def troca(antigo, novo, nome):
        nonlocal html
        if html.count(antigo) != 1:
            raise SystemExit(f"planejamento/{nome}: trecho encontrado {html.count(antigo)} vez(es) — a página mudou; revise o ajuste.")
        html = html.replace(antigo, novo)

    i, j = html.find(INICIO_MARCOS), html.find(FIM_SIMULADOR)
    if i < 0 or j < i:
        raise SystemExit("planejamento: seções 01/02 não encontradas — a página mudou; revise o ajuste.")
    html = html[:i] + MARCOS + html[j:]
    a, b = html.find("function renderTimeline(){"), html.find("function renderMonths(){")
    if a < 0 or b < a:
        raise SystemExit("planejamento: funções renderTimeline/renderStaff não encontradas.")
    html = html[:a] + RENDER + html[b:]
    troca(READHOST_ANTIGO, READHOST_NOVO, "readHost")
    troca(UPDATE_ANTIGO, UPDATE_NOVO, "update")
    troca(CAPACIDADE_ANTIGA, CAPACIDADE_NOVA, "capacidade")
    # "+ Nova sessão" e "Configurações" já existem na própria página da Seleção Prévia
    troca('<button id="newSession">+ Nova sessão</button><button id="settings">Configurações</button>', '', "botões")
    troca("$('newSession').onclick=()=>root.renderVals().newSession();\n$('settings').onclick=()=>root.setState({dialog:true});\n", '', "botões-js")
    troca("</head>", CSS + "</head>", "css")
    return html
