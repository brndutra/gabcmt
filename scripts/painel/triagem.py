"""Triagem Processual — nova aba do Painel Central, no padrão da Seleção Prévia.

- No Acervo Central, o seletor de sessão destino ganha a opção "Triagem Processual": os processos marcados vão para a
  triagem (campo interno _triagem = data do encaminhamento), sem mexer em Seleção Prévia, sessão ou pauta.
- A aba tem à esquerda a BANDEJA DA TRIAGEM (fichas dos processos ainda sem escaninho: busca, marcação, remoção) e à
  direita o MÓVEL DE ESCANINHOS: nichos com placa (título e subtítulo), pilha de autos proporcional à quantidade,
  bilhete com a observação e cor da pasta. Marca-se fichas e clica-se no escaninho (ou arrastam-se as fichas até ele)
  para guardá-las (campo interno _escaninho). Clicar num escaninho o abre logo abaixo, no próprio móvel: placa,
  subtítulo, bilhete e cor editáveis, processos guardados (devolver à bandeja ou remover da triagem), excluir.
  Os escaninhos (this.escaninhos) são gravados junto com o restante do painel.
"""

TRI = "__triagem__"

CSS = """    .tri-page{display:grid;gap:14px;min-width:0}
    .tri-kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}
    .tri-kpi{border-radius:12px;background:#fff;border:1px solid #e3e7ec;padding:12px 14px;box-shadow:0 8px 20px rgba(20,38,60,.04)}
    .tri-kpi>span{display:block;font-size:9px;font-weight:850;letter-spacing:.07em;color:#7e8b99}
    .tri-grid{display:grid;grid-template-columns:330px minmax(0,1fr);gap:16px;align-items:start;min-width:0}
    .tri-bandeja{border-radius:16px;background:#fff;border:1px solid #e3e7ec;box-shadow:0 10px 30px rgba(20,38,60,.08);overflow:hidden;position:sticky;top:12px}
    .tri-band-topo{padding:13px 14px 10px;background:linear-gradient(180deg,#f6f7f9,#fff);border-bottom:1px solid #e3e7ec}
    .tri-band-topo input{margin-top:8px;width:100%;border:1px solid #e3e7ec;border-radius:10px;background:#eff1f4;color:#14263c;padding:8px 11px;font:inherit;font-size:12px;outline:none}
    .tri-band-topo input:focus{border-color:#1f3d63;background:#fff}
    .tri-band-lista{max-height:calc(100vh - 330px);min-height:220px;overflow:auto;padding:10px 12px 12px;display:grid;gap:8px;align-content:start}
    .tri-ficha{position:relative;display:grid;grid-template-columns:auto minmax(0,1fr);gap:9px;align-items:start;background:#fbfaf6;color:#1d2a38;border:1px solid #e1dccf;border-radius:8px;padding:9px 10px;cursor:grab}
    .tri-ficha::before{content:"";position:absolute;left:0;top:8px;bottom:8px;width:3px;border-radius:0 3px 3px 0;background:#c9cfd8}
    .tri-ficha:hover{border-color:#c8c1ad}
    .tri-ficha.sel{border-color:#d9a441;background:#fffaf0}.tri-ficha.sel::before{background:#d9a441}
    .tri-ficha .num{font:600 11.5px "IBM Plex Mono",ui-monospace,SFMono-Regular,Consolas,monospace;letter-spacing:-.02em}
    .tri-ficha .meta{font-size:11px;color:#56636f;margin-top:2px;line-height:1.35}
    .tri-tag{display:inline-block;font-size:9px;font-weight:850;letter-spacing:.03em;padding:2px 6px;border-radius:99px;background:#e9edf2;color:#33506e;margin:4px 4px 0 0}
    .tri-tag.ouro{background:#f7e7c4;color:#7a5512}
    .tri-mover{display:flex;gap:6px;align-items:stretch;margin-top:8px}
    .tri-mover select{flex:1;min-width:0;border:1px solid #d8dee5;border-radius:9px;background:#fff;padding:7px 8px;font:inherit;font-size:11px;font-weight:700;color:#14263c;outline:none;cursor:pointer}
    .tri-mover-btn{flex:0 0 auto;display:inline-flex;align-items:center;gap:4px;border:0;border-radius:9px;background:#d9a441;color:#33240a;padding:6px 11px;font-size:15px;line-height:1;cursor:pointer}
    .tri-mover-btn b{font-size:10.5px;font-weight:900;background:rgba(51,36,10,.12);border-radius:99px;padding:2px 6px}
    .tri-mover-btn.sp{background:#1f3d63;color:#fff}.tri-mover-btn.sp b{background:rgba(255,255,255,.18)}
    .tri-sp-envio{margin-top:6px}
    .tri-selbar{display:flex;align-items:center;gap:10px;flex-wrap:wrap;padding:8px 12px;margin:0 0 10px;border:1px solid #e1e7ee;border-radius:11px;background:#f7f9fc;font-size:11.5px;color:#55657a}
    .tri-selbar.on{border-color:#e7c77d;background:#fff9ea}
    .tri-sel-todos{display:inline-flex;align-items:center;gap:6px;font-weight:850;color:#1f3d63;cursor:pointer}
    .tri-sel-msg{flex:1 1 220px;min-width:0}
    .tri-sel-sp{display:inline-flex;align-items:center;gap:6px;margin-left:auto}.tri-sel-sp select{max-width:220px;border:1px solid #d6e0ea;border-radius:8px;padding:5px 8px;font:inherit;font-size:11.5px;background:#fff}
    .tri-chk,.tri-sel-todos input{width:15px;height:15px;accent-color:#1f3d63;cursor:pointer;margin:0}
    .tri-pc-marca{display:inline-flex!important;align-items:center;gap:6px}
    .tri-pcard.marcada{box-shadow:0 0 0 2px #e3b453 inset,0 1px 3px rgba(0,0,0,.05)}
    .tri-plan-tr.marcada .c{background:#fff6dc}
    .tri-mover-btn:disabled{background:#e9edf2;color:#98a4b0;cursor:not-allowed}
    .tri-band-pe{display:flex;gap:6px;align-items:center;justify-content:space-between;flex-wrap:wrap;padding:10px 12px;border-top:1px solid #e3e7ec;font-size:11px;color:#6d7b8a}
    .tri-movel{position:relative;border-radius:16px;background:#fff;border:1px solid #e3e7ec;box-shadow:0 10px 30px rgba(20,38,60,.08);min-width:0;overflow:hidden}
    .tri-movel-topo{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;padding:13px 14px 10px;background:linear-gradient(180deg,#f6f7f9,#fff);border-bottom:1px solid #e3e7ec;color:#14263c}
    .tri-placa-mestra{font-size:12.5px;font-weight:900;letter-spacing:.06em;color:#14263c}
    .tri-placa-mestra i{display:none}
    .tri-filtro{border:1px solid #d8dee5;background:#fff;color:#1f3d63;border-radius:99px;padding:5px 11px;font-size:10.5px;font-weight:800;cursor:pointer}
    .tri-filtro.on{background:#1f3d63;color:#fff;border-color:#1f3d63}
    .tri-dica{margin:0;padding:9px 14px 0;font-size:10.5px;color:#6d7b8a}
    .tri-grade{display:grid;grid-template-columns:repeat(auto-fill,minmax(158px,1fr));gap:10px;padding:10px 14px 12px}
    .tri-nicho{position:relative;height:132px;border-radius:10px;border:1px solid #e3e7ec;padding:0;text-align:left;font:inherit;background:#f6f8fa;cursor:pointer;overflow:hidden}
    .tri-nicho:hover{border-color:#b7c6d6;background:#f1f5f9}
    .tri-nicho:focus-visible{outline:2px solid #d9a441;outline-offset:2px}
    .tri-nicho.alvo,.tri-nicho.pronto:hover{border-color:#d9a441;background:#fffaf0}
    .tri-nicho.aberto{border:2px solid #1f3d63;background:#eef3f8}
    .tri-pilha{position:absolute;left:12px;right:12px;bottom:46px;height:40px}
    .tri-folha{position:absolute;left:0;right:0;height:6px;border-radius:2px;background:#fff;border:1px solid #d9d4c7}
    .tri-capa{position:absolute;left:0;right:0;height:8px;border-radius:2px}
    .tri-contador{position:absolute;top:7px;right:7px;min-width:22px;height:19px;padding:0 6px;border-radius:99px;display:grid;place-items:center;background:#1f3d63;color:#fff;font-weight:900;font-size:10.5px}
    .tri-vazio-nicho{position:absolute;left:0;right:0;top:52px;text-align:center;color:#98a4b0;font-size:11px;font-weight:700}
    .tri-placa{position:absolute;left:6px;right:6px;bottom:6px;height:34px;display:flex;flex-direction:column;justify-content:center;border-radius:8px;padding:4px 10px 4px 12px;background:#fff;border:1px solid #e3e7ec;border-left:4px solid #d9a441;color:#14263c}
    .tri-placa .t{display:block;font-weight:850;font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .tri-placa .s{display:block;font-size:9px;font-weight:650;color:#6d7b8a;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .tri-bilhete{position:absolute;top:7px;left:7px;max-width:70%;padding:3px 6px;background:#fff4c2;border:1px solid #efdf94;color:#4a3d0f;font-size:8.5px;line-height:1.3;border-radius:5px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;white-space:pre-wrap}
    .tri-nicho.novo{display:grid;place-items:center;text-align:center;background:#fff;border:2px dashed #cfd8e2;color:#6d7b8a}
    .tri-nicho.novo:hover{border-color:#d9a441;color:#8a6416;background:#fffaf0}
    .tri-aberto{margin:0 14px 14px;border-radius:12px;background:#f6f8fa;border:1px solid #d6e0ea;color:#14263c;overflow:hidden}
    .tri-aberto-topo{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:nowrap;padding:10px 12px;background:#eef3f8;border-bottom:1px solid #d6e0ea}
    .tri-aberto-topo .tri-placa{position:relative;left:auto;right:auto;bottom:auto;height:auto;flex:0 1 auto;min-width:200px;max-width:380px;padding:7px 12px 6px 12px}
    .tri-aberto-topo .tri-placa .t{font-size:14px}.tri-aberto-topo .tri-placa .s{font-size:11px}
    .tri-aberto-corpo{display:grid;grid-template-columns:minmax(240px,.8fr) minmax(0,1.2fr);gap:16px;padding:14px}
    .tri-config-barra{flex:1 1 0;min-width:0;display:flex;align-items:center;gap:10px}
    .tri-config-toggle{flex:0 0 auto;white-space:nowrap;border:1px solid #d6e0ea;background:#fff;border-radius:8px;padding:5px 10px;font-size:10.5px;font-weight:850;color:#1f3d63;cursor:pointer}
    .tri-config-resumo{display:flex;align-items:center;gap:6px;min-width:0;flex:1;font-size:10.5px;color:#6d7b8a;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .tri-cor-ponto{flex:0 0 auto;width:10px;height:10px;border-radius:50%}
    .tri-config{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;padding:12px;border-bottom:1px solid #d6e0ea}
    .tri-config .tri-campo{margin:0}.tri-config .tri-l2{grid-column:span 1}
    .tri-config textarea{min-height:58px}
    .tri-procs{padding:12px;max-height:72vh;overflow:auto}
    .tri-pcard{background:#fff;border:1px solid #dfe6ee;border-radius:12px;margin-bottom:9px;overflow:hidden}
    .tri-pcard-topo{display:grid;grid-template-columns:minmax(180px,.9fr) minmax(0,1fr) minmax(0,.9fr) minmax(0,1.5fr) 112px 140px auto;align-items:stretch}
    .tri-minutado{display:flex;align-items:center;gap:6px;border:1px solid #d6e0ea;border-radius:8px;padding:4px 7px;font-size:10.5px;font-weight:800;color:#6d7b8a;cursor:pointer;background:#fff;align-self:flex-start}
    .tri-minutado input{accent-color:#7a5ba6;margin:0}.tri-minutado.on{border-color:#cfc3ea;background:#f3effa;color:#5b4a8a}
    .tri-tarefa{display:flex;align-items:center;gap:6px;min-width:0}.tri-tarefa b{flex:1;min-width:0}
    .tri-pill{flex:0 0 auto;margin-left:auto;font-style:normal;font-size:9px;font-weight:850;color:#33506e;background:#e8eef5;border-radius:99px;padding:2px 8px;white-space:nowrap;cursor:help}
    .tri-pc-cel.larga i{white-space:normal;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;font-size:10.5px;color:#56636f}
    .tri-classe{display:flex;align-items:center;gap:5px;min-width:0;margin-top:2px}
    .tri-cls{flex:0 0 auto;font-style:normal;font-size:9px;font-weight:900;letter-spacing:.04em;border-radius:5px;padding:2px 5px;line-height:1.2}
    .tri-qualif{display:flex;flex-wrap:wrap;gap:3px;margin-top:3px}.tri-qualif span{font-size:8.5px;font-weight:850;letter-spacing:.03em;color:#8a5a00;background:#fdf2dc;border-radius:99px;padding:1px 6px}
    .tri-pc-cel b.dica{cursor:help;text-decoration:underline dotted #c3ccd6;text-underline-offset:3px}
    .tri-ind{display:flex;flex-direction:column;gap:6px;min-width:0;max-width:290px}
    .tri-cx-sel{display:flex;align-items:center;gap:7px;border:1px solid #d6e0ea;border-radius:9px;background:#fff;padding:3px 6px 3px 4px}
    .tri-cx-sel i{flex:0 0 auto;width:22px;height:22px;border-radius:50%;display:grid;place-items:center;color:#fff;font-style:normal;font-size:12px;font-weight:800;font-family:"Times New Roman",Georgia,serif}
    .tri-cx-sel select{flex:1;min-width:0;border:0;background:transparent;font:inherit;font-size:11.5px;font-weight:750;color:#14263c;outline:none;cursor:pointer}
    .tri-ind-chips{display:flex;flex-wrap:wrap;gap:4px}
    .tri-ind-chip{display:inline-flex;align-items:center;gap:3px;border-radius:99px;padding:3px 8px;font-size:9.5px;font-weight:850;background:#eef1f5;color:#6d7b8a;white-space:nowrap;cursor:help}
    .tri-ind-chip.on{background:#fbe9e3;color:#a64f35}.tri-ind-chip.meta{background:#fdf2dc;color:#8a5a00}.tri-ind-chip.off{background:#f4f6f9;color:#a4afba}.tri-ind-chip.tempo{background:#e8eef5;color:#33506e}
    .tri-info .tri-faixa-barra{background:#f4f6f9;color:#33506e}.tri-info .tri-faixa-barra .rot{color:#1f3d63}.tri-info .tri-faixa-barra:hover{background:#eceff3}
    .tri-pc-cel{display:flex;flex-direction:column;gap:2px;min-width:0;padding:9px 12px;border-left:1px solid #f0f2f5}
    .tri-pc-cel:first-child{border-left:0}
    .tri-pc-cel>span,.tri-pc-campo>span{font-size:8.5px;font-weight:850;letter-spacing:.06em;color:#98a4b0;text-transform:uppercase}
    .tri-pc-cel b{font-size:11.5px;font-weight:650;color:#3d4c5c;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .tri-pc-cel b.num{font:600 11.5px "IBM Plex Mono",ui-monospace,SFMono-Regular,Consolas,monospace;color:#14263c}
    .tri-pc-cel i{font-style:normal;font-size:10px;color:#7e8b99;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .tri-pc-cel em{font-style:normal;align-self:flex-start;max-width:100%;padding:3px 9px;border-radius:99px;font-size:9px;font-weight:850;letter-spacing:.03em;line-height:1.3}
    .tri-pc-acoes{display:flex;align-items:center;gap:4px;padding:0 10px;border-left:1px solid #f0f2f5;background:#f8fafb}
    .tri-pcard-campos{display:grid;grid-template-columns:repeat(auto-fill,minmax(175px,1fr));gap:1px;background:#eef1f4;border-top:1px solid #eef1f4}
    .tri-pc-campo{display:flex;flex-direction:column;gap:2px;min-width:0;background:#fbfcfd;padding:6px 10px}
    .tri-pc-campo b{font-size:11px;font-weight:600;color:#3d4c5c;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;word-break:break-word}
    .tri-faixa{border-top:1px solid #eef1f4;background:#fbfaf6}
    .tri-faixa-barra{width:100%;display:flex;align-items:center;gap:8px;border:0;background:#f6f2e7;padding:6px 12px;font:inherit;font-size:10.5px;color:#5d5137;cursor:pointer;text-align:left}
    .tri-faixa-barra:hover{background:#f1ead8}
    .tri-faixa-barra .rot{font-size:9px;font-weight:900;letter-spacing:.08em;color:#7a5512}
    .tri-faixa-barra .res{min-width:0;flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:#6d6046}
    .tri-cx-mini{flex:0 0 auto;width:18px;height:18px;border-radius:50%;display:grid;place-items:center;color:#fff;font-size:10.5px;font-weight:800;font-family:"Times New Roman",Georgia,serif}
    .tri-faixa-corpo{display:grid;gap:10px;padding:10px 12px 12px;border-top:1px solid #efe7d2}
    .tri-fx-l1{display:grid;grid-template-columns:minmax(230px,280px) repeat(4,minmax(0,1fr));gap:8px;align-items:start;background:#fff;border:1px solid #e3e7ec;border-radius:10px;padding:9px 10px}
    .tri-fx-l1 .tri-ind{max-width:none}
    .tri-ctl{display:flex;flex-direction:column;gap:5px;min-width:0;border-left:1px solid #eef1f4;padding-left:8px}
    .tri-ctl select,.tri-ctl input:not([type=checkbox]){width:100%;min-width:0;border:1px solid #d6e0ea;border-radius:8px;background:#fff;padding:5px 7px;font:inherit;font-size:11px;color:#14263c;outline:none}
    .tri-ctl select:disabled,.tri-ctl input:disabled{background:#f4f6f9;color:#98a4b0}
    .tri-ctl-checks{display:flex;gap:10px}.tri-ctl label{display:inline-flex;align-items:center;gap:4px;font-size:11px;font-weight:750;color:#3d4c5c;cursor:pointer}
    .tri-ctl input[type=checkbox]{accent-color:#1f3d63;margin:0}
    .tri-ctl-par{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.2fr);gap:4px}
    .tri-fx-l1b{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(0,1fr);gap:10px}
    .tri-fx-sint{display:flex;flex-direction:column;min-width:0}
    .tri-fx-l1b .tri-fx-sintese{min-height:70px}
    .tri-fx-l2{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,1fr) minmax(0,1fr) minmax(0,1.15fr);gap:10px}
    .tri-fx-rot{display:block;font-size:8.5px;font-weight:900;letter-spacing:.08em;color:#7e8b99;margin-bottom:5px}
    .tri-cx{display:grid;gap:4px}
    .tri-cx-op{display:flex;align-items:center;gap:8px;border:1px solid #e3e7ec;background:#fff;border-radius:8px;padding:4px 12px 4px 5px;font:inherit;font-size:11.5px;font-weight:650;color:#3d4c5c;cursor:pointer;text-align:left;min-width:150px}
    .tri-cx-op i{width:22px;height:22px;border-radius:50%;display:grid;place-items:center;color:#fff;font-style:normal;font-size:12.5px;font-weight:800;font-family:"Times New Roman",Georgia,serif;opacity:.45}
    .tri-cx-op:hover i,.tri-cx-op.on i{opacity:1}
    .tri-cx-op.on{border-color:#1f3d63;background:#eef3f8;color:#14263c;font-weight:800}
    .tri-fx-sintese{width:100%;height:100%;min-height:82px;border:1px solid #d6e0ea;border-radius:9px;background:#fff;color:#14263c;padding:8px 10px;font:inherit;font-size:12px;line-height:1.45;resize:vertical;outline:none}
    .tri-fx-sintese:focus{border-color:#1f3d63}
    .tri-fx-caixa{border:1px solid #e3e7ec;border-radius:10px;background:#fff;padding:8px 9px;min-width:0;display:flex;flex-direction:column}
    .tri-fx-caixa.alvo{border-color:#d9a441;background:#fffaf0;box-shadow:inset 0 0 0 1px #d9a441}
    .tri-fx-caixa.obs{border-top:3px solid #4a8f74}
    .tri-fx-obs{flex:1;min-height:96px;width:100%;resize:vertical;border:1px solid #e3e7ec;border-radius:8px;background:#fbfdfc;padding:7px 9px;font:inherit;font-size:11.5px;line-height:1.55;color:#14263c;outline:none;white-space:pre-wrap}
    .tri-fx-obs:focus{border-color:#4a8f74;background:#fff}
    .tri-chip button.o{color:#2f6b52}
    .tri-fx-caixa.tema{border-top:3px solid #2f6690}.tri-fx-caixa.esp{border-top:3px solid #7a5ba6}.tri-fx-caixa.etq{border-top:3px solid #d9a441}
    .tri-fx-chips{display:flex;flex-wrap:wrap;gap:5px;align-content:flex-start;min-height:30px;max-height:150px;overflow:auto;flex:1}
    .tri-fx-chips em{font-style:normal;font-size:10.5px;color:#98a4b0}
    .tri-chip{display:inline-flex;align-items:center;gap:3px;max-width:100%;border-radius:99px;padding:2px 3px 2px 9px;font-size:10.5px;font-weight:700;background:#f7e7c4;color:#6b4a0e;cursor:grab}
    .tri-chip>span{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0}
    .tri-chip button{flex:0 0 auto;border:0;width:18px;height:18px;border-radius:50%;font-size:9px;font-weight:900;cursor:pointer;background:rgba(255,255,255,.75);color:#1f3d63;padding:0}
    .tri-chip button.e{color:#5b4a8a}.tri-chip button:hover{background:#fff}
    .tri-chip.tema{background:#e3edf6;color:#1f4d73;cursor:default}.tri-chip.esp{background:#ece6f6;color:#4f3d7a;cursor:default}
    .tri-chip.tema button,.tri-chip.esp button{color:#a64f35}
    .tri-fx-add{display:flex;gap:4px;margin-top:7px}
    .tri-fx-add input{flex:1;min-width:0;border:1px solid #d6e0ea;border-radius:8px;padding:5px 8px;font:inherit;font-size:11px;outline:none;background:#fafbfc}
    .tri-fx-add input:focus{border-color:#1f3d63;background:#fff}
    .tri-fx-add button{border:0;border-radius:8px;background:#1f3d63;color:#fff;font-weight:900;padding:0 10px;cursor:pointer}
    .tri-fx-ctrl{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1px;background:#e7eaee;border:1px solid #e3e7ec;border-radius:10px;overflow:hidden}
    .tri-fx-ctrl>div{background:#fff;min-width:0}
    .tri-fx-ctrl .cab{color:#6d7b8a;font-size:9px;font-weight:800;letter-spacing:.04em;padding:5px 8px}
    @media(max-width:1100px){.tri-fx-l1{grid-template-columns:repeat(2,minmax(0,1fr))}.tri-fx-l1b,.tri-fx-l2{grid-template-columns:minmax(0,1fr)}}
    /* bandeja integrada ao móvel de escaninhos */
    .tri-int-corpo{display:grid;grid-template-columns:300px minmax(0,1fr);align-items:stretch;min-width:0}
    .tri-int .tri-bandeja{position:static;border:0;border-right:1px solid #e3e7ec;border-radius:0;box-shadow:none;display:flex;flex-direction:column;min-width:0;background:#fbfcfd}
    .tri-int .tri-band-topo{background:transparent}
    .tri-int .tri-band-lista{max-height:560px;min-height:260px;flex:1}
    .tri-int-nichos{min-width:0}
    .tri-band-vazia-rot{display:none}
    .tri-int-corpo.semband{grid-template-columns:40px minmax(0,1fr)}
    .tri-bandeja.semband{background:#f4f6f9;cursor:not-allowed;min-height:0;overflow:hidden}
    .tri-bandeja.semband>*:not(.tri-band-vazia-rot){display:none!important}
    .tri-bandeja.semband .tri-band-vazia-rot{display:flex;align-items:center;justify-content:center;height:auto;min-height:150px;flex:1;writing-mode:vertical-rl;transform:rotate(180deg);font-size:9.5px;font-weight:900;letter-spacing:.14em;color:#a4afba}
    .tri-topo-num{font-size:10.5px;color:#6d7b8a}.tri-topo-num b{color:#14263c}
    .tri-int .tri-aberto{margin:0 14px 14px}
    .tri-int .tri-aberto{border-top:1px solid #d6e0ea}
    /* cabeçalho do escaninho aberto */
    .tri-aberto-topo{border-top:4px solid #2f6690}
    .tri-ab-id{display:flex;align-items:center;gap:10px;min-width:0;flex:0 1 auto}
    .tri-ab-pasta{flex:0 0 auto;width:34px;height:34px;border-radius:9px;display:grid;place-items:center;font-size:17px}
    .tri-ab-t{font-size:15px;font-weight:850;color:#14263c;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:360px}
    .tri-ab-s{font-size:11px;font-weight:600;color:#6d7b8a;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:360px}
    .tri-ab-chip{flex:0 0 auto;font-size:10px;font-weight:850;color:#33506e;background:#fff;border:1px solid #d6e0ea;border-radius:99px;padding:3px 9px;white-space:nowrap}
    .tri-ab-ferr{display:flex;align-items:center;gap:6px;flex-wrap:wrap;flex:0 0 auto;margin-left:auto}
    .tri-seg{display:flex;gap:2px;background:#e3eaf2;border-radius:9px;padding:3px}
    .tri-seg button{border:0;background:transparent;border-radius:7px;padding:6px 11px;font-size:10.5px;font-weight:850;color:#5c6a78;cursor:pointer;white-space:nowrap}
    .tri-seg button.on{background:#fff;color:#1f3d63;box-shadow:0 1px 2px rgba(20,38,60,.14)}
    .tri-ab-btn{display:inline-flex;align-items:center;gap:5px;height:32px;border:1px solid #d6e0ea;border-radius:9px;background:#fff;color:#1f3d63;padding:0 11px;font-size:10.5px;font-weight:850;cursor:pointer;white-space:nowrap}
    .tri-ab-btn:hover{border-color:#9fb3c9}
    .tri-ab-btn.on{background:#1f3d63;border-color:#1f3d63;color:#fff}
    .tri-ab-btn.ouro{background:#d9a441;border-color:#d9a441;color:#33240a}
    .tri-ab-btn.perigo{color:#a64f35}.tri-ab-btn.perigo:hover{border-color:#e2b3a5;background:#fdf3f0}
    .tri-ab-btn.icone{width:32px;justify-content:center;padding:0;font-size:14px}
    .tri-exp{display:inline-flex;gap:0;border:1px solid #d6e0ea;border-radius:9px;overflow:hidden}
    .tri-exp .tri-ab-btn.icone{width:auto;border:0;border-radius:0;padding:0 9px;gap:3px;font-size:13px}.tri-exp .tri-ab-btn.icone+.tri-ab-btn{border-left:1px solid #e3e7ec}
    .tri-exp b{font-size:8.5px;font-weight:900;letter-spacing:.05em}
    .tri-aberto-topo .tri-config-resumo{flex:1 1 160px;min-width:0}
    /* modo planilha */
    .tri-plan-wrap{overflow:auto;max-height:72vh;border:1px solid #dfe6ee;border-radius:10px;background:#fff}
    .tri-plan{display:table;width:max-content;min-width:100%;border-collapse:collapse;font-size:11.5px}
    .tri-plan-tr{display:table-row}
    .tri-plan-tr>*{display:table-cell;padding:7px 8px;border-bottom:1px solid #eef1f4;vertical-align:top;color:#3d4c5c;max-width:220px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
    .tri-plan-tr.cab>span{position:sticky;top:0;z-index:1;background:#f4f6f9;color:#5c6a78;font-size:8.5px;font-weight:900;letter-spacing:.06em;text-transform:uppercase;padding:8px;border-bottom:1px solid #e3e7ec}
    .tri-plan-tr>.quebra{white-space:normal;min-width:160px;max-width:260px}
    .tri-plan-tr>.c:first-child,.tri-plan-tr.cab>span:first-child{position:sticky;left:0;z-index:2;background:#fff}.tri-plan-tr.cab>span:first-child{z-index:3;background:#f4f6f9}
    .tri-plan-tr>.obs{white-space:pre-line;font-size:11px}
    .tri-plan-tr:not(.cab):hover>*{background:#fafcfe}
    .tri-plan b.num{display:block;font:600 11.5px "IBM Plex Mono",ui-monospace,SFMono-Regular,Consolas,monospace;color:#14263c}
    .tri-plan .c>i{display:block;font-style:normal;font-size:10px;color:#7e8b99}
    .tri-plan em{font-style:normal;display:inline-block;padding:3px 8px;border-radius:99px;font-size:9px;font-weight:850}
    .tri-plan .acoes{white-space:nowrap;text-align:right}
    .tri-plan-cx{display:inline-flex;gap:3px}
    .tri-plan-cx button{width:22px;height:22px;border-radius:50%;border:1px solid #e3e7ec;background:#f4f6f9;color:#a4afba;font:800 11.5px "Times New Roman",Georgia,serif;cursor:pointer;padding:0}
    .tri-plan-cx button.on{background:var(--c);border-color:var(--c);color:#fff}
    .tri-plan-cx button:hover{border-color:var(--c);color:var(--c)}.tri-plan-cx button.on:hover{color:#fff}
    .tri-campo{display:grid;gap:4px;margin-bottom:9px}
    .tri-campo label{font-size:9px;font-weight:900;letter-spacing:.08em;color:#6d7b8a}
    .tri-campo input,.tri-campo textarea{width:100%;border:1px solid #d6e0ea;border-radius:9px;background:#fff;color:#14263c;padding:8px 10px;font:inherit;font-size:12.5px;outline:none}
    .tri-campo textarea{min-height:78px;resize:vertical;background:#fff4c2;border-color:#e8d78a;color:#4a3d0f}
    .tri-cor{width:22px;height:22px;border-radius:50%;border:2px solid #fff;outline:1px solid #d6e0ea;cursor:pointer;padding:0}
    .tri-cor.on{outline:2px solid #14263c}
    .tri-guardados{display:grid;gap:6px;max-height:360px;overflow:auto;align-content:start}
    .tri-guardado{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px;align-items:center;background:#fff;border:1px solid #dfe6ee;border-radius:9px;padding:8px 10px}
    .tri-guardado .num{font:600 12px "IBM Plex Mono",ui-monospace,SFMono-Regular,Consolas,monospace}
    .tri-guardado .meta{font-size:10.5px;color:#6d7b8a}
    .tri-icone{border:1px solid #dfe6ee;background:#fff;border-radius:7px;padding:3px 8px;font-size:12px;font-weight:900;cursor:pointer;color:#1f3d63}
    @media(max-width:1100px){.tri-aberto-topo{flex-wrap:wrap}.tri-config{grid-template-columns:repeat(2,minmax(0,1fr))}.tri-pcard-topo{grid-template-columns:repeat(2,minmax(0,1fr))}.tri-pc-acoes{padding:8px 12px}.tri-grid{grid-template-columns:minmax(0,1fr)}.tri-bandeja{position:static}.tri-int-corpo{grid-template-columns:minmax(0,1fr)}.tri-int .tri-bandeja{border-right:0;border-bottom:1px solid #e3e7ec}.tri-fx-l2{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}.tri-band-lista{max-height:340px}.tri-kpis{grid-template-columns:repeat(2,minmax(0,1fr))}.tri-aberto-corpo{grid-template-columns:minmax(0,1fr)}}
"""

