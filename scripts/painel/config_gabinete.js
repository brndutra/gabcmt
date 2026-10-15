/* Configurações Globais › aba "Gabinete" (somente leitura).
 * Junta Calendário, Sessões, Servidores e Atribuições numa aba de consulta: esses dados vêm do repositório do
 * gabinete (o painel só lê). O botão "Atualizar conforme o repositório" relê o arquivo e reaplica no painel.
 * Exceção, fora daqui: início da produção, entrega das minutas e liberação, alterados na Seleção Prévia, são
 * gravados no repositório na hora. Roda dentro do iframe das Configurações Globais. */
(function () {
  "use strict";
  const ABAS = ["calendario", "sessoes", "team", "atribuicoes"];
  const root = () => parent.__painelCentralComponent, sinc = () => parent.__acervoGitHub && parent.__acervoGitHub.gabinete;
  const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const br = d => /^\d{4}-\d\d-\d\d/.test(d || "") ? d.slice(8, 10) + "/" + d.slice(5, 7) + "/" + d.slice(0, 4) : "—";
  const quando = iso => { try { return iso ? new Date(iso).toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" }) : "—"; } catch (e) { return iso; } };
  const DIAS = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"];
  let abertos = new Set(["sessoes", "servidores"]);

  const css = document.createElement("style");
  css.textContent = `
.gab-ro{display:grid;gap:14px;padding:4px 2px 30px}
.gab-card{background:#fff;border:1px solid #e3e7ec;border-radius:12px;box-shadow:0 8px 22px rgba(20,38,60,.05);overflow:hidden}
.gab-topo{display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap;padding:16px 18px;background:linear-gradient(135deg,#1f3d63,#16304e);color:#fff}
.gab-topo .k{font-size:10px;font-weight:900;letter-spacing:.1em;color:#e9c46a}.gab-topo h2{margin:3px 0 2px;font-size:18px;color:#fff}.gab-topo p{margin:0;font-size:11.5px;color:#cddbe8;max-width:760px;line-height:1.5}
.gab-btn{display:inline-flex;align-items:center;gap:7px;border:1px solid #d9a441;background:#d9a441;color:#33240a;border-radius:9px;padding:9px 14px;font:inherit;font-size:11.5px;font-weight:850;cursor:pointer;white-space:nowrap}
.gab-btn:disabled{opacity:.6;cursor:wait}
.gab-st{display:flex;gap:8px;flex-wrap:wrap;padding:10px 18px;border-top:1px solid rgba(255,255,255,.12);background:#16304e;color:#cddbe8;font-size:11px}
.gab-st b{color:#fff}.gab-st .err{color:#f3b4a5}
.gab-kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}
.gab-kpi{background:#fff;border:1px solid #e3e7ec;border-radius:11px;padding:11px 13px}.gab-kpi span{display:block;font-size:9px;font-weight:900;letter-spacing:.07em;color:#7e8b99}.gab-kpi b{display:block;font-size:22px;font-weight:850;color:#14263c;margin-top:2px}
.gab-sec>summary{list-style:none;display:flex;align-items:center;justify-content:space-between;gap:10px;padding:12px 16px;cursor:pointer;background:#f7f9fc;border-bottom:1px solid #e3e7ec}
.gab-sec>summary::-webkit-details-marker{display:none}
.gab-sec>summary h3{margin:0;font-size:13.5px;color:#14263c}.gab-sec>summary small{font-size:11px;color:#6d7b8a;font-weight:600}
.gab-sec>summary .seta{color:#6d7b8a;font-weight:900}
.gab-corpo{padding:12px 16px 16px}
.gab-tab{width:100%;border-collapse:collapse;font-size:12px}
.gab-tab th{text-align:left;font-size:9px;font-weight:900;letter-spacing:.06em;color:#5c6a78;background:#f4f6f9;padding:8px;border-bottom:1px solid #e3e7ec;text-transform:uppercase}
.gab-tab td{padding:8px;border-bottom:1px solid #eef1f4;color:#3d4c5c;vertical-align:top}
.gab-tab tr.passada td{opacity:.55}.gab-tab tr.proxima td{background:#fffaf0}
.gab-ed{display:inline-block;font-size:8.5px;font-weight:900;letter-spacing:.04em;color:#2f6b52;background:#e6f2ea;border-radius:99px;padding:1px 6px;margin-left:4px;vertical-align:middle}
.gab-chips{display:flex;gap:5px;flex-wrap:wrap}
.gab-chip{display:inline-flex;align-items:center;gap:5px;border-radius:99px;padding:4px 10px;font-size:11px;font-weight:750;background:#eef3f8;color:#33506e}
.gab-chip.off{background:#f4f6f9;color:#a4afba}.gab-chip.fer{background:#fdf2dc;color:#8a5a00}
.gab-serv{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:10px}
.gab-s{border:1px solid #e3e7ec;border-radius:10px;padding:10px 12px;background:#fbfcfd}
.gab-s .n{display:flex;align-items:center;gap:8px;font-weight:850;color:#14263c}.gab-s .n i{font-style:normal;font-size:10px;font-weight:700;color:#6d7b8a}
.gab-s .l{font-size:9px;font-weight:900;letter-spacing:.06em;color:#98a4b0;margin:8px 0 3px}
.gab-s .v{font-size:11.5px;color:#3d4c5c;line-height:1.45}
.gab-at{display:grid;gap:8px}
.gab-at details{border:1px solid #e3e7ec;border-radius:9px;background:#fbfcfd}
.gab-at summary{cursor:pointer;padding:9px 12px;font-weight:800;font-size:12px;color:#14263c}
.gab-at summary small{font-weight:650;color:#6d7b8a;margin-left:6px}
.gab-at p{margin:0;padding:0 12px 11px;font-size:11.5px;line-height:1.55;color:#3d4c5c;white-space:pre-line}
.gab-vazio{padding:14px;color:#7e8b99;font-size:12px}
@media(max-width:900px){.gab-kpis{grid-template-columns:repeat(2,minmax(0,1fr))}}`;
  document.head.appendChild(css);

  function desenhar(app) {
    const r = root(), g = sinc(); if (!r) return;
    const cfg = r.globalConfigSnapshot(), st = (g && g.estado) || {}, hoje = new Date().toISOString().slice(0, 10);
    const cal = cfg.workCalendar || { weekdays: [], excluded: [] }, membros = (cfg.team && cfg.team.members) || [], cat = (cfg.team && cfg.team.catalog) || [];
    const nomeFuncao = id => (cat.find(c => c.id === id) || {}).name || id;
    const sessoes = (cfg.sessions || []).map(s => ({ s, m: cfg.sessionDetails[s] || {} })).sort((a, b) => (a.m.date || "9999").localeCompare(b.m.date || "9999"));
    const prox = sessoes.find(x => x.m.date && x.m.date >= hoje);
    const content = document.getElementById("app-content"); if (!content) return;
    const sec = (id, titulo, sub, corpo) => `<details class="gab-card gab-sec" data-gab-sec="${id}" ${abertos.has(id) ? "open" : ""}><summary><span><h3>${titulo}</h3><small>${sub}</small></span><span class="seta">${abertos.has(id) ? "▾" : "▸"}</span></summary><div class="gab-corpo">${corpo}</div></details>`;
    const tabSessoes = sessoes.length ? `<table class="gab-tab"><thead><tr><th>Sessão</th><th>Julgamento</th><th>Pautar até</th><th>Início da produção</th><th>Entrega das minutas</th><th>Liberação</th><th>Gabinete</th></tr></thead><tbody>${sessoes.map(x => `<tr class="${x.m.date && x.m.date < hoje ? "passada" : x === prox ? "proxima" : ""}"><td><b>${esc(x.s)}</b>${x === prox ? ' <span class="gab-ed" style="background:#fdf2dc;color:#8a5a00">PRÓXIMA</span>' : ""}</td><td>${br(x.m.date)}</td><td>${br(x.m.pautaDeadline || x.m.deadline)}</td><td>${br(x.m.prepStart)}</td><td>${br(x.m.minutasDeadline)}</td><td>${br(x.m.releaseDeadline)}</td><td>${esc(x.m.gabinete || "—")}</td></tr>`).join("")}</tbody></table><p style="margin:10px 0 0;font-size:11px;color:#6d7b8a">Início da produção, entrega das minutas e liberação <span class="gab-ed">EDITÁVEIS NA SELEÇÃO PRÉVIA</span> — ao alterá-los lá, o repositório é atualizado na hora. Os demais dados só mudam no repositório.</p>` : `<div class="gab-vazio">Nenhuma sessão no repositório.</div>`;
    const tabCal = `<div style="display:grid;gap:10px"><div><div style="font-size:9px;font-weight:900;letter-spacing:.06em;color:#98a4b0;margin-bottom:5px">DIAS DE EXPEDIENTE</div><div class="gab-chips">${DIAS.map((d, k) => `<span class="gab-chip ${cal.weekdays.includes(k) ? "" : "off"}">${d}</span>`).join("")}</div></div>
      <div><div style="font-size:9px;font-weight:900;letter-spacing:.06em;color:#98a4b0;margin-bottom:5px">DIAS SEM EXPEDIENTE · FERIADOS E FOLGAS (${cal.excluded.length})</div><div class="gab-chips">${cal.excluded.slice().sort().map(d => `<span class="gab-chip fer">${br(d)}</span>`).join("") || '<span class="gab-vazio" style="padding:0">Nenhum.</span>'}</div></div></div>`;
    const tabServ = membros.length ? `<div class="gab-serv">${membros.map(m => { const aus = (m.absences || []).filter(a => (a.to || a.end || "") >= hoje); const esp = m.specializations && typeof m.specializations === "object" ? Object.entries(m.specializations).filter(([, v]) => v && (v === true || (Array.isArray(v) ? v.length : String(v).trim()))).map(([k, v]) => Array.isArray(v) ? `${k}: ${v.join(", ")}` : v === true ? k : `${k}: ${v}`) : [];
      const escopos = (m.minutaScopes || []).map(s => [s.docType, s.specificity, s.subjectId && ((cfg.team.subjects || []).find(x => x.id === s.subjectId) || {}).name].filter(Boolean).join(" · ")).filter(Boolean);
      return `<div class="gab-s"><div class="n">${esc(m.name)} <i>${esc(m.hierarchy || "")}</i></div>
        <div class="l">ATRIBUIÇÕES</div><div class="v">${(m.functions || []).map(f => `<span class="gab-chip" style="margin:0 4px 4px 0">${esc(nomeFuncao(f))}</span>`).join("") || "—"}</div>
        ${esp.length ? `<div class="l">ESPECIALIDADES</div><div class="v">${esc(esp.join(" · "))}</div>` : ""}
        ${escopos.length ? `<div class="l">ESCOPO DAS MINUTAS</div><div class="v">${esc(escopos.join(" · "))}</div>` : ""}
        <div class="l">AUSÊNCIAS PREVISTAS</div><div class="v">${aus.map(a => `${br(a.from || a.start)} a ${br(a.to || a.end)}`).join(" · ") || "nenhuma"}</div></div>`; }).join("")}</div>` : `<div class="gab-vazio">Nenhum servidor no repositório.</div>`;
    const tabAt = cat.length ? `<div class="gab-at">${cat.map(c => `<details><summary>${esc(c.name)}<small>${esc(c.group || "")} · ${membros.filter(m => (m.functions || []).includes(c.id)).map(m => m.name).join(", ") || "sem servidor"}</small></summary><p>${esc(c.atribuicoes || c.description || "")}</p></details>`).join("")}</div>` : `<div class="gab-vazio">Nenhuma atribuição no repositório.</div>`;
    content.innerHTML = `<div class="gab-ro">
      <section class="gab-card"><div class="gab-topo"><div><div class="k">GABINETE · FONTE ÚNICA</div><h2>Sessões, calendário e equipe</h2><p>Estes dados vêm do repositório do gabinete e aqui são apenas consultados. Para mudar uma sessão, o calendário, um servidor ou uma atribuição, edite o repositório e clique em “Atualizar conforme o repositório”.</p></div>
        <button class="gab-btn" data-gab="atualizar" ${st.enviando ? "disabled" : ""}>⟳ Atualizar conforme o repositório</button></div>
        <div class="gab-st">${st.erro ? `<span class="err">Sem leitura: ${esc(st.erro)}</span>` : `<span>Versão do repositório: <b>${esc(quando(st.versao))}</b></span><span>· lida em <b>${esc(quando(st.lidoEm))}</b></span>`}${st.pendente && st.pendente.length ? `<span>· <b>${st.pendente.length}</b> marco(s) aguardando gravação</span>` : ""}</div></section>
      <div class="gab-kpis"><div class="gab-kpi"><span>SESSÕES</span><b>${sessoes.length}</b></div><div class="gab-kpi"><span>PRÓXIMA SESSÃO</span><b style="font-size:16px;padding-top:4px">${prox ? br(prox.m.date) : "—"}</b></div><div class="gab-kpi"><span>SERVIDORES</span><b>${membros.length}</b></div><div class="gab-kpi"><span>DIAS SEM EXPEDIENTE</span><b>${cal.excluded.length}</b></div></div>
      ${sec("sessoes", "Sessões de julgamento", `${sessoes.length} sessões · marcos e prazos`, tabSessoes)}
      ${sec("calendario", "Calendário de trabalho", "expediente, feriados e folgas", tabCal)}
      ${sec("servidores", "Servidores", `${membros.length} servidores · atribuições, especialidades e ausências`, tabServ)}
      ${sec("atribuicoes", "Atribuições", `${cat.length} atribuições do gabinete`, tabAt)}
    </div>`;
  }
  document.addEventListener("click", async e => {
    const b = e.target.closest && e.target.closest('[data-gab="atualizar"]'); if (!b) return;
    const g = sinc(); if (!g) return; b.disabled = true; b.textContent = "Atualizando…";
    await g.puxar(false); const app = window.PautaApp; if (app) { app.state.tab = "gabinete"; app.renderConfig(); }
  });
  document.addEventListener("toggle", e => { const d = e.target; if (d.dataset && d.dataset.gabSec) { d.open ? abertos.add(d.dataset.gabSec) : abertos.delete(d.dataset.gabSec); const s = d.querySelector(".seta"); if (s) s.textContent = d.open ? "▾" : "▸"; } }, true);

  function instalar(app) {
    const P = Object.getPrototypeOf(app); if (P.__gabInstalado) return; P.__gabInstalado = true;
    const orig = P.renderConfig;
    P.renderConfig = function () {
      const quer = this.state.tab, nossa = !quer || quer === "gabinete" || quer === "settings" || ABAS.includes(quer);
      if (nossa) this.state.tab = "calendario";
      orig.call(this);
      const nav = document.getElementById("cfg-tabs");
      if (nav) {
        nav.querySelectorAll("[data-cfg-tab]").forEach(b => { if (ABAS.includes(b.dataset.cfgTab)) b.remove(); });
        if (!nav.querySelector('[data-cfg-tab="gabinete"]')) nav.insertAdjacentHTML("afterbegin", `<button type="button" class="cfg-tab" data-cfg-tab="gabinete" title="Sessões, calendário, servidores e atribuições — vindos do repositório (somente leitura)">Gabinete <b>⟳</b></button>`);
      }
      if (nossa) { this.state.tab = "gabinete"; desenhar(this); }
      if (nav) nav.querySelectorAll("[data-cfg-tab]").forEach(b => { const on = b.dataset.cfgTab === this.state.tab; b.classList.toggle("is-on", on); b.setAttribute("aria-current", String(on)); });
      const sub = document.getElementById("app-subtitle"); if (sub && nossa) sub.textContent = "Sessões, calendário e equipe vêm do repositório do gabinete; aqui, somente consulta.";
    };
    if (app._configModalOpen) app.renderConfig();
  }
  const espera = setInterval(() => { const app = window.PautaApp; if (app && typeof app.renderConfig === "function") { clearInterval(espera); instalar(app); } }, 80);
  // depois de atualizar pelo repositório, a aba se redesenha com os dados novos
  window.__gabRedesenhar = () => { const app = window.PautaApp; if (app && app.state.tab === "gabinete") desenhar(app); };
})();
