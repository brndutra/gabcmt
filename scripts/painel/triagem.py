"""Triagem Processual — nova aba do Painel Central, no padrão da Seleção Prévia.

- No Acervo Central, o seletor de sessão destino ganha a opção "Triagem Processual": os processos marcados vão para a
  triagem (campo interno _triagem = data do encaminhamento), sem mexer em Seleção Prévia, sessão ou pauta.
- A aba lista os processos em triagem (busca, marcação, retirada) e organiza-os em ESCANINHOS: pastas com título,
  subtítulo opcional e observação (this.escaninhos, gravado junto com o restante do painel). Marca-se os processos e
  insere-se no escaninho escolhido (campo interno _escaninho = id do escaninho).
"""

TRI = "__triagem__"

CSS = """    .tri-page{display:grid;gap:14px;min-width:0}
    .tri-kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}
    .tri-kpi{border-radius:12px;background:#fff;border:1px solid #e3e7ec;padding:12px 14px;box-shadow:0 8px 20px rgba(20,38,60,.04)}
    .tri-kpi>span{display:block;font-size:9px;font-weight:850;letter-spacing:.07em;color:#7e8b99}
    .tri-kpi b{display:block;font-size:22px;font-weight:850;color:#14263c;margin-top:2px}
    .tri-grid{display:grid;grid-template-columns:300px minmax(0,1fr);gap:14px;align-items:start;min-width:0}
    .tri-escs{border-radius:14px;background:#fff;border:1px solid #e3e7ec;padding:14px;display:grid;gap:8px;position:sticky;top:12px;max-height:calc(100vh - 40px);overflow:auto}
    .tri-list{border-radius:14px;background:#fff;border:1px solid #e3e7ec;min-width:0;overflow:hidden}
    .tri-esc{display:block;width:100%;text-align:left;border:1px solid #e3e7ec;border-radius:10px;background:#fafbfc;padding:9px 10px;cursor:pointer;color:#14263c;font:inherit}
    .tri-esc:hover{border-color:#b7c6d6}
    .tri-esc.on{border-color:#1f3d63;background:#eef3f8;box-shadow:inset 3px 0 0 #1f3d63}
    .tri-form input,.tri-form textarea{width:100%;border:1px solid #d8dee5;border-radius:8px;background:#fff;padding:7px 9px;font:inherit;font-size:11.5px;color:#14263c;outline:none}
    .tri-form textarea{min-height:64px;resize:vertical}
    .tri-table{border-collapse:separate;border-spacing:0;width:100%;min-width:780px}
    @media(max-width:1100px){.tri-grid{grid-template-columns:minmax(0,1fr)}.tri-escs{position:static;max-height:none}.tri-kpis{grid-template-columns:repeat(2,minmax(0,1fr))}}
"""

BTN = "border:1px solid #d8dee5;border-radius:8px;background:#fff;color:#1f3d63;padding:7px 10px;font-size:10px;font-weight:850;cursor:pointer;white-space:nowrap"
BTN_PRI = "border:0;border-radius:8px;background:#1f3d63;color:#fff;padding:8px 12px;font-size:10px;font-weight:850;cursor:pointer;white-space:nowrap"
BTN_OURO = "border:0;border-radius:8px;background:#d9a441;color:#33240a;padding:8px 12px;font-size:10px;font-weight:900;cursor:pointer;white-space:nowrap"
TH = "position:sticky;top:0;z-index:1;background:#f4f6f9;color:#5c6a78;font-size:8.5px;font-weight:900;letter-spacing:.05em;text-align:left;padding:8px 9px;white-space:nowrap;border-bottom:1px solid #e3e7ec"
TD = "padding:8px 9px;border-bottom:1px solid #f0f2f5;font-size:10.5px;color:#3d4c5c;vertical-align:top"

