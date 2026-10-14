<!-- Questões do caso · extensão da aba Matriz do workbench (v31).
     Inserir antes de </body> da aba Matriz e, na página principal, passar ao modelo
     questoes/questoesAbertura/questoesTopico (de esqueleto._questoes, _questoesAbertura, _questoesTopico)
     nos dois construtores de modelo (importarModeloParadigma e sincronizarBibliotecaParadigmas). -->
<style id="cmt-questoes-css">
.qz{margin:0 0 14px;padding:12px 14px;border:1px solid var(--line2);border-radius:10px;background:var(--panel)}
.qz-h{display:flex;align-items:baseline;gap:8px;margin:0 0 8px}
.qz-h b{font:800 10px/1 Inter,system-ui,sans-serif;letter-spacing:.09em;text-transform:uppercase;color:var(--amber)}
.qz-h span{font:12px/1.3 Inter,system-ui,sans-serif;color:var(--muted)}
.qz-g{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin:6px 0 0}
.qz-g>i{font:700 9.5px/1 Inter,system-ui,sans-serif;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);font-style:normal;min-width:118px}
.qz-c{font:600 12.5px/1.2 Inter,system-ui,sans-serif;padding:6px 11px;border-radius:999px;border:1px solid var(--line2);background:var(--panel2);color:var(--text);cursor:pointer}
.qz-c:hover{border-color:var(--al)}
.qz-c.on{background:var(--amber);border-color:var(--amber);color:#fff}
.qz-c.on::before{content:'✓ '}
.qz-c[disabled]{opacity:.45;cursor:not-allowed}
.qz-n{font:12px/1.45 Inter,system-ui,sans-serif;color:var(--muted);margin:8px 0 0}
</style>
<script id="cmt-questoes-js">
/* Questões do modelo: cada controvérsia/questão é um item selecionável.
   Ao marcar, entra na frase da Controvérsia e liga os blocos (subtópicos) e parágrafos vinculados a ela;
   ao desmarcar, sai da frase e desliga o que só ela usava. Definição em esqueletoModelo._questoes. */
(function(){
'use strict';
const Q=()=>{const m=model();return m&&Array.isArray(m.questoes)?m.questoes:[]};
const ativas=()=>{const st=state();if(!Array.isArray(st.questoes))st.questoes=[];return st.questoes};
const card=(c)=>CAT.paragrafos.find(p=>p.matrizId===model().id&&p.secao===c.secao&&posOf(p)===(+c.ordem||1)&&verOf(p)===String(c.versao||'a').toLowerCase());
function frase(){
  const on=new Set(ativas()),L=Q().filter(q=>on.has(q.id)&&q.frase).map(q=>{let f=String(q.frase).trim().replace(/[.;]+$/,'');
    Q().forEach(s=>{if(on.has(s.id)&&s.sufixoEm&&s.sufixoEm.questao===q.id)f+=s.sufixoEm.texto});return f});
  if(!L.length)return '';
  const ab=(model().questoesAbertura||'A controvérsia envolve discutir');
  if(L.length===1)return ab+' '+L[0]+'.';
  return ab+': '+L.map((f,i)=>`(${i+1}) ${f}`).map((x,i,a)=>i===a.length-1?'e '+x:x).join('; ')+'.';
}
function posicoes(alvos){const m=new Set();(alvos||[]).forEach(q=>(q&&q.cartoes||[]).forEach(c=>m.add(c.secao+'|'+(+c.ordem||1))));return [...m]}
function aplicar(alvos){
  const st=state(),on=new Set(ativas()),QS=Q();
  if(!st.estr||typeof st.estr!=='object')st.estr={ord:{},nomes:{},rem:[],extra:[]};const e=st.estr;e.rem=Array.isArray(e.rem)?e.rem:[];
  const obr=new Set((model().__topBase||model().topicos||[]).filter(t=>t&&t.obrigatorio).map(t=>t.id));
  /* subtópicos: presentes se alguma questão marcada os usa; os demais geridos por questões saem (recuperáveis em “+ subtópico”) */
  const usados=new Set(),geridos=new Set();
  QS.forEach(q=>[...(q.topicos||[]),...(q.cartoes||[]).map(c=>c.secao)].forEach(t=>{geridos.add(t);if(on.has(q.id))usados.add(t)}));
  geridos.forEach(t=>{if(obr.has(t))return;const u=usados.has(t);(st.secao[t]??={}).ativo=u;e.rem=e.rem.filter(x=>x!==t);if(!u)e.rem.push(t)});
  /* parágrafos: em cada posição tocada, vale o da última questão marcada (na ordem do modelo) que a define */
  posicoes(alvos).forEach(k=>{
    const [sec,ord]=k.split('|');
    st.incluidos[sec]=(st.incluidos[sec]||[]).filter(x=>{const p=CAT.paragrafos.find(y=>y.id===x.pid);return !(p&&p.matrizId===model().id&&p.secao===sec&&posOf(p)===+ord)});
    let esc=null;QS.forEach(q=>{if(on.has(q.id))(q.cartoes||[]).forEach(c=>{if(c.secao===sec&&(+c.ordem||1)===+ord)esc=c})});
    if(esc){const p=card(esc);if(p){st.incluidos[sec].push({uid:guid('ins'),pid:p.id,texto:p.texto})}}
  });
  /* frase da controvérsia, numerada na ordem do modelo */
  const ct=model().questoesTopico||'contro';
  (st.secao[ct]??={}).texto=frase();st.secao[ct].ativo=true;
  st.questoes=QS.filter(q=>on.has(q.id)).map(q=>q.id);
}
function iniciar(){const QS=Q();if(!QS.length)return false;const st=state();if(st.questoesIni)return false;
  st.questoesIni=true;st.questoes=QS.filter(q=>q.padrao).map(q=>q.id);aplicar(QS);return true}
function toggle(id){
  const QS=Q(),q=QS.find(x=>x.id===id);if(!q)return;const a=ativas(),i=a.indexOf(id);
  if(i>=0){a.splice(i,1);QS.forEach(s=>{if((s.requer||[]).includes(id)){const j=a.indexOf(s.id);if(j>=0){a.splice(j,1);aplicar([s])}}})}
  else{(q.requer||[]).forEach(r=>{if(!a.includes(r)){a.push(r);aplicar([QS.find(x=>x.id===r)])}});a.push(id)}
  aplicar([q]);
  notifyChange();renderSkeleton();if(!pvDirty)refreshPreview(true);
}
function painel(){
  const sk=$('skeleton');if(!sk)return;let box=$('qzBox');const QS=Q();
  if(!QS.length){if(box)box.remove();return}
  if(!box){box=document.createElement('section');box.id='qzBox';box.className='qz';sk.parentNode.insertBefore(box,sk)}
  const on=new Set(ativas()),grupos=[];QS.forEach(q=>{const g=q.grupo||'Controvérsias';if(!grupos.includes(g))grupos.push(g)});
  box.innerHTML=`<div class="qz-h"><b>Questões do caso</b><span>marque as que o caso apresenta — a controvérsia e os blocos vinculados entram sozinhos</span></div>`
   +grupos.map(g=>`<div class="qz-g"><i>${esc(g)}</i>${QS.filter(q=>(q.grupo||'Controvérsias')===g).map(q=>{const falta=(q.requer||[]).filter(r=>!on.has(r));return `<button type="button" class="qz-c${on.has(q.id)?' on':''}" data-qz="${esc(q.id)}" title="${esc(q.dica||'')}${falta.length?' (marca também: '+falta.map(r=>(QS.find(x=>x.id===r)||{}).rotulo||r).join(', ')+')':''}">${esc(q.rotulo)}</button>`}).join('')}</div>`).join('')
   +(on.size?'':`<div class="qz-n">Nenhuma questão marcada: a controvérsia fica vazia e só os subtópicos obrigatórios aparecem.</div>`);
}
document.addEventListener('click',ev=>{const b=ev.target.closest&&ev.target.closest('[data-qz]');if(!b)return;ev.preventDefault();toggle(b.dataset.qz)},true);
const _rs=window.renderSkeleton;window.renderSkeleton=function(){let r=_rs.apply(this,arguments);try{if(iniciar()){r=_rs.apply(this,arguments);if(!pvDirty)refreshPreview(true)}painel()}catch(e){console.error('questões',e)}return r};
try{renderSkeleton()}catch(e){}
window.cmtQuestoes={toggle,frase,ativas,reiniciar(){state().questoesIni=false;renderSkeleton()}};
})();
</script>
