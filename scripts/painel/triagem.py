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
    .tri-band-lista{max-height:calc(100vh - 300px);min-height:220px;overflow:auto;padding:10px 12px 12px;display:grid;gap:8px;align-content:start}
    .tri-ficha{position:relative;display:grid;grid-template-columns:auto minmax(0,1fr);gap:9px;align-items:start;background:#fbfaf6;color:#1d2a38;border:1px solid #d9d4c7;border-radius:6px;padding:9px 10px 9px 10px;cursor:grab;box-shadow:0 1px 0 rgba(0,0,0,.04),0 3px 8px rgba(20,38,60,.06);transition:transform .15s,box-shadow .15s}
    .tri-ficha::before{content:"";position:absolute;left:0;top:8px;bottom:8px;width:3px;border-radius:0 3px 3px 0;background:#c9cfd8}
    .tri-ficha:hover{transform:translateY(-1px) rotate(-.3deg);box-shadow:0 6px 16px rgba(20,38,60,.12)}
    .tri-ficha.sel{outline:2px solid #d9a441;outline-offset:1px}.tri-ficha.sel::before{background:#d9a441}
    .tri-ficha .num{font:600 11.5px "IBM Plex Mono",ui-monospace,SFMono-Regular,Consolas,monospace;letter-spacing:-.02em}
    .tri-ficha .meta{font-size:11px;color:#56636f;margin-top:2px;line-height:1.35}
    .tri-tag{display:inline-block;font-size:9px;font-weight:850;letter-spacing:.03em;padding:2px 6px;border-radius:99px;background:#e9edf2;color:#33506e;margin:4px 4px 0 0}
    .tri-tag.ouro{background:#f7e7c4;color:#7a5512}
    .tri-band-pe{display:flex;gap:6px;align-items:center;justify-content:space-between;flex-wrap:wrap;padding:10px 12px;border-top:1px solid #e3e7ec;font-size:11px;color:#6d7b8a}
    .tri-movel{position:relative;border-radius:20px;padding:16px 16px 20px;background:linear-gradient(180deg,rgba(255,255,255,.06),transparent 30%),repeating-linear-gradient(90deg,rgba(255,255,255,.018) 0 2px,transparent 2px 9px),linear-gradient(160deg,#2a3f58,#1d2f45);box-shadow:inset 0 1px 0 rgba(255,255,255,.12),0 24px 50px rgba(20,38,60,.28);min-width:0}
    .tri-movel-topo{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;margin:0 2px 12px;color:#dbe6f2}
    .tri-placa-mestra{display:inline-flex;align-items:center;gap:10px;padding:7px 14px;border-radius:8px;background:linear-gradient(180deg,#e9c46a,#c9922f);color:#33240a;font-weight:900;font-size:11px;letter-spacing:.14em;box-shadow:inset 0 1px 0 rgba(255,255,255,.5),0 2px 0 rgba(0,0,0,.25)}
    .tri-placa-mestra i{width:6px;height:6px;border-radius:50%;background:#7a5512}
    .tri-filtro{border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.06);color:#dbe6f2;border-radius:99px;padding:5px 11px;font-size:10.5px;font-weight:800;cursor:pointer}
    .tri-filtro.on{background:#fff;color:#14304e;border-color:#fff}
    .tri-dica{margin:-4px 2px 12px;font-size:10.5px;color:#9fb3c9}
    .tri-dica b{color:#e9c46a}
    .tri-grade{display:grid;grid-template-columns:repeat(auto-fill,minmax(205px,1fr));gap:14px}
    .tri-nicho{position:relative;height:204px;border-radius:12px;border:0;padding:0;text-align:left;font:inherit;background:radial-gradient(120% 70% at 50% 0%,rgba(255,255,255,.07),transparent 60%),linear-gradient(180deg,#0f1c2c,#16263a 22%);box-shadow:inset 0 10px 18px rgba(0,0,0,.55),inset 0 -2px 0 rgba(255,255,255,.05),0 1px 0 rgba(255,255,255,.08);cursor:pointer;transition:transform .18s,box-shadow .18s;overflow:hidden}
    .tri-nicho:hover{transform:translateY(-2px)}
    .tri-nicho:focus-visible{outline:none;box-shadow:inset 0 10px 18px rgba(0,0,0,.55),0 0 0 3px #d9a441}
    .tri-nicho.alvo,.tri-nicho.pronto:hover{box-shadow:inset 0 10px 18px rgba(0,0,0,.55),0 0 0 3px #d9a441,0 0 28px rgba(217,164,65,.55)}
    .tri-nicho.aberto{box-shadow:inset 0 10px 18px rgba(0,0,0,.55),0 0 0 3px #fff}
    .tri-nicho.aberto::after{content:"";position:absolute;left:50%;bottom:-1px;margin-left:-9px;border:9px solid transparent;border-bottom-color:#eef3f8}
    .tri-pilha{position:absolute;left:18px;right:18px;bottom:62px;height:74px}
    .tri-folha{position:absolute;left:0;right:0;height:14px;border-radius:3px;background:#fbfaf6;border:1px solid #d9d4c7;box-shadow:0 1px 0 rgba(0,0,0,.25)}
    .tri-folha:nth-child(odd){transform:translateX(-2px) rotate(-.6deg)}.tri-folha:nth-child(3n){transform:translateX(3px) rotate(.7deg)}
    .tri-capa{position:absolute;left:-2px;right:-2px;height:16px;border-radius:3px 3px 2px 2px;box-shadow:inset 0 1px 0 rgba(255,255,255,.35),0 2px 3px rgba(0,0,0,.35)}
    .tri-capa::after{content:"";position:absolute;right:14px;top:-7px;width:34px;height:9px;border-radius:4px 4px 0 0;background:inherit;filter:brightness(1.1)}
    .tri-contador{position:absolute;top:12px;right:12px;min-width:30px;height:30px;padding:0 8px;border-radius:99px;display:grid;place-items:center;background:rgba(255,255,255,.1);color:#fff;font-weight:900;font-size:13px;border:1px solid rgba(255,255,255,.14)}
    .tri-vazio-nicho{position:absolute;left:0;right:0;top:92px;text-align:center;color:rgba(219,230,242,.45);font-size:11px;font-weight:700}
    .tri-placa{position:absolute;left:10px;right:10px;bottom:10px;height:44px;border-radius:6px;padding:6px 10px 5px 26px;background:linear-gradient(180deg,#f1d48a,#cf9c3a 55%,#b9852a);color:#3a2706;box-shadow:inset 0 1px 0 rgba(255,255,255,.6),inset 0 -1px 0 rgba(0,0,0,.18),0 3px 6px rgba(0,0,0,.4)}
    .tri-placa::before,.tri-placa::after{content:"";position:absolute;left:9px;width:6px;height:6px;border-radius:50%;background:radial-gradient(circle at 35% 35%,#fff3c8,#7a5512)}
    .tri-placa::before{top:8px}.tri-placa::after{bottom:8px}
    .tri-placa .t{display:block;font-weight:900;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .tri-placa .s{display:block;font-size:10px;font-weight:700;opacity:.78;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .tri-bilhete{position:absolute;top:10px;left:12px;max-width:62%;padding:6px 8px 7px;background:#fff4c2;color:#4a3d0f;font-size:9.5px;line-height:1.35;border-radius:2px;transform:rotate(-3deg);box-shadow:0 4px 10px rgba(0,0,0,.35);display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;white-space:pre-wrap}
    .tri-nicho.novo{display:grid;place-items:center;text-align:center;background:transparent;box-shadow:none;border:2px dashed rgba(219,230,242,.28);color:#dbe6f2}
    .tri-nicho.novo:hover{border-color:#d9a441;color:#d9a441}
    .tri-aberto{margin-top:16px;border-radius:14px;background:#eef3f8;color:#14263c;overflow:hidden;box-shadow:0 10px 26px rgba(0,0,0,.25);animation:triAbre .28s cubic-bezier(.2,.8,.2,1)}
    @keyframes triAbre{from{opacity:0;transform:translateY(-10px)}to{opacity:1;transform:none}}
    .tri-aberto-topo{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;padding:12px 14px;background:linear-gradient(180deg,#e2eaf3,#eef3f8);border-bottom:1px solid #d6e0ea}
    .tri-aberto-topo .tri-placa{position:relative;left:auto;right:auto;bottom:auto;height:auto;min-width:260px;max-width:520px;padding:8px 14px 7px 28px}
    .tri-aberto-topo .tri-placa .t{font-size:14.5px}.tri-aberto-topo .tri-placa .s{font-size:11px}
    .tri-aberto-corpo{display:grid;grid-template-columns:minmax(240px,.8fr) minmax(0,1.2fr);gap:16px;padding:14px}
    .tri-campo{display:grid;gap:4px;margin-bottom:9px}
    .tri-campo label{font-size:9px;font-weight:900;letter-spacing:.08em;color:#6d7b8a}
    .tri-campo input,.tri-campo textarea{width:100%;border:1px solid #d6e0ea;border-radius:9px;background:#fff;color:#14263c;padding:8px 10px;font:inherit;font-size:12.5px;outline:none}
    .tri-campo textarea{min-height:78px;resize:vertical;background:#fff4c2;border-color:#e8d78a;color:#4a3d0f}
    .tri-cor{width:22px;height:22px;border-radius:50%;border:2px solid transparent;box-shadow:inset 0 0 0 2px rgba(255,255,255,.6);cursor:pointer;padding:0}
    .tri-cor.on{border-color:#14263c}
    .tri-guardados{display:grid;gap:6px;max-height:360px;overflow:auto;align-content:start}
    .tri-guardado{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px;align-items:center;background:#fff;border:1px solid #dfe6ee;border-radius:9px;padding:8px 10px}
    .tri-guardado .num{font:600 12px "IBM Plex Mono",ui-monospace,SFMono-Regular,Consolas,monospace}
    .tri-guardado .meta{font-size:10.5px;color:#6d7b8a}
    .tri-icone{border:1px solid #dfe6ee;background:#fff;border-radius:7px;padding:3px 8px;font-size:12px;font-weight:900;cursor:pointer;color:#1f3d63}
    @media(max-width:1100px){.tri-grid{grid-template-columns:minmax(0,1fr)}.tri-bandeja{position:static}.tri-band-lista{max-height:340px}.tri-kpis{grid-template-columns:repeat(2,minmax(0,1fr))}.tri-aberto-corpo{grid-template-columns:minmax(0,1fr)}}
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
        <div class="tri-grid">
          <aside class="tri-bandeja" aria-label="Bandeja da triagem">
            <div class="tri-band-topo">
              <div style="display:flex;justify-content:space-between;align-items:center;gap:8px"><span style="font-size:12.5px;font-weight:900;letter-spacing:.06em;color:#14263c">BANDEJA DA TRIAGEM</span><span style="font-size:10px;font-weight:800;color:#6d7b8a">{{ triBandejaCount }} na bandeja</span></div>
              <input value="{{ triSearch }}" sc-camel-on-input="{{ onTriSearch }}" placeholder="Buscar processo, classe, assunto, tarefa…" aria-label="Buscar na bandeja">
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

          <section class="tri-movel" aria-label="Móvel de escaninhos">
            <div class="tri-movel-topo">
              <span class="tri-placa-mestra"><i></i>GABINETE A · ESCANINHOS<i></i></span>
              <span style="display:flex;gap:6px;flex-wrap:wrap"><sc-for list="{{ triFiltros }}" as="f"><button class="tri-filtro {{ f.cls }}" sc-camel-on-click="{{ f.pick }}">{{ f.label }}</button></sc-for></span>
            </div>
            <div class="tri-dica">{{ triDica }}</div>
            <div class="tri-grade">
              <sc-for list="{{ triEscaninhos }}" as="e" hint-placeholder-count="3">
                <button class="tri-nicho {{ e.cls }}" data-tri-esc="{{ e.key }}" sc-camel-on-click="{{ e.click }}" aria-label="{{ e.aria }}" title="{{ e.title }}">
                  <sc-if value="{{ e.hasObs }}"><span class="tri-bilhete">{{ e.obs }}</span></sc-if>
                  <span class="tri-contador">{{ e.count }}</span>
                  <span class="tri-pilha"><sc-for list="{{ e.layers }}" as="l"><span class="tri-folha" style="bottom:{{ l.b }}px"></span></sc-for><sc-if value="{{ e.hasCapa }}"><span class="tri-capa" style="background:{{ e.cor }};bottom:{{ e.capaB }}px"></span></sc-if></span>
                  <sc-if value="{{ e.vazio }}"><span class="tri-vazio-nicho">vazio · solte autos aqui</span></sc-if>
                  <span class="tri-placa"><span class="t">{{ e.titulo }}</span><span class="s">{{ e.subLabel }}</span></span>
                </button>
              </sc-for>
              <button class="tri-nicho novo" sc-camel-on-click="{{ newEscaninho }}"><span><span style="display:block;font-size:30px;line-height:1">+</span><span style="font-size:11px;font-weight:850;letter-spacing:.08em">NOVO ESCANINHO</span></span></button>
            </div>

            <sc-if value="{{ triHasOpen }}" hint-placeholder-val="{{ false }}">
              <div class="tri-aberto" aria-label="Escaninho aberto">
                <div class="tri-aberto-topo">
                  <span class="tri-placa"><span class="t">{{ triOpenTitulo }}</span><span class="s">{{ triOpenSub }}</span></span>
                  <span style="display:flex;gap:6px;flex-wrap:wrap"><button sc-camel-on-click="{{ triDevolverTodos }}" style="BTN_OURO">↩ Devolver todos à bandeja</button><button sc-camel-on-click="{{ triExcluir }}" style="BTN;color:#a64f35">Excluir escaninho</button><button sc-camel-on-click="{{ triRecolher }}" style="BTN">⌃ Recolher</button></span>
                </div>
                <div class="tri-aberto-corpo">
                  <div>
                    <div class="tri-campo"><label>TÍTULO DA PLACA</label><input value="{{ triOpenTitulo }}" sc-camel-on-input="{{ onTriTitulo }}" maxlength="70" aria-label="Título do escaninho"></div>
                    <div class="tri-campo"><label>SUBTÍTULO (OPCIONAL)</label><input value="{{ triOpenSubRaw }}" sc-camel-on-input="{{ onTriSub }}" maxlength="90" aria-label="Subtítulo do escaninho"></div>
                    <div class="tri-campo"><label>BILHETE · OBSERVAÇÃO</label><textarea value="{{ triOpenObs }}" sc-camel-on-input="{{ onTriObs }}" aria-label="Observação do escaninho"></textarea></div>
                    <div class="tri-campo"><label>COR DA PASTA</label><span style="display:flex;gap:7px;flex-wrap:wrap"><sc-for list="{{ triCores }}" as="c"><button class="tri-cor {{ c.cls }}" style="background:{{ c.cor }}" sc-camel-on-click="{{ c.pick }}" aria-label="Cor da pasta"></button></sc-for></span></div>
                    <div style="font-size:9.5px;color:#7e8b99">Criado em {{ triOpenCriado }} · alterações salvas automaticamente</div>
                  </div>
                  <div>
                    <div style="font-size:9px;font-weight:900;letter-spacing:.08em;color:#6d7b8a;margin-bottom:6px">PROCESSOS GUARDADOS · {{ triOpenCount }}</div>
                    <div class="tri-guardados">
                      <sc-for list="{{ triOpenRows }}" as="g" hint-placeholder-count="3">
                        <div class="tri-guardado"><div style="min-width:0"><div class="num">{{ g.proc }}</div><div class="meta">{{ g.classe }} · {{ g.assunto }} · {{ g.tarefa }}</div></div><span style="display:flex;gap:4px"><button class="tri-icone" sc-camel-on-click="{{ g.devolver }}" title="Devolver à bandeja">↩</button><button class="tri-icone" sc-camel-on-click="{{ g.remover }}" title="Remover da triagem (volta só ao acervo)" style="color:#a64f35">✕</button></span></div>
                      </sc-for>
                      <sc-if value="{{ triOpenVazio }}"><div style="padding:18px;text-align:center;color:#7e8b99;font-size:11.5px;border:1px dashed #c9d5e2;border-radius:9px">Escaninho vazio. Marque fichas na bandeja e clique neste escaninho — ou arraste-as até ele.</div></sc-if>
                    </div>
                  </div>
                </div>
              </div>
            </sc-if>
          </section>
        </div>
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
        key: e.id, titulo: e.titulo, subLabel: txt(e.subtitulo) || "—", obs: e.obs || "", hasObs: !!txt(e.obs), count: n, cor: e.cor, vazio: !n,
        layers: Array.from({ length: cam }, (_, k) => ({ key: k, b: k * 9 })), hasCapa: !!n, capaB: cam * 9,
        cls: [aberto && aberto.id === e.id ? "aberto" : "", marcados ? "pronto" : ""].join(" "),
        aria: `Escaninho ${e.titulo}, ${n} processo(s)`, title: marcados ? `Guardar ${marcados} ficha(s) aqui` : "Abrir escaninho",
        click: () => { if (self.triSel.size) self.triGuardar([...self.triSel], e.id); else self.setState({ triOpen: s.triOpen === e.id ? "" : e.id }); }
      }; }),
      newEscaninho: () => { const id = "esc_" + Date.now().toString(36) + Math.random().toString(36).slice(2, 6); self.escaninhos.push({ id, titulo: "Novo escaninho", subtitulo: "", obs: "", cor: PAL[self.escaninhos.length % PAL.length], criado: new Date().toISOString().slice(0,10) }); self.setState({ triOpen: id, triFiltro: "todos" }); salvar("Escaninho criado — dê um título à placa."); },
      triHasOpen: !!aberto,
      triOpenTitulo: aberto ? aberto.titulo : "", triOpenSubRaw: aberto ? aberto.subtitulo || "" : "", triOpenSub: aberto ? (txt(aberto.subtitulo) || "sem subtítulo") : "",
      triOpenObs: aberto ? aberto.obs || "" : "", triOpenCriado: aberto ? fmtD(aberto.criado) : "", triOpenCount: aberto ? count.get(aberto.id) || 0 : 0,
      onTriTitulo: e => { if (!aberto) return; aberto.titulo = e.target.value || "Sem título"; self.saveDeb(); self.refresh(); },
      onTriSub: e => { if (!aberto) return; aberto.subtitulo = e.target.value; self.saveDeb(); self.refresh(); },
      onTriObs: e => { if (!aberto) return; aberto.obs = e.target.value; self.saveDeb(); self.refresh(); },
      triCores: PAL.map(c => ({ key: c, cor: c, cls: aberto && aberto.cor === c ? "on" : "", pick: () => { if (!aberto) return; aberto.cor = c; self.saveDeb(); self.refresh(); } })),
      triOpenRows: aberto ? all.filter(({r}) => escOf(r) === aberto.id).map(({r}) => ({ key: "g" + procId(r.Processo), ...linha(r),
        devolver: () => { r._escaninho = ""; salvar("Processo devolvido à bandeja."); },
        remover: () => { if (!window.confirm(`Remover ${r.Processo} da Triagem Processual? Ele continua no Acervo Central.`)) return; r._triagem = ""; r._escaninho = ""; salvar("Processo removido da triagem."); } })) : [],
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
]