BTN = "border:1px solid #d8dee5;border-radius:8px;background:#fff;color:#1f3d63;padding:6px 10px;font-size:10px;font-weight:850;cursor:pointer;white-space:nowrap"
BTN_OURO = "border:0;border-radius:8px;background:#d9a441;color:#33240a;padding:7px 12px;font-size:10px;font-weight:900;cursor:pointer;white-space:nowrap"
KPI_B = "display:block;font-size:22px;font-weight:850;color:#14263c;margin-top:2px;line-height:1.2"

MARKUP = """
    <sc-if value="{{ isTriagem }}" hint-placeholder-val="{{ false }}">
      <div class="tri-page">
        <div class="tri-kpis">
          <div class="tri-kpi"><span>EM TRIAGEM</span><b style="KPI_B">{{ triTotal }}</b></div>
          <div class="tri-kpi"><span>EM ESCANINHOS</span><b style="KPI_B">{{ triInEsc }}</b></div>
          <div class="tri-kpi"><span>NA BANDEJA</span><b style="KPI_B">{{ triSemEsc }}</b></div>
          <div class="tri-kpi"><span>ESCANINHOS</span><b style="KPI_B">{{ triEscCount }}</b></div>
        </div>
          <section class="tri-movel tri-int" aria-label="Gabinete A · Escaninhos">
            <div class="tri-movel-topo">
              <span class="tri-placa-mestra">GABINETE A · ESCANINHOS</span>
              <span class="tri-topo-num"><b>{{ triBandejaCount }}</b> na bandeja · <b>{{ triInEsc }}</b> em {{ triEscCount }} escaninho(s)</span>
              <span style="display:flex;gap:6px;flex-wrap:wrap;margin-left:auto"><sc-for list="{{ triFiltros }}" as="f"><button class="tri-filtro {{ f.cls }}" sc-camel-on-click="{{ f.pick }}">{{ f.label }}</button></sc-for></span>
            </div>
            <div class="tri-int-corpo {{ triCorpoCls }}">
            <aside class="tri-bandeja {{ triCorpoCls }}" aria-label="Bandeja da triagem" aria-disabled="{{ triBandejaOff }}"><div class="tri-band-vazia-rot" title="Bandeja vazia: encaminhe processos do Acervo Central (seletor de sessão → Triagem Processual)">BANDEJA VAZIA</div>
              <div class="tri-band-topo">
                <div style="display:flex;justify-content:space-between;align-items:center;gap:8px"><span style="font-size:12.5px;font-weight:900;letter-spacing:.06em;color:#14263c">BANDEJA DA TRIAGEM</span><span style="font-size:10px;font-weight:800;color:#6d7b8a">{{ triBandejaCount }} na bandeja</span></div>
                <input value="{{ triSearch }}" sc-camel-on-input="{{ onTriSearch }}" placeholder="Buscar processo, classe, assunto, tarefa…" aria-label="Buscar na bandeja">
                <div class="tri-mover">
                <sc-raw-select value="{{ triTarget }}" sc-camel-on-change="{{ onTriTarget }}" aria-label="Escaninho de destino" title="Escaninho de destino">
                  <option value="">Escaninho de destino…</option>
                  <sc-for list="{{ triTargetOptions }}" as="o"><option value="{{ o.value }}">{{ o.label }}</option></sc-for>
                </sc-raw-select>
                <button class="tri-mover-btn" sc-camel-on-click="{{ triMoverMarcados }}" disabled="{{ triMoverOff }}" title="Mover os processos marcados para o escaninho escolhido" aria-label="Mover os processos marcados para o escaninho escolhido"><span aria-hidden="true">🗂</span><span aria-hidden="true" style="font-size:13px">➜</span><b>{{ triSelCount }}</b></button>
              </div>
                <div class="tri-mover tri-sp-envio">
                <sc-raw-select value="{{ triSessao }}" sc-camel-on-change="{{ onTriSessao }}" aria-label="Sessão da Seleção Prévia" title="Sessão de destino na Seleção Prévia">
                  <option value="">Sessão da Seleção Prévia…</option>
                  <sc-for list="{{ triSessaoOpts }}" as="o"><option value="{{ o.value }}">{{ o.label }}</option></sc-for>
                </sc-raw-select>
                <button class="tri-mover-btn sp" sc-camel-on-click="{{ triBandSP }}" disabled="{{ triBandSPOff }}" title="Lançar os processos marcados na Seleção Prévia da sessão escolhida" aria-label="Lançar os marcados na Seleção Prévia"><span aria-hidden="true">✓</span><span aria-hidden="true" style="font-size:13px">➜</span><b>{{ triSelCount }}</b></button>
              </div>
              </div>
              <div class="tri-band-lista">
                <sc-for list="{{ triFichas }}" as="p" hint-placeholder-count="4">
                  <div class="tri-ficha {{ p.cls }}" draggable="true" data-tri-ficha="{{ p.id }}" title="Arraste para um escaninho, ou marque e clique no escaninho">
                    <input type="checkbox" checked="{{ p.sel }}" sc-camel-on-change="{{ p.toggle }}" aria-label="Marcar processo" style="margin:2px 0 0;width:15px;height:15px;accent-color:#1f3d63;cursor:pointer">
                    <div style="min-width:0"><div class="num">{{ p.proc }}</div><div class="meta">{{ p.classe }} · {{ p.assunto }}</div><div><span class="tri-tag">{{ p.tarefa }}</span><sc-for list="{{ p.tags }}" as="t"><span class="tri-tag ouro">{{ t.label }}</span></sc-for></div></div>
                  </div>
                </sc-for>
                <sc-if value="{{ triBandejaVazia }}"><div style="padding:26px 10px;text-align:center;color:#7e8b99;font-size:12px;line-height:1.5">{{ triBandejaMsg }}</div></sc-if>
                <sc-if value="{{ triTruncated }}"><div style="font-size:10.5px;color:#7e8b99;text-align:center">{{ triTruncMsg }}</div></sc-if>
              </div>
              <div class="tri-band-pe">
                <span style="font-weight:800;color:{{ triClearFg }}">{{ triSelCount }} marcado(s)</span>
                <span style="display:flex;gap:5px;flex-wrap:wrap"><button sc-camel-on-click="{{ triSelectAll }}" style="BTN">Marcar todos</button><button sc-camel-on-click="{{ triClearSel }}" style="BTN">Limpar</button><button sc-camel-on-click="{{ removeFromTriagem }}" title="Devolver os marcados ao acervo (saem da triagem)" style="BTN;color:#a64f35">Remover da triagem</button></span>
              </div>
            </aside>
              <div class="tri-int-nichos">
                <div class="tri-dica">{{ triDica }}</div>
                <div class="tri-grade">
                  <sc-for list="{{ triEscaninhos }}" as="e" hint-placeholder-count="3">
                    <button class="tri-nicho {{ e.cls }}" data-tri-esc="{{ e.key }}" sc-camel-on-click="{{ e.click }}" aria-label="{{ e.aria }}" title="{{ e.title }}">
                      <sc-if value="{{ e.hasObs }}"><span class="tri-bilhete">{{ e.obs }}</span></sc-if>
                      <span class="tri-contador">{{ e.count }}</span>
                      <span class="tri-pilha"><sc-for list="{{ e.layers }}" as="l"><span class="tri-folha" style="bottom:{{ l.b }}px"></span></sc-for><sc-if value="{{ e.hasCapa }}"><span class="tri-capa" style="background:{{ e.cor }};bottom:{{ e.capaB }}px"></span></sc-if></span>
                      <sc-if value="{{ e.vazio }}"><span class="tri-vazio-nicho">vazio · solte autos aqui</span></sc-if>
                      <span class="tri-placa" style="border-left-color:{{ e.cor }}"><span class="t">{{ e.titulo }}</span><sc-if value="{{ e.hasSub }}"><span class="s">{{ e.subLabel }}</span></sc-if></span>
                    </button>
                  </sc-for>
                  <button class="tri-nicho novo" sc-camel-on-click="{{ newEscaninho }}"><span><span style="display:block;font-size:24px;line-height:1">+</span><span style="font-size:10px;font-weight:850;letter-spacing:.08em">NOVO ESCANINHO</span></span></button>
                </div>

              </div>
            </div>

            <sc-if value="{{ triHasOpen }}" hint-placeholder-val="{{ false }}">
              <div class="tri-aberto" aria-label="Escaninho aberto">
                <div class="tri-aberto-topo" style="border-top-color:{{ triOpenCor }}">
                  <div class="tri-ab-id">
                    <span class="tri-ab-pasta" style="background:{{ triOpenCor }}" aria-hidden="true">🗂</span>
                    <div style="min-width:0"><div class="tri-ab-t">{{ triOpenTitulo }}</div><sc-if value="{{ triOpenHasSub }}"><div class="tri-ab-s">{{ triOpenSub }}</div></sc-if></div>
                    <span class="tri-ab-chip">{{ triOpenCount }} processo(s)</span>
                  </div>
                  <span class="tri-config-resumo" title="Bilhete do escaninho">{{ triConfigResumo }}</span>
                  <div class="tri-ab-ferr">
                    <div class="tri-seg" role="group" aria-label="Modo de exibição"><button class="{{ triVistaCardsCls }}" sc-camel-on-click="{{ triVerCards }}" aria-pressed="{{ triVistaCards }}" title="Cards completos, com a faixa de triagem">▦ Cards</button><button class="{{ triVistaPlanCls }}" sc-camel-on-click="{{ triVerPlanilha }}" aria-pressed="{{ triVistaPlanilha }}" title="Lista em planilha, uma linha por processo">☰ Planilha</button></div>
                    <span class="tri-exp" role="group" aria-label="Exportar a relação"><button class="tri-ab-btn icone" sc-camel-on-click="{{ triExpCompleta }}" title="Exportar a relação em Excel completo — todos os campos do cartão" aria-label="Exportar Excel completo">⇩<b>XLSX</b></button><button class="tri-ab-btn icone" sc-camel-on-click="{{ triExpSimples }}" title="Excel simplificado — item, processo, indicadores (ED · AgInt · AI · META), assunto, tema e observações; ordenado pelo item" aria-label="Exportar relação simplificada">⇩<b>ITEM</b></button><button class="tri-ab-btn icone" sc-camel-on-click="{{ triImprimir }}" title="Versão para impressão — A4 retrato, sem margens, no máximo 2 páginas; ordenada pelo item" aria-label="Imprimir relação simplificada">⎙<b>A4</b></button></span>
                    <button class="tri-ab-btn {{ triConfigCls }}" sc-camel-on-click="{{ triToggleConfig }}" aria-expanded="{{ triConfigAberta }}" title="Placa, subtítulo, bilhete e cor da pasta"><span aria-hidden="true">⚙</span> Configurar <span aria-hidden="true">{{ triConfigSeta }}</span></button>
                    <button class="tri-ab-btn ouro" sc-camel-on-click="{{ triDevolverTodos }}" title="Devolver todos os processos deste escaninho à bandeja"><span aria-hidden="true">↩</span> Devolver todos</button>
                    <button class="tri-ab-btn perigo" sc-camel-on-click="{{ triExcluir }}" title="Excluir o escaninho (os processos voltam à bandeja)"><span aria-hidden="true">🗑</span> Excluir</button>
                    <button class="tri-ab-btn icone" sc-camel-on-click="{{ triRecolher }}" title="Recolher o escaninho" aria-label="Recolher o escaninho">⌃</button>
                  </div>
                </div>
                <sc-if value="{{ triConfigAberta }}" hint-placeholder-val="{{ false }}">
                  <div class="tri-config">
                    <div class="tri-campo"><label>TÍTULO DA PLACA</label><input value="{{ triOpenTitulo }}" sc-camel-on-input="{{ onTriTitulo }}" maxlength="70" aria-label="Título do escaninho"></div>
                    <div class="tri-campo"><label>SUBTÍTULO (OPCIONAL)</label><input value="{{ triOpenSubRaw }}" sc-camel-on-input="{{ onTriSub }}" maxlength="90" aria-label="Subtítulo do escaninho"></div>
                    <div class="tri-campo tri-l2"><label>BILHETE · OBSERVAÇÃO</label><textarea value="{{ triOpenObs }}" sc-camel-on-input="{{ onTriObs }}" aria-label="Observação do escaninho"></textarea></div>
                    <div class="tri-campo"><label>COR DA PASTA</label><span style="display:flex;gap:7px;flex-wrap:wrap"><sc-for list="{{ triCores }}" as="c"><button class="tri-cor {{ c.cls }}" style="background:{{ c.cor }}" sc-camel-on-click="{{ c.pick }}" aria-label="Cor da pasta"></button></sc-for></span><span style="font-size:9.5px;color:#7e8b99;margin-top:6px">Criado em {{ triOpenCriado }} · salvo automaticamente</span></div>
                  </div>
                </sc-if>
                <div class="tri-procs">
                  <div class="tri-selbar {{ triEscSelCls }}" role="group" aria-label="Marcação dos processos do escaninho">
                    <label class="tri-sel-todos"><input type="checkbox" checked="{{ triEscTodos }}" sc-camel-on-change="{{ triEscToggleTodos }}" aria-label="Marcar todos os processos do escaninho"><span>Marcar todos</span></label>
                    <span class="tri-sel-msg">{{ triEscSelMsg }}</span>
                    <button class="tri-ab-btn" sc-camel-on-click="{{ triEscLimpar }}" disabled="{{ triEscLimparOff }}" title="Desmarcar todos">Limpar</button>
                    <span class="tri-sel-sp"><sc-raw-select value="{{ triSessao }}" sc-camel-on-change="{{ onTriSessao }}" aria-label="Sessão da Seleção Prévia" title="Sessão de destino na Seleção Prévia"><option value="">Sessão…</option><sc-for list="{{ triSessaoOpts }}" as="o"><option value="{{ o.value }}">{{ o.label }}</option></sc-for></sc-raw-select><button class="tri-mover-btn sp" sc-camel-on-click="{{ triEscSP }}" disabled="{{ triEscSPOff }}" title="Lançar os processos marcados na Seleção Prévia da sessão escolhida" aria-label="Lançar os marcados na Seleção Prévia"><span aria-hidden="true">✓</span><span aria-hidden="true" style="font-size:13px">➜</span><b>{{ triEscSelCount }}</b></button></span>
                  </div>
                  <sc-if value="{{ triVistaPlanilha }}" hint-placeholder-val="{{ false }}">
                    <div class="tri-plan-wrap"><div class="tri-plan" role="table" aria-label="Processos do escaninho">
                      <div class="tri-plan-tr cab" role="row"><span></span><sc-for list="{{ triPlanCols }}" as="c"><span class="{{ c.cls }}">{{ c.label }}</span></sc-for></div>
                      <sc-for list="{{ triPlanLinhas }}" as="g" hint-placeholder-count="3"><div class="tri-plan-tr {{ g.selCls }}" role="row">
                        <div class="c acoes"><input class="tri-chk" type="checkbox" checked="{{ g.sel }}" sc-camel-on-change="{{ g.toggleSel }}" aria-label="Marcar processo"><button class="tri-icone" sc-camel-on-click="{{ g.abrirCard }}" title="Abrir no modo cards">▸</button><button class="tri-icone" sc-camel-on-click="{{ g.devolver }}" title="Devolver à bandeja">↩</button><button class="tri-icone" sc-camel-on-click="{{ g.remover }}" title="Remover da triagem (volta só ao acervo)" style="color:#a64f35">✕</button></div>
                        <sc-for list="{{ g.vals }}" as="v"><div class="c {{ v.cls }}" title="{{ v.v }}">{{ v.v }}</div></sc-for>
                      </div></sc-for>
                    </div></div>
                  </sc-if>
                  <sc-if value="{{ triVistaCards }}" hint-placeholder-val="{{ true }}">
                  <sc-for list="{{ triOpenRows }}" as="g" hint-placeholder-count="2">
                    <div class="tri-pcard {{ g.selCls }}" data-tri-card="{{ g.pid }}" style="border-left:4px solid {{ g.clsCor }}">
                      <div class="tri-pcard-topo">
                        <div class="tri-pc-cel"><span class="tri-pc-marca"><input class="tri-chk" type="checkbox" checked="{{ g.sel }}" sc-camel-on-change="{{ g.toggleSel }}" aria-label="Marcar processo">PROCESSO</span><b class="num">{{ g.proc }}</b><div class="tri-classe" title="{{ g.clsTitulo }}"><em class="tri-cls" style="background:{{ g.clsFundo }};color:{{ g.clsCor }}">{{ g.clsSigla }}</em><i>{{ g.classe }}</i></div><sc-if value="{{ g.temQualif }}"><div class="tri-qualif"><sc-for list="{{ g.qualifs }}" as="q"><span>▸ {{ q.label }}</span></sc-for></div></sc-if></div>
                        <div class="tri-pc-cel"><span>ASSUNTO</span><b title="{{ g.assuntoTitulo }}" class="dica">{{ g.assunto }}</b></div>
                        <div class="tri-pc-cel"><span>ETIQUETAS ATUAIS</span><b title="{{ g.etiquetas }}">{{ g.etiquetas }}</b></div>
                        <div class="tri-pc-cel larga"><span>TAREFA ATUAL · ÚLTIMO MOVIMENTO</span><div class="tri-tarefa"><b title="{{ g.tarefa }}">{{ g.tarefa }}</b><sc-if value="{{ g.temEntrada }}"><em class="tri-pill" title="{{ g.entradaTitulo }}">desde {{ g.entrada }}</em></sc-if></div><i title="{{ g.movimentoTitulo }}">{{ g.movimento }}</i></div>
                        <div class="tri-pc-cel"><span>MINUTADO</span><label class="tri-minutado {{ g.minutCls }}" title="{{ g.minutTitulo }}"><input type="checkbox" checked="{{ g.minutado }}" sc-camel-on-change="{{ g.onMinut }}"><span>{{ g.minutTxt }}</span></label></div>
                        <div class="tri-pc-cel"><span>SITUAÇÃO ATUAL</span><em style="background:{{ g.sitBg }};color:{{ g.sitFg }}">{{ g.situacao }}</em></div>
                        <div class="tri-pc-acoes"><button class="tri-icone" sc-camel-on-click="{{ g.devolver }}" title="Devolver à bandeja">↩</button><button class="tri-icone" sc-camel-on-click="{{ g.remover }}" title="Remover da triagem (volta só ao acervo)" style="color:#a64f35">✕</button></div>
                      </div>
                      <div class="tri-pcard-campos">
                        <sc-for list="{{ g.camposA }}" as="f"><div class="tri-pc-campo"><span>{{ f.col }}</span><b title="{{ f.val }}">{{ f.val }}</b></div></sc-for>
                      </div>
                      <div class="tri-faixa">
                        <button class="tri-faixa-barra" sc-camel-on-click="{{ g.toggleFaixa }}" aria-expanded="{{ g.faixaAberta }}"><span aria-hidden="true">{{ g.faixaSeta }}</span><span class="rot">TRIAGEM DO PROCESSO</span><span class="tri-cx-mini" style="background:{{ g.cxCor }}">{{ g.cxSimb }}</span><span class="res">{{ g.faixaResumo }}</span></button>
                        <sc-if value="{{ g.faixaAberta }}" hint-placeholder-val="{{ false }}">
                          <div class="tri-faixa-corpo">
                            <div class="tri-fx-l1">
                              <div class="tri-ind"><span class="tri-fx-rot">COMPLEXIDADE · INDICADORES</span>
                                <label class="tri-cx-sel"><i style="background:{{ g.cxCor }}">{{ g.cxSimb }}</i><sc-raw-select value="{{ g.cxValor }}" sc-camel-on-change="{{ g.onCx }}" aria-label="Complexidade"><option value="">Complexidade…</option><option value="1">Ω · Padrão</option><option value="2">A · Intermediário</option><option value="3">Σ · Complexo</option></sc-raw-select></label>
                                <div class="tri-ind-chips">
                                  <sc-for list="{{ g.metas }}" as="m"><span class="tri-ind-chip meta" title="Meta: {{ m.label }}">🎯 {{ m.label }}</span></sc-for><sc-if value="{{ g.semMeta }}"><span class="tri-ind-chip off" title="Sem meta registrada">sem meta</span></sc-if>
                                  <span class="tri-ind-chip {{ g.prioCls }}" title="{{ g.prioTitulo }}">⚑ prioridade</span>
                                  <span class="tri-ind-chip {{ g.pendCls }}" title="{{ g.pendTitulo }}">1º julg. {{ g.pendTxt }}</span>
                                  <span class="tri-ind-chip tempo" title="{{ g.tempoTitulo }}">⏱ {{ g.tempo }}</span>
                                </div>
                              </div>
                              <div class="tri-ctl"><span class="tri-fx-rot">TEMPESTIVIDADE</span><sc-raw-select value="{{ g.tempVal }}" sc-camel-on-change="{{ g.onTemp }}" aria-label="Tempestividade"><sc-for list="{{ g.tempOpts }}" as="o"><option value="{{ o.v }}">{{ o.l }}</option></sc-for></sc-raw-select></div>
                              <div class="tri-ctl"><span class="tri-fx-rot">PREPARO</span><sc-raw-select value="{{ g.prepVal }}" sc-camel-on-change="{{ g.onPrep }}" disabled="{{ g.dpu }}" aria-label="Preparo"><sc-for list="{{ g.prepOpts }}" as="o"><option value="{{ o.v }}">{{ o.l }}</option></sc-for></sc-raw-select><span class="tri-ctl-checks"><label><input type="checkbox" checked="{{ g.dpu }}" sc-camel-on-change="{{ g.onDpu }}"> DPU</label><label><input type="checkbox" checked="{{ g.ajg }}" disabled="{{ g.dpu }}" sc-camel-on-change="{{ g.onAjg }}"> AJG</label></span></div>
                              <div class="tri-ctl"><span class="tri-fx-rot">IMPEDIMENTO / SUSPEIÇÃO</span><label class="tri-ctl-check1"><input type="checkbox" checked="{{ g.restr }}" sc-camel-on-change="{{ g.onRestr }}"> {{ g.restrRot }}</label><sc-if value="{{ g.restr }}"><span class="tri-ctl-par"><sc-raw-select value="{{ g.restrTipo }}" sc-camel-on-change="{{ g.onRestrTipo }}" aria-label="Tipo"><option value="Impedimento">Impedimento</option><option value="Suspeição">Suspeição</option></sc-raw-select><input value="{{ g.restrNome }}" sc-camel-on-change="{{ g.onRestrNome }}" placeholder="Magistrado" aria-label="Magistrado"></span></sc-if></div>
                              <div class="tri-ctl"><span class="tri-fx-rot">REPRESENTAÇÃO · ID</span><sc-raw-select value="{{ g.repVal }}" sc-camel-on-change="{{ g.onRep }}" aria-label="Representação"><sc-for list="{{ g.repOpts }}" as="o"><option value="{{ o.v }}">{{ o.l }}</option></sc-for></sc-raw-select><input value="{{ g.repId }}" sc-camel-on-change="{{ g.onRepId }}" disabled="{{ g.repSemId }}" placeholder="{{ g.repIdPh }}" aria-label="ID da procuração"></div>
                            </div>
                            <div class="tri-fx-l1b">
                              <div class="tri-fx-sint"><span class="tri-fx-rot">SÍNTESE PROCESSUAL</span><textarea class="tri-fx-sintese" value="{{ g.sintese }}" sc-camel-on-input="{{ g.onSintese }}" placeholder="Resumo do caso: pedido, sentença, recurso e o ponto controvertido…" aria-label="Síntese processual"></textarea></div>
                              <div class="tri-fx-sint"><span class="tri-fx-rot">INTERCORRÊNCIAS · UMA POR LINHA</span><textarea class="tri-fx-sintese" value="{{ g.interc }}" sc-camel-on-change="{{ g.onInterc }}" placeholder="Ex.: falta procuração; mídia ilegível…" aria-label="Intercorrências"></textarea></div>
                            </div>
                            <div class="tri-fx-l2">
                              <div class="tri-fx-caixa etq">
                                <span class="tri-fx-rot">TODAS AS ETIQUETAS · {{ g.etqCount }} · arraste ou use T / E / O</span>
                                <div class="tri-fx-chips"><sc-for list="{{ g.etqs }}" as="t"><span class="tri-chip" draggable="true" data-tri-tag="{{ t.drag }}" title="{{ t.label }}"><span>{{ t.label }}</span><button sc-camel-on-click="{{ t.toTema }}" title="Encaminhar para TEMAS" aria-label="Encaminhar para temas">T</button><button class="e" sc-camel-on-click="{{ t.toEsp }}" title="Encaminhar para ESPECIFICIDADES" aria-label="Encaminhar para especificidades">E</button><button class="o" sc-camel-on-click="{{ t.toObs }}" title="Encaminhar para OBSERVAÇÕES" aria-label="Encaminhar para observações">O</button></span></sc-for><sc-if value="{{ g.etqVazio }}"><em>Sem etiquetas atuais.</em></sc-if></div>
                              </div>
                            <div class="tri-fx-caixa tema" data-tri-dest="{{ g.destTema }}">
                              <span class="tri-fx-rot">TEMAS · {{ g.temasCount }}</span>
                              <div class="tri-fx-chips"><sc-for list="{{ g.temas }}" as="t"><span class="tri-chip tema" title="{{ t.label }}"><span>{{ t.label }}</span><button sc-camel-on-click="{{ t.remover }}" title="Remover (se veio de etiqueta, volta às etiquetas)" aria-label="Remover">✕</button></span></sc-for><sc-if value="{{ g.temasVazio }}"><em>Arraste etiquetas para cá ou crie abaixo.</em></sc-if></div>
                              <div class="tri-fx-add"><input placeholder="+ novo tema" sc-camel-on-key-down="{{ g.addTemaKey }}" aria-label="+ novo tema"><button sc-camel-on-click="{{ g.addTemaBtn }}" title="Incluir" aria-label="Incluir">+</button></div>
                            </div>
                            <div class="tri-fx-caixa esp" data-tri-dest="{{ g.destEsp }}">
                              <span class="tri-fx-rot">ESPECIFICIDADES · {{ g.espsCount }}</span>
                              <div class="tri-fx-chips"><sc-for list="{{ g.esps }}" as="t"><span class="tri-chip esp" title="{{ t.label }}"><span>{{ t.label }}</span><button sc-camel-on-click="{{ t.remover }}" title="Remover (se veio de etiqueta, volta às etiquetas)" aria-label="Remover">✕</button></span></sc-for><sc-if value="{{ g.espsVazio }}"><em>Arraste etiquetas para cá ou crie abaixo.</em></sc-if></div>
                              <div class="tri-fx-add"><input placeholder="+ nova especificidade" sc-camel-on-key-down="{{ g.addEspKey }}" aria-label="+ nova especificidade"><button sc-camel-on-click="{{ g.addEspBtn }}" title="Incluir" aria-label="Incluir">+</button></div>
                            </div>
                            <div class="tri-fx-caixa obs" data-tri-dest="{{ g.destObs }}">
                              <span class="tri-fx-rot">OBSERVAÇÕES · {{ g.obsCount }}</span>
                              <textarea class="tri-fx-obs" value="{{ g.obsTxt }}" sc-camel-on-input="{{ g.onObs }}" placeholder="Arraste etiquetas para cá (entram como tópicos “• …”) ou escreva livremente." aria-label="Observações do processo"></textarea>
                            </div>
                            </div>
                          </div>
                        </sc-if>
                      </div>
                      <div class="tri-faixa tri-info">
                        <button class="tri-faixa-barra" sc-camel-on-click="{{ g.toggleInfo }}" aria-expanded="{{ g.infoAberta }}"><span aria-hidden="true">{{ g.infoSeta }}</span><span class="rot">+ INFORMAÇÕES</span><span class="res">{{ g.infoResumo }}</span></button>
                        <sc-if value="{{ g.infoAberta }}" hint-placeholder-val="{{ false }}">
                      <div class="tri-pcard-campos">
                        <sc-for list="{{ g.camposB }}" as="f"><div class="tri-pc-campo"><span>{{ f.col }}</span><b title="{{ f.val }}">{{ f.val }}</b></div></sc-for>
                      </div>
                      </sc-if>
                      </div>
                    </div>
                  </sc-for>
                  </sc-if>
                  <sc-if value="{{ triOpenVazio }}"><div style="padding:18px;text-align:center;color:#7e8b99;font-size:11.5px;border:1px dashed #c9d5e2;border-radius:9px">Escaninho vazio. Marque fichas na bandeja e clique neste escaninho — ou arraste-as até ele.</div></sc-if>
                </div>
              </div>
            </sc-if>
          </section>
      </div>
    </sc-if>
""".replace('style="KPI_B"', 'style="' + KPI_B + '"').replace('style="BTN_OURO"', 'style="' + BTN_OURO + '"').replace('style="BTN;', 'style="' + BTN + ';').replace('style="BTN"', 'style="' + BTN + '"')

