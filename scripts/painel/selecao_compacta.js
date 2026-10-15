/* Seleção Prévia · painel compacto (layout da prévia aplicado aos dados reais).
 *
 * Roda dentro da página da Seleção Prévia (iframe #pre-integrated-frame). Lê e grava pelo Painel Central
 * (parent.__preParentHost) com os mesmos caminhos da visão clássica: preCommit, cell(...).onSelect,
 * preReviewChange, removeFromPre, reorderPre e as funções de pauta de window.PautaControl.
 *
 * Estrutura: [cabeçalho da sessão] [planejamento (iframe original, recolhível)] [barra de comando + conteúdo]
 * [visão clássica (#controle-pauta-root), oculta no modo compacto e acessível pelo botão "Visão clássica"].
 */
(function () {
  "use strict";
  const P = () => window.__preParentHost || parent.__painelCentralComponent, H = () => window.__preHost, PC = () => window.PautaControl;
  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const txt = v => String(v ?? "").trim();
  const yes = v => /^(sim|s|true|1|x|ok)$/i.test(txt(v));
  const iso = v => { const s = txt(v); let m = s.match(/^(\d{4})-(\d\d)-(\d\d)/); if (m) return m[0]; m = s.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/); return m ? `${m[3]}-${m[2].padStart(2, "0")}-${m[1].padStart(2, "0")}` : ""; };
  const br = d => d ? d.slice(8, 10) + "/" + d.slice(5, 7) : "—";
  const brFull = d => d ? d.slice(8, 10) + "/" + d.slice(5, 7) + "/" + d.slice(0, 4) : "";
  const hoje = () => { const d = new Date(); return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10); };
  const addDia = (d, n) => { const x = new Date(d + "T12:00:00Z"); x.setUTCDate(x.getUTCDate() + n); return x.toISOString().slice(0, 10); };
  const norm = v => txt(v).normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  const PAL = ["#2f6690", "#7a5ba6", "#3d8b9c", "#a6545e", "#4a8f74", "#b4763a", "#6b7d2f", "#5b6f8f", "#c0843d", "#46708a"];
  const ETAPAS = [["Selecionado", "#98a4b0"], ["Designado", "#33506e"], ["Minutado", "#7a5ba6"]];
  const CX = [["Ω", "Padrão", "#2f8a5e"], ["A", "Intermediário", "#e3a21a"], ["Σ", "Complexo", "#cf4b3b"]];
  const OPC = {
    Tempestividade: ["Não Verificado", "Tempestivo", "Intempestivo"],
    Preparo: ["Não Verificado", "Comprovado", "Não Recolhido", "Dispensado", "Não se Aplica"],
    "Representação": ["Não Verificado", "Regular", "Negativo"],
    MPF: ["Não se Aplica", "Com Parecer", "Sem Parecer"],
    "Sentença - Decisão": ["Procedente", "Parcialmente procedente", "Improcedente", "Extinção sem resolução do mérito", "Homologatória", "Outra"],
    "Voto - Resultado": ["Dar provimento", "Dar parcial provimento", "Negar provimento", "Não conhecer", "Anular a sentença", "Extinguir sem resolução do mérito", "Prejudicado"],
    "Voto - Honorários": ["Majorar (art. 85, § 11, CPC)", "Manter", "Inverter", "Fixar", "Redistribuir", "Sem honorários recursais", "Não se aplica"],
    Status: ["PENDENTE", "PAUTADO", "ADIADO", "RETIRADO DE PAUTA", "JULGADO"]
  };
  const REV = [["Rev - Ementa", "Ementa"], ["Rev - Subementa", "Subementa"], ["Rev - IDs", "IDs"], ["Rev - Mérito", "Mérito"], ["Rev - Honorários", "Honorários"], ["Rev - Atenção", "Atenção"], ["CORRIGIDO", "Corrigido"]];

  const st = { visao: "lista", busca: "", etapa: null, serv: null, secao: null, alerta: false, aberto: null, aba: "id", sel: new Set(), plano: false, assin: "",
    avancada: false, status: null, criterios: [], tags: [], lote: null, modoBusca: "texto", loteTexto: "", fcol: "Assunto", fop: "contains", fcombine: "any", fvals: new Set(), fvalBusca: "", ftrechos: "",
    cap: true, asof: "" };
  let arrastando = false;
  try { const u = H() && H().uiPref("sp2", null); if (u) Object.assign(st, { visao: u.visao || "lista", plano: !!u.plano, cap: u.cap !== false, avancada: !!u.avancada }); } catch (e) {}
  const lembrar = () => { try { H().setUiPref("sp2", { visao: st.visao, plano: st.plano, cap: st.cap, avancada: st.avancada, modo: modo() }); } catch (e) {} };
  const modo = () => { try { return (H().uiPref("sp2", {}) || {}).modo === "classico" ? "classico" : "compacto"; } catch (e) { return "compacto"; } };
  let modoAtual = "compacto";

  // ------------------------------------------------------------------ dados
  const sessao = () => P().normalizeSelectionSession();
  const linhas = () => P().selectionSessionRows(sessao());
  const etapa = r => iso(r.MINUTADO) ? 2 : txt(r.SERVIDOR) ? 1 : 0;
  const compl = r => { const n = Math.round(Number(r.Dificuldade)); return n >= 1 && n <= 3 ? n : 0; };
  const reg = r => ({
    t: r.Tempestividade === "Tempestivo" ? "ok" : r.Tempestividade === "Intempestivo" ? "ruim" : "pend",
    p: ["Comprovado", "Dispensado", "Não se Aplica"].includes(r.Preparo) ? "ok" : r.Preparo === "Não Recolhido" ? "ruim" : "pend",
    r: r["Representação"] === "Regular" ? "ok" : r["Representação"] === "Negativo" ? "ruim" : "pend",
    m: ["Com Parecer", "Não se Aplica"].includes(r.MPF) ? "ok" : "pend"
  });
  const temAlerta = r => Object.values(reg(r)).some(v => v !== "ok");
  const secao = r => { try { return txt(P().secaoCompetente(r)) || txt(r["Seção Competente"]) || "Sem seção"; } catch (e) { return txt(r["Seção Competente"]) || "Sem seção"; } };
  const nomes = rows => [...new Set([...(P().names || []), ...rows.map(x => txt(x.r.SERVIDOR))].filter(Boolean))].sort((a, b) => a.localeCompare(b, "pt-BR"));
  const corDe = (n, todos) => n ? PAL[Math.max(0, todos.indexOf(n)) % PAL.length] : "#c3ccd6";
  const ini = n => n ? n.trim().slice(0, 2).toUpperCase() : "—";
  const porDia = x => x === null || x === undefined || !isFinite(x) ? "—" : x <= 0 ? "0" : x < .5 ? "1 a cada " + Math.round(1 / x) + " d" : String(Math.round(x * 10) / 10).replace(".", ",") + "/dia";
  function equipe(s, rows) {
    const m = P().sessionDetails[s] || {}, sim = (m.planningSimulation || {}).staff || [], todos = nomes(rows);
    const removidos = new Set((m.planningSimulation || {}).removed || []);
    return todos.filter(n => !removidos.has(n)).map(name => {
      const incl = Array.isArray(m.planningStaff) ? m.planningStaff.includes(name) : (P().teamProfile && P().teamProfile(name)?.functions?.minutar) !== false;
      const salvo = sim.find(x => x.name === name) || {};
      const rate = Math.max(0, Number(m.staffRates?.[name] ?? salvo.rate ?? 3) || 0);
      const aus = String(m.staffExcluded?.[name] || "").split(/[\n;,]+/).map(iso).filter(Boolean);
      return { name, incl, rate, aus, cargas: rows.filter(x => txt(x.r.SERVIDOR) === name).length };
    });
  }
  function diasUteis(a, b, aus = [], nome = "") {
    if (!a || !b) return null; if (a > b) return 0;
    const cal = P().selectionCalendar(); let n = 0;
    for (let d = a, k = 0; d <= b && k < 3660; d = addDia(d, 1), k++) {
      const wd = new Date(d + "T12:00:00Z").getUTCDay();
      if (cal.weekdays.includes(wd) && !cal.excluded.includes(d) && !aus.includes(d) && !(nome && P().teamAbsent && P().teamAbsent(nome, d))) n++;
    }
    return n;
  }
  // colunas do construtor de critérios (equivalentes às do Acervo Central, com os campos da Seleção Prévia)
  const tagsDe = r => { try { return P().allTags(r) || []; } catch (e) { return []; } };
  const statusDe = r => txt(r["Status de Julgamento"]) || "PENDENTE";
  const COLS = [["Processo", r => r.Processo], ["Assunto", r => r.Assunto || r.assunto_judicial], ["Tema", r => r.Tema], ["Seção competente", r => secao(r)], ["Classe", r => r.classe_judicial || r.Classe],
    ["Tarefa atual", r => r.tarefa_atual], ["META", r => r.META], ["Etiquetas", r => tagsDe(r).join(", ")], ["Servidor", r => r.SERVIDOR], ["Corretor", r => r.CORRETOR], ["Etapa", r => ETAPAS[etapa(r)][0]],
    ["Complexidade", r => compl(r) ? CX[compl(r) - 1][1] : ""], ["Tempestividade", r => r.Tempestividade], ["Preparo", r => r.Preparo], ["Representação", r => r["Representação"]], ["MPF", r => r.MPF],
    ["Sentença - Decisão", r => r["Sentença - Decisão"]], ["Voto - Resultado", r => r["Voto - Resultado"]], ["Voto - Honorários", r => r["Voto - Honorários"]], ["Status de Julgamento", statusDe],
    ["Item (Pauta de Julgamento)", r => r["Item (Pauta de Julgamento)"]], ["Observações", r => r.Observações], ["Intercorrências", r => r.Intercorrências], ["Data de distribuição", r => r["data_distribuição"] || r["Data_Distribuição"]],
    ["Polo ativo", r => r.polo_ativo || r.Polo_Ativo], ["Polo passivo", r => r.polo_passivo || r.Polo_Passivo], ["Último movimento", r => r.ultimo_movimento || r["Última_Movimentação"]]];
  const colFn = c => (COLS.find(x => x[0] === c) || [c, r => r[c]])[1];
  const valoresDe = (c, r) => { if (c === "Etiquetas") return tagsDe(r); const v = txt(colFn(c)(r)); if (c === "Tema" || c === "Observações" || c === "Intercorrências") return v.split("\n").map(txt).filter(Boolean); return v ? [v] : []; };
  const textoLinha = r => norm([...COLS.map(([, f]) => f(r)), r.Processo].join(" "));
  function casa(cr, r) {
    if (cr.col === "__busca__") return cr.itens.every(it => textoLinha(r).includes(norm(it.v)));
    const vs = valoresDe(cr.col, r);
    if (cr.op === "notempty") return vs.length > 0; if (cr.op === "empty") return !vs.length;
    if (!cr.itens.length) return true;
    const t = it => it.exato || cr.op === "equals" ? vs.some(v => norm(v) === norm(it.v)) : vs.some(v => norm(v).includes(norm(it.v)));
    return cr.combine === "all" ? cr.itens.every(t) : cr.itens.some(t);
  }
  const rotuloCrit = cr => cr.col === "__busca__" ? `busca · “${cr.itens.map(i => i.v).join(" + ")}”` : `${cr.col} ${{ contains: "contém", equals: "=", notempty: "não vazio", empty: "vazio" }[cr.op]}${cr.itens.length ? " " + cr.itens.map(i => i.v).join(cr.combine === "all" ? " E " : " OU ") : ""}`;
  function filtrados(rows, pular) {
    const q = norm(st.busca);
    return rows.filter(({ r }) => (st.etapa === null || etapa(r) === st.etapa) && (!st.serv || (st.serv === "—" ? !txt(r.SERVIDOR) : txt(r.SERVIDOR) === st.serv)) && (!st.secao || secao(r) === st.secao) && (!st.alerta || temAlerta(r))
      && (pular === "status" || !st.status || statusDe(r) === st.status)
      && (!st.lote || st.lote.has(String(r.Processo).replace(/\D/g, "")))
      && st.criterios.every(cr => casa(cr, r))
      && st.tags.every(tg => tagsDe(r).some(a => norm(a) === norm(tg)))
      && (!q || textoLinha(r).includes(q)));
  }
  const filtrosAtivos = () => st.etapa !== null || st.serv || st.secao || st.alerta || st.busca || st.status || st.lote || st.criterios.length || st.tags.length;
  const limparFiltros = () => Object.assign(st, { etapa: null, serv: null, secao: null, alerta: false, busca: "", status: null, lote: null, criterios: [], tags: [], fvals: new Set(), ftrechos: "", loteTexto: "" });
  const salvar = () => { P().saveDeb(); P().refresh(); render(); };

  // ------------------------------------------------------------------ montagem
  let raiz, cab, cap, corpo, barraClassica;
  function montar() {
    const classico = document.getElementById("controle-pauta-root"), plano = document.getElementById("selection-planning-frame");
    if (!classico || !plano || !P() || !H() || !PC()) return false;
    if (document.getElementById("sp2-cab")) return true;
    cab = document.createElement("section"); cab.id = "sp2-cab"; cab.className = "sp2 sp-card sp-sessao"; cab.setAttribute("aria-label", "Sessão");
    cap = document.createElement("section"); cap.id = "sp2-cap"; cap.className = "sp2 sp-card sp-cap"; cap.setAttribute("aria-label", "Capacidade e distribuição por servidor");
    corpo = document.createElement("div"); corpo.id = "sp2-corpo"; corpo.className = "sp2";
    barraClassica = document.createElement("div"); barraClassica.id = "sp2-classica"; barraClassica.className = "sp2 sp-classica";
    barraClassica.innerHTML = `<span><b>Visão clássica</b> · planilha e cards completos da Seleção Prévia</span><button class="sp-btn sp-pri" data-sp="modo-compacto">☰ Voltar ao painel compacto</button>`;
    plano.before(barraClassica); plano.before(cab); plano.before(cap); plano.after(corpo);
    document.addEventListener("click", clique); document.addEventListener("change", mudanca); document.addEventListener("input", digitacao);
    document.addEventListener("keydown", e => { if (e.key === "Enter" && e.target && e.target.id === "sp-busca") { e.preventDefault(); incluirBusca(); } });
    document.addEventListener("keydown", e => { if (e.key === "Escape" && document.querySelector(".sp-menu.on")) document.querySelector(".sp-menu.on").classList.remove("on"); });
    arrastar();
    aplicarModo(modo());
    return true;
  }
  function aplicarModo(m) {
    modoAtual = m;
    const classico = document.getElementById("controle-pauta-root"), plano = document.getElementById("selection-planning-frame");
    const c = m === "compacto";
    cab.hidden = !c; cap.hidden = !c; corpo.hidden = !c; barraClassica.hidden = c;
    if (classico) classico.style.display = c ? "none" : "";
    if (plano) plano.style.display = !c || st.plano ? "block" : "none";
    if (c) render();
  }

  // ------------------------------------------------------------------ desenho
  let assinatura = "";
  function assinar() {
    const s = sessao(), rows = linhas();
    return JSON.stringify([s, P().upcomingSessions(true), P().sessionDetails[s], P().names, P().selectionCalendar(), rows.map(({ r, i }) => [i, r.Processo, r.SERVIDOR, r.MINUTADO, r.Dificuldade, r.Tempestividade, r.Preparo, r["Representação"], r.MPF, r["Voto - Resultado"], r["Status de Julgamento"], r._preOrder, r.Assunto, r.Tema, r.META, r.CORRETOR, r.CORRIGIDO])]);
  }
  const chaveFoco = el => { if (!el || !el.dataset) return null; for (const k of ["campo", "cap", "capd", "spIn"]) if (el.dataset[k] !== undefined) return `[data-${k.replace(/[A-Z]/g, c => "-" + c.toLowerCase())}="${CSS.escape(el.dataset[k])}"]` + (el.dataset.i !== undefined ? `[data-i="${el.dataset.i}"]` : "") + (el.dataset.name !== undefined ? `[data-name="${CSS.escape(el.dataset.name)}"]` : ""); return el.id ? "#" + CSS.escape(el.id) : null; };
  const emEdicao = () => { const a = document.activeElement; return !!(a && [cab, cap, corpo].some(x => x && x.contains(a)) && a.matches("input,textarea,select")); };
  function render() {
    if (!cab || modoAtual !== "compacto") return;
    const a = document.activeElement, chave = a && [cab, cap, corpo].some(x => x && x.contains(a)) ? chaveFoco(a) : null, pos = a && "selectionStart" in a ? (() => { try { return a.selectionStart; } catch (e) { return null; } })() : null;
    const rolagem = window.scrollY;
    assinatura = assinar();
    const s = sessao(), rows = linhas(), todos = nomes(rows), m = P().sessionDetails[s] || {};
    const mapa = new Map(rows.map((x, k) => [x.i, k + 1]));
    desenharCab(s, rows, todos, m);
    desenharCap(s, rows, todos, m);
    desenharCorpo(s, rows, todos, mapa);
    if (chave) { const n = document.querySelector(chave); if (n) { n.focus({ preventScroll: true }); if (pos !== null) try { n.setSelectionRange(pos, pos); } catch (e) {} } }
    if (Math.abs(window.scrollY - rolagem) > 2) window.scrollTo(0, rolagem);
  }
  function desenharCab(s, rows, todos, m) {
    const sessoes = P().upcomingSessions(true), d = iso(m.date);
    const mk = [["PAUTAR ATÉ", iso(m.pautaDeadline || m.deadline)], ["INÍCIO PRODUÇÃO", iso(m.prepStart)], ["ENTREGA MINUTAS", iso(m.minutasDeadline)], ["LIBERAÇÃO", iso(m.releaseDeadline)], ["JULGAMENTO", d]];
    const gaps = ["preparo", "produção", "revisão", "anteced."];
    const hj = hoje();
    const marcos = mk.map(([l, v], k) => (k ? (() => { const p = mk[k - 1][1], n = p && v && v >= p ? diasUteis(addDia(p, 1), v) : null; return `<div class="sp-entre ${k === 2 ? "prod" : ""}"><i>${n === null ? "—" : n + " út."}${k === 2 && n !== null ? " de produção" : ""}</i></div>`; })() : "")
      + `<div class="sp-marco ${v && v < hj ? "passou" : ""}"><span>${l}</span><b>${br(v)}</b></div>`).join("");
    // indicadores (mesmas regras do simulador 02)
    const eq = equipe(s, rows), ativos = eq.filter(x => x.incl);
    const total = rows.length, des = rows.filter(x => txt(x.r.SERVIDOR)).length, livres = total - des;
    const ini0 = iso(m.prepStart), fim = iso(m.minutasDeadline), de = ini0 && ini0 > hj ? ini0 : hj;
    const dias = fim ? diasUteis(de, fim) : null;
    const cap = fim ? ativos.filter(x => x.rate > 0).reduce((a, x) => a + (diasUteis(de, fim, x.aus, x.name) || 0) * x.rate, 0) : null;
    const cargas = ativos.map(x => x.cargas);
    const kp = (l, v, h, c = "", t = "") => `<div class="sp-kpi ${c}" ${t ? `title="${esc(t)}"` : ""}><span>${l}</span><b>${v}</b><small>${h}</small></div>`;
    const kpis = kp("Total da sessão", total, "processos")
      + kp("Designados", des, total ? Math.round(des / total * 100) + "% da sessão" : "—")
      + kp("Sem designação", livres, livres > 0 && ativos.length ? "+" + Math.ceil(livres / ativos.length) + " p/ cada um" : livres > 0 ? "sem servidores ativos" : "tudo designado")
      + kp("Dias úteis", dias === null ? "—" : dias, dias === null ? "defina a entrega" : ini0 && ini0 > hj ? "do início à entrega" : "de hoje à entrega")
      + kp("Meta da equipe", dias ? porDia(total / dias) : "—", "total ÷ dias úteis")
      + kp("Meta por servidor", dias && ativos.length ? porDia(total / dias / ativos.length) : "—", ativos.length + " servidor(es) ativo(s)")
      + kp("Capacidade no ritmo", cap === null ? "—" : Math.round(cap) + " · " + total, cap === null ? "defina a entrega" : cap >= total ? "folga de " + Math.round(cap - total) : "faltam " + Math.round(total - cap), cap === null ? "" : cap >= total ? "ok" : "ruim", "Ritmo habitual × dias úteis de cada servidor ativo, contra o total da sessão")
      + kp("Equilíbrio", cargas.length ? Math.min(...cargas) + "–" + Math.max(...cargas) : "—", cargas.length ? "média " + String(Math.round(cargas.reduce((a, b) => a + b, 0) / cargas.length * 10) / 10).replace(".", ",") + " por servidor" : "menor–maior carga");
    const base = Math.max(total, 1);
    const dist = todos.map(n => { const a = rows.filter(x => txt(x.r.SERVIDOR) === n).length; if (!a) return ""; const w = a / base * 100; return `<i style="width:${w}%;background:${corDe(n, todos)}" title="${esc(n)}: ${a} processo(s) · ${Math.round(a / base * 100)}%">${w > 7 ? esc(n.split(/\s+/)[0]) + " " + a : w > 3 ? a : ""}</i>`; }).join("")
      + (livres > 0 ? `<i class="sp-livre" style="width:${livres / base * 100}%" title="Sem designação: ${livres}">${livres / base > .06 ? "livres " + livres : ""}</i>` : "");
    const esteira = ETAPAS.map(([l, c], k) => { const n = rows.filter(x => etapa(x.r) === k).length, acum = rows.filter(x => etapa(x.r) >= k).length, pct = total ? Math.round(acum / total * 100) : 0; return `<button class="sp-etapa ${st.etapa === k ? "on" : ""}" data-sp="etapa" data-v="${k}" title="${pct}% da sessão já passou por esta etapa · clique para filtrar"><span class="pct">${pct}%</span><div class="n">${n}</div><div class="l">${l.toUpperCase()}</div><div class="barra"><i style="width:${pct}%;background:${c}"></i></div></button>`; }).join("");
    const semServ = rows.filter(x => !txt(x.r.SERVIDOR)).length, irreg = rows.filter(x => Object.values(reg(x.r)).includes("ruim")).length, pend = rows.filter(x => Object.values(reg(x.r)).includes("pend")).length, semVoto = rows.filter(x => etapa(x.r) === 2 && !txt(x.r["Voto - Resultado"])).length, minut = rows.filter(x => etapa(x.r) === 2).length;
    const alertas = [semServ ? `<button class="sp-al a" data-sp="serv" data-v="—">● ${semServ} sem servidor</button>` : "", irreg ? `<button class="sp-al p" data-sp="alerta">● ${irreg} com irregularidade</button>` : "", pend ? `<button class="sp-al a" data-sp="alerta">● ${pend} com verificação pendente</button>` : "", semVoto ? `<span class="sp-al a">● ${semVoto} minutado(s) sem resultado do voto</span>` : "", `<span class="sp-al o">✓ ${minut} minutado(s)</span>`].join("");
    cab.innerHTML = `<div class="sp-sessao-topo"><div><div class="sp-eyebrow">Seleção Prévia</div><h1>${esc(s)}${d ? ` <small>· julgamento ${brFull(d)}</small>` : ""}</h1></div>
        <div class="sp-abas-sessao">${sessoes.map(x => { const dd = iso((P().sessionDetails[x] || {}).date); return `<button class="sp-aba-s ${x === s ? "on" : ""}" data-sp="sessao" data-v="${esc(x)}"><b>${dd ? brFull(dd) : esc(x)}</b><span>${esc(x)} · ${P().selectionSessionRows(x).length} proc.</span></button>`; }).join("") || `<span class="sp-vazio">Nenhuma sessão futura com processos selecionados.</span>`}</div></div>
      <div class="sp-marcos" aria-label="Marcos da sessão">${marcos}<button class="sp-abrir" data-sp="plano" aria-expanded="${st.plano}" title="Marcos editáveis e simulador de designação">Planejamento ${st.plano ? "▴" : "▾"}</button></div>
      <div class="sp-distrib" aria-label="Distribuição dos processos por servidor"><div class="sp-kpis">${kpis}</div><div class="sp-dist">${dist || `<i class="sp-livre" style="width:100%">sem processos</i>`}</div></div>
      <div class="sp-esteira" aria-label="Esteira do trabalho — clique numa etapa para filtrar">${esteira}</div>
      <div class="sp-alertas">${alertas}</div>`;
  }
  // ------------------------------------------------------------------ capacidade e distribuição por servidor
  const fmt = n => new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 1 }).format(n);
  function desenharCap(s, rows, todos, m) {
    const hj = hoje(), asof = st.asof || hj, ini0 = iso(m.prepStart), fim = iso(m.minutasDeadline), cal = P().selectionCalendar();
    const usados = todos.filter(n => rows.some(x => txt(x.r.SERVIDOR) === n)).sort((a, b) => rows.filter(x => txt(x.r.SERVIDOR) === b).length - rows.filter(x => txt(x.r.SERVIDOR) === a).length || a.localeCompare(b, "pt-BR"));
    const livres = rows.filter(x => !txt(x.r.SERVIDOR)).length, eq = equipe(s, rows);
    const uteis = ini0 && fim ? diasUteis(ini0, fim) : null, comeco = asof > ini0 ? asof : ini0;
    let soma = 0, capT = 0, demT = 0;
    const linhasCap = usados.map(name => {
      const n = rows.filter(x => txt(x.r.SERVIDOR) === name).length, e = eq.find(z => z.name === name) || { aus: [], rate: 3 };
      const rate = Number(m.staffRates?.[name] ?? e.rate ?? 3), disp = Number(m.staffAvailability?.[name] ?? 100), esf = Number(m.staffEffort?.[name] ?? 1);
      const full = ini0 && fim ? diasUteis(ini0, fim, e.aus, name) : null, rest = ini0 && fim ? diasUteis(comeco, fim, e.aus, name) : null;
      const effDays = full === null ? null : full * disp / 100, effRem = rest === null ? null : rest * disp / 100, capacidade = effDays === null ? null : effDays * rate, demanda = n * esf;
      const folga = capacidade === null ? null : capacidade - demanda, occ = capacidade ? demanda / capacidade * 100 : capacidade === 0 ? Infinity : null, meta = effDays ? n / effDays : null;
      soma += n; demT += demanda; capT += capacidade || 0;
      return `<tr><td><span class="sp-cap-nome"><span class="sp-av" style="background:${corDe(name, todos)}">${ini(name)}</span><b>${esc(name)}</b></span></td><td><b>${n}</b></td>
        <td><input type="number" min="0" max="50" step="0.25" data-cap="rate" data-name="${esc(name)}" value="${rate}" aria-label="Capacidade diária de ${esc(name)}"></td>
        <td><input type="number" min="0" max="100" step="5" data-cap="disp" data-name="${esc(name)}" value="${disp}" aria-label="Disponibilidade de ${esc(name)}"></td>
        <td><input type="number" min="0.1" max="5" step="0.1" data-cap="esf" data-name="${esc(name)}" value="${esf}" aria-label="Esforço médio de ${esc(name)}"></td>
        <td><div class="sp-cap-dias">${full === null ? `<span class="mut">defina início e entrega</span>` : `<span><b>${full}</b> úteis</span><span>${fmt(effDays)} totais</span><span>${fmt(effRem)} restantes</span><span class="${folga < 0 ? "ruim" : "bom"}">${folga < 0 ? "Déficit" : "Folga"} ${fmt(Math.abs(folga))} un.</span>`}</div></td>
        <td><b>${meta === null ? "—" : fmt(meta)}</b></td><td><span class="sp-cap-pct ${occ === null ? "" : occ > 100 ? "ruim" : occ <= 85 ? "bom" : "med"}">${occ === null ? "—" : isFinite(occ) ? fmt(occ) + "%" : "sem capacidade"}</span></td></tr>`;
    }).join("") + (livres ? `<tr class="sp-cap-livre"><td><span class="sp-cap-nome"><span class="sp-av" style="background:#c3ccd6">—</span><b>A DEFINIR</b></span></td><td><b>${livres}</b></td><td colspan="4" class="mut">sem servidor designado — designe na lista ou em lote para entrar na capacidade</td><td>—</td><td>—</td></tr>` : "");
    const occT = capT ? demT / capT * 100 : null;
    const fe = (k, v, rot, tipo = "date", extra = "") => `<label>${rot}<input type="${tipo}" data-capd="${k}" value="${esc(v)}" ${extra}></label>`;
    cap.innerHTML = `<div class="sp-cap-topo"><button class="sp-cap-tit" data-sp="cap" aria-expanded="${st.cap}"><span aria-hidden="true">${st.cap ? "▾" : "▸"}</span> Capacidade e distribuição por servidor <small>· ${esc(m.date ? brFull(iso(m.date)) : s)}</small></button>
        <span class="sp-cap-chips"><span class="sp-cap-chip">Processos <b>${rows.length}</b></span><span class="sp-cap-chip">Dias úteis <b>${uteis === null ? "—" : uteis}</b></span><span class="sp-cap-chip ${occT === null ? "" : occT > 100 ? "ruim" : occT <= 85 ? "bom" : "med"}">Ocupação <b>${occT === null ? "—" : fmt(occT) + "%"}</b></span></span></div>
      ${st.cap ? `<div class="sp-cap-barra">${fe("prepStart", ini0, "Início da preparação")}${fe("minutasDeadline", fim, "Entrega das minutas")}${fe("asof", asof, "Referência")}${fe("holidays", cal.excluded.map(d => d.split("-").reverse().join("/")).join(", ") || "nenhum", "Dias sem expediente", "text", `readonly class="sp-ro" title="Calendário do gabinete: vem do repositório (Configurações › Gabinete)"`)}<span class="grow"></span><button class="sp-btn" data-sp="cap-restaurar" title="Volta capacidade 3/dia, disponibilidade 100% e esforço 1,0 para os servidores desta sessão">Restaurar</button></div>
      <div class="sp-cap-wrap"><table class="sp-cap-tab"><thead><tr><th>Servidor</th><th>Processos</th><th>Capac./dia<br><span>editável</span></th><th>Disponib.<br><span>% editável</span></th><th>Esforço<br><span>médio editável</span></th><th>Dias de trabalho · folga/déficit</th><th>Meta<br>minutas/dia</th><th>Ocupação<br>estimada</th></tr></thead>
        <tbody>${linhasCap || `<tr><td colspan="8" class="mut" style="text-align:center;padding:16px">Nenhum processo designado nesta sessão.</td></tr>`}</tbody>
        <tfoot><tr><td>TOTAL</td><td>${soma}${livres ? ` <span class="mut">+${livres} a definir</span>` : ""}</td><td colspan="3" class="mut">Capacidade total: ${fmt(capT)} un.</td><td>${uteis === null ? "—" : `<span class="${demT > capT ? "ruim" : "bom"}">${demT > capT ? "Déficit" : "Folga"} ${fmt(Math.abs(capT - demT))} un.</span>`}</td><td>—</td><td>${occT === null ? "—" : fmt(occT) + "%"}</td></tr></tfoot></table></div>
      <p class="sp-cap-nota"><b>Dias:</b> úteis do período (calendário e ausências do servidor) · dias equivalentes de trabalho (úteis × disponibilidade) · dias equivalentes restantes a partir da referência. <b>Folga/déficit:</b> capacidade em unidades de esforço menos a demanda ponderada. <b>Ocupação:</b> demanda ponderada ÷ capacidade estimada. <b>Esforço médio</b> é premissa (1,0 = minuta padrão). Capacidade diária é o mesmo ritmo habitual do simulador do Planejamento.</p>` : ""}`;
  }
  const regIcon = r => { const g = reg(r); return [["t", "T", "Tempestividade"], ["p", "P", "Preparo"], ["r", "R", "Representação"], ["m", "M", "MPF"]].map(([k, l, n]) => `<i class="${g[k]}" title="${n}: ${g[k] === "ok" ? "regular" : g[k] === "ruim" ? "irregular" : "não verificado"}">${l}</i>`).join(""); };
  const sel = (campo, i, val, ops, extra = "") => `<select data-campo="${esc(campo)}" data-i="${i}" ${extra}>${[...new Set(["", ...ops, txt(val)])].map(o => `<option value="${esc(o)}" ${o === txt(val) ? "selected" : ""}>${esc(o || "—")}</option>`).join("")}</select>`;
  const inp = (campo, i, val, ph = "") => `<input type="text" data-campo="${esc(campo)}" data-i="${i}" value="${esc(val)}" placeholder="${esc(ph)}">`;
  const area = (campo, i, val, ph = "") => `<textarea data-campo="${esc(campo)}" data-i="${i}" placeholder="${esc(ph)}">${esc(val)}</textarea>`;
  const campo = (rot, html, cls = "") => `<div class="sp-campo ${cls}"><label>${rot}</label>${html}</div>`;
  function detalhe(x, todos) {
    const { r, i } = x, g = reg(r), s = sessao();
    const abas = [["id", "Identificação"], ["elab", "Elaboração e revisão"], ["reg", "Regularidade", Object.values(g).filter(v => v !== "ok").length], ["aleg", "Alegações e contrarrazões"], ["voto", "Voto"], ["julg", "Julgamento e histórico"]];
    const hist = (Array.isArray(r._pautaHistory) ? r._pautaHistory : []).slice(-6).reverse().map(h => `<li><b>${esc(brFull(String(h.at || "").slice(0, 10)))}</b> · ${esc(h.action || "")}${h.session ? " · " + esc(h.session) : ""}${h.status ? " · " + esc(h.status) : ""}</li>`).join("");
    const corpoAba = {
      id: `<div class="sp-grade">${campo("ASSUNTO CNJ", inp("Assunto", i, r.Assunto || r.assunto_judicial), "l2")}${campo("SEÇÃO COMPETENTE", `<input type="text" value="${esc(secao(r))}" disabled>`)}${campo("TEMA", inp("Tema", i, r.Tema))}
        ${campo("COMPLEXIDADE", `<div class="sp-cx">${CX.map(([s1, n, c], k) => `<button class="${compl(r) === k + 1 ? "on" : ""}" data-sp="cx" data-i="${i}" data-v="${k + 1}" title="${n}"><i style="background:${c}">${s1}</i>${n}</button>`).join("")}</div>`, "l2")}
        ${campo("META", inp("META", i, r.META))}${campo("ITEM OFICIAL DA PAUTA", inp("Item (Pauta de Julgamento)", i, r["Item (Pauta de Julgamento)"], "opcional · até 3 dígitos"))}</div>`,
      elab: `<div class="sp-grade">${campo("SERVIDOR", sel("SERVIDOR", i, r.SERVIDOR, todos))}${campo("DATA DA MINUTA", `<input type="date" data-campo="MINUTADO" data-i="${i}" value="${esc(iso(r.MINUTADO))}" max="${hoje()}">`)}${campo("CORRETOR", sel("CORRETOR", i, r.CORRETOR, todos))}${campo("ETAPA", `<input type="text" value="${ETAPAS[etapa(r)][0]}" disabled title="Definida pelo servidor e pela data da minuta">`)}
        ${campo("REVISÃO", `<div class="sp-checks">${REV.map(([f, l]) => `<label class="sp-check"><input type="checkbox" data-rev="${esc(f)}" data-i="${i}" ${yes(r[f]) ? "checked" : ""}> ${l}</label>`).join("")}</div>`, "l4")}</div>`,
      reg: `<div class="sp-grade">${campo("TEMPESTIVIDADE", sel("Tempestividade", i, r.Tempestividade, OPC.Tempestividade))}${campo("PREPARO", sel("Preparo", i, r.Preparo, OPC.Preparo))}${campo("REPRESENTAÇÃO", sel("Representação", i, r["Representação"], OPC["Representação"]))}${campo("ID DA PROCURAÇÃO", inp("ID da Procuração", i, r["ID da Procuração"]))}
        ${campo("MPF", sel("MPF", i, r.MPF, OPC.MPF))}${campo("ID DO PARECER MPF", inp("ID do Parecer MPF", i, r["ID do Parecer MPF"]))}${campo("OBSERVAÇÕES", area("Observações", i, r.Observações), "l2")}${campo("INTERCORRÊNCIAS (UMA POR LINHA)", area("Intercorrências", i, r.Intercorrências), "l2")}</div>`,
      aleg: `<div class="sp-grade">${campo("SENTENÇA · DECISÃO", sel("Sentença - Decisão", i, r["Sentença - Decisão"], OPC["Sentença - Decisão"]), "l2")}${campo("HONORÁRIOS DA SENTENÇA", inp("Sentença - Honorários", i, r["Sentença - Honorários"], "ex.: 10% sobre as parcelas vencidas"), "l2")}
        ${campo("ALEGAÇÕES DO RECURSO", area("Descrição das Alegações", i, r["Descrição das Alegações"], "Resumo das alegações do recurso"), "l2")}${campo("CONTRARRAZÕES", `<label class="sp-check" style="margin-bottom:6px"><input type="checkbox" data-chk="Contrarrazões Ausentes" data-i="${i}" ${yes(r["Contrarrazões Ausentes"]) ? "checked" : ""}> Não tem contrarrazões</label>` + area("Descrição das Contrarrazões", i, r["Descrição das Contrarrazões"], "Resumo das contrarrazões"), "l2")}</div>`,
      voto: `<div class="sp-grade">${campo("RESULTADO", sel("Voto - Resultado", i, r["Voto - Resultado"], OPC["Voto - Resultado"]))}${campo("HONORÁRIOS RECURSAIS", sel("Voto - Honorários", i, r["Voto - Honorários"], OPC["Voto - Honorários"]))}${campo("TÓPICO-SÍNTESE", inp("Tópico-síntese", i, r["Tópico-síntese"]), "l2")}${campo("FUNDAMENTOS E DISPOSITIVO", area("Voto - Descrição", i, r["Voto - Descrição"], "Resumo do voto"), "l4")}</div>`,
      julg: `<div class="sp-grade">${campo("STATUS", sel("__status", i, r["Status de Julgamento"] || "PENDENTE", OPC.Status))}${campo("SESSÃO DESTINO", sel("Sessão Destino", i, r["Sessão Destino"], P().upcomingSessions(false)))}${campo("ITEM OFICIAL", inp("Item (Pauta de Julgamento)", i, r["Item (Pauta de Julgamento)"]))}${campo("REMOVER", `<button class="sp-btn" data-sp="remover1" data-i="${i}" style="color:#a64f35">Remover da seleção</button>`)}
        ${campo("HISTÓRICO", hist ? `<ul class="sp-hist">${hist}</ul>` : `<div class="sp-dica" style="margin:0">Sem registros de histórico.</div>`, "l4")}</div>`
    };
    return `<div class="sp-detalhe"><div class="sp-abas">${abas.map(([k, l, b]) => `<button class="${st.aba === k ? "on" : ""}" data-sp="aba" data-v="${k}">${l}${b ? `<span class="b">${b}</span>` : ""}</button>`).join("")}</div>${corpoAba[st.aba] || corpoAba.id}<div class="sp-dica">Alterações gravadas na hora, nos mesmos campos da visão clássica. Alegações em tópicos, mídias e demais controles: “Visão clássica”.</div></div>`;
  }
  function desenharCorpo(s, rows, todos, mapa) {
    const fs = filtrados(rows), cont = f => rows.filter(f).length;
    const secoes = [...new Set(rows.map(x => secao(x.r)))].sort((a, b) => a.localeCompare(b, "pt-BR"));
    const ativos = filtrosAtivos();
    const chips = `<span class="rot">SERVIDOR</span>${[...todos.filter(n => rows.some(x => txt(x.r.SERVIDOR) === n)), "—"].map(n => `<button class="sp-chip ${st.serv === n ? "on" : ""}" data-sp="serv" data-v="${esc(n)}"><span class="sp-av" style="width:15px;height:15px;font-size:7px;background:${n === "—" ? "#c3ccd6" : corDe(n, todos)}">${n === "—" ? "" : ini(n)}</span>${n === "—" ? "sem servidor" : esc(n)}<small>${cont(x => n === "—" ? !txt(x.r.SERVIDOR) : txt(x.r.SERVIDOR) === n)}</small></button>`).join("")}
      <span class="rot" style="margin-left:8px">SEÇÃO</span>${secoes.map(c => `<button class="sp-chip ${st.secao === c ? "on" : ""}" data-sp="secao" data-v="${esc(c)}">${esc(c)}<small>${cont(x => secao(x.r) === c)}</small></button>`).join("")}
      <button class="sp-chip ${st.alerta ? "on" : ""}" data-sp="alerta">⚠ com alertas<small>${cont(x => temAlerta(x.r))}</small></button>${ativos ? `<button class="sp-chip" data-sp="limpar" style="border-style:dashed">✕ limpar filtros</button>` : ""}`;
    const n = st.sel.size, nCrit = st.criterios.length + st.tags.length + (st.lote ? 1 : 0) + (st.status ? 1 : 0);
    // faixa expansível: ferramentas de busca e filtro do Acervo Central, adaptadas à Seleção Prévia
    let faixa = "";
    const ativosHtml = [...st.criterios.map((cr, k) => `<button class="sp-crit" data-sp="rm-crit" data-v="${k}" title="Remover critério">${esc(rotuloCrit(cr))} ×</button>`), ...st.tags.map((tg, k) => `<button class="sp-crit tag" data-sp="rm-tag" data-v="${k}" title="Remover etiqueta">🏷 ${esc(tg)} ×</button>`),
      st.lote ? `<button class="sp-crit lote" data-sp="rm-lote" title="Limpar lote">LOTE ${st.lote.size} ×</button>` : "", st.status ? `<button class="sp-crit" data-sp="status" data-v="${esc(st.status)}" title="Remover agrupador">status · ${esc(st.status)} ×</button>` : ""].join("");
    if (st.avancada) {
      const contStatus = new Map(); filtrados(rows, "status").forEach(({ r }) => contStatus.set(statusDe(r), (contStatus.get(statusDe(r)) || 0) + 1));
      const grupos = OPC.Status.map(sv => `<button class="sp-grupo ${st.status === sv ? "on" : ""}" data-sp="status" data-v="${sv}">${sv}<span>${contStatus.get(sv) || 0}</span></button>`).join("");
      const cont = new Map(); fs.forEach(({ r }) => valoresDe(st.fcol, r).forEach(v => cont.set(v, (cont.get(v) || 0) + 1)));
      const qv = norm(st.fvalBusca), vals = [...cont.entries()].filter(([v]) => !qv || norm(v).includes(qv)).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0], "pt-BR"));
      const todasTags = [...new Set(rows.flatMap(x => tagsDe(x.r)))].filter(tg => !st.tags.some(a => norm(a) === norm(tg))).sort((a, b) => a.localeCompare(b, "pt-BR"));
      const opSel = (k, ops) => `<select data-sp-in="${k}">${ops.map(([v, l]) => `<option value="${v}" ${st[k] === v ? "selected" : ""}>${l}</option>`).join("")}</select>`;
      faixa = `<div class="sp-faixa" aria-label="Busca avançada">
        <div class="sp-faixa-cab"><span>CONSTRUTOR DE CRITÉRIOS</span><small>vários valores/trechos · bloco E/OU · acumuláveis · lote de processos · etiquetas</small></div>
        <div class="sp-grupos"><span class="rot">STATUS DE JULGAMENTO · AGRUPADORES</span>${grupos}</div>
        <div class="sp-construtor">
          <div class="sp-cons-col"><label>COLUNA${opSel("fcol", COLS.map(([c]) => [c, c]))}</label><label>OPERADOR${opSel("fop", [["contains", "contém"], ["equals", "é igual a"], ["notempty", "não vazio"], ["empty", "vazio"]])}</label><label>LÓGICA DO BLOCO${opSel("fcombine", [["any", "QUALQUER (OU)"], ["all", "TODOS (E)"]])}</label></div>
          <div class="sp-cons-col"><span class="cap">VALORES EXISTENTES · MÚLTIPLOS</span><input type="search" data-sp-in="fvalBusca" value="${esc(st.fvalBusca)}" placeholder="Buscar nos valores existentes…" aria-label="Buscar nos valores existentes"><small>${vals.length} valor(es) em ${fs.length} processo(s) filtrado(s)</small>
            <div class="sp-vals">${vals.slice(0, 300).map(([v, c]) => `<label title="${esc(v)}"><input type="checkbox" data-fval="${esc(v)}" ${st.fvals.has(v) ? "checked" : ""}><span>${esc(v)}</span><b>${c}</b></label>`).join("") || `<em>Nenhum valor nesta coluna.</em>`}</div><small>${st.fvals.size ? st.fvals.size + " valor(es) marcado(s)" : "nenhum valor marcado"}</small></div>
          <div class="sp-cons-col"><span class="cap">TRECHOS LIVRES · MÚLTIPLOS</span><textarea data-sp-in="ftrechos" placeholder="Um por linha, vírgula ou ;">${esc(st.ftrechos)}</textarea><small>um trecho por linha</small></div>
        </div>
        <div class="sp-faixa-acoes"><label class="tag">ETIQUETA<select data-sp-in="tag"><option value="">${todasTags.length ? "Filtrar por etiqueta (todas devem constar)…" : "Sem etiquetas nesta sessão"}</option>${todasTags.map(tg => `<option>${esc(tg)}</option>`).join("")}</select></label>
          <button class="sp-btn sp-pri" data-sp="aplicar-bloco">+ APLICAR BLOCO</button><button class="sp-btn" data-sp="limpar">LIMPAR</button></div>
        ${ativosHtml ? `<div class="sp-ativos"><span class="rot">CRITÉRIOS ATIVOS</span>${ativosHtml}</div>` : ""}
        <div class="sp-faixa-pe"><button class="sp-btn" data-sp="marcar-filtrados" title="Marcar todos os processos filtrados">☑ Marcar ${fs.length} filtrado(s)</button><button class="sp-btn" data-sp="lote-limpar" title="Limpar seleção">✕ ${n}</button><button class="sp-btn" data-sp="exportar-filtrados" title="Exportar somente os processos filtrados (colunas da Seleção Prévia)">⇩ EXPORTAR ${fs.length}</button><span class="mut">${fs.length} de ${rows.length} processos com os filtros atuais</span></div>
      </div>`;
    } else if (ativosHtml) faixa = `<div class="sp-ativos solto"><span class="rot">CRITÉRIOS ATIVOS</span>${ativosHtml}</div>`;
    const comando = `<section class="sp-card sp-comando ${st.avancada ? "aberta" : ""}" aria-label="Busca, filtros e ações"><div class="sp-linha1">
        <div class="sp-busca"><span class="sp-seg" role="group" aria-label="Modo da busca"><button class="${st.modoBusca === "texto" ? "on" : ""}" data-sp="modo-busca" data-v="texto" title="Buscar por texto">TEXTO</button><button class="${st.modoBusca === "lote" ? "on" : ""}" data-sp="modo-busca" data-v="lote" title="Buscar por lista de processos">LOTE</button></span>
          ${st.modoBusca === "lote" ? `<textarea id="sp-lote-txt" rows="1" placeholder="Colar processos em lote — um por linha, vírgula ou ;" aria-label="Processos em lote">${esc(st.loteTexto)}</textarea><button class="sp-incluir" data-sp="lote-incluir" title="Acrescentar estes processos ao lote ativo">+ INCLUIR</button><button class="sp-aplicar" data-sp="lote-aplicar" title="Substituir o lote ativo por esta lista">APLICAR</button>`
            : `<input id="sp-busca" type="search" value="${esc(st.busca)}" placeholder="Buscar processo, assunto, tema, servidor, observação… (Enter inclui o termo como critério)" aria-label="Buscar"><button class="sp-incluir" data-sp="incluir-busca" title="Incluir o termo como critério da busca (Enter)">+ INCLUIR</button>`}</div>
        <button class="sp-btn sp-btn-av ${st.avancada ? "on" : ""}" data-sp="avancada" aria-expanded="${st.avancada}" title="Construtor de critérios, lote, agrupadores e etiquetas — as ferramentas do Acervo Central">⚲ Busca avançada${nCrit ? ` <b>${nCrit}</b>` : ""} ${st.avancada ? "▴" : "▾"}</button>
        <div class="sp-visoes" role="tablist" aria-label="Visão">${[["lista", "☰ Lista"], ["quadro", "▥ Quadro por etapa"], ["servidor", "👤 Por servidor"]].map(([k, l]) => `<button role="tab" aria-selected="${st.visao === k}" class="${st.visao === k ? "on" : ""}" data-sp="visao" data-v="${k}">${l}</button>`).join("")}</div>
        <div class="sp-menu" id="sp-menu-exp"><button class="sp-btn" data-sp="menu" aria-haspopup="menu">⇩ Exportar ▾</button><div class="sp-menu-lista" role="menu">
          <button data-sp="exp" data-v="complete-xlsx"><b>Excel completo</b><span>Todos os campos e controles da sessão</span></button>
          <button data-sp="exp" data-v="parent-export"><b>Excel resumido</b><span>Uma linha por processo, campos essenciais</span></button><hr>
          <button data-sp="exp" data-v="parent-simple"><b>Pauta simplificada · Excel</b></button>
          <button data-sp="exp" data-v="parent-simple-pdf"><b>Pauta simplificada · PDF</b></button>
          <button data-sp="exp" data-v="parent-info"><b>⎙ Informações de pauta</b><span>Impressão para a sessão</span></button><hr>
          <button data-sp="exp" data-v="complete-csv"><b>CSV</b><span>Dados tabulares</span></button>
          <button data-sp="exp" data-v="complete-json"><b>JSON</b><span>Sessão completa</span></button></div></div>
        <button class="sp-btn" data-sp="modo-classico" title="Planilha e cards completos, colunas e grupos, estatísticas">⚙ Visão clássica</button></div>
      ${faixa}
      <div class="sp-chips">${chips}</div>
      <div class="sp-lote ${n ? "on" : ""}"><b>${n} selecionado(s)</b>
        <select data-lote="serv" aria-label="Designar servidor"><option value="">Designar servidor…</option>${todos.map(x => `<option>${esc(x)}</option>`).join("")}<option value="__nenhum">— retirar servidor</option></select>
        <select data-lote="etapa" aria-label="Mover para a etapa"><option value="">Mover para a etapa…</option>${ETAPAS.map((e, k) => `<option value="${k}">${e[0]}</option>`).join("")}</select>
        <select data-lote="sessao" aria-label="Mudar sessão"><option value="">Mudar sessão…</option>${P().upcomingSessions(false).filter(x => x !== s).map(x => `<option>${esc(x)}</option>`).join("")}</select>
        <button data-sp="lote-remover">Remover da seleção</button><button class="x" data-sp="lote-limpar">✕ Limpar seleção</button></div></section>`;
    let conteudo;
    if (st.visao === "quadro") conteudo = `<section class="sp-card"><div class="sp-quadro">${ETAPAS.map(([l, c], k) => { const it = fs.filter(x => etapa(x.r) === k); return `<div class="sp-coluna" data-col="${k}"><h3><span style="color:${c}">● ${l.toUpperCase()}</span><span class="q">${it.length}</span></h3><div class="sp-kcards">${it.map(({ r, i }) => `<div class="sp-kcard" draggable="true" data-k="${i}"><div class="p sp-mono">${esc(r.Processo)}</div><div class="a">${esc(r.Assunto || r.assunto_judicial || "—")}</div><div class="rr"><span class="sp-serv ${txt(r.SERVIDOR) ? "" : "vazio"}"><span class="sp-av" style="width:18px;height:18px;font-size:8px;background:${corDe(txt(r.SERVIDOR), todos)}">${ini(txt(r.SERVIDOR))}</span><span style="font-size:10.5px">${esc(txt(r.SERVIDOR) || "—")}</span></span><span class="sp-alertas-i">${regIcon(r)}</span></div></div>`).join("")}</div></div>`; }).join("")}</div><div class="sp-rodape"><span>Arraste os cartões entre as colunas para mudar a etapa (Designado exige servidor; Minutado registra a minuta hoje).</span><span>${fs.length} processos</span></div></section>`;
    else if (st.visao === "servidor") {
      const m = P().sessionDetails[s] || {}, ini0 = iso(m.prepStart), fim = iso(m.minutasDeadline), hj = hoje(), de = ini0 && ini0 > hj ? ini0 : hj, eq = equipe(s, rows);
      conteudo = `<section class="sp-card"><div class="sp-raias">${[...todos, ""].map(nm => { const it = fs.filter(x => txt(x.r.SERVIDOR) === nm); if (!it.length && (!nm || !eq.some(e => e.name === nm && e.incl))) return ""; const e = eq.find(z => z.name === nm), d = nm && fim ? diasUteis(de, fim, e ? e.aus : [], nm) : null, meta = d ? it.length / d : null;
        return `<div class="sp-raia"><div class="sp-raia-topo"><div class="nome"><span class="sp-av" style="background:${corDe(nm, todos)}">${ini(nm)}</span>${esc(nm || "Sem servidor")}</div><div class="sp-carga" title="Distribuição por etapa">${ETAPAS.map(([l, c], k) => { const q = it.filter(x => etapa(x.r) === k).length; return q ? `<i style="width:${q / Math.max(it.length, 1) * 100}%;background:${c}" title="${l}: ${q}"></i>` : ""; }).join("")}</div><div class="meta"><b>${it.length}</b> processo(s)${nm ? ` · meta ${meta === null ? "—" : porDia(meta)}${d !== null ? ` em ${d} d. úteis` : ""}` : ""} · ${it.filter(x => etapa(x.r) === 2).length} minutado(s)</div></div>
          <div class="sp-raia-proc">${it.map(({ r, i }) => `<button data-sp="abrir-de" data-i="${i}" title="${esc(r.Assunto || "")} · ${ETAPAS[etapa(r)][0]}"><b style="color:${ETAPAS[etapa(r)][1]}">●</b> <span class="sp-mono">${esc(String(r.Processo).slice(0, 15))}</span></button>`).join("") || "<i style='color:#98a4b0'>nenhum</i>"}</div></div>`; }).join("")}</div><div class="sp-rodape"><span>Carga e andamento de cada servidor (barra colorida = etapas). Meta = designados ÷ dias úteis até a entrega das minutas.</span><span>${fs.length} processos</span></div></section>`;
    } else {
      const linhasHtml = fs.map(x => { const { r, i } = x, sv = txt(r.SERVIDOR), e = etapa(r), c = compl(r), ab = st.aberto === i;
        return `<div class="sp-linha ${st.sel.has(i) ? "sel" : ""} ${ab ? "aberta" : ""}" data-linha="${i}" draggable="true">
          <input type="checkbox" data-selrow="${i}" ${st.sel.has(i) ? "checked" : ""} aria-label="Selecionar ${esc(r.Processo)}">
          <span class="sp-num">${mapa.get(i)}</span><span class="sp-alca" title="Arrastar para reordenar">⠿</span>
          <div class="sp-proc"><div class="p sp-mono">${esc(r.Processo)}</div><div class="c">${esc(r.classe_judicial || r.Classe || "")}${txt(r.META) ? ` · <b style="color:#8a6416">${esc(r.META)}</b>` : ""}</div></div>
          <div class="sp-assunto"><div>${esc(r.Assunto || r.assunto_judicial || "—")}</div><div class="tema">${esc([txt(r.Tema).split("\n")[0], secao(r)].filter(Boolean).join(" · "))}</div></div>
          <div class="sp-compl" title="Complexidade: ${c ? CX[c - 1][1] : "não definida"}">${CX.map(([s1, nm, cor], k) => `<i class="${k + 1 === c ? "on" : ""}" style="${k + 1 === c ? `background:${cor};color:#fff` : ""}">${s1}</i>`).join("")}</div>
          <div class="sp-serv ${sv ? "" : "vazio"}"><span class="sp-av" style="background:${corDe(sv, todos)}">${ini(sv)}</span><span>${esc(sv || "sem servidor")}</span></div>
          <div><span class="sp-pill sp-e${e}">${ETAPAS[e][0].toUpperCase()}</span></div>
          <div class="sp-alertas-i">${regIcon(r)}</div>
          <div class="sp-voto ${txt(r["Voto - Resultado"]) ? "" : "vazio"}">${esc(txt(r["Voto - Resultado"]) || "sem voto")}</div>
          <div><span class="sp-pill ${r["Status de Julgamento"] === "PAUTADO" ? "sp-e5" : "sp-e0"}">${esc(r["Status de Julgamento"] || "PENDENTE")}</span></div>
          <button class="sp-seta" data-sp="abrir" data-i="${i}" aria-expanded="${ab}" aria-label="Abrir detalhes">${ab ? "⌃" : "⌄"}</button>
        </div>${ab ? detalhe(x, todos) : ""}`; }).join("");
      conteudo = `<section class="sp-card sp-lista"><div class="sp-cab"><span><input type="checkbox" data-sp="sel-todos" aria-label="Selecionar todos" ${fs.length && fs.every(x => st.sel.has(x.i)) ? "checked" : ""}></span><span>Nº</span><span></span><span>PROCESSO</span><span>ASSUNTO · TEMA · SEÇÃO</span><span>COMPLEX.</span><span>SERVIDOR</span><span>ETAPA</span><span>REGULARIDADE</span><span>VOTO</span><span>STATUS</span><span></span></div>
        ${linhasHtml || `<div style="padding:40px;text-align:center;color:#6d7b8a">${rows.length ? "Nenhum processo corresponde aos filtros." : "Nenhum processo selecionado para esta sessão. No Acervo Central, marque processos e use SELECIONAR."}</div>`}
        <div class="sp-rodape"><span>${fs.length} de ${rows.length} processos · ordem manual (arraste ⠿) · clique na linha para abrir</span><span>${ativos ? "filtros ativos" : ""}</span></div></section>`;
    }
    corpo.innerHTML = comando + conteudo;
  }

  // ------------------------------------------------------------------ ações
  function gravar(campoNome, i, v) {
    const p = P(), h = H(), r = p.rows[i]; if (!r || p._exclusive) return;
    if (campoNome === "SERVIDOR" || campoNome === "CORRETOR") { const c = p.cell(i, campoNome); if (c && c.onSelect) c.onSelect(v); else p.preCommit(i, campoNome, v); }
    else if (campoNome === "MINUTADO") { if (!PC().recordMinutado(h, r, v)) return render(); }
    else if (campoNome === "__status") { if (!PC().setStatus(h, r, v, r["Sessão Destino"])) return render(); }
    else if (campoNome === "Intercorrências") { PC().setIncidents ? PC().setIncidents(r, v) : (r["Intercorrências"] = v); }
    else p.preCommit(i, campoNome, v);
    salvar();
  }
  function moverEtapa(i, k) {
    const p = P(), r = p.rows[i]; if (!r) return false;
    if (k === 0) { if (iso(r.MINUTADO)) PC().recordMinutado(H(), r, ""); const c = p.cell(i, "SERVIDOR"); c && c.onSelect ? c.onSelect("") : p.preCommit(i, "SERVIDOR", ""); return true; }
    if (k === 1) { if (!txt(r.SERVIDOR)) return false; if (iso(r.MINUTADO)) PC().recordMinutado(H(), r, ""); return true; }
    if (!txt(r.SERVIDOR)) return false;
    return iso(r.MINUTADO) ? true : PC().recordMinutado(H(), r, hoje());
  }
  function clique(e) {
    const t = e.target; if (!cab || !(cab.contains(t) || cap.contains(t) || corpo.contains(t) || barraClassica.contains(t))) { const mm = document.querySelector(".sp-menu.on"); if (mm) mm.classList.remove("on"); return; }
    const b = t.closest("[data-sp]");
    const menu = document.getElementById("sp-menu-exp"); if (menu && !t.closest("#sp-menu-exp")) menu.classList.remove("on");
    if (!b) { const ln = t.closest(".sp-linha"); if (ln && !t.closest("input,select,button,textarea")) { const i = +ln.dataset.linha; st.aberto = st.aberto === i ? null : i; if (st.aberto !== null) st.aba = "id"; render(); } return; }
    const a = b.dataset.sp, v = b.dataset.v, i = b.dataset.i !== undefined ? +b.dataset.i : null;
    const p = P();
    switch (a) {
      case "sessao": p.preFilters.session = v; st.aberto = null; st.sel.clear(); p.refresh(); render(); break;
      case "plano": st.plano = !st.plano; lembrar(); aplicarModo("compacto"); break;
      case "etapa": st.etapa = st.etapa === +v ? null : +v; render(); break;
      case "serv": st.serv = st.serv === v ? null : v; render(); break;
      case "secao": st.secao = st.secao === v ? null : v; render(); break;
      case "alerta": st.alerta = !st.alerta; render(); break;
      case "limpar": limparFiltros(); render(); break;
      case "avancada": st.avancada = !st.avancada; lembrar(); render(); break;
      case "modo-busca": st.modoBusca = v; render(); setTimeout(() => { const el = document.getElementById(v === "lote" ? "sp-lote-txt" : "sp-busca"); el && el.focus(); }, 0); break;
      case "incluir-busca": incluirBusca(); break;
      case "lote-incluir": case "lote-aplicar": { const ids = String(st.loteTexto || "").split(/[\n,;\s]+/).map(x => x.replace(/\D/g, "")).filter(x => x.length >= 15); if (!ids.length) { p.notify("Cole ao menos um número de processo.", "warn"); break; } st.lote = new Set(a === "lote-incluir" && st.lote ? [...st.lote, ...ids] : ids); st.loteTexto = ""; render(); break; }
      case "rm-lote": st.lote = null; render(); break;
      case "rm-crit": st.criterios.splice(+v, 1); render(); break;
      case "rm-tag": st.tags.splice(+v, 1); render(); break;
      case "status": st.status = st.status === v ? null : v; render(); break;
      case "aplicar-bloco": { const itens = [...[...st.fvals].map(x => ({ v: x, exato: true })), ...String(st.ftrechos || "").split(/[\n;,]+/).map(txt).filter(Boolean).map(x => ({ v: x }))];
        if (["contains", "equals"].includes(st.fop) && !itens.length) { p.notify("Marque valores existentes ou digite trechos para montar o bloco.", "warn"); break; }
        st.criterios.push({ col: st.fcol, op: st.fop, combine: st.fcombine, itens }); st.fvals = new Set(); st.ftrechos = ""; st.fvalBusca = ""; render(); break; }
      case "marcar-filtrados": filtrados(linhas()).forEach(x => st.sel.add(x.i)); render(); break;
      case "exportar-filtrados": { const fs = filtrados(linhas()); if (!fs.length) { p.notify("Nenhum processo nos filtros atuais.", "warn"); break; } try { const X = window.XLSX || parent.XLSX, wb = X.utils.book_new(); p.addSheet(wb, "Seleção filtrada", p.columnConfig.selecao, fs.map(x => x.r), "2F6690"); X.writeFile(wb, "Selecao_Previa_Filtrada.xlsx"); p.notify(`${fs.length} processo(s) exportado(s).`); } catch (err) { p.notify("Falha ao exportar: " + (err.message || err), "err"); } break; }
      case "cap": st.cap = !st.cap; lembrar(); render(); break;
      case "cap-restaurar": { const s = sessao(), m = p.sessionDetails[s]; if (!m || !window.confirm("Restaurar capacidade 3/dia, disponibilidade 100% e esforço 1,0 para os servidores desta sessão?")) break; const ns = nomes(linhas()); ns.forEach(nm => { if (m.staffRates) m.staffRates[nm] = 3; if (m.staffAvailability) delete m.staffAvailability[nm]; if (m.staffEffort) delete m.staffEffort[nm]; }); st.asof = ""; p.syncConfigSeed && p.syncConfigSeed(); salvar(); break; }
      case "visao": st.visao = v; lembrar(); render(); break;
      case "aba": st.aba = v; render(); break;
      case "abrir": st.aberto = st.aberto === i ? null : i; st.aba = "id"; render(); break;
      case "abrir-de": st.visao = "lista"; st.aberto = i; st.aba = "id"; lembrar(); render(); setTimeout(() => { const l = corpo.querySelector(`[data-linha="${i}"]`); l && l.scrollIntoView({ block: "center" }); }, 30); break;
      case "cx": p.preCommit(i, "Dificuldade", v); salvar(); break;
      case "menu": menu.classList.toggle("on"); break;
      case "exp": { menu.classList.remove("on"); const pg = PC().page; if (pg) { pg.scope = "all"; pg.render(); } const btn = document.querySelector(`#controle-pauta-root [data-action="${v}"]`); if (btn) btn.click(); else p.notify("Exportação indisponível no momento — tente pela visão clássica.", "warn"); break; }
      case "modo-classico": { const u = H().uiPref("sp2", {}) || {}; H().setUiPref("sp2", { ...u, modo: "classico" }); aplicarModo("classico"); break; }
      case "modo-compacto": { const u = H().uiPref("sp2", {}) || {}; H().setUiPref("sp2", { ...u, modo: "compacto" }); aplicarModo("compacto"); break; }
      case "sel-todos": { const fs = filtrados(linhas()), todosSel = fs.every(x => st.sel.has(x.i)); fs.forEach(x => todosSel ? st.sel.delete(x.i) : st.sel.add(x.i)); render(); break; }
      case "lote-limpar": st.sel.clear(); render(); break;
      case "lote-remover": { const ids = [...st.sel]; if (!ids.length) break; if (!window.confirm(`Remover ${ids.length} processo(s) da Seleção Prévia? Eles continuam no Acervo Central.`)) break; ids.forEach(k => p.removeFromPre(k)); st.sel.clear(); st.aberto = null; render(); break; }
      case "remover1": if (window.confirm("Remover este processo da Seleção Prévia? Ele continua no Acervo Central.")) { p.removeFromPre(i); st.aberto = null; render(); } break;
    }
  }
  function incluirBusca() { const v = txt(st.busca); if (!v) return P().notify("Digite um termo para incluir.", "warn"); st.criterios.push({ col: "__busca__", op: "contains", combine: "all", itens: [{ v }] }); st.busca = ""; render(); }
  function mudanca(e) {
    const t = e.target; if (!corpo || !(corpo.contains(t) || (cap && cap.contains(t)))) return;
    if (t.dataset.cap) {
      const s = sessao(), p = P(), nm = t.dataset.name, k = t.dataset.cap, v = Number(t.value);
      if (!Number.isFinite(v) || v < 0 || (k === "esf" && v <= 0) || (k === "disp" && v > 100) || (k === "rate" && v > 50)) { p.notify("Valor inválido.", "warn"); return render(); }
      p.ensureSession && p.ensureSession(s); const m = p.sessionDetails[s] || (p.sessionDetails[s] = {});
      const chave = { rate: "staffRates", disp: "staffAvailability", esf: "staffEffort" }[k]; m[chave] = { ...(m[chave] || {}), [nm]: v };
      p.syncConfigSeed && p.syncConfigSeed(); salvar(); return;
    }
    if (t.dataset.capd) {
      const s = sessao(), p = P(), k = t.dataset.capd;
      if (k === "asof") { st.asof = iso(t.value); return render(); }
      if (["prepStart", "minutasDeadline"].includes(k)) { p.setSessionMeta(s, k, iso(t.value)); return render(); }
    }
    if (t.dataset.fval !== undefined) { const v = t.dataset.fval; t.checked ? st.fvals.add(v) : st.fvals.delete(v); return render(); }
    if (t.dataset.spIn) { const k = t.dataset.spIn;
      if (k === "tag") { if (t.value && !st.tags.includes(t.value)) st.tags.push(t.value); return render(); }
      if (["fcol", "fop", "fcombine"].includes(k)) { st[k] = t.value; if (k === "fcol") { st.fvals = new Set(); st.fvalBusca = ""; } return render(); }
      return; }
    if (t.dataset.selrow !== undefined) { const i = +t.dataset.selrow; t.checked ? st.sel.add(i) : st.sel.delete(i); render(); return; }
    if (t.dataset.rev) { P().preReviewChange(+t.dataset.i, t.dataset.rev, t.checked); render(); return; }
    if (t.dataset.chk) { P().preCommit(+t.dataset.i, t.dataset.chk, t.checked ? "Sim" : ""); salvar(); return; }
    if (t.dataset.campo) { gravar(t.dataset.campo, +t.dataset.i, t.value); return; }
    if (t.dataset.lote) {
      const v = t.value, ids = [...st.sel], p = P(); if (!v || !ids.length) return;
      if (t.dataset.lote === "serv") { ids.forEach(i => { const c = p.cell(i, "SERVIDOR"), nv = v === "__nenhum" ? "" : v; c && c.onSelect ? c.onSelect(nv) : p.preCommit(i, "SERVIDOR", nv); }); p.notify(`${ids.length} processo(s) ${v === "__nenhum" ? "sem servidor" : "designado(s) a " + v}.`); }
      if (t.dataset.lote === "etapa") { let ok = 0; ids.forEach(i => { if (moverEtapa(i, +v)) ok++; }); p.notify(`${ok} processo(s) movido(s) para ${ETAPAS[+v][0]}` + (ok < ids.length ? ` · ${ids.length - ok} sem servidor ficaram onde estavam` : "") + ".", ok < ids.length ? "warn" : undefined); }
      if (t.dataset.lote === "sessao") { ids.forEach(i => p.preCommit(i, "Sessão Destino", v)); p.notify(`${ids.length} processo(s) movido(s) para ${v}.`); }
      st.sel.clear(); salvar();
    }
  }
  function digitacao(e) {
    const t = e.target;
    if (t.id === "sp-busca") { st.busca = t.value; render(); return; }
    if (t.id === "sp-lote-txt") { st.loteTexto = t.value; return; }
    if (t.dataset && t.dataset.spIn === "fvalBusca") { st.fvalBusca = t.value; render(); return; }
    if (t.dataset && t.dataset.spIn === "ftrechos") { st.ftrechos = t.value; return; }
  }
  function arrastar() {
    let arr = null;
    document.addEventListener("dragstart", e => { const l = e.target.closest && e.target.closest(".sp-linha,.sp-kcard"); if (!l || !corpo.contains(l)) return; arr = l.classList.contains("sp-kcard") ? { tipo: "k", i: +l.dataset.k } : { tipo: "l", i: +l.dataset.linha }; arrastando = true; e.dataTransfer.effectAllowed = "move"; e.dataTransfer.setData("text/plain", "sp2"); e.stopPropagation(); }, true);
    document.addEventListener("dragover", e => { if (!arr) return; const c = e.target.closest(arr.tipo === "k" ? ".sp-coluna" : ".sp-linha"); if (!c) return; e.preventDefault(); corpo.querySelectorAll(".alvo").forEach(x => x !== c && x.classList.remove("alvo")); c.classList.add("alvo"); });
    document.addEventListener("drop", e => {
      if (!arr) return; e.preventDefault(); e.stopPropagation(); corpo.querySelectorAll(".alvo").forEach(x => x.classList.remove("alvo"));
      const p = P();
      if (arr.tipo === "k") { const c = e.target.closest(".sp-coluna"); if (c) { const k = +c.dataset.col; if (moverEtapa(arr.i, k)) p.notify(`${p.rows[arr.i].Processo} → ${ETAPAS[k][0]}.`); else p.notify("Designe um servidor antes de mover para esta etapa.", "warn"); } }
      else { const l = e.target.closest(".sp-linha"); if (l && +l.dataset.linha !== arr.i) { p.reorderPre(arr.i, +l.dataset.linha); } }
      arr = null; arrastando = false; salvar();
    }, true);
    document.addEventListener("dragend", () => { arr = null; arrastando = false; if (corpo) corpo.querySelectorAll(".alvo").forEach(x => x.classList.remove("alvo")); });
  }

  // ------------------------------------------------------------------ ciclo
  const iniciar = setInterval(() => { try { if (montar()) clearInterval(iniciar); } catch (e) { console.warn("[sp2]", e); } }, 200);
  setInterval(() => {
    try { if (!cab || modoAtual !== "compacto" || arrastando || emEdicao()) return; if (assinar() !== assinatura) render(); } catch (e) {}
  }, 700);
  window.SelecaoCompacta = { render: () => render(), estado: st, modo: m => aplicarModo(m), moverEtapa };
})();
