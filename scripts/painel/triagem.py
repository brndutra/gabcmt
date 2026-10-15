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
    .tri-pcard-topo{display:grid;grid-template-columns:minmax(170px,.9fr) minmax(0,1.1fr) minmax(0,1fr) minmax(0,1fr) 160px auto;align-items:stretch}
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
    .tri-fx-l1{display:grid;grid-template-columns:auto minmax(0,1fr);gap:12px;align-items:stretch}
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
    @media(max-width:1100px){.tri-fx-l1,.tri-fx-l2{grid-template-columns:minmax(0,1fr)}}
    /* bandeja integrada ao móvel de escaninhos */
    .tri-int-corpo{display:grid;grid-template-columns:300px minmax(0,1fr);align-items:stretch;min-width:0}
    .tri-int .tri-bandeja{position:static;border:0;border-right:1px solid #e3e7ec;border-radius:0;box-shadow:none;display:flex;flex-direction:column;min-width:0;background:#fbfcfd}
    .tri-int .tri-band-topo{background:transparent}
    .tri-int .tri-band-lista{max-height:560px;min-height:260px;flex:1}
    .tri-int-nichos{min-width:0}
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
    .tri-aberto-topo .tri-config-resumo{flex:1 1 160px;min-width:0}
    /* modo planilha */
    .tri-plan-wrap{overflow:auto;max-height:72vh;border:1px solid #dfe6ee;border-radius:10px;background:#fff}
    .tri-plan{display:table;width:100%;border-collapse:collapse;min-width:1180px;font-size:11.5px}
    .tri-plan-tr{display:table-row}
    .tri-plan-tr>*{display:table-cell;padding:7px 8px;border-bottom:1px solid #eef1f4;vertical-align:top;color:#3d4c5c;max-width:220px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
    .tri-plan-tr.cab>span{position:sticky;top:0;z-index:1;background:#f4f6f9;color:#5c6a78;font-size:8.5px;font-weight:900;letter-spacing:.06em;text-transform:uppercase;padding:8px;border-bottom:1px solid #e3e7ec}
    .tri-plan-tr>.quebra{white-space:normal;min-width:120px}
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
            <div class="tri-int-corpo">
            <aside class="tri-bandeja" aria-label="Bandeja da triagem">
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
                  <sc-if value="{{ triVistaPlanilha }}" hint-placeholder-val="{{ false }}">
                    <div class="tri-plan-wrap"><div class="tri-plan" role="table" aria-label="Processos do escaninho">
                      <div class="tri-plan-tr cab" role="row"><span>Processo</span><span>Assunto</span><span>Complex.</span><span>Etiquetas</span><span>Temas</span><span>Especificidades</span><span>Observações</span><span>Tarefa atual</span><span>Situação</span><span>Polo ativo</span><span>Polo passivo</span><span></span></div>
                      <sc-for list="{{ triOpenRows }}" as="g" hint-placeholder-count="3"><div class="tri-plan-tr" role="row">
                        <div class="c"><b class="num">{{ g.proc }}</b><i>{{ g.classe }}</i></div><div class="c" title="{{ g.assunto }}">{{ g.assunto }}</div>
                        <div class="c"><span class="tri-plan-cx"><sc-for list="{{ g.cxOpcoes }}" as="o"><button class="{{ o.cls }}" style="--c:{{ o.cor }}" sc-camel-on-click="{{ o.pick }}" title="{{ o.nome }}" aria-pressed="{{ o.on }}">{{ o.simb }}</button></sc-for></span></div>
                        <div class="c quebra" title="{{ g.etiquetas }}">{{ g.etiquetas }}</div><div class="c quebra">{{ g.temasTxt }}</div><div class="c quebra">{{ g.espsTxt }}</div><div class="c quebra obs" title="{{ g.obsTxt }}">{{ g.obsTxt }}</div>
                        <div class="c" title="{{ g.tarefa }}">{{ g.tarefa }}</div><div class="c"><em style="background:{{ g.sitBg }};color:{{ g.sitFg }}">{{ g.situacao }}</em></div>
                        <div class="c" title="{{ g.poloA }}">{{ g.poloA }}</div><div class="c" title="{{ g.poloP }}">{{ g.poloP }}</div>
                        <div class="c acoes"><button class="tri-icone" sc-camel-on-click="{{ g.abrirCard }}" title="Abrir no modo cards, com a faixa de triagem">▸</button><button class="tri-icone" sc-camel-on-click="{{ g.devolver }}" title="Devolver à bandeja">↩</button><button class="tri-icone" sc-camel-on-click="{{ g.remover }}" title="Remover da triagem (volta só ao acervo)" style="color:#a64f35">✕</button></div>
                      </div></sc-for>
                    </div></div>
                  </sc-if>
                  <sc-if value="{{ triVistaCards }}" hint-placeholder-val="{{ true }}">
                  <sc-for list="{{ triOpenRows }}" as="g" hint-placeholder-count="2">
                    <div class="tri-pcard" data-tri-card="{{ g.pid }}">
                      <div class="tri-pcard-topo">
                        <div class="tri-pc-cel"><span>PROCESSO</span><b class="num">{{ g.proc }}</b><i>{{ g.classe }}</i></div>
                        <div class="tri-pc-cel"><span>ASSUNTO</span><b>{{ g.assunto }}</b></div>
                        <div class="tri-pc-cel"><span>ETIQUETAS ATUAIS</span><b title="{{ g.etiquetas }}">{{ g.etiquetas }}</b></div>
                        <div class="tri-pc-cel"><span>TAREFA ATUAL</span><b title="{{ g.tarefa }}">{{ g.tarefa }}</b></div>
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
                              <div><span class="tri-fx-rot">COMPLEXIDADE</span><div class="tri-cx" role="radiogroup" aria-label="Complexidade"><sc-for list="{{ g.cxOpcoes }}" as="o"><button class="tri-cx-op {{ o.cls }}" role="radio" aria-checked="{{ o.on }}" sc-camel-on-click="{{ o.pick }}"><i style="background:{{ o.cor }}">{{ o.simb }}</i>{{ o.nome }}</button></sc-for></div></div>
                              <div style="display:flex;flex-direction:column;min-width:0"><span class="tri-fx-rot">SÍNTESE PROCESSUAL</span><textarea class="tri-fx-sintese" value="{{ g.sintese }}" sc-camel-on-input="{{ g.onSintese }}" placeholder="Resumo do caso: pedido, sentença, recurso e o ponto controvertido…" aria-label="Síntese processual"></textarea></div>
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
                            <div class="tri-fx-ctrl"><sc-for list="{{ g.ctrls }}" as="cell"><div><div class="cab">{{ cell.col }}</div><dc-import name="Celula" kind="{{ cell.kind }}" value="{{ cell.value }}" options="{{ cell.options }}" checked="{{ cell.checked }}" chips="{{ cell.chips }}" tags="{{ cell.tags }}" auto="{{ cell.auto }}" manual="{{ cell.manual }}" on-text="{{ cell.onText }}" on-select="{{ cell.onSelect }}" on-check="{{ cell.onCheck }}" on-manual="{{ cell.onManual }}" on-tag-add="{{ cell.onTagAdd }}" hint-size="100%,38px"></dc-import></div></sc-for></div>
                          </div>
                        </sc-if>
                      </div>
                      <div class="tri-pcard-campos">
                        <sc-for list="{{ g.camposB }}" as="f"><div class="tri-pc-campo"><span>{{ f.col }}</span><b title="{{ f.val }}">{{ f.val }}</b></div></sc-for>
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
    const lista = escs.filter(e => filtro === "todos" || (filtro === "cheios" ? count.get(e.id) : !count.get(e.id)));
    const camposDados = [...new Set([...this.columnConfig.central, ...this.centralKnownColumns].map(centralColumn))]
      .filter(c => isVisibleColumn(c) && !WORK_COLUMNS.has(c) && !["Processo","processo","Assunto","Etiquetas","etiquetas","Etiquetas Originais","Etiquetas Operacionais","tarefa_atual","Tema","Especificidades","Síntese Processual","Dificuldade"].includes(c));
    const linha = r => ({ proc: r.Processo || "—", classe: txt(r.classe_judicial || r.Classe) || "—", assunto: txt(r.Assunto || r.assunto_judicial) || "—", tarefa: txt(r.tarefa_atual) || "—" });
    return {
      isTriagem: s.tab === "triagem",
      triTotal: all.length, triInEsc: all.filter(({r}) => escOf(r)).length, triSemEsc: all.filter(({r}) => !escOf(r)).length, triEscCount: escs.length,
      triSearch: s.triSearch || "", onTriSearch: e => self.setState({ triSearch: e.target.value }),
      triBandejaCount: count.get("") || 0,
      triFichas: bandeja.slice(0, LIM).map(({r}) => { const id = procId(r.Processo), sel = self.triSel.has(id); return { key: "f" + id, id, ...linha(r), sel, cls: sel ? "sel" : "",
        tags: this.sourceTags(r).slice(0, 3).map((t, k) => ({ key: k, label: t })),
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
      triVistaPlanCls: s.triVista === "planilha" ? "on" : "", triVistaCardsCls: s.triVista !== "planilha" ? "on" : "",
      triVerCards: () => self.setState({ triVista: "cards" }), triVerPlanilha: () => self.setState({ triVista: "planilha" }),
      triToggleConfig: () => self.setState({ triConfig: !s.triConfig }),
      triOpenCor: aberto ? aberto.cor : "#c3ccd6",
      triConfigResumo: aberto ? (txt(aberto.obs) ? "📝 " + String(aberto.obs).replace(/\s+/g, " ").trim() : "sem bilhete") : "",
      triOpenRows: aberto ? all.filter(({r}) => escOf(r) === aberto.id).map(({r, i}) => { const sit = self.situacao(r), pid = procId(r.Processo), aberta = self.triFaixa.has(pid);
        const campos = (() => { const vistos = new Set(); return camposDados.map(c => ({ key: c, col: c, val: txt(r[c]) })).filter(f => { if (!f.val) return false; const k = fieldKey(f.col) + "|" + canon(f.val), k2 = "v|" + canon(f.val) + "|" + canon(f.col).replace(/[^a-z]/g, "").slice(0, 6); if (vistos.has(k) || vistos.has(k2)) return false; vistos.add(k); vistos.add(k2); return true; }); })();
        let corte = campos.findIndex(f => /polo/.test(canon(f.col))); if (corte < 0) corte = campos.length;
        const etqs = self.sourceTags(r), temas = self.triLista(r, "Tema"), esps = self.triLista(r, "Especificidades"), cx = CX.find(c => c[0] === String(txt(r.Dificuldade)));
        const addKey = c => e => { if (e.key !== "Enter") return; e.preventDefault(); const v = e.target.value; e.target.value = ""; self.triAddItem(i, c, v); };
        const addBtn = c => e => { const inp = e.currentTarget.parentElement.querySelector("input"); const v = inp.value; inp.value = ""; self.triAddItem(i, c, v); };
        const plural = (n, s, p) => n + " " + (n === 1 ? s : p);
        let ctrls = [];
        if (aberta) { try { ctrls = self.preControllers(i).parts.map(c => ({ ...c, key: c.col })); if (!ctrls.some(c => /id da procura/.test(canon(c.col)))) ctrls.push({ ...self.cell(i, "ID da Procuração"), col: "ID DA PROCURAÇÃO", key: "idproc" }); } catch (err) { ctrls = ["Tempestividade","Impedimento / Suspeição","Preparo","Representação","ID da Procuração"].map(c => ({ ...self.cell(i, c), col: c.toUpperCase(), key: c })); } }
        const obsTxt = String(r["Observações"] || ""), poloA = txt(r.polo_ativo || r.Polo_Ativo) || "—", poloP = txt(r.polo_passivo || r.Polo_Passivo) || "—";
        return { key: "g" + pid, pid, ...linha(r), poloA, poloP, obsTxt, obsCount: obsTxt.split("\n").filter(l => l.trim()).length,
        temasTxt: temas.join(" · ") || "—", espsTxt: esps.join(" · ") || "—", destObs: pid + "|Observações",
        onObs: e => { r["Observações"] = e.target.value; self.saveDeb(); },
        abrirCard: () => { self.triFaixa.add(pid); self.setState({ triVista: "cards" }); setTimeout(() => { const n = document.querySelector(`[data-tri-card="${pid}"]`); n && n.scrollIntoView({ block: "start", behavior: "smooth" }); }, 60); },
        camposA: campos.slice(0, corte), camposB: campos.slice(corte),
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
        etiquetas: self.sourceTags(r).join(", ") || "—", situacao: sit.label, sitBg: sit.bg, sitFg: sit.fg,
        devolver: () => { r._escaninho = ""; salvar("Processo devolvido à bandeja."); },
        remover: () => { if (!window.confirm(`Remover ${r.Processo} da Triagem Processual? Ele continua no Acervo Central.`)) return; r._triagem = ""; r._escaninho = ""; salvar("Processo removido da triagem."); } }; }) : [],
      triOpenVazio: !!aberto && !(count.get(aberto.id) || 0),
      triDevolverTodos: () => { if (!aberto) return; const m = all.filter(({r}) => escOf(r) === aberto.id); m.forEach(({r}) => { r._escaninho = ""; }); salvar(`${m.length} processo(s) devolvido(s) à bandeja.`); },
      triExcluir: () => { if (!aberto) return; const n = count.get(aberto.id) || 0; if (!window.confirm(`Excluir o escaninho "${aberto.titulo}"?` + (n ? `\n\nOs ${n} processo(s) dele voltam para a bandeja.` : ""))) return; self.rows.forEach(r => { if (r._escaninho === aberto.id) r._escaninho = ""; }); self.escaninhos = self.escaninhos.filter(x => x.id !== aberto.id); self.setState({ triOpen: "" }); salvar(`Escaninho "${aberto.titulo}" excluído.`); },
      triRecolher: () => self.setState({ triOpen: "" })
    };
  }
'''


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
    # estilos
    ("    .central-stats-stack{display:grid;gap:14px;min-width:0}", CSS + "    .central-stats-stack{display:grid;gap:14px;min-width:0}"),
    # exportação: TEMAS (coluna Tema, cabeçalho "Temas"), ESPECIFICIDADES e SÍNTESE; etiquetas sem as convertidas e sem "Seção"
    ('"Status: Corrigido":"CORRIGIDO"};', '"Status: Corrigido":"CORRIGIDO","Temas":"Tema"};'),
    ("  addSheet(wb, name, cols, dataRows, accent) {\n    const data = this.exportRows(cols, dataRows);\n    const ws = XLSX.utils.json_to_sheet(data, { header: cols });",
     "  addSheet(wb, name, cols, dataRows, accent) {\n    cols = this.triColsExport(cols);\n    const data = this.exportRows(cols, dataRows);\n    const ws = XLSX.utils.json_to_sheet(data, { header: cols });\n    cols.forEach((c, j) => { const a = XLSX.utils.encode_cell({ r: 0, c: j }); if (c === \"Tema\" && ws[a]) ws[a].v = \"Temas\"; });"),
    ('        else o[c] = r[c] == null ? "" : r[c];\n      });\n      return o;',
     '        else if (fieldKey(c) === "etiquetas" || c === "Etiquetas Originais") o[c] = this.triEtqExport(r, r[c]);\n        else o[c] = r[c] == null ? "" : r[c];\n      });\n      return o;'),
]