METODOS = r'''  triagemRows() { return this.rows.map((r,i)=>({r,i})).filter(({r})=>!!txt(r._triagem)); }
  sendToTriagem() {
    if (!this.selected.size) return this.notify("Selecione pelo menos um processo.", "warn");
    const hoje = new Date().toISOString().slice(0,10); let n = 0, ja = 0;
    this.rows.forEach(r => { if (this.selected.has(procId(r.Processo))) { if (txt(r._triagem)) ja++; else { r._triagem = hoje; n++; } } });
    this.selected.clear(); this.saveDB(); this.refresh();
    this.notify(`${n} processo(s) encaminhados à Triagem Processual` + (ja ? ` · ${ja} já estavam na triagem` : "") + ".");
  }
  triGuardar(ids, escId) {
    const e = (this.escaninhos || []).find(x => x.id === escId); if (!e) return;
    const set = new Set(ids.map(String)); let n = 0;
    this.rows.forEach(r => { const id = procId(r.Processo); if (set.has(id) && txt(r._triagem)) { r._escaninho = escId; n++; } this.triSel && this.triSel.delete(id); });
    this.saveDB(); this.refresh();
    if (n) this.notify(`${n} processo(s) guardado(s) no escaninho "${e.titulo}".`);
  }
  /* ---------- cartão de processo (Triagem Processual e Seleção Prévia): regras comuns ---------- */
  cardAssunto(v) {
    const M = window.__ASSUNTOS_CNJ || {};
    return txt(v).replace(/\b\d{3,6}\b/g, n => M[n] ? M[n][0] : n);
  }
  cardCaminhoAssunto(cod) {
    const M = window.__ASSUNTOS_CNJ || {}, out = []; let c = txt(cod), k = 0;
    while (c && M[c] && k++ < 12) { out.unshift(M[c][0]); c = M[c][1]; }
    return out.join(" › ");
  }
  cardClasse(r) {
    const nome = txt(r.classe_judicial || r.Classe), t = canon(nome);
    const tipos = [[/apela/, "AP", "Apelação", "#2f6690", "#e3edf6"], [/agravo de instrumento/, "AI", "Agravo de Instrumento", "#b4691f", "#fbecd9"], [/agravo interno/, "AgI", "Agravo Interno", "#7a5ba6", "#efe9f7"],
      [/embargos de declara/, "ED", "Embargos de Declaração", "#3d8b9c", "#e3f2f4"], [/remessa/, "RN", "Remessa Necessária", "#4a8f74", "#e6f2ea"], [/mandado de seg/, "MS", "Mandado de Segurança", "#a6545e", "#f7e6e8"]];
    const hit = tipos.find(([re]) => re.test(t));
    return hit ? { nome: nome || hit[2], sigla: hit[1], rotulo: hit[2], cor: hit[3], fundo: hit[4] } : { nome: nome || "—", sigla: "•", rotulo: nome || "Classe não informada", cor: "#7e8b99", fundo: "#eef1f5" };
  }
  cardQualifica(label) {
    const t = canon(label);
    if (/^(?:ai|agravo de instrumento)(?:$|\s*[-:(])/.test(t)) return "AGRAVO DE INSTRUMENTO";
    if (/^(?:ed|embargos? de declaracao)(?:$|\s*[-:(])/.test(t)) return "EMBARGOS DE DECLARAÇÃO";
    if (/^(?:ms|mandado de seguranca)(?:$|\s*[-:(])/.test(t)) return "MANDADO DE SEGURANÇA";
    return "";
  }
  /* etiquetas que não aparecem no cartão: seção (vira Seção Competente), DPU e AJG (viram campos), qualificações da classe */
  cardEtiquetaOculta(label) {
    const t = canon(label), papel = this.tagRole(label);
    return papel === "section" || /\bsecao\b/.test(t) || papel === "dpu" || papel === "ajg" || !!this.cardQualifica(label);
  }
  /* DPU e AJG: se o cadastro ainda não registra, registra a partir da etiqueta (fica como preenchimento do processo) */
  cardRegras(r) {
    let mudou = false; const tags = this.sourceTags(r);
    if (tags.some(x => this.tagRole(x) === "dpu") && !truthy(r["DPU (controle)"])) { r._dpuManual = true; r["DPU (controle)"] = "Sim"; r.AJG = "Sim"; mudou = true; }
    if (tags.some(x => this.tagRole(x) === "ajg") && !truthy(r.AJG)) { r._ajgManual = true; r.AJG = "Sim"; mudou = true; }
    if (mudou) { try { this.syncFinancialControls(r); } catch (e) {} }
    return mudou;
  }
  cardInfo(r) {
    const tags = this.sourceTags(r), cl = this.cardClasse(r), sim = v => /^(sim|s|true|1|x|pendente)$/i.test(txt(v));
    const qualif = [...new Set(tags.map(x => this.cardQualifica(x)).filter(Boolean).filter(q => canon(q) !== canon(cl.nome)))];
    const visiveis = tags.filter(x => !this.cardEtiquetaOculta(x));
    const codClasse = txt(r["Código_Classe"]), codAss = txt(r["Código_Assunto_Principal"]);
    const assunto = this.cardAssunto(r.Assunto || r.assunto_judicial || r["Assunto_Principal"]) || "—";
    const prio = txt(r.prioridade || r.Prioridade), prioOn = !!prio && !/^(n|nao|não|0|false|-|sem)$/i.test(prio);
    const pendRaw = txt(r.Pendente_1Julgamento || r.SIN_PEND_1JULG), pend = pendRaw ? sim(pendRaw) : null;
    const tempoRaw = txt(r["Tempo_de_Tramitação"]);
    let tempo = tempoRaw;
    if (/^\d+([.,]\d+)?$/.test(tempoRaw)) { const d = Math.round(Number(tempoRaw.replace(",", "."))); const a = Math.floor(d / 365), m = Math.floor((d % 365) / 30); tempo = a ? `${a}a ${m}m` : m ? `${m}m ${d % 30}d` : `${d}d`; }
    const datas = [["Conclusão", r["Data_Conclusão"] || r["data_conclusão"]], ["Última movimentação", r["Data_Última_Movimentação"]]].filter(([, v]) => txt(v)).map(([k, v]) => `${k}: ${txt(v)}`);
    return { classe: cl, qualificacoes: qualif, etiquetas: visiveis, assunto,
      assuntoTitulo: [assunto, codAss ? `Código CNJ do assunto principal: ${codAss}` : "", codAss && this.cardCaminhoAssunto(codAss) ? this.cardCaminhoAssunto(codAss) : ""].filter(Boolean).join("\n"),
      classeTitulo: [cl.nome, codClasse ? `Código da classe: ${codClasse}` : ""].filter(Boolean).join("\n"),
      metas: splitTags(r.META).map(txt).filter(Boolean), prioridade: prioOn, prioridadeTitulo: prioOn ? `Prioridade: ${prio}` : "Sem prioridade legal registrada",
      pendente: pend, pendenteTitulo: pend === null ? "Pendência de 1º julgamento não informada" : pend ? "Pendente de 1º julgamento" : "Sem pendência de 1º julgamento",
      tempo: tempo || "—", tempoTitulo: ["Tempo de tramitação" + (tempoRaw ? `: ${tempoRaw}${/^\d+$/.test(tempoRaw) ? " dias" : ""}` : " não informado"), ...datas].join("\n"),
      ...(() => { const raw = txt(r.data_entrada_tarefa || r.Data_Entrada_Tarefa), d = raw.match(/^(\d{4})-(\d\d)-(\d\d)/) ? raw.slice(0, 10) : (raw.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})/) ? raw.replace(/^(\d{1,2})\/(\d{1,2})\/(\d{4}).*$/, (m0, a, b, c) => `${c}-${b.padStart(2, "0")}-${a.padStart(2, "0")}`) : "");
        const dias = d ? Math.round((Date.now() - Date.parse(d + "T12:00:00Z")) / 86400000) : null;
        return { entrada: d ? d.slice(8, 10) + "/" + d.slice(5, 7) + "/" + d.slice(2, 4) : raw, entradaTitulo: raw ? `Entrada na tarefa: ${raw}${dias !== null ? ` · há ${dias} dia(s)` : ""}` : "" }; })(),
      tarefa: txt(r.tarefa_atual) || "—", movimento: this.cardAssunto(txt(r.ultimo_movimento || r["Última_Movimentação"])) || "—",
      movimentoTitulo: [txt(r.ultimo_movimento || r["Última_Movimentação"]), txt(r["Data_Última_Movimentação"]) ? "em " + txt(r["Data_Última_Movimentação"]) : ""].filter(Boolean).join(" ") };
  }
  /* campos de dados do cartão: os de cima (até as partes) e os de "+ Informações" (das partes em diante) */
  cardCampos(r) {
    const fora = new Set(["Processo","processo","Assunto","Etiquetas","etiquetas","Etiquetas Originais","Etiquetas Operacionais","tarefa_atual","Tema","Especificidades","Síntese Processual","Dificuldade",
      "Código_Classe","Código_Assunto_Principal","classe_judicial","Classe","ultimo_movimento","Última_Movimentação","Data_Última_Movimentação","prioridade","Prioridade","Pendente_1Julgamento","SIN_PEND_1JULG","Tempo_de_Tramitação","Data_Conclusão","data_conclusão","META","data_entrada_tarefa","Data_Entrada_Tarefa"]);
    const cols = [...new Set([...this.columnConfig.central, ...this.centralKnownColumns].map(centralColumn))].filter(c => isVisibleColumn(c) && !WORK_COLUMNS.has(c) && !fora.has(c));
    const vistos = new Set();
    const campos = cols.map(c => { let v = txt(r[c]); if (/assunto/i.test(c)) v = this.cardAssunto(v); return { key: c, col: c.replace(/_/g, " "), val: v }; }).filter(f => {
      if (!f.val) return false; const k = fieldKey(f.key) + "|" + canon(f.val), k2 = "v|" + canon(f.val) + "|" + canon(f.key).replace(/[^a-z]/g, "").slice(0, 6);
      if (vistos.has(k) || vistos.has(k2)) return false; vistos.add(k); vistos.add(k2); return true; });
    let corte = campos.findIndex(f => /polo|advogado|parte/.test(canon(f.key))); if (corte < 0) corte = campos.length;
    return { A: campos.slice(0, corte), B: campos.slice(corte) };
  }
  /* controles de regularidade em formato compacto (mesma lógica dos controles da Seleção Prévia) */
  cardControles(i) {
    const r = this.rows[i], self = this, op = (lista, v) => [...new Set(["", ...lista, txt(v)])].map(x => ({ key: x || "_", v: x, l: x || "—" }));
    const ok = () => { self.recompute(r); self.saveDeb(); self.refresh(); };
    const dpu = truthy(r["DPU (controle)"]), restr = !!r._restricaoTipo, rep = txt(r["Representação"]);
    return {
      tempVal: txt(r.Tempestividade), tempOpts: op(DROPDOWNS.Tempestividade || ["Não Verificado", "Tempestivo", "Intempestivo"], r.Tempestividade), onTemp: e => { self.cell(i, "Tempestividade").onSelect(e.target.value); ok(); },
      prepVal: txt(r.Preparo), prepOpts: op(DROPDOWNS.Preparo || [], r.Preparo), onPrep: e => { self.financialChange(r, "Preparo", e.target.value); ok(); },
      dpu, ajg: truthy(r.AJG), onDpu: e => { self.financialChange(r, "DPU (controle)", e.target.checked); ok(); }, onAjg: e => { self.financialChange(r, "AJG", e.target.checked); ok(); },
      restr, restrRot: restr ? (r._restricaoTipo || "Registrado") : "Nenhum", restrTipo: r._restricaoTipo || "Impedimento", restrNome: txt(r._magistradoRestricao),
      onRestr: e => { self.cell(i, "Impedimento / Suspeição").onSelect(e.target.checked ? "Impedimento" : ""); ok(); },
      onRestrTipo: e => { self.cell(i, "Impedimento / Suspeição").onSelect(e.target.value); ok(); },
      onRestrNome: e => { self.cell(i, "Impedimento / Suspeição").onManual(e.target.value); ok(); },
      repVal: rep, repOpts: op(DROPDOWNS["Representação"] || ["Não Verificado", "Regular", "Negativo"], rep), onRep: e => { self.cell(i, "Representação").onSelect(e.target.value); ok(); },
      repId: txt(r["ID da Procuração"]), repSemId: rep !== "Regular", repIdPh: rep === "Regular" ? "ID da procuração" : "ID (se regular)", onRepId: e => { self.cell(i, "ID da Procuração").onText(e.target.value); ok(); },
      interc: txt(r["Intercorrências"]), onInterc: e => { self.cardIntercorrencias(r, e.target.value); self.saveDeb(); }
    };
  }
  /* planilha: uma coluna para cada campo do cartão (+ extras da página) e, depois, os campos de dados */
  cardPlanilha(itens, extras = []) {
    const yn = v => truthy(v) ? "Sim" : "Não", CXN = { 1: "Ω Padrão", 2: "A Intermediário", 3: "Σ Complexo" };
    const base = [["Processo", r => r.Processo], ["Classe", (r, f) => f.classe.nome], ["Qualificação", (r, f) => f.qualificacoes.join(" · ")], ["Assunto", (r, f) => f.assunto], ["Etiquetas", (r, f) => f.etiquetas.join(", ")],
      ["Tarefa atual", (r, f) => f.tarefa], ["Entrada na tarefa", (r, f) => f.entrada], ["Último movimento", (r, f) => f.movimento], ["Situação", r => { try { return this.situacao(r).label; } catch (e) { return ""; } }],
      ["Complexidade", r => CXN[Math.round(Number(r.Dificuldade))] || ""], ["Meta", (r, f) => f.metas.join(" · ")], ["Prioridade", (r, f) => f.prioridade ? txt(r.prioridade || r.Prioridade) || "Sim" : "Não"],
      ["1º julgamento", (r, f) => f.pendente === null ? "" : f.pendente ? "Pendente" : "Não"], ["Tramitação", (r, f) => f.tempo === "—" ? "" : f.tempo],
      ["Tempestividade", r => r.Tempestividade], ["Preparo", r => r.Preparo], ["DPU", r => yn(r["DPU (controle)"])], ["AJG", r => yn(r.AJG)], ["Impedimento / Suspeição", r => r["Impedimento / Suspeição"]],
      ["Representação", r => r["Representação"]], ["ID da Procuração", r => r["ID da Procuração"]], ["Síntese processual", r => r["Síntese Processual"]], ["Intercorrências", r => r["Intercorrências"]],
      ["Temas", r => this.triLista(r, "Tema").join(" · ")], ["Especificidades", r => this.triLista(r, "Especificidades").join(" · ")], ["Observações", r => r["Observações"]], ...extras];
    const dados = [], porLinha = itens.map(({ r }) => { const f = this.cardInfo(r), cc = this.cardCampos(r), m = {}; [...cc.A, ...cc.B].forEach(c => { if (!dados.includes(c.col)) dados.push(c.col); m[c.col] = c.val; }); return { r, f, m }; });
    const longas = new Set(["Etiquetas", "Síntese processual", "Intercorrências", "Observações", "Temas", "Especificidades", "Último movimento", "Assunto"]);
    const cols = [...base.map(b => b[0]), ...dados];
    return { cols: cols.map(c => ({ key: c, label: c, cls: longas.has(c) ? "quebra" : "" })),
      linhas: porLinha.map(({ r, f, m }) => ({ r, vals: [...base.map(([c, fn]) => ({ key: c, v: txt(fn(r, f)) || "—", cls: longas.has(c) ? "quebra" : "" })), ...dados.map(c => ({ key: c, v: m[c] || "—", cls: "" }))] })) };
  }
  /* ordem da relação: Assunto › Tema › Especificidade; agravos de instrumento e, por último, embargos de declaração ao final */
  cardGrupo(r) {
    const sig = this.cardClasse(r).sigla, q = this.sourceTags(r).map(x => this.cardQualifica(x));
    if (sig === "ED" || q.includes("EMBARGOS DE DECLARAÇÃO")) return 2;
    if (sig === "AI" || q.includes("AGRAVO DE INSTRUMENTO")) return 1;
    return 0;
  }
  cardOrdenar(itens) {
    const chave = new Map(itens.map(x => { const r = x.r; return [x, [this.cardGrupo(r), canon(this.cardAssunto(r.Assunto || r.assunto_judicial || r.Assunto_Principal)) || "~", canon(this.triLista(r, "Tema")[0] || "") || "~", canon(this.triLista(r, "Especificidades")[0] || "") || "~", Number(r._preOrder) || 0, txt(r.Processo)]]; }));
    const cmp = (a, b) => { const A = chave.get(a), B = chave.get(b); for (let k = 0; k < A.length; k++) { if (A[k] === B[k]) continue; return typeof A[k] === "number" ? A[k] - B[k] : String(A[k]).localeCompare(String(B[k]), "pt-BR"); } return 0; };
    return itens.slice().sort(cmp);
  }
  /* item provisório: posição do processo na relação ordenada da sua sessão (vira ITEM / ITEM DE PAUTA nas exportações) */
  itemProvisorio(r) {
    const s = txt(r["Sessão Destino"]) || "Sem sessão", agora = Date.now();
    if (!this._itemCache || agora - this._itemCache.t > 1500) this._itemCache = { t: agora, m: new Map() };
    let mapa = this._itemCache.m.get(s);
    if (!mapa) { mapa = new Map(); this.cardOrdenar(this.selectionSessionRows(s === "Sem sessão" ? "" : s).filter(({ r: x }) => (txt(x["Sessão Destino"]) || "Sem sessão") === s)).forEach((x, k) => mapa.set(x.r, k + 1)); this._itemCache.m.set(s, mapa); }
    return mapa.get(r) || "";
  }
  itemDePauta(r) { return txt(r["Item (Pauta de Julgamento)"]) || this.itemProvisorio(r); }
  /* relação simplificada (planilha e impressão A4): ITEM · PROCESSO · IND. · ASSUNTO · TEMA · OBSERVAÇÕES, ordenada pelo item */
  relIndicadores(r) {
    const out = [], g = this.cardGrupo(r), ok = (f) => { try { return f(); } catch (e) { return false; } };
    if (g === 2 || ok(() => this.pautaClass(r, "EMBARGOS DE DECLARAÇÃO"))) out.push({ k: "ed", s: "ED", t: "Embargos de declaração" });
    if (ok(() => this.pautaClass(r, "AGRAVO INTERNO")) || /agravo interno|\bagint\b/i.test([txt(r.classe_judicial || r.Classe), ...this.sourceTags(r)].join(" | "))) out.push({ k: "agint", s: "AgInt", t: "Agravo interno" });
    if (g === 1) out.push({ k: "ai", s: "AI", t: "Agravo de instrumento" });
    const metas = [...splitTags(r.META).map(txt), ...this.allTags(r).filter(t => { try { return this.tagRole(t) === "meta"; } catch (e) { return false; } })].filter(Boolean);
    const vistos = new Set();
    metas.forEach(m => { const full = /meta/i.test(m) ? m.toUpperCase().replace(/\s+/g, " ").trim() : "META " + txt(m); const curto = (full.match(/META\s*\d+[A-Z]?/) || [full])[0].replace(/\s+/g, " "); const c = canon(curto); if (vistos.has(c)) return; vistos.add(c); out.push({ k: "meta", s: curto, t: full }); });
    return out;
  }
  relSimplesLinha(r, item) {
    const ind = this.relIndicadores(r), restr = this.restrictionValue(r);
    const obs = txt(r["Observações"]).split("\n").map(x => x.trim()).filter(Boolean);
    if (restr && !obs.some(o => canon(o).includes(canon(restr)))) obs.push("⚠ " + (/impediment|suspei/i.test(restr) ? restr : "Impedimento/Suspeição: " + restr));
    return { item: item === undefined || item === null ? "" : item, processo: txt(r.Processo) || txt(r.processo), ind, indTxt: ind.map(b => b.s).join(" · "),
      assunto: this.cardAssunto(r.Assunto || r.assunto_judicial || r.Assunto_Principal) || "—",
      tema: this.triLista(r, "Tema").join(" · ") || txt(r.Tema) || "—", especificidades: this.triLista(r, "Especificidades").join(" · "),
      grupo: ["", "ai", "ed"][this.cardGrupo(r)] || "", pend1: (() => { try { return this.cardInfo(r).pendente === true; } catch (e) { return false; } })(), observacoes: obs.join("\n") || "—" };
  }
  relOrdenarPorItem(linhas) {
    const n = v => { const x = parseFloat(String(v).replace(",", ".")); return isNaN(x) ? Infinity : x; };
    return linhas.map((l, k) => ({ l, k })).sort((a, b) => (n(a.l.item) - n(b.l.item)) || (a.k - b.k)).map(x => x.l);
  }
  relSimplesSelecao() { return this.relOrdenarPorItem(this.cardOrdenar(this.effectivePre()).map(({ r }) => this.relSimplesLinha(r, this.itemDePauta(r)))); }
  relSimples(itens) {
    const ord = this.cardOrdenar(itens), pos = new Map(ord.map((x, k) => [x.r, k + 1]));
    const sel = r => r["Seleção Prévia"] === "SELECIONADO PREVIAMENTE";
    return this.relOrdenarPorItem(ord.map(({ r }) => this.relSimplesLinha(r, sel(r) ? this.itemDePauta(r) : pos.get(r))));
  }
@@REL_IMPRIMIR@@
  /* lança processos (por procId) na Seleção Prévia da sessão escolhida; continuam na triagem */
  triParaSelecao(ids, session) {
    if (!session) return this.notify("Escolha a sessão de destino (com data atual ou futura).", "warn");
    const set = new Set((ids || []).map(String)); if (!set.size) return this.notify("Marque pelo menos um processo.", "warn");
    let n = 0, ja = 0, mov = 0;
    this.rows.forEach(r => {
      if (!set.has(procId(r.Processo))) return;
      const sel = r["Seleção Prévia"] === "SELECIONADO PREVIAMENTE";
      if (sel && r["Sessão Destino"] === session) { ja++; return; }
      if (sel && txt(r["Sessão Destino"])) { mov++; r["Item (Pauta de Julgamento)"] = ""; }
      r["Sessão Destino"] = session; r["Seleção Prévia"] = "SELECIONADO PREVIAMENTE";
      if (r["Status de Julgamento"] !== "PAUTADO") r["Status de Julgamento"] = "PENDENTE";
      if (!Number.isFinite(Number(r._preOrder)) || !Number(r._preOrder)) r._preOrder = this.nextPreOrder();
      n++;
    });
    this.saveDB(); this.refresh();
    this.notify(`${n} processo(s) lançado(s) na Seleção Prévia de ${session}` + (mov ? ` (${mov} vindo(s) de outra sessão)` : "") + (ja ? ` · ${ja} já estava(m) nela` : "") + ".", n ? "ok" : "warn");
  }
  /* JSON compatível com "Importar sessões" do Hub de Sessões do Controle de Pauta (formato controle-pauta-hub-sessoes v1) */
  exportarJsonHub(session, itens) {
    if (!session || session === "Todas as sessões") return this.notify("Escolha uma sessão para exportar em JSON.", "warn");
    const copia = v => JSON.parse(JSON.stringify(v == null ? null : v)), dig = v => String(v || "").replace(/\D/g, "");
    const lista = (itens || this.selectionSessionRows(session)).filter(({ r }) => dig(r.Processo).length === 20);
    if (!lista.length) return this.notify("Não há processos (com número CNJ de 20 dígitos) nesta relação.", "warn");
    const agora = new Date().toISOString(), soData = v => { const t = txt(v); let m = /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/.exec(t); if (m) return `${m[3]}-${m[2].padStart(2, "0")}-${m[1].padStart(2, "0")}`; m = /^(\d{4}-\d{2}-\d{2})/.exec(t); return m ? m[1] : ""; };
    const det = copia(this.sessionDetails[session] || {});
    ["date", "prepStart", "minutasDeadline", "releaseDeadline", "pautaDeadline", "deadline"].forEach(f => { if (det[f] !== undefined && det[f] !== "") det[f] = soData(det[f]); });
    const ord = this.relOrdenarPorItem ? this.cardOrdenar(lista) : lista;
    const rows = ord.map(({ r }) => {
      const o = copia(r), item = String(this.itemDePauta(r) || "");
      o["Sessão Destino"] = session; o["Seleção Prévia"] = "SELECIONADO PREVIAMENTE"; o["Status de Julgamento"] = txt(r["Status de Julgamento"]) || "PENDENTE";
      const ents = Array.isArray(o._pautaEntries) ? o._pautaEntries.filter(e => e && typeof e === "object") : [];
      let e = ents.find(x => x.session === session);
      if (!e) { e = { session, item, status: o["Status de Julgamento"], next: "", includedAt: agora, closed: false, source: "painel-central" }; ents.push(e); }
      else if (!txt(e.item)) e.item = item;
      o._pautaEntries = ents; o._pautaHistory = Array.isArray(o._pautaHistory) ? o._pautaHistory : [];
      return o;
    });
    let cfg = {}; try { cfg = this.globalConfigSnapshot() || {}; } catch (err) {}
    const cal = cfg.workCalendar || (() => { try { return this.selectionCalendar(); } catch (err) { return null; } })();
    const contar = f => rows.filter(f).length;
    const data = { formato: "controle-pauta-hub-sessoes", versao: 1, exportadoEm: agora, origem: "Painel Central · Seleção Prévia",
      sessions: [session], sessionDetails: { [session]: det }, rows,
      pautaPreferences: { session, jsonSessionLists: { [session]: [...new Set(rows.map(o => dig(o.Processo)))] } }, pautaDaily: {},
      ...(cal && typeof cal === "object" ? { workCalendar: { weekdays: Array.isArray(cal.weekdays) ? cal.weekdays : [1, 2, 3, 4, 5], excluded: (cal.excluded || []).map(soData).filter(Boolean), labels: cal.labels && typeof cal.labels === "object" ? copia(cal.labels) : {} } } : {}),
      ...(cfg.team && typeof cfg.team === "object" ? { team: copia(cfg.team) } : {}), names: copia(this.names || []),
      estatisticas: { [session]: { total: rows.length, minutados: contar(o => txt(o.MINUTADO)), corrigidos: contar(o => /^(sim|s|true|1|x)$/i.test(txt(o.CORRIGIDO))), liberados: 0, julgados: contar(o => !["", "PENDENTE", "PAUTADO"].includes(txt(o["Status de Julgamento"]))), aMinutar: contar(o => !txt(o.MINUTADO)), mediaMinutasServidorDia: null, avisos: [] } } };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json;charset=utf-8" }), url = URL.createObjectURL(blob), a = document.createElement("a");
    a.href = url; a.download = ("Hub_Sessoes_" + session + "_" + agora.slice(0, 10)).replace(/[^\w.\-]+/g, "_") + ".json"; document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 1500);
    this.notify(`JSON da sessão ${session} exportado · ${rows.length} processo(s) · importável em “Importar sessões” do Controle de Pauta.`);
  }
  /* planilha do Acervo Central: todos os campos de dados do processo (não operacionais), além das colunas configuradas */
  centralDadosExtras(cols) {
    const agora = Date.now(), n = this.rows.length;
    if (!this._dadosCache || agora - this._dadosCache.t > 4000 || this._dadosCache.n !== n) {
      const chaves = new Set([...ACERVO_COLUMNS, ...GAB_SOURCE_COLUMNS, ...this.centralKnownColumns]);
      this.rows.forEach(r => { for (const k in (r || {})) chaves.add(k); });
      const OPER = new Set(["Especificidades", "Síntese processual", "Síntese Processual", "Intercorrências", "Dificuldade", "COMPLEXIDADE", "Etiquetas Originais", "Etiquetas Operacionais", "Regularidade Manual"].map(canon));
      const ordem = new Map([...ACERVO_COLUMNS, ...GAB_SOURCE_COLUMNS].map((c, k) => [c, k]));
      const lista = [...new Set([...chaves].map(centralColumn))]
        .filter(c => isVisibleColumn(c) && !WORK_COLUMNS.has(c) && !OPER.has(canon(c)) && this.rows.some(r => r && r[c] != null && txt(r[c]) !== ""))
        .sort((a, b) => (ordem.has(a) ? ordem.get(a) : 1e6) - (ordem.has(b) ? ordem.get(b) : 1e6) || a.localeCompare(b, "pt-BR"));
      this._dadosCache = { t: agora, n, lista };
    }
    const tem = new Set(cols.map(centralColumn));
    // mesma coluna com grafias distintas (ex.: Classe/classe_judicial são campos distintos e permanecem; só nomes idênticos após normalização são fundidos)
    const temK = new Set([...tem].map(c => canonKey(c)));
    return this._dadosCache.lista.filter(c => !tem.has(c) && !temK.has(canonKey(c)));
  }
  imprimirRelacao(itens, titulo, sub) {
    if (!itens.length) return this.notify("Não há processos nesta relação.", "warn");
    const linhas = this.relSimples(itens), pauta = linhas.length && itens.every(({ r }) => r["Seleção Prévia"] === "SELECIONADO PREVIAMENTE");
    this.printPautaSimplificada(linhas, titulo, sub, pauta ? "ITEM DE PAUTA" : "ITEM");
  }
  /* exportação da relação exibida (cartões): completa (todos os campos) ou simplificada (item, processo, indicadores, assunto, tema e observações) */
  exportarRelacao(itens, nome, simplificado, extras = []) {
    if (!itens.length) return this.notify("Não há processos nesta relação.", "warn");
    try {
      const ord = this.cardOrdenar(itens), X = window.XLSX, wb = X.utils.book_new(), pos = new Map(ord.map((x, k) => [x.r, k + 1]));
      const sel = r => r["Seleção Prévia"] === "SELECIONADO PREVIAMENTE", item = r => sel(r) ? this.itemDePauta(r) : pos.get(r), prov = r => sel(r) ? this.itemProvisorio(r) : pos.get(r);
      let aoa;
      if (simplificado) { const pauta = ord.every(({ r }) => sel(r)); return this.exportPautaSimplificada(this.relSimples(itens), `${nome}_simplificada.xlsx`.replace(/[^\w.\-]+/g, "_"), pauta ? "ITEM DE PAUTA" : "ITEM"); }
      else { const pl = this.cardPlanilha(ord, extras); aoa = [["ITEM", "Item provisório", ...pl.cols.map(c => c.label)], ...pl.linhas.map(({ r, vals }) => [item(r), prov(r), ...vals.map(v => v.v === "—" ? "" : v.v)])]; }
      const ws = X.utils.aoa_to_sheet(aoa), bd = { style: "thin", color: { rgb: "D9DCEF" } };
      aoa[0].forEach((_, j) => { const a = X.utils.encode_cell({ r: 0, c: j }); if (ws[a]) ws[a].s = { fill: { fgColor: { rgb: "1F3D63" } }, font: { bold: true, color: { rgb: "FFFFFF" } }, alignment: { horizontal: "center", vertical: "center", wrapText: true }, border: { top: bd, bottom: bd, left: bd, right: bd } }; });
      ws["!cols"] = aoa[0].map((h, j) => ({ wch: j === 0 ? 8 : Math.min(48, Math.max(12, String(h).length + 4)) }));
      ws["!autofilter"] = { ref: `A1:${X.utils.encode_col(aoa[0].length - 1)}${aoa.length}` };
      X.utils.book_append_sheet(wb, ws, simplificado ? "Relação" : "Relação completa");
      const arq = `${nome}_${simplificado ? "simplificada" : "completa"}.xlsx`.replace(/[^\w.\-]+/g, "_");
      X.writeFile(wb, arq); this.notify(`${ord.length} processo(s) exportado(s) — ${simplificado ? "item e processo" : aoa[0].length + " colunas"}.`);
    } catch (e) { this.notify("Falha ao exportar: " + (e.message || e), "err"); }
  }
  cardIntercorrencias(r, texto) {
    const antes = Array.isArray(r._pautaIncidents) ? r._pautaIncidents : [];
    const linhas = String(texto || "").split("\n").map(x => x.trim()).filter(Boolean);
    r._pautaIncidents = linhas.map((tx, k) => { const old = antes.find(i => txt(i.text) === tx); return old ? old : { id: "inc" + Date.now().toString(36) + k, text: tx, resolved: false, at: new Date().toISOString() }; });
    r["Intercorrências"] = linhas.join("\n");
  }
  triLista(r, c) { return dedupeLabels(splitTags(r[c])); }
  triAddItem(i, c, label) {
    const r = this.rows[i]; label = txt(label); if (!r || !label) return;
    const cur = this.triLista(r, c); if (!cur.some(t => canon(t) === canon(label))) r[c] = [...cur, label].join("\n");
    this.saveDeb(); this.refresh();
  }
  triMoverEtiqueta(i, label, c) {
    const r = this.rows[i]; if (!r || this._exclusive) return;
    const labels = this.sourceTags(r), key = canon(label); if (!labels.some(t => canon(t) === key)) return;
    if (c === "Observações") {
      // entra como tópico: "• Etiqueta", uma por linha, sem repetir
      const linhas = String(r[c] || "").replace(/\r/g, "").split("\n").map(l => l.replace(/\s+$/, "")).filter((l, k, a) => l || (k && a[k - 1]));
      const limpo = String(label).replace(/\s+/g, " ").trim(), item = "• " + limpo.charAt(0).toUpperCase() + limpo.slice(1);
      if (!linhas.some(l => canon(l.replace(/^[•\-–—*]\s*/, "")) === key)) { while (linhas.length && !linhas[linhas.length - 1].trim()) linhas.pop(); linhas.push(item); }
      r[c] = linhas.join("\n");
    } else { const cur = this.triLista(r, c); if (!cur.some(t => canon(t) === key)) r[c] = [...cur, label].join("\n"); }
    this.setCurrentTags(r, labels.filter(t => canon(t) !== key)); this.routeSpecialTags(r);
    this.saveDeb(); this.refresh();
  }
  triRemoverItem(i, c, label) {
    const r = this.rows[i]; if (!r) return; const key = canon(label);
    r[c] = this.triLista(r, c).filter(t => canon(t) !== key).join("\n");
    if (this.originalTags(r).some(t => canon(t) === key) && !this.sourceTags(r).some(t => canon(t) === key)) { this.setCurrentTags(r, [...this.sourceTags(r), label]); this.routeSpecialTags(r); }
    this.saveDeb(); this.refresh();
  }
  triColsExport(cols) {
    const out = [...cols]; let at = out.findIndex(c => fieldKey(c) === "etiquetas"); at = at < 0 ? out.length : at + 1;
    ["Tema", "Especificidades", "Síntese Processual"].forEach(c => { if (!out.includes(c)) out.splice(at++, 0, c); else at = Math.max(at, out.indexOf(c) + 1); });
    return out;
  }
  triEtqExport(r, v) {
    const fora = new Set([...splitTags(r.Tema), ...splitTags(r.Especificidades)].map(canon));
    return dedupeLabels(splitTags(v)).filter(t => !/secao/.test(canon(t)) && !fora.has(canon(t))).join(", ");
  }
  triagemValues() {
    const s = this.state, self = this, PAL = ["#2f6690","#4a8f74","#b4763a","#7a5ba6","#a6545e","#3d8b9c","#6b7d2f","#c0843d"];
    if (!this.triSel) this.triSel = new Set();
    if (!Array.isArray(this.escaninhos)) this.escaninhos = [];
    if (!window.__triDnd) {
      window.__triDnd = true;
      const alvo = e => e.target && e.target.closest && e.target.closest("[data-tri-esc]");
      document.addEventListener("dragstart", e => { const f = e.target && e.target.closest && e.target.closest("[data-tri-ficha]"); if (!f) return; const c = window.__painelCentralComponent; if (!c.triSel) c.triSel = new Set(); c.triSel.add(String(f.dataset.triFicha)); e.dataTransfer.setData("text/plain", "tri:" + [...c.triSel].join(",")); e.dataTransfer.effectAllowed = "move"; });
      document.addEventListener("dragover", e => { const n = alvo(e); if (!n) return; e.preventDefault(); document.querySelectorAll(".tri-nicho.alvo").forEach(x => { if (x !== n) x.classList.remove("alvo"); }); n.classList.add("alvo"); });
      document.addEventListener("dragleave", e => { const n = alvo(e); if (n && !n.contains(e.relatedTarget)) n.classList.remove("alvo"); });
      document.addEventListener("drop", e => { const n = alvo(e); if (!n) return; e.preventDefault(); n.classList.remove("alvo"); const d = e.dataTransfer.getData("text/plain") || ""; if (d.startsWith("tri:")) window.__painelCentralComponent.triGuardar(d.slice(4).split(",").filter(Boolean), n.dataset.triEsc); });
    }
    if (!window.__triDndTag) {
      window.__triDndTag = true;
      const caixa = e => e.target && e.target.closest && e.target.closest("[data-tri-dest]");
      document.addEventListener("dragstart", e => { const c = e.target && e.target.closest && e.target.closest("[data-tri-tag]"); if (!c) return; e.dataTransfer.setData("text/plain", "tag:" + c.dataset.triTag); e.dataTransfer.effectAllowed = "move"; e.stopPropagation(); }, true);
      document.addEventListener("dragover", e => { const n = caixa(e); if (!n) return; e.preventDefault(); n.classList.add("alvo"); });
      document.addEventListener("dragleave", e => { const n = caixa(e); if (n && !n.contains(e.relatedTarget)) n.classList.remove("alvo"); });
      document.addEventListener("drop", e => { const n = caixa(e); if (!n) return; e.preventDefault(); n.classList.remove("alvo");
        const d = e.dataTransfer.getData("text/plain") || ""; if (!d.startsWith("tag:")) return;
        const [pid, ...resto] = d.slice(4).split("|"), [dpid, dest] = String(n.dataset.triDest).split("|"); if (pid !== dpid) return;
        const c = window.__painelCentralComponent, i = c.rows.findIndex(r => procId(r.Processo) === pid); if (i >= 0) c.triMoverEtiqueta(i, resto.join("|"), dest); });
    }
    if (!this.triFaixa) this.triFaixa = new Set();
    const CX = [["1", "Ω", "Padrão", "#2f8a5e"], ["2", "A", "Intermediário", "#e3a21a"], ["3", "Σ", "Complexo", "#cf4b3b"]];
    const escs = this.escaninhos; escs.forEach((e, i) => { if (!e.cor) e.cor = PAL[i % PAL.length]; });
    const ids = new Set(escs.map(e => e.id));
    const all = this.triagemRows(), escOf = r => ids.has(r._escaninho) ? r._escaninho : "";
    const count = new Map(); all.forEach(({r}) => { const k = escOf(r); count.set(k, (count.get(k) || 0) + 1); });
    const q = canon(s.triSearch || ""), LIM = 300;
    const fmtD = d => /^\d{4}-\d\d-\d\d/.test(d || "") ? d.slice(0,10).split("-").reverse().join("/") : "—";
    const bandeja = all.filter(({r}) => !escOf(r) && (!q || canon([r.Processo, r.classe_judicial || r.Classe, r.Assunto || r.assunto_judicial, r.tarefa_atual, this.sourceTags(r).join(" ")].join(" ")).includes(q)));
    const visiveis = new Set(all.filter(({r}) => !escOf(r)).map(({r}) => procId(r.Processo)));
    [...this.triSel].forEach(id => { if (!visiveis.has(id)) this.triSel.delete(id); });
    const salvar = msg => { self.saveDB(); self.refresh(); if (msg) self.notify(msg); };
    const filtro = s.triFiltro || "todos", aberto = escs.find(e => e.id === s.triOpen) || null;
    const marcados = this.triSel.size;
    if (!this.triEscSel) this.triEscSel = new Set();
    const noAberto = aberto ? all.filter(({r}) => escOf(r) === aberto.id) : [];
    const idsAberto = new Set(noAberto.map(({r}) => procId(r.Processo)));
    [...this.triEscSel].forEach(id => { if (!idsAberto.has(id)) this.triEscSel.delete(id); });
    const escMarc = noAberto.filter(({r}) => this.triEscSel.has(procId(r.Processo)));
    const relExp = () => escMarc.length ? escMarc : noAberto, sufixo = () => escMarc.length ? "_marcados" : "";
    const sessoes = (() => { try { return this.upcomingSessions(); } catch (e) { return []; } })();
    const sessaoSP = sessoes.includes(s.triSessao) ? s.triSessao : (sessoes[0] || "");
    const lista = escs.filter(e => filtro === "todos" || (filtro === "cheios" ? count.get(e.id) : !count.get(e.id)));
    const camposDados = [...new Set([...this.columnConfig.central, ...this.centralKnownColumns].map(centralColumn))]
      .filter(c => isVisibleColumn(c) && !WORK_COLUMNS.has(c) && !["Processo","processo","Assunto","Etiquetas","etiquetas","Etiquetas Originais","Etiquetas Operacionais","tarefa_atual","Tema","Especificidades","Síntese Processual","Dificuldade"].includes(c));
    const linha = r => ({ proc: r.Processo || "—", classe: txt(r.classe_judicial || r.Classe) || "—", assunto: txt(r.Assunto || r.assunto_judicial) || "—", tarefa: txt(r.tarefa_atual) || "—" });
    return {
      isTriagem: s.tab === "triagem",
      triTotal: all.length, triInEsc: all.filter(({r}) => escOf(r)).length, triSemEsc: all.filter(({r}) => !escOf(r)).length, triEscCount: escs.length,
      triSearch: s.triSearch || "", onTriSearch: e => self.setState({ triSearch: e.target.value }),
      triBandejaCount: count.get("") || 0,
      triBandejaOff: !(count.get("") || 0) && !q, triCorpoCls: !(count.get("") || 0) && !q ? "semband" : "",
      triFichas: bandeja.slice(0, LIM).map(({r}) => { const id = procId(r.Processo), sel = self.triSel.has(id); return { key: "f" + id, id, ...linha(r), sel, cls: sel ? "sel" : "",
        tags: this.sourceTags(r).filter(x => !this.cardEtiquetaOculta(x)).slice(0, 3).map((t, k) => ({ key: k, label: t })),
        toggle: ev => { ev.target.checked ? self.triSel.add(id) : self.triSel.delete(id); self.refresh(); } }; }),
      triBandejaVazia: !bandeja.length,
      triBandejaMsg: !all.length ? "Nenhum processo na triagem. No Acervo Central, marque processos, escolha “Triagem Processual” no seletor de sessão destino e clique em ENCAMINHAR." : q ? "Nenhuma ficha corresponde à busca." : "Bandeja vazia — tudo guardado nos escaninhos.",
      triTruncated: bandeja.length > LIM, triTruncMsg: `Mostrando ${LIM} de ${bandeja.length} fichas — refine pela busca. “Marcar todos” marca as ${bandeja.length}.`,
      triTarget: ids.has(s.triTarget) ? s.triTarget : (aberto ? aberto.id : ""), onTriTarget: e => self.setState({ triTarget: e.target.value }),
      triTargetOptions: escs.map(e => ({ key: e.id, value: e.id, label: "🗂 " + e.titulo + " (" + (count.get(e.id) || 0) + ")" })),
      triMoverOff: !marcados || !escs.length,
      triMoverMarcados: () => {
        const alvo = ids.has(s.triTarget) ? s.triTarget : (aberto ? aberto.id : "");
        if (!escs.length) return self.notify("Crie um escaninho primeiro (+ Novo escaninho).", "warn");
        if (!alvo) return self.notify("Escolha o escaninho de destino.", "warn");
        if (!self.triSel.size) return self.notify("Marque pelo menos uma ficha da bandeja.", "warn");
        self.triGuardar([...self.triSel], alvo);
      },
      triSessaoOpts: sessoes.map(x => ({ key: x, value: x, label: x })), triSessao: sessaoSP, onTriSessao: e => self.setState({ triSessao: e.target.value }),
      triBandSP: () => { if (!self.triSel.size) return self.notify("Marque pelo menos uma ficha da bandeja.", "warn"); self.triParaSelecao([...self.triSel], sessaoSP); self.triSel.clear(); self.refresh(); }, triBandSPOff: !marcados || !sessaoSP,
      triEscSelCount: escMarc.length, triEscTodos: !!noAberto.length && escMarc.length === noAberto.length,
      triEscToggleTodos: e => { if (e.target.checked) noAberto.forEach(({r}) => self.triEscSel.add(procId(r.Processo))); else self.triEscSel.clear(); self.refresh(); },
      triEscLimpar: () => { self.triEscSel.clear(); self.refresh(); }, triEscLimparOff: !escMarc.length,
      triEscSP: () => { if (!escMarc.length) return self.notify("Marque processos do escaninho (ou “Marcar todos”).", "warn"); self.triParaSelecao(escMarc.map(({r}) => procId(r.Processo)), sessaoSP); self.triEscSel.clear(); self.refresh(); }, triEscSPOff: !escMarc.length || !sessaoSP,
      triEscSelMsg: escMarc.length ? `${escMarc.length} de ${noAberto.length} marcado(s) · exportação somente dos marcados` : `${noAberto.length} processo(s) · nenhum marcado — exportação de todos`,
      triEscSelCls: escMarc.length ? "on" : "",
      triSelCount: marcados, triClearFg: marcados ? "#a5730f" : "#6d7b8a",
      triSelectAll: () => { bandeja.forEach(({r}) => self.triSel.add(procId(r.Processo))); self.refresh(); },
      triClearSel: () => { self.triSel.clear(); self.refresh(); },
      removeFromTriagem: () => {
        const m = all.filter(({r}) => self.triSel.has(procId(r.Processo))); if (!m.length) return self.notify("Marque pelo menos uma ficha da bandeja.", "warn");
        if (!window.confirm(`Remover ${m.length} processo(s) da Triagem Processual? Eles continuam no Acervo Central.`)) return;
        m.forEach(({r}) => { r._triagem = ""; r._escaninho = ""; }); self.triSel.clear(); salvar(`${m.length} processo(s) removidos da triagem.`);
      },
      triFiltros: [["todos","Todos"],["cheios","Com processos"],["vazios","Vazios"]].map(([k, l]) => ({ key: k, label: l, cls: filtro === k ? "on" : "", pick: () => self.setState({ triFiltro: k }) })),
      triDica: marcados ? `${marcados} ficha(s) marcada(s) — clique no escaninho de destino para guardá-las.` : "Marque fichas na bandeja e clique num escaninho — ou arraste as fichas até ele. Clique num escaninho para abri-lo.",
      triEscaninhos: lista.map(e => { const n = count.get(e.id) || 0, cam = n ? Math.min(6, 1 + Math.ceil(Math.log2(n + 1) * 1.6)) : 0; return {
        key: e.id, titulo: e.titulo, subLabel: txt(e.subtitulo), hasSub: !!txt(e.subtitulo), obs: e.obs || "", hasObs: !!txt(e.obs), count: n, cor: e.cor, vazio: !n,
        layers: Array.from({ length: cam }, (_, k) => ({ key: k, b: k * 5 })), hasCapa: !!n, capaB: cam * 5,
        cls: [aberto && aberto.id === e.id ? "aberto" : "", marcados ? "pronto" : ""].join(" "),
        aria: `Escaninho ${e.titulo}, ${n} processo(s)`, title: marcados ? `Guardar ${marcados} ficha(s) aqui` : "Abrir escaninho",
        click: () => { if (self.triSel.size) self.triGuardar([...self.triSel], e.id); else self.setState({ triOpen: s.triOpen === e.id ? "" : e.id, triConfig: false }); }
      }; }),
      newEscaninho: () => { const id = "esc_" + Date.now().toString(36) + Math.random().toString(36).slice(2, 6); self.escaninhos.push({ id, titulo: "Novo escaninho", subtitulo: "", obs: "", cor: PAL[self.escaninhos.length % PAL.length], criado: new Date().toISOString().slice(0,10) }); self.setState({ triOpen: id, triFiltro: "todos", triConfig: true }); salvar("Escaninho criado — dê um título à placa."); },
      triHasOpen: !!aberto,
      triOpenTitulo: aberto ? aberto.titulo : "", triOpenSubRaw: aberto ? aberto.subtitulo || "" : "", triOpenSub: aberto ? txt(aberto.subtitulo) : "", triOpenHasSub: !!(aberto && txt(aberto.subtitulo)),
      triOpenObs: aberto ? aberto.obs || "" : "", triOpenCriado: aberto ? fmtD(aberto.criado) : "", triOpenCount: aberto ? count.get(aberto.id) || 0 : 0,
      onTriTitulo: e => { if (!aberto) return; aberto.titulo = e.target.value || "Sem título"; self.saveDeb(); self.refresh(); },
      onTriSub: e => { if (!aberto) return; aberto.subtitulo = e.target.value; self.saveDeb(); self.refresh(); },
      onTriObs: e => { if (!aberto) return; aberto.obs = e.target.value; self.saveDeb(); self.refresh(); },
      triCores: PAL.map(c => ({ key: c, cor: c, cls: aberto && aberto.cor === c ? "on" : "", pick: () => { if (!aberto) return; aberto.cor = c; self.saveDeb(); self.refresh(); } })),
      triConfigAberta: !!s.triConfig, triConfigSeta: s.triConfig ? "▴" : "▾", triConfigCls: s.triConfig ? "on" : "",
      triVistaPlanilha: s.triVista === "planilha", triVistaCards: s.triVista !== "planilha",
      ...(() => { if (s.triVista !== "planilha" || !aberto) return { triPlanCols: [], triPlanLinhas: [] }; const itens = self.cardOrdenar(all.filter(({r}) => escOf(r) === aberto.id)); itens.forEach(({r}) => { if (self.cardRegras(r)) self.saveDeb(); }); const pl = self.cardPlanilha(itens);
        return { triPlanCols: pl.cols, triPlanLinhas: pl.linhas.map(({ r, vals }) => { const pid = procId(r.Processo); return { key: "p" + pid, vals, sel: self.triEscSel.has(pid), selCls: self.triEscSel.has(pid) ? "marcada" : "", toggleSel: e => { e.target.checked ? self.triEscSel.add(pid) : self.triEscSel.delete(pid); self.refresh(); },
          abrirCard: () => { self.triFaixa.add(pid); self.setState({ triVista: "cards" }); setTimeout(() => { const n = document.querySelector(`[data-tri-card="${pid}"]`); n && n.scrollIntoView({ block: "start", behavior: "smooth" }); }, 60); },
          devolver: () => { r._escaninho = ""; salvar("Processo devolvido à bandeja."); },
          remover: () => { if (!window.confirm(`Remover ${r.Processo} da Triagem Processual? Ele continua no Acervo Central.`)) return; r._triagem = ""; r._escaninho = ""; salvar("Processo removido da triagem."); } }; }) }; })(),
      triVistaPlanCls: s.triVista === "planilha" ? "on" : "", triVistaCardsCls: s.triVista !== "planilha" ? "on" : "",
      triVerCards: () => self.setState({ triVista: "cards" }),
      triExpCompleta: () => aberto && self.exportarRelacao(relExp(), "Escaninho_" + aberto.titulo + sufixo(), false),
      triExpSimples: () => aberto && self.exportarRelacao(relExp(), "Escaninho_" + aberto.titulo + sufixo(), true),
      triImprimir: () => aberto && self.imprimirRelacao(relExp(), "Escaninho · " + aberto.titulo, "Triagem Processual · Gabinete A" + (escMarc.length ? " · " + escMarc.length + " marcado(s)" : "")), triVerPlanilha: () => self.setState({ triVista: "planilha" }),
      triToggleConfig: () => self.setState({ triConfig: !s.triConfig }),
      triOpenCor: aberto ? aberto.cor : "#c3ccd6",
      triConfigResumo: aberto ? (txt(aberto.obs) ? "📝 " + String(aberto.obs).replace(/\s+/g, " ").trim() : "sem bilhete") : "",
      triOpenRows: aberto ? self.cardOrdenar(all.filter(({r}) => escOf(r) === aberto.id)).map(({r, i}) => { const sit = self.situacao(r), pid = procId(r.Processo), aberta = self.triFaixa.has(pid);
        if (self.cardRegras(r)) self.saveDeb();
        const info = self.cardInfo(r), cc = self.cardCampos(r), infoAberta = !!(self.triInfo && self.triInfo.has(pid));
        const etqs = info.etiquetas, temas = self.triLista(r, "Tema"), esps = self.triLista(r, "Especificidades"), cx = CX.find(c => c[0] === String(txt(r.Dificuldade)));
        const addKey = c => e => { if (e.key !== "Enter") return; e.preventDefault(); const v = e.target.value; e.target.value = ""; self.triAddItem(i, c, v); };
        const addBtn = c => e => { const inp = e.currentTarget.parentElement.querySelector("input"); const v = inp.value; inp.value = ""; self.triAddItem(i, c, v); };
        const plural = (n, s, p) => n + " " + (n === 1 ? s : p);
        let ctrls = [];
        if (aberta) { try { ctrls = self.preControllers(i).parts.map(c => ({ ...c, key: c.col })); if (!ctrls.some(c => /id da procura/.test(canon(c.col)))) ctrls.push({ ...self.cell(i, "ID da Procuração"), col: "ID DA PROCURAÇÃO", key: "idproc" });
            ctrls.push({ col: "INTERCORRÊNCIAS", key: "interc", kind: "area", value: txt(r["Intercorrências"]), options: [], chips: [], tags: [], checked: false, auto: "", manual: "", onText: v => { self.cardIntercorrencias(r, v); self.saveDeb(); } }); } catch (err) { ctrls = ["Tempestividade","Impedimento / Suspeição","Preparo","Representação","ID da Procuração"].map(c => ({ ...self.cell(i, c), col: c.toUpperCase(), key: c })); } }
        const obsTxt = String(r["Observações"] || ""), poloA = txt(r.polo_ativo || r.Polo_Ativo) || "—", poloP = txt(r.polo_passivo || r.Polo_Passivo) || "—";
        return { key: "g" + pid, pid, ...linha(r), poloA, poloP, obsTxt, sel: self.triEscSel.has(pid), selCls: self.triEscSel.has(pid) ? "marcada" : "", toggleSel: e => { e.target.checked ? self.triEscSel.add(pid) : self.triEscSel.delete(pid); self.refresh(); }, obsCount: obsTxt.split("\n").filter(l => l.trim()).length,
        temasTxt: temas.join(" · ") || "—", espsTxt: esps.join(" · ") || "—", destObs: pid + "|Observações",
        onObs: e => { r["Observações"] = e.target.value; self.saveDeb(); },
        abrirCard: () => { self.triFaixa.add(pid); self.setState({ triVista: "cards" }); setTimeout(() => { const n = document.querySelector(`[data-tri-card="${pid}"]`); n && n.scrollIntoView({ block: "start", behavior: "smooth" }); }, 60); },
        camposA: cc.A, camposB: cc.B, infoAberta, infoSeta: infoAberta ? "▾" : "▸",
        infoResumo: cc.B.length ? cc.B.slice(0, 4).map(f => f.col.toLowerCase()).join(" · ") + (cc.B.length > 4 ? ` · +${cc.B.length - 4}` : "") : "sem outras informações",
        toggleInfo: () => { if (!self.triInfo) self.triInfo = new Set(); infoAberta ? self.triInfo.delete(pid) : self.triInfo.add(pid); self.refresh(); },
        clsSigla: info.classe.sigla, clsCor: info.classe.cor, clsFundo: info.classe.fundo, clsTitulo: info.classeTitulo, classe: info.classe.nome,
        qualifs: info.qualificacoes.map(q => ({ key: q, label: q })), temQualif: info.qualificacoes.length > 0,
        assunto: info.assunto, assuntoTitulo: info.assuntoTitulo, tarefa: info.tarefa, temEntrada: !!info.entrada, entrada: info.entrada, entradaTitulo: info.entradaTitulo, movimento: info.movimento, movimentoTitulo: info.movimentoTitulo,
        metas: info.metas.map(m => ({ key: m, label: m })), semMeta: !info.metas.length,
        prioCls: info.prioridade ? "on" : "off", prioTitulo: info.prioridadeTitulo,
        pendCls: info.pendente ? "on" : "off", pendTxt: info.pendente === null ? "—" : info.pendente ? "pendente" : "não", pendTitulo: info.pendenteTitulo,
        tempo: info.tempo, tempoTitulo: info.tempoTitulo,
        cxValor: cx ? cx[0] : "", onCx: e => { r.Dificuldade = e.target.value; self.saveDeb(); self.refresh(); },
        ...self.cardControles(i),
        ...(() => { const d = workflowDate(r.MINUTADO), br = d ? d.split("-").reverse().join("/") : ""; return { minutado: !!d, minutCls: d ? "on" : "", minutTxt: d ? br : "a minutar", minutTitulo: d ? `Minuta concluída em ${br} — desmarque para desfazer` : "Marque quando a minuta estiver concluída (registra a data de hoje)",
          onMinut: e => { const hj = new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 10); self.cell(i, "MINUTADO").onText(e.target.checked ? hj : ""); self.saveDeb(); self.refresh(); } }; })(),
        faixaAberta: aberta, faixaSeta: aberta ? "▾" : "▸",
        toggleFaixa: () => { aberta ? self.triFaixa.delete(pid) : self.triFaixa.add(pid); self.refresh(); },
        cxCor: cx ? cx[3] : "#c3ccd6", cxSimb: cx ? cx[1] : "·",
        faixaResumo: [cx ? cx[2] : "complexidade não definida", plural(etqs.length, "etiqueta", "etiquetas"), plural(temas.length, "tema", "temas"), plural(esps.length, "especificidade", "especificidades"), txt(r["Síntese Processual"]) ? "síntese ✓" : "sem síntese"].join(" · "),
        cxOpcoes: CX.map(([v, simb, nome, cor]) => ({ key: v, simb, nome, cor, on: cx && cx[0] === v, cls: cx && cx[0] === v ? "on" : "", pick: () => { r.Dificuldade = cx && cx[0] === v ? "" : v; self.saveDeb(); self.refresh(); } })),
        sintese: r["Síntese Processual"] || "", onSintese: e => { r["Síntese Processual"] = e.target.value; self.saveDeb(); },
        etqCount: etqs.length, etqVazio: !etqs.length,
        etqs: aberta ? etqs.map(l => ({ key: l, label: l, drag: pid + "|" + l, toTema: () => self.triMoverEtiqueta(i, l, "Tema"), toEsp: () => self.triMoverEtiqueta(i, l, "Especificidades"), toObs: () => self.triMoverEtiqueta(i, l, "Observações") })) : [],
        destTema: pid + "|Tema", destEsp: pid + "|Especificidades",
        temasCount: temas.length, temasVazio: !temas.length, temas: aberta ? temas.map(l => ({ key: l, label: l, remover: () => self.triRemoverItem(i, "Tema", l) })) : [],
        espsCount: esps.length, espsVazio: !esps.length, esps: aberta ? esps.map(l => ({ key: l, label: l, remover: () => self.triRemoverItem(i, "Especificidades", l) })) : [],
        addTemaKey: addKey("Tema"), addTemaBtn: addBtn("Tema"), addEspKey: addKey("Especificidades"), addEspBtn: addBtn("Especificidades"),
        ctrls,
        etiquetas: info.etiquetas.join(", ") || "—", situacao: sit.label, sitBg: sit.bg, sitFg: sit.fg,
        devolver: () => { r._escaninho = ""; salvar("Processo devolvido à bandeja."); },
        remover: () => { if (!window.confirm(`Remover ${r.Processo} da Triagem Processual? Ele continua no Acervo Central.`)) return; r._triagem = ""; r._escaninho = ""; salvar("Processo removido da triagem."); } }; }) : [],
      triOpenVazio: !!aberto && !(count.get(aberto.id) || 0),
      triDevolverTodos: () => { if (!aberto) return; const m = all.filter(({r}) => escOf(r) === aberto.id); m.forEach(({r}) => { r._escaninho = ""; }); salvar(`${m.length} processo(s) devolvido(s) à bandeja.`); },
      triExcluir: () => { if (!aberto) return; const n = count.get(aberto.id) || 0; if (!window.confirm(`Excluir o escaninho "${aberto.titulo}"?` + (n ? `\n\nOs ${n} processo(s) dele voltam para a bandeja.` : ""))) return; self.rows.forEach(r => { if (r._escaninho === aberto.id) r._escaninho = ""; }); self.escaninhos = self.escaninhos.filter(x => x.id !== aberto.id); self.setState({ triOpen: "" }); salvar(`Escaninho "${aberto.titulo}" excluído.`); },
      triRecolher: () => self.setState({ triOpen: "" })
    };
  }
'''
METODOS = METODOS.replace("@@REL_IMPRIMIR@@", __import__('pathlib').Path(__file__).with_name("relacao_impressao.js").read_text(encoding="utf-8").rstrip("\n"))