MARKUP = f"""
    <sc-if value="{{{{ isTriagem }}}}" hint-placeholder-val="{{{{ false }}}}">
      <div class="tri-page">
        <div class="tri-kpis">
          <div class="tri-kpi"><span>EM TRIAGEM</span><b style="display:block;font-size:22px;font-weight:850;color:#14263c;margin-top:2px;line-height:1.2">{{{{ triTotal }}}}</b></div>
          <div class="tri-kpi"><span>EM ESCANINHOS</span><b style="display:block;font-size:22px;font-weight:850;color:#14263c;margin-top:2px;line-height:1.2">{{{{ triInEsc }}}}</b></div>
          <div class="tri-kpi"><span>SEM ESCANINHO</span><b style="display:block;font-size:22px;font-weight:850;color:#14263c;margin-top:2px;line-height:1.2">{{{{ triSemEsc }}}}</b></div>
          <div class="tri-kpi"><span>ESCANINHOS</span><b style="display:block;font-size:22px;font-weight:850;color:#14263c;margin-top:2px;line-height:1.2">{{{{ triEscCount }}}}</b></div>
        </div>
        <div class="tri-grid">
          <aside class="tri-escs" aria-label="Escaninhos">
            <div style="display:flex;align-items:center;justify-content:space-between;gap:8px">
              <div><div style="font-size:9.5px;font-weight:900;letter-spacing:.08em;color:#1f3d63">ESCANINHOS</div><div style="font-size:10px;color:#7e8b99;margin-top:2px">Pastas para guardar listas da triagem</div></div>
              <button sc-camel-on-click="{{{{ newEscaninho }}}}" style="{BTN_OURO}">+ NOVO</button>
            </div>
            <sc-if value="{{{{ triFormOpen }}}}" hint-placeholder-val="{{{{ false }}}}">
              <div class="tri-form" style="display:grid;gap:7px;border:1px solid #d9a441;border-radius:10px;background:#fffaf0;padding:10px">
                <div style="font-size:9.5px;font-weight:900;letter-spacing:.06em;color:#7a5512">{{{{ triFormLabel }}}}</div>
                <input value="{{{{ triFTitulo }}}}" sc-camel-on-input="{{{{ onTriFTitulo }}}}" placeholder="Título (obrigatório)" aria-label="Título do escaninho">
                <input value="{{{{ triFSub }}}}" sc-camel-on-input="{{{{ onTriFSub }}}}" placeholder="Subtítulo (opcional)" aria-label="Subtítulo do escaninho">
                <textarea value="{{{{ triFObs }}}}" sc-camel-on-input="{{{{ onTriFObs }}}}" placeholder="Observação" aria-label="Observação do escaninho"></textarea>
                <div style="display:flex;gap:6px;justify-content:flex-end"><button sc-camel-on-click="{{{{ cancelTriForm }}}}" style="{BTN}">CANCELAR</button><button sc-camel-on-click="{{{{ saveTriForm }}}}" style="{BTN_PRI}">SALVAR</button></div>
              </div>
            </sc-if>
            <sc-for list="{{{{ triFixedFilters }}}}" as="f" hint-placeholder-count="2">
              <button class="tri-esc {{{{ f.cls }}}}" sc-camel-on-click="{{{{ f.pick }}}}" style="display:flex;justify-content:space-between;align-items:center;gap:8px"><span style="font-size:11px;font-weight:800">{{{{ f.label }}}}</span><span style="border-radius:99px;background:#e8eef5;color:#33506e;padding:2px 8px;font-size:9.5px;font-weight:900">{{{{ f.count }}}}</span></button>
            </sc-for>
            <sc-for list="{{{{ triEscaninhos }}}}" as="e" hint-placeholder-count="2">
              <div class="tri-esc {{{{ e.cls }}}}" style="padding:0;overflow:hidden">
                <button sc-camel-on-click="{{{{ e.pick }}}}" title="Ver processos deste escaninho" style="display:block;width:100%;text-align:left;border:0;background:transparent;padding:9px 10px 6px;cursor:pointer;color:#14263c;font:inherit">
                  <span style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px"><span style="font-size:11.5px;font-weight:850;line-height:1.3">🗂 {{{{ e.titulo }}}}</span><span style="border-radius:99px;background:#1f3d63;color:#fff;padding:2px 8px;font-size:9.5px;font-weight:900">{{{{ e.count }}}}</span></span>
                  <sc-if value="{{{{ e.hasSub }}}}"><span style="display:block;font-size:10px;font-weight:700;color:#4c6480;margin-top:2px">{{{{ e.subtitulo }}}}</span></sc-if>
                  <sc-if value="{{{{ e.hasObs }}}}"><span style="display:block;font-size:10px;color:#7e8b99;margin-top:4px;line-height:1.4;white-space:pre-wrap">{{{{ e.obs }}}}</span></sc-if>
                </button>
                <div style="display:flex;justify-content:space-between;align-items:center;gap:6px;padding:0 10px 8px"><span style="font-size:9px;color:#98a4b0">criado em {{{{ e.criado }}}}</span><span style="display:flex;gap:4px"><button sc-camel-on-click="{{{{ e.edit }}}}" title="Editar escaninho" style="{BTN};padding:3px 7px">✎</button><button sc-camel-on-click="{{{{ e.remove }}}}" title="Excluir escaninho (os processos continuam na triagem)" style="{BTN};padding:3px 7px;color:#a64f35">×</button></span></div>
              </div>
            </sc-for>
            <sc-if value="{{{{ triNoEsc }}}}"><div style="font-size:10.5px;color:#7e8b99;line-height:1.5;padding:4px 2px">Nenhum escaninho ainda. Crie um em “+ NOVO”, marque processos na lista e use “INSERIR NO ESCANINHO”.</div></sc-if>
          </aside>
          <section class="tri-list">
            <div style="padding:12px 14px;border-bottom:1px solid #e3e7ec;display:grid;gap:9px">
              <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:10px;flex-wrap:wrap">
                <div style="min-width:0"><div style="font-size:14px;font-weight:850;color:#14263c">{{{{ triViewTitle }}}}</div><sc-if value="{{{{ triViewHasSub }}}}"><div style="font-size:11px;font-weight:700;color:#4c6480;margin-top:2px">{{{{ triViewSub }}}}</div></sc-if><sc-if value="{{{{ triViewHasObs }}}}"><div style="font-size:10.5px;color:#7e8b99;margin-top:4px;max-width:720px;white-space:pre-wrap">{{{{ triViewObs }}}}</div></sc-if></div>
                <input value="{{{{ triSearch }}}}" sc-camel-on-input="{{{{ onTriSearch }}}}" placeholder="Buscar processo, classe, assunto, tarefa, etiqueta…" style="flex:0 1 320px;min-width:200px;border:1px solid #d8dee5;border-radius:9px;background:#fafbfc;padding:8px 10px;font-size:11px;color:#14263c;outline:none">
              </div>
              <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap">
                <button sc-camel-on-click="{{{{ triSelectAll }}}}" title="Marcar todos os processos listados" style="{BTN}">☑ MARCAR LISTADOS</button>
                <button sc-camel-on-click="{{{{ triClearSel }}}}" title="Desmarcar" style="{BTN};color:{{{{ triClearFg }}}}">✕ {{{{ triSelCount }}}} MARCADO(S)</button>
                <span style="flex:1"></span>
                <div style="display:flex;align-items:stretch;border:1px solid #dee3e9;border-radius:9px;overflow:hidden;background:#fff">
                  <sc-raw-select value="{{{{ triTarget }}}}" sc-camel-on-change="{{{{ onTriTarget }}}}" title="Escaninho de destino" style="min-width:190px;border:0;background:#fafbfc;padding:8px;font-size:10px;font-weight:700;color:#14263c;outline:none;cursor:pointer">
                    <option value="">Escaninho de destino…</option>
                    <sc-for list="{{{{ triTargetOptions }}}}" as="o" hint-placeholder-count="2"><option value="{{{{ o.value }}}}">{{{{ o.label }}}}</option></sc-for>
                  </sc-raw-select>
                  <button sc-camel-on-click="{{{{ insertIntoEscaninho }}}}" style="border:0;background:#d9a441;color:#33240a;padding:8px 12px;font-size:9.5px;font-weight:900;cursor:pointer;white-space:nowrap">INSERIR NO ESCANINHO</button>
                </div>
                <button sc-camel-on-click="{{{{ removeFromEscaninho }}}}" title="Tirar os marcados do escaninho (continuam na triagem)" style="{BTN}">RETIRAR DO ESCANINHO</button>
                <button sc-camel-on-click="{{{{ removeFromTriagem }}}}" title="Devolver os marcados ao acervo (saem da triagem)" style="{BTN};color:#a64f35">REMOVER DA TRIAGEM</button>
              </div>
            </div>
            <div style="overflow:auto;max-height:70vh">
              <sc-raw-table class="tri-table">
                <sc-raw-thead><sc-raw-tr>
                  <sc-raw-th style="{TH};width:34px"></sc-raw-th><sc-raw-th style="{TH}">PROCESSO</sc-raw-th><sc-raw-th style="{TH}">CLASSE</sc-raw-th><sc-raw-th style="{TH}">ASSUNTO</sc-raw-th><sc-raw-th style="{TH}">TAREFA ATUAL</sc-raw-th><sc-raw-th style="{TH}">ETIQUETAS</sc-raw-th><sc-raw-th style="{TH}">ESCANINHO</sc-raw-th><sc-raw-th style="{TH}">NA TRIAGEM</sc-raw-th>
                </sc-raw-tr></sc-raw-thead>
                <sc-raw-tbody>
                  <sc-for list="{{{{ triRows }}}}" as="p" hint-placeholder-count="6">
                    <sc-raw-tr style="background:{{{{ p.bg }}}}">
                      <sc-raw-td style="{TD}"><input type="checkbox" checked="{{{{ p.sel }}}}" sc-camel-on-change="{{{{ p.toggle }}}}" aria-label="Marcar processo" style="width:15px;height:15px;accent-color:#1f3d63;cursor:pointer"></sc-raw-td>
                      <sc-raw-td style="{TD};white-space:nowrap;font-weight:850;color:#14263c">{{{{ p.proc }}}}</sc-raw-td>
                      <sc-raw-td style="{TD}">{{{{ p.classe }}}}</sc-raw-td>
                      <sc-raw-td style="{TD};max-width:260px">{{{{ p.assunto }}}}</sc-raw-td>
                      <sc-raw-td style="{TD};max-width:200px">{{{{ p.tarefa }}}}</sc-raw-td>
                      <sc-raw-td style="{TD};max-width:220px;color:#5c6a78">{{{{ p.tags }}}}</sc-raw-td>
                      <sc-raw-td style="{TD}"><sc-if value="{{{{ p.hasEsc }}}}"><span style="display:inline-block;border-radius:99px;background:#e8eef5;color:#1f3d63;padding:3px 8px;font-size:9.5px;font-weight:850;white-space:nowrap">🗂 {{{{ p.esc }}}}</span></sc-if><sc-if value="{{{{ !p.hasEsc }}}}"><span style="color:#98a4b0">—</span></sc-if></sc-raw-td>
                      <sc-raw-td style="{TD};white-space:nowrap">{{{{ p.desde }}}}</sc-raw-td>
                    </sc-raw-tr>
                  </sc-for>
                </sc-raw-tbody>
              </sc-raw-table>
              <sc-if value="{{{{ triEmpty }}}}"><div style="padding:36px;text-align:center;font-size:12px;font-weight:600;color:#7e8b99">{{{{ triEmptyMsg }}}}</div></sc-if>
              <sc-if value="{{{{ triTruncated }}}}"><div style="padding:10px 14px;font-size:10.5px;color:#7e8b99;border-top:1px solid #edf0f3">{{{{ triTruncMsg }}}}</div></sc-if>
            </div>
          </section>
        </div>
      </div>
    </sc-if>
"""

