<!-- Controvérsias no topo da Minuta · extensão da aba Matriz do workbench (v38). Inserir antes de </body> da aba Matriz, depois de workbench-controversias-numeradas.js.
     Inclui a correção do redesenho: a estrutura ficava um passo atrás das controvérsias marcadas. -->
<style id="cmt-cv-topo-css">
.cvt{margin:0 0 12px;padding:10px 14px 12px;border:1px solid var(--line2);border-radius:10px;background:var(--panel)}
.cvt-h{display:flex;align-items:baseline;gap:8px;margin:0 0 8px;flex-wrap:wrap}
.cvt-h b{font:800 10px/1 Inter,system-ui,sans-serif;letter-spacing:.09em;text-transform:uppercase;color:var(--amber)}
.cvt-h span{font:12px/1.3 Inter,system-ui,sans-serif;color:var(--muted)}
.cvt-r{display:flex;align-items:flex-start;gap:8px;margin:6px 0 0}
.cvt-r>i{font:800 11px/26px Inter,system-ui,sans-serif;font-style:normal;color:var(--muted);min-width:24px}
.cvt-l{display:flex;flex-wrap:wrap;gap:6px}
.cvt-c{font:600 12.5px/1.25 Inter,system-ui,sans-serif;padding:5px 11px;border-radius:999px;border:1px solid var(--line2);background:var(--panel2,transparent);color:var(--text);cursor:pointer;text-align:left;max-width:100%}
.cvt-c:hover{border-color:var(--al)}
.cvt-c.on{background:var(--amber);border-color:var(--amber);color:#fff}
.cvt-c.on::before{content:'✓ '}
.cvt-n{font:12px/1.4 Inter,system-ui,sans-serif;color:var(--muted);margin:8px 0 0}
</style>
<script id="cmt-cv-topo">
/* Controvérsias do modelo no topo da Minuta: as mesmas C1, C2… do subtópico Controvérsia, em chips.
   Clicar inclui/retira a controvérsia (e, com ela, os trechos vinculados); versões da mesma posição se substituem. */
(function(){
const lista=()=>{let m;try{m=model()}catch(e){return []}return CAT.paragrafos.filter(p=>p.matrizId===m.id&&p.controversia)};
const incl=()=>{const s=new Set();Object.values(state().incluidos||{}).forEach(a=>(a||[]).forEach(x=>s.add(x.pid)));return s};
function painel(){const sk=$('skeleton');if(!sk)return;let box=$('cvTopo');const L=lista();
  if(!L.length){if(box)box.remove();return}
  if(!box){box=document.createElement('section');box.id='cvTopo';box.className='cvt'}
  if(box.nextElementSibling!==sk)sk.parentNode.insertBefore(box,sk);
  const on=incl(),pos=[...new Set(L.map(posOf))].sort((a,b)=>a-b);
  const html=`<div class="cvt-h"><b>Controvérsias do caso</b><span>marque as do processo — a frase da controvérsia e os trechos vinculados entram sozinhos; versões da mesma linha se substituem</span></div>`
   +pos.map(o=>`<div class="cvt-r"><i>C${o}</i><div class="cvt-l">${L.filter(p=>posOf(p)===o).sort((a,b)=>verOf(a).localeCompare(verOf(b))).map(p=>`<button type="button" class="cvt-c${on.has(p.id)?' on':''}" data-cvt="${esc(p.id)}" title="${esc(p.texto||'')}">${esc(p.titulo||('Controvérsia '+o+verOf(p)))}</button>`).join('')}</div></div>`).join('')
   +(L.some(p=>on.has(p.id))?'':'<div class="cvt-n">Nenhuma controvérsia marcada: só os subtópicos obrigatórios aparecem.</div>');
  if(box.dataset.h!==html){box.innerHTML=html;box.dataset.h=html}}
document.addEventListener('click',e=>{const b=e.target.closest&&e.target.closest('[data-cvt]');if(!b)return;e.preventDefault();e.stopPropagation();
  const p=CAT.paragrafos.find(x=>x.id===b.dataset.cvt);if(!p)return;togglePar(p);notifyChange();renderSkeleton();if(!pvDirty)refreshPreview(true)},true);
/* correção: a v38 sincroniza os vínculos (cvSync) ao montar a prévia, depois de desenhar a estrutura,
   e a estrutura ficava um passo atrás; se a sincronização mudar o estado, redesenha a estrutura em seguida */
{const _p=window.paras;let pend=false;window.paras=function(){let a;try{a=state().cvSig}catch(e){}const r=_p.apply(this,arguments);
  try{if(state().cvSig!==a&&!pend){pend=true;setTimeout(()=>{pend=false;renderSkeleton()},0)}}catch(e){}return r}}
const _rs=window.renderSkeleton;window.renderSkeleton=function(){const r=_rs.apply(this,arguments);try{painel()}catch(e){console.error('cv-topo',e)}return r};
try{painel()}catch(e){}
})();
</script>