PATCHES = [
    # persistência dos escaninhos junto com o painel
    ("centralKnownColumns:[...this.centralKnownColumns], gabSourceColumns:[...this.gabSourceColumns], deletedTags:this.deletedTags }));",
     "centralKnownColumns:[...this.centralKnownColumns], gabSourceColumns:[...this.gabSourceColumns], deletedTags:this.deletedTags, escaninhos:Array.isArray(this.escaninhos)?this.escaninhos:[] }));"),
    ("this.deletedTags = Array.isArray(d.deletedTags) ? d.deletedTags : [];",
     "this.deletedTags = Array.isArray(d.deletedTags) ? d.deletedTags : []; this.escaninhos = Array.isArray(d.escaninhos) ? d.escaninhos : [];"),
    # métodos novos
    ("  addToPreselection() {\n    const session = this.state.centralSession;",
     METODOS + "  addToPreselection() {\n    if (this.state.centralSession === \"" + TRI + "\") return this.sendToTriagem();\n    const session = this.state.centralSession;"),
    # o seletor aceita a opção fixa da triagem
    ('if(this.state.centralSession&&!this.upcomingSessions().includes(this.state.centralSession))this.state.centralSession="";',
     'if(this.state.centralSession&&this.state.centralSession!=="' + TRI + '"&&!this.upcomingSessions().includes(this.state.centralSession))this.state.centralSession="";'),
    ('if (!r["Sessão Destino"] && this.state.centralSession) r["Sessão Destino"]=this.state.centralSession;',
     'if (!r["Sessão Destino"] && this.state.centralSession && this.state.centralSession !== "' + TRI + '") r["Sessão Destino"]=this.state.centralSession;'),
    ("      sessionOptions: this.upcomingSessions().map(",
     '      selectBtnLabel: s.centralSession === "' + TRI + '" ? "ENCAMINHAR" : "SELECIONAR",\n      sessionOptions: [{key:"' + TRI + '",value:"' + TRI + '",label:"⧉ Triagem Processual"}].concat(this.upcomingSessions().map('),
    ("+(m.deadline?' · prazo '+fmtBr(m.deadline):'')};}),", "+(m.deadline?' · prazo '+fmtBr(m.deadline):'')};})),"),
    # nav e títulos
    ('const navDefs = [["central", "Acervo Central", this.rows.length, "▣"], ["selecao", "Seleção Prévia", selCount, "✓"]];',
     'const navDefs = [["central", "Acervo Central", this.rows.length, "▣"], ["triagem", "Triagem Processual", this.rows.filter(r => txt(r._triagem)).length, "⧉"], ["selecao", "Seleção Prévia", selCount, "✓"]];'),
    ('      import: ["Importar / atualizar", "Central de importação do Acervo e das planilhas suplementares Gab A."]',
     '      triagem: ["Triagem Processual", "Processos encaminhados do Acervo Central para triagem, organizados em escaninhos — pastas com título, subtítulo e observação."],\n      import: ["Importar / atualizar", "Central de importação do Acervo e das planilhas suplementares Gab A."]'),
    ("      ...self.decisionValues(),", "      ...self.decisionValues(),\n      ...self.triagemValues(),"),
    # botão do seletor no Acervo Central
    ('title="Enviar selecionados à Seleção Prévia" style="border:0;cursor:pointer;padding:8px 13px;font-weight:850;font-size:9px;background:#d9a441;color:#33240a;white-space:nowrap">SELECIONAR</button>',
     'title="Enviar selecionados à sessão escolhida (Seleção Prévia) ou à Triagem Processual" style="border:0;cursor:pointer;padding:8px 13px;font-weight:850;font-size:9px;background:#d9a441;color:#33240a;white-space:nowrap">{{ selectBtnLabel }}</button>'),
    # aba
    ("    </sc-if>\n  </main></div>", "    </sc-if>\n" + MARKUP + "  </main></div>"),
    # relação simplificada: colunas IND./ASSUNTO/TEMA/OBSERVAÇÕES, indicadores e ordem pelo item (planilha e impressão A4)
    ("  simplifiedPautaRows() {", "  simplifiedPautaRows() { return this.relSimplesSelecao(); }\n  simplifiedPautaRowsLegado() {"),
    ('  exportPautaSimplificada() {\n    const rows=this.simplifiedPautaRows();if(!rows.length)return this.notify("Não há processos nos filtros atuais.","warn");\n    const heads=["ITEM DE PAUTA","PROCESSO","ASSUNTO CNJ","TEMA","OBSERVAÇÕES"],keys=["item","processo","assunto","tema","observacoes"];',
     '  exportPautaSimplificada(rowsIn, arquivo, itemHead) {\n    const rows=rowsIn || this.simplifiedPautaRows();if(!rows.length)return this.notify("Não há processos nos filtros atuais.","warn");\n    const heads=[itemHead || "ITEM DE PAUTA","PROCESSO","IND.","ASSUNTO CNJ","TEMA","OBSERVAÇÕES"],keys=["item","processo","indTxt","assunto","tema","observacoes"];'),
    ("for(let j=0;j<5;j++)", "for(let j=0;j<6;j++)"),
    ('horizontal:j===0?"center":"left"},border};}', 'horizontal:j===0||j===2?"center":"left"},border};}'),
    ("{wch:7},{wch:27},", "{wch:7},{wch:27},{wch:11},"),
    ('ws["!autofilter"]={ref:"A1:E"', 'ws["!autofilter"]={ref:"A1:F"'),
    ('this.downloadPautaBytes(this.pautaXlsxBytes(wb));this.notify("Pauta Simplificada baixada em Excel · "+rows.length+" processos.");',
     'if(arquivo)XLSX.writeFile(wb,arquivo);else this.downloadPautaBytes(this.pautaXlsxBytes(wb));this.notify((arquivo ? "Relação simplificada" : "Pauta Simplificada")+" baixada em Excel · "+rows.length+" processos · ordenada pelo item.");'),
    ('  printPautaSimplificada() {\n    const rows=this.simplifiedPautaRows();\n    if(!rows.length)return this.notify("Não há processos na Seleção Prévia para gerar a pauta simplificada.","warn");',
     '  printPautaSimplificada(rowsIn, tituloIn, subIn, itemHead) {\n    const rows=Array.isArray(rowsIn) ? rowsIn : this.simplifiedPautaRows();\n    if(!rows.length)return this.notify("Não há processos nesta relação para gerar a versão de impressão.","warn");\n    if(!Array.isArray(rowsIn)){const ss=[...new Set(this.effectivePre().map(({r})=>txt(r["Sessão Destino"])).filter(Boolean))];tituloIn=ss.map(n=>{const d=(this.sessionDetails[n]||{}).date;return n+(d&&n!==fmtBr(d)?" · "+fmtBr(d):"");}).join(" / ")||"Pauta simplificada";subIn="Seleção Prévia · pauta simplificada";itemHead="ITEM DE PAUTA";}\n    return this.relImprimirHtml(rows,tituloIn,subIn,itemHead);'),
    ("item = width * .05, remaining = Math.max(0, width - item - processWidth);", "item = width * .05, ind = width * .07, remaining = Math.max(0, width - item - ind - processWidth);"),
    ("const widths = [item, processWidth, remaining * 25 / 71, remaining * 20 / 71, remaining * 26 / 71];", "const widths = [item, processWidth, ind, remaining * 25 / 71, remaining * 20 / 71, remaining * 26 / 71];"),
    ("<title>Pauta simplificada — Seleção Prévia</title>", "<title>${esc(tituloIn || \"Pauta simplificada — Seleção Prévia\")}</title>"),
    ("tr{break-inside:avoid;page-break-inside:avoid}thead{display:table-header-group}",
     "tr{break-inside:avoid;page-break-inside:avoid}thead{display:table-header-group}td.ind{text-align:center;white-space:normal}.b{display:inline-block;border:.15mm solid #666;border-radius:.6mm;padding:0 .5mm;margin:0 .2mm .25mm;font-size:6.6pt;font-weight:700;line-height:1.2;white-space:nowrap;print-color-adjust:exact;-webkit-print-color-adjust:exact}.b-ed{background:#ffe2b8;border-color:#b26a00}.b-agint{background:#eadcff;border-color:#6a3fb5}.b-ai{background:#d6e9ff;border-color:#2563a8}.b-meta{background:#d4f3df;border-color:#1f7a45}.legenda{font-size:6.5pt;margin:.6mm 0 0}"),
    ('<h1>Pauta simplificada${sessionText ? " — "+esc(sessionText) : ""}</h1><div class="sub">Seleção Prévia · ${rows.length} processo(s)</div></header><table><colgroup><col style="width:5%"><col style="width:24%">',
     '<h1>${tituloIn ? esc(tituloIn) : "Pauta simplificada"+(sessionText ? " — "+esc(sessionText) : "")}</h1><div class="sub">${esc(subIn || "Seleção Prévia")} · ${rows.length} processo(s) · ordem pelo ${itemHead==="ITEM" ? "item" : "item de pauta"}</div><div class="legenda"><span class="b b-ed">ED</span> embargos de declaração <span class="b b-agint">AgInt</span> agravo interno <span class="b b-ai">AI</span> agravo de instrumento <span class="b b-meta">META</span> meta · impedimento/suspeição nas observações (⚠)</div></header><table><colgroup><col style="width:5%"><col style="width:24%"><col style="width:7%">'),
    ("<thead><tr><th>ITEM DE PAUTA</th><th>PROCESSO</th><th>ASSUNTO CNJ</th>", "<thead><tr><th>${esc(itemHead || \"ITEM DE PAUTA\")}</th><th>PROCESSO</th><th>IND.</th><th>ASSUNTO CNJ</th>"),
    ('<td class="processo">${esc(r.processo)}</td><td>${esc(r.assunto)}</td>', '<td class="processo">${esc(r.processo)}</td><td class="ind">${(r.ind || []).map(b=>`<span class="b b-${b.k}" title="${esc(b.t)}">${esc(b.s)}</span>`).join("")}</td><td>${esc(r.assunto)}</td>'),
    # Acervo Central · planilha: todos os campos de dados do processo (não operacionais), independentemente da configuração dos cartões
    ('const sheetDisplayCols=cols.filter(c => !["Etiquetas Originais","Seção Competente"].includes(c));',
     'const sheetExtra=this.centralDadosExtras(cols),sheetSig=new Set(SIGILO_COLUMNS);\n    const sheetDisplayCols=[...cols,...sheetExtra].filter(c => c !== "Etiquetas Originais");'),
    ('const sheetGroups=[{label:"PROCESSO, TEMA E ETIQUETAS",cols:leading},...cardColumnGroups.map(g => ({...g,cols:g.cols.filter(c => sheetDisplayCols.includes(c) && !leadingSet.has(c))}))]',
     'const sheetGroups=[{label:"PROCESSO, TEMA E ETIQUETAS",cols:leading},...(cardColumnGroups.some(g => g.label==="DADOS DO PROCESSO") ? cardColumnGroups : [{label:"DADOS DO PROCESSO",cols:[]},...cardColumnGroups]).map(g => ({...g,cols:[...g.cols,...(g.label==="DADOS DO PROCESSO" ? sheetExtra.filter(c => !sheetSig.has(c)) : g.label==="SIGILO" ? sheetExtra.filter(c => sheetSig.has(c)) : [])].filter(c => sheetDisplayCols.includes(c) && !leadingSet.has(c))}))]'),
    # pauta simplificada: item provisório (ordem Assunto › Tema › Especificidade; AI e ED ao final)
    ('return {item:txt(r["Item (Pauta de Julgamento)"]) || this.rows.filter(x=>x["Seleção Prévia"]==="SELECIONADO PREVIAMENTE").sort((a,b)=>Number(a._preOrder)-Number(b._preOrder)).indexOf(r)+1,', 'return {item:this.itemDePauta(r),'),
    ('    return this.effectivePre().map(({r},idx)=>{', '    return this.cardOrdenar(this.effectivePre()).map(({r},idx)=>{'),
    # estilos
    ("    .central-stats-stack{display:grid;gap:14px;min-width:0}", CSS + "    .central-stats-stack{display:grid;gap:14px;min-width:0}"),
    # exportação: TEMAS (coluna Tema, cabeçalho "Temas"), ESPECIFICIDADES e SÍNTESE; etiquetas sem as convertidas e sem "Seção"
    ('"Status: Corrigido":"CORRIGIDO"};', '"Status: Corrigido":"CORRIGIDO","Temas":"Tema"};'),
    ("  addSheet(wb, name, cols, dataRows, accent) {\n    const data = this.exportRows(cols, dataRows);\n    const ws = XLSX.utils.json_to_sheet(data, { header: cols });",
     "  addSheet(wb, name, cols, dataRows, accent) {\n    cols = this.triColsExport(cols);\n    const data = this.exportRows(cols, dataRows);\n    const ws = XLSX.utils.json_to_sheet(data, { header: cols });\n    cols.forEach((c, j) => { const a = XLSX.utils.encode_cell({ r: 0, c: j }); if (c === \"Tema\" && ws[a]) ws[a].v = \"Temas\"; });"),
    ('        else o[c] = r[c] == null ? "" : r[c];\n      });\n      return o;',
     '        else if (fieldKey(c) === "etiquetas" || c === "Etiquetas Originais") o[c] = this.triEtqExport(r, r[c]);\n        else if ((c === "Item (Pauta de Julgamento)" || c === "Numeração Prévia") && !txt(r[c]) && r["Seleção Prévia"] === "SELECIONADO PREVIAMENTE") o[c] = this.itemProvisorio(r);\n        else o[c] = r[c] == null ? "" : r[c];\n      });\n      return o;'),
]