METODOS = r'''  triagemRows() { return this.rows.map((r,i)=>({r,i})).filter(({r})=>!!txt(r._triagem)); }
  sendToTriagem() {
    if (!this.selected.size) return this.notify("Selecione pelo menos um processo.", "warn");
    const hoje = new Date().toISOString().slice(0,10); let n = 0, ja = 0;
    this.rows.forEach(r => { if (this.selected.has(procId(r.Processo))) { if (txt(r._triagem)) ja++; else { r._triagem = hoje; n++; } } });
    this.selected.clear(); this.saveDB(); this.refresh();
    this.notify(`${n} processo(s) encaminhados à Triagem Processual` + (ja ? ` · ${ja} já estavam na triagem` : "") + ".");
  }
  triagemValues() {
    const s = this.state, self = this;
    if (!this.triSel) this.triSel = new Set();
    if (!Array.isArray(this.escaninhos)) this.escaninhos = [];
    const escs = this.escaninhos, ids = new Set(escs.map(e => e.id));
    const all = this.triagemRows();
    const escOf = r => ids.has(r._escaninho) ? r._escaninho : "";
    const count = new Map(); all.forEach(({r}) => { const k = escOf(r); count.set(k, (count.get(k) || 0) + 1); });
    const filt = s.triEsc === undefined ? "*" : s.triEsc, q = canon(s.triSearch || "");
    const fmtD = d => /^\d{4}-\d\d-\d\d/.test(d || "") ? d.slice(0,10).split("-").reverse().join("/") : "—";
    const list = all.filter(({r}) => (filt === "*" || escOf(r) === filt) && (!q || canon([r.Processo, r.classe_judicial || r.Classe, r.Assunto || r.assunto_judicial, r.tarefa_atual, this.sourceTags(r).join(" "), (escs.find(e => e.id === escOf(r)) || {}).titulo].join(" ")).includes(q)));
    const visiveis = new Set(all.map(({r}) => procId(r.Processo)));
    [...this.triSel].forEach(id => { if (!visiveis.has(id)) this.triSel.delete(id); });
    const cur = escs.find(e => e.id === filt), LIM = 500;
    const form = s.triForm || null;
    const marcados = () => all.filter(({r}) => self.triSel.has(procId(r.Processo)));
    const salvar = msg => { self.triSel.clear(); self.saveDB(); self.refresh(); if (msg) self.notify(msg); };
    const fixedStyle = k => filt === k ? "on" : "";
    return {
      isTriagem: s.tab === "triagem",
      triTotal: all.length, triInEsc: all.filter(({r}) => escOf(r)).length, triSemEsc: all.filter(({r}) => !escOf(r)).length, triEscCount: escs.length,
      triFixedFilters: [
        { key: "all", label: "Todos na triagem", count: all.length, cls: fixedStyle("*"), pick: () => self.setState({ triEsc: "*" }) },
        { key: "none", label: "Sem escaninho", count: count.get("") || 0, cls: fixedStyle(""), pick: () => self.setState({ triEsc: "" }) }
      ],
      triEscaninhos: escs.map(e => ({
        key: e.id, titulo: e.titulo, subtitulo: e.subtitulo || "", hasSub: !!txt(e.subtitulo), obs: e.obs || "", hasObs: !!txt(e.obs),
        count: count.get(e.id) || 0, criado: fmtD(e.criado), cls: filt === e.id ? "on" : "",
        pick: () => self.setState({ triEsc: e.id, triTarget: e.id }),
        edit: () => self.setState({ triForm: { id: e.id, titulo: e.titulo, subtitulo: e.subtitulo || "", obs: e.obs || "" } }),
        remove: () => {
          const n = count.get(e.id) || 0;
          if (!window.confirm(`Excluir o escaninho "${e.titulo}"?` + (n ? `\n\nOs ${n} processo(s) dele continuam na Triagem Processual, sem escaninho.` : ""))) return;
          self.escaninhos = self.escaninhos.filter(x => x.id !== e.id);
          self.rows.forEach(r => { if (r._escaninho === e.id) r._escaninho = ""; });
          self.setState({ triEsc: filt === e.id ? "*" : filt, triTarget: s.triTarget === e.id ? "" : s.triTarget });
          salvar(`Escaninho "${e.titulo}" excluído.`);
        }
      })),
      triNoEsc: !escs.length,
      triFormOpen: !!form, triFormLabel: form && form.id ? "EDITAR ESCANINHO" : "NOVO ESCANINHO",
      triFTitulo: form ? form.titulo : "", triFSub: form ? form.subtitulo : "", triFObs: form ? form.obs : "",
      onTriFTitulo: e => self.setState({ triForm: { ...self.state.triForm, titulo: e.target.value } }),
      onTriFSub: e => self.setState({ triForm: { ...self.state.triForm, subtitulo: e.target.value } }),
      onTriFObs: e => self.setState({ triForm: { ...self.state.triForm, obs: e.target.value } }),
      newEscaninho: () => self.setState({ triForm: { id: "", titulo: "", subtitulo: "", obs: "" } }),
      cancelTriForm: () => self.setState({ triForm: null }),
      saveTriForm: () => {
        const f = self.state.triForm || {}, titulo = txt(f.titulo);
        if (!titulo) return self.notify("Informe o título do escaninho.", "warn");
        if (f.id) { const e = self.escaninhos.find(x => x.id === f.id); if (e) Object.assign(e, { titulo, subtitulo: txt(f.subtitulo), obs: String(f.obs || "").trim() }); }
        else { const id = "esc_" + Date.now().toString(36) + Math.random().toString(36).slice(2, 6); self.escaninhos.push({ id, titulo, subtitulo: txt(f.subtitulo), obs: String(f.obs || "").trim(), criado: new Date().toISOString().slice(0,10) }); self.setState({ triTarget: id }); }
        self.setState({ triForm: null }); salvar(f.id ? `Escaninho "${titulo}" atualizado.` : `Escaninho "${titulo}" criado.`);
      },
      triViewTitle: filt === "*" ? "Todos os processos em triagem" : filt === "" ? "Sem escaninho" : cur ? "🗂 " + cur.titulo : "Todos os processos em triagem",
      triViewHasSub: !!(cur && txt(cur.subtitulo)), triViewSub: cur ? cur.subtitulo || "" : "",
      triViewHasObs: !!(cur && txt(cur.obs)), triViewObs: cur ? cur.obs || "" : "",
      triSearch: s.triSearch || "", onTriSearch: e => self.setState({ triSearch: e.target.value }),
      triSelCount: this.triSel.size, triClearFg: this.triSel.size ? "#c0454f" : "#98a4b0",
      triSelectAll: () => { list.forEach(({r}) => self.triSel.add(procId(r.Processo))); self.refresh(); },
      triClearSel: () => { self.triSel.clear(); self.refresh(); },
      triTarget: ids.has(s.triTarget) ? s.triTarget : "", onTriTarget: e => self.setState({ triTarget: e.target.value }),
      triTargetOptions: escs.map(e => ({ key: e.id, value: e.id, label: "🗂 " + e.titulo + (e.subtitulo ? " · " + e.subtitulo : "") })),
      insertIntoEscaninho: () => {
        const alvo = escs.find(e => e.id === s.triTarget);
        if (!alvo) return self.notify(escs.length ? "Escolha o escaninho de destino." : "Crie um escaninho primeiro (+ NOVO).", "warn");
        const m = marcados(); if (!m.length) return self.notify("Marque pelo menos um processo da triagem.", "warn");
        m.forEach(({r}) => { r._escaninho = alvo.id; });
        salvar(`${m.length} processo(s) inseridos no escaninho "${alvo.titulo}".`);
      },
      removeFromEscaninho: () => {
        const m = marcados().filter(({r}) => escOf(r)); if (!m.length) return self.notify("Nenhum processo marcado está em escaninho.", "warn");
        m.forEach(({r}) => { r._escaninho = ""; }); salvar(`${m.length} processo(s) retirados do escaninho (continuam na triagem).`);
      },
      removeFromTriagem: () => {
        const m = marcados(); if (!m.length) return self.notify("Marque pelo menos um processo da triagem.", "warn");
        if (!window.confirm(`Remover ${m.length} processo(s) da Triagem Processual? Eles continuam no Acervo Central.`)) return;
        m.forEach(({r}) => { r._triagem = ""; r._escaninho = ""; }); salvar(`${m.length} processo(s) removidos da triagem.`);
      },
      triRows: list.slice(0, LIM).map(({r}) => { const id = procId(r.Processo), e = escs.find(x => x.id === escOf(r)), sel = self.triSel.has(id); return {
        key: "t" + id, proc: r.Processo || "—", classe: txt(r.classe_judicial || r.Classe) || "—", assunto: txt(r.Assunto || r.assunto_judicial) || "—",
        tarefa: txt(r.tarefa_atual) || "—", tags: this.sourceTags(r).join(", ") || "—", hasEsc: !!e, esc: e ? e.titulo : "", desde: fmtD(r._triagem),
        sel, bg: sel ? "#f3f7fc" : "#fff", toggle: ev => { ev.target.checked ? self.triSel.add(id) : self.triSel.delete(id); self.refresh(); } }; }),
      triEmpty: !list.length,
      triEmptyMsg: !all.length ? "Nenhum processo na triagem. No Acervo Central, marque processos, escolha “Triagem Processual” no seletor de sessão destino e clique em ENCAMINHAR." : "Nenhum processo corresponde a esta pasta ou busca.",
      triTruncated: list.length > LIM, triTruncMsg: `Mostrando ${LIM} de ${list.length} processos — refine pela busca ou por escaninho. “Marcar listados” marca todos os ${list.length}.`
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
