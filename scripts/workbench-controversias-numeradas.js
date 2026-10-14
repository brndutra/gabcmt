<!-- Controvérsias numeradas · extensão da aba Matriz do workbench (v38). Inserir antes de </body> da aba Matriz.
     Controvérsias (parágrafos com controversia:true) incluídas em sequência saem numa só frase numerada. -->
<script id="cmt-cv-frase">
/* Controvérsias incluídas em sequência viram uma só frase numerada:
   “A controvérsia envolve discutir: (1) …; e (2) ….” (cada controvérsia continua sendo incluída uma a uma). */
(function(){
const RX=/^(Senhores Desembargadores,\s*)?a\s+controv[ée]rsia\s+envolve\s+discutir:?\s+/i;
const _p=window.paras;if(typeof _p!=='function')return;
window.paras=function(){const P=_p.apply(this,arguments);if(!Array.isArray(P))return P;
  let cvs=[];try{const m=model(),st=state(),inc=new Set();Object.values(st.incluidos||{}).forEach(a=>(a||[]).forEach(x=>inc.add(x.pid)));
    cvs=CAT.paragrafos.filter(p=>p.matrizId===m.id&&p.controversia&&inc.has(p.id)).map(p=>String(p.texto||'').trim().replace(RX,'').replace(/[.;\s]+$/,''))}catch(e){}
  if(cvs.length<2)return P;
  const out=[];let run=null;
  const flush=()=>{if(!run)return;const L=run.itens;
    if(L.length<2)out.push(run.primeiro);
    else out.push({...run.primeiro,text:(run.pref?run.pref+'a':'A')+' controvérsia envolve discutir: '+L.map((f,i)=>(i===L.length-1?'e ':'')+'('+(i+1)+') '+f).join('; ')+'.'});
    run=null};
  P.forEach(x=>{const tx=String((x&&x.text)||'').trim(),m=x&&x.tipo!=='hdr'&&x.tipo!=='quote'&&tx.match(RX),f=m?tx.slice(m[0].length).replace(/[.;\s]+$/,''):'';
    if(m&&cvs.includes(f)){if(!run)run={primeiro:x,pref:m[1]||'',itens:[]};run.itens.push(f)}else{flush();out.push(x)}});
  flush();return out};
try{if(!pvDirty)refreshPreview(true)}catch(e){}
})();
</script>
