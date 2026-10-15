/* Banco do Acervo Geral — brndutra/gabcmt · main · banco/acervo.json
   Injetado no Painel Central por scripts/painel/montar.py.

   - Ao abrir o painel, lê banco/acervo.json e mescla no Acervo Central (cria o que falta; atualiza o que,
     no banco, é mais recente que a cópia local; nunca apaga nada e nunca toca nos controles de trabalho).
   - Cada importação de planilha (Acervo, Sigilosos, PJe 2G) marca os processos alterados e, se a opção
     estiver ligada, encaminha o acervo ao GitHub: o banco passa a refletir a importação.
   - Também importa/exporta o banco como arquivo: acervo.json (gabA.acervo) ou acervo.html (página
     legível com o mesmo JSON embutido, reimportável aqui ou por scripts/construir.py).
   - Saneamento obrigatório (o repositório é público): processos sigilosos não entram; celulares,
     telefones, e-mails e CPF não entram. */
(function () {
  "use strict";
  if (window.__acervoGitHub) return;

  const GH = { dono: "brndutra", repo: "gabcmt", ramo: "main", pasta: "banco", arquivo: "acervo.json" };
  const SCHEMA = "gabA.acervo";
  const SANEAMENTO = "Sem processos sigilosos; sem celulares, telefones, e-mails e CPF (repositório público).";
  const LS_AUTO = "acv_gh_auto";

  /* ---------- campos do banco: só os dados de origem do acervo, nunca os controles de trabalho ---------- */
  const ACERVO_COLUMNS = ["processo","classe_judicial","assunto_judicial","data_distribuição","tarefa_atual","data_entrada_tarefa","prioridade","etiquetas","polo_ativo","advogado_pa","polo_passivo","advogado_pp","dpu","mpf","valor_causa","ultimo_movimento","dt_distribuicao_1g","celular_pa","celular_pp"];
  const GAB_ACERVO_COLUMNS = ["Ano","Mês","Processo","Gabinete","Julgador_Colegiado","Data_Distribuição","Código_Classe","Classe","Código_Assunto_Principal","Assunto_Principal","Assuntos_do_Processo","Pendente_1Julgamento","Conclusão?","Data_Conclusão","Data_Fase","Fase","Complemento","Última_Movimentação","Data_Última_Movimentação","Tempo_de_Tramitação","Polo_Ativo","Polo_Passivo","Seção de Origem","Valor_da_Causa","etiquetas","tarefa_atual","DAT_FIM","NUM_CPF_MAGIST","SIN_PRAZO_LEGAL","SIN_SECRETARIA","SIN_CONTADORIA","SIN_REM_EXTERNA","SIN_UFOR","BASE","K_TEMPO"];
  const EXTRAS = ["Consta_Acervo_Gab_A", "Assunto", "Etiquetas Originais"];
  /* "etiquetas"/"Etiquetas" ficam de fora: as originais vão em "Etiquetas Originais"; as atuais são controle do painel */
  const CAMPOS = new Set([...ACERVO_COLUMNS, ...GAB_ACERVO_COLUMNS, ...EXTRAS].filter(c => !/^etiquetas$/i.test(c)));
  /* exportação COMPLETA (só no computador do usuário, nunca no GitHub): inclui sigilosos e todos os campos de origem */
  const GAB_SIGILOSOS_COLUMNS = ["Ano","Mês","Processo","Gabinete","Julgador_Colegiado","Nível_Sigilo","Data_Distribuição","Tempo_Última_Movimentação","DAT_FIM","NUM_CPF_MAGIST","SIN_PEND_1JULG","SIN_CLS","SIN_PRAZO_LEGAL","SIN_SECRETARIA","SIN_CONTADORIA","SIN_REM_EXTERNA","SIN_UFOR","BASE","DES_ULTIMA_MOVIME_SIGILO","K_TEMPO"];
  const CAMPOS_COMPLETO = new Set([...CAMPOS, ...GAB_SIGILOSOS_COLUMNS, "Consta_Acervo_Sigiloso"]);
  const AVISO_COMPLETO = "ACERVO COMPLETO — contém processos sigilosos e dados pessoais. Uso interno: guarde só no seu computador; não publique nem envie ao GitHub.";
  const SENSIVEL = /celular|telefone|fone|whats|e-?mail|cpf|sigilo/i;
  const META = new Set(["id", "processo", "atualizado_em"]);

  const txt = v => String(v == null ? "" : v).trim();
  const procId = v => txt(v).replace(/\D/g, "");
  const agora = () => new Date().toISOString();
  const esc = s => txt(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const sim = v => /^(sim|s|true|1|x)$/i.test(txt(v));

  function sigiloso(r) {
    if (sim(r.Consta_Acervo_Sigiloso)) return true;
    for (const k of Object.keys(r)) {
      if (!/sigil|segredo/i.test(k) || /^consta_acervo/i.test(k)) continue;
      const v = txt(r[k]);
      if (v && !/^(0|n[aã]o|nao|n|false|p[uú]blico|-)$/i.test(v)) return true;
    }
    return false;
  }
  function valorSimples(v) {
    if (v == null) return "";
    if (v instanceof Date) return isNaN(v) ? "" : v.toISOString().slice(0, 10);
    if (typeof v === "object") return "";
    return v;
  }
  /* registro do banco a partir de uma linha do Acervo Central (sem o carimbo de data) */
  function camposDe(r, completo) {
    const o = {}, aceitos = completo ? CAMPOS_COMPLETO : CAMPOS;
    Object.keys(r).sort().forEach(k => {
      if (k.startsWith("_") || !aceitos.has(k) || (!completo && SENSIVEL.test(k))) return;
      const v = valorSimples(r[k]);
      if (txt(v) === "") return;
      o[k] = typeof v === "string" ? v.trim() : v;
    });
    return o;
  }
  function registroDe(r, completo) {
    const proc = txt(r.Processo || r.processo), p = procId(proc);
    if (p.length < 15 || (!completo && sigiloso(r))) return null;
    return { id: "acv-" + p, processo: proc, ...camposDe(r, completo), atualizado_em: r._acervoSync || "" };
  }
  function assinatura(r) { return JSON.stringify(camposDe(r)) + "|" + (sigiloso(r) ? "S" : ""); }

  /* ---------- mescla (mesma regra de scripts/banco/importar.py) ---------- */
  function mesclar(remotos, locais, opts = {}) {
    const rem = new Map(remotos.filter(r => r && r.id).map(r => [r.id, r]));
    const mapa = opts.substituir ? new Map() : new Map(rem);
    let novos = 0, alterados = 0;
    locais.forEach(l => {
      const r = rem.get(l.id);
      if (!r) { mapa.set(l.id, l); novos++; return; }
      const usar = txt(l.atualizado_em) >= txt(r.atualizado_em) ? l : r;
      mapa.set(l.id, usar);
      if (usar === l && JSON.stringify(l) !== JSON.stringify(r)) alterados++;
    });
    (opts.remover || []).forEach(id => mapa.delete(id));
    const registros = [...mapa.values()].sort((a, b) => a.id < b.id ? -1 : a.id > b.id ? 1 : 0);
    return { registros, novos, alterados };
  }
  function documento(registros, base = {}) {
    const t = agora();
    return { schema: SCHEMA, schema_versao: 1, versao: t.slice(0, 10), atualizado_em: t, saneamento: SANEAMENTO, registros };
  }
  /* um registro por linha: diffs legíveis no GitHub e arquivo menor */
  function serializar(doc) {
    const cab = Object.entries(doc).filter(([k]) => k !== "registros").map(([k, v]) => `  ${JSON.stringify(k)}: ${JSON.stringify(v)}`);
    const regs = doc.registros.map(r => "    " + JSON.stringify(r));
    return "{\n" + cab.join(",\n") + ',\n  "registros": [\n' + regs.join(",\n") + (regs.length ? "\n" : "") + "  ]\n}\n";
  }

  /* ---------- leitura (pública) ---------- */
  const NO_SITE = /^https?:$/.test(location.protocol) && /(^|\.)github\.io$/i.test(location.hostname);
  const apiUrl = () => `https://api.github.com/repos/${GH.dono}/${GH.repo}/contents/${GH.pasta}/${GH.arquivo}`;
  const FONTES = [
    ...(NO_SITE ? [() => `${GH.pasta}/${GH.arquivo}?t=${Date.now()}`] : []),
    () => `https://${GH.dono}.github.io/${GH.repo}/${GH.pasta}/${GH.arquivo}?t=${Date.now()}`,
    () => `https://raw.githubusercontent.com/${GH.dono}/${GH.repo}/${GH.ramo}/${GH.pasta}/${GH.arquivo}?t=${Date.now()}`,
    () => `https://cdn.jsdelivr.net/gh/${GH.dono}/${GH.repo}@${GH.ramo}/${GH.pasta}/${GH.arquivo}`
  ];
  let FONTE_OK = -1;
  async function lerPublico() {
    const ordem = FONTE_OK >= 0 ? [FONTE_OK, ...FONTES.keys()].filter((v, i, a) => a.indexOf(v) === i) : [...FONTES.keys()];
    let ult = "";
    for (const i of ordem) {
      try {
        const r = await fetch(FONTES[i](), { cache: "no-store" });
        if (r.status === 404) { ult = "arquivo ainda não existe"; continue; }
        if (!r.ok) { ult = "HTTP " + r.status; continue; }
        const d = await r.json(); FONTE_OK = i; return d;
      } catch (e) { ult = e.message || "rede bloqueada"; }
    }
    throw new Error(ult || "sem acesso");
  }

  /* ---------- escrita (API do GitHub, token só na memória da aba) ---------- */
  let TOKEN = "";
  function b64(str) {
    const bytes = new TextEncoder().encode(str); let s = "";
    for (let i = 0; i < bytes.length; i += 0x8000) s += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
    return btoa(s);
  }
  async function api(opts = {}, accept = "application/vnd.github+json") {
    const r = await fetch(apiUrl() + (opts.method ? "" : `?ref=${GH.ramo}&t=${Date.now()}`), {
      ...opts, cache: "no-store",
      headers: { Accept: accept, Authorization: "Bearer " + TOKEN, "X-GitHub-Api-Version": "2022-11-28", ...(opts.headers || {}) }
    });
    if (r.status === 404 && !opts.method) return null;
    const corpo = accept.includes("raw") && r.ok ? await r.text() : await r.json().catch(() => ({}));
    if (!r.ok) { const e = new Error((corpo && corpo.message) || "HTTP " + r.status); e.status = r.status; throw e; }
    return corpo;
  }
  function pedirToken(motivo) {
    return new Promise(res => {
      if (TOKEN) { res(TOKEN); return; }
      const bg = document.createElement("div"); bg.className = "acv-modal";
      bg.innerHTML = `<form class="acv-box"><h3>Encaminhar o acervo ao GitHub</h3>
        <p>${esc(motivo || "")} Informe um <b>token de acesso do GitHub</b> com permissão <i>Contents: leitura e escrita</i> em <code>${GH.dono}/${GH.repo}</code>. Ele fica só na memória desta aba e some ao fechá-la.</p>
        <input type="password" autocomplete="off" placeholder="github_pat_…" required>
        <div class="acv-acoes"><button type="button" data-n>Agora não</button><button type="submit" class="acv-pri">Encaminhar</button></div></form>`;
      document.body.appendChild(bg);
      const fim = v => { bg.remove(); res(v); };
      bg.querySelector("[data-n]").onclick = () => fim("");
      bg.addEventListener("mousedown", e => { if (e.target === bg) fim(""); });
      bg.querySelector("form").onsubmit = e => { e.preventDefault(); const v = bg.querySelector("input").value.trim(); if (v) TOKEN = v; fim(v); };
      setTimeout(() => bg.querySelector("input").focus(), 30);
    });
  }

  /* ---------- ponte com o Painel Central ---------- */
  const comp = () => window.__painelCentralComponent;
  const pronto = c => c && Array.isArray(c.rows) && !c._exclusive && !(c.state && c.state.storageBusy);
  const ST = { total: null, versao: "", lidoEm: "", erro: "", enviando: false, pendentes: 0, ultimoEnvio: "" };
  function avisar(msg, tipo) { try { comp().notify(msg, tipo); } catch (e) { console.log("[acervo]", msg); } desenhar(); }

  function locaisParaBanco(c) {
    const regs = [], sigilosos = [];
    c.rows.forEach(r => {
      const p = procId(r.Processo || r.processo); if (p.length < 15) return;
      if (sigiloso(r)) { sigilosos.push("acv-" + p); return; }
      const reg = registroDe(r); if (reg) regs.push(reg);
    });
    return { regs, sigilosos };
  }

  /* aplica um registro do banco numa linha do painel, como faria a importação da planilha Acervo */
  function aplicar(c, r, rec, completo) {
    const aceitos = completo ? CAMPOS_COMPLETO : CAMPOS;
    Object.keys(rec).forEach(k => { if (!META.has(k) && aceitos.has(k) && (completo || !SENSIVEL.test(k)) && k !== "Etiquetas Originais") r[k] = rec[k]; });
    try { c.applyCanonicalSource(r, rec, completo && sigiloso(rec) ? "sigilosos" : "acervo"); } catch (e) { console.warn(e); }
    if (txt(rec["Etiquetas Originais"])) { try { c.setImportedTags(r, rec["Etiquetas Originais"], r._tagOriginalSource || "acervo"); } catch (e) { r["Etiquetas Originais"] = rec["Etiquetas Originais"]; } }
    r._acervoSync = txt(rec.atualizado_em) || agora();
    try { c.recompute(r); } catch (e) { console.warn(e); }
  }

  /* mescla um documento gabA.acervo no Acervo Central */
  async function receber(doc, origem) {
    const c = comp(); if (!pronto(c)) throw new Error("O painel ainda está carregando; tente de novo em instantes.");
    const regs = Array.isArray(doc) ? doc : (doc && Array.isArray(doc.registros) ? doc.registros : null);
    if (!regs) throw new Error("O arquivo não contém um banco gabA.acervo (lista \"registros\").");
    if (doc.schema && doc.schema !== SCHEMA) throw new Error(`Banco de outro tipo (${doc.schema}); esperado ${SCHEMA}.`);
    const completo = !!(doc && doc.completo);
    const mapa = new Map(c.rows.map(r => [procId(r.Processo || r.processo), r]).filter(x => x[0]));
    let criados = 0, atualizados = 0, iguais = 0, ignorados = 0;
    for (const rec of regs) {
      const proc = txt(rec && (rec.processo || rec.Processo)), p = procId(proc);
      if (p.length < 15 || (!completo && sigiloso(rec))) { ignorados++; continue; }
      let r = mapa.get(p);
      if (!r) {
        r = c.ensureShape({ Processo: proc, processo: proc });
        aplicar(c, r, rec, completo); c.rows.push(r); mapa.set(p, r); criados++;
      } else if (txt(rec.atualizado_em) > txt(r._acervoSync)) {
        const antes = assinatura(r); aplicar(c, r, rec, completo);
        if (assinatura(r) !== antes) atualizados++; else iguais++;
      } else iguais++;
    }
    if (criados || atualizados) {
      c.rows = c.rows.map(r => c.ensureShape(r));
      await c.saveDB(); c.refresh();
    }
    const msg = `Banco do acervo (${origem}): ${criados} novo(s) · ${atualizados} atualizado(s) · ${iguais} já em dia` + (ignorados ? ` · ${ignorados} ignorado(s)` : "") + ".";
    return { criados, atualizados, iguais, ignorados, msg };
  }

  async function puxar(silencioso) {
    ST.erro = "";
    try {
      const doc = await lerPublico();
      ST.total = (doc.registros || []).length; ST.versao = doc.atualizado_em || doc.versao || ""; ST.lidoEm = agora();
      const r = await receber(doc, "GitHub");
      if (!silencioso || r.criados || r.atualizados) avisar(r.msg, "ok"); else desenhar();
      return r;
    } catch (e) {
      ST.erro = e.message || String(e);
      if (!silencioso) avisar("Banco do acervo no GitHub: " + ST.erro, "warn"); else desenhar();
      return null;
    }
  }

  async function encaminhar(opts = {}) {
    const c = comp(); if (!pronto(c)) return avisar("O painel ainda está carregando; tente de novo em instantes.", "warn");
    if (ST.enviando) return;
    const tok = await pedirToken(opts.motivo); if (!tok) { desenhar(); return; }
    ST.enviando = true; desenhar();
    try {
      for (let tentativa = 0; tentativa < 2; tentativa++) {
        const meta = await api({}, "application/vnd.github.object+json");
        let remoto = { registros: [] };
        if (meta) { const bruto = await api({}, "application/vnd.github.raw+json"); try { remoto = JSON.parse(bruto); } catch (e) { remoto = { registros: [] }; } }
        const { regs, sigilosos } = locaisParaBanco(c);
        const agoraIso = agora();
        regs.forEach(r => { if (!r.atualizado_em) r.atualizado_em = agoraIso; });
        const remotos = Array.isArray(remoto.registros) ? remoto.registros : [];
        const m = mesclar(remotos, regs, { substituir: !!opts.substituir, remover: sigilosos });
        const removidos = remotos.length + m.novos - m.registros.length;
        if (JSON.stringify(m.registros) === JSON.stringify(remotos)) {
          ST.total = remotos.length; ST.pendentes = 0;
          avisar(`Nada a encaminhar: banco/acervo.json já está igual ao acervo deste painel (${remotos.length} processos).`, "ok");
          return;
        }
        const doc = documento(m.registros);
        try {
          await api({ method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({
            message: `Atualiza banco/acervo.json pelo Painel Central (${m.novos} novo(s), ${m.alterados} atualizado(s)${removidos > 0 ? `, ${removidos} removido(s)` : ""})`,
            content: b64(serializar(doc)), branch: GH.ramo, ...(meta && meta.sha ? { sha: meta.sha } : {}) }) });
        } catch (e) { if (e.status === 409 && tentativa === 0) continue; throw e; }
        ST.total = m.registros.length; ST.versao = doc.atualizado_em; ST.pendentes = 0; ST.ultimoEnvio = agoraIso;
        avisar(`Acervo encaminhado ao GitHub: ${m.novos} novo(s) · ${m.alterados} atualizado(s)${removidos > 0 ? ` · ${removidos} removido(s)` : ""} · ${m.registros.length} processos em banco/acervo.json (sigilosos, celulares e CPF ficam de fora).`, "ok");
        return;
      }
    } catch (e) {
      if (e.status === 401 || e.status === 403) TOKEN = "";
      avisar("Falha ao encaminhar o acervo ao GitHub: " + (e.message || e), "err");
    } finally { ST.enviando = false; desenhar(); }
  }

  /* a importação de planilha passa a carimbar o que mudou e, se ligado, a encaminhar ao GitHub */
  function envolverImportacao(c) {
    if (!c || c.__acvEnvolvido) return;
    const original = c.importTyped;
    if (typeof original !== "function") return;
    c.__acvEnvolvido = true;
    c.importTyped = async function (file, type) {
      const antes = new Map(this.rows.map(r => [procId(r.Processo || r.processo), assinatura(r)]));
      const ep = await original.call(this, file, type);
      const t = agora(); let n = 0;
      this.rows.forEach(r => { const p = procId(r.Processo || r.processo); if (p && antes.get(p) !== assinatura(r)) { r._acervoSync = t; n++; } });
      if (n) { await this.saveDB(); ST.pendentes += n; desenhar(); if (autoLigado()) setTimeout(() => encaminhar({ motivo: `A importação alterou ${n} processo(s) do acervo.` }), 400); }
      return ep;
    };
  }

  /* ---------- arquivos: acervo.json e acervo.html ---------- */
  function baixar(nome, conteudo, tipo) {
    const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([conteudo], { type: tipo }));
    a.download = nome; document.body.appendChild(a); a.click(); setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
  }
  function docLocal(completo) {
    const c = comp(); if (!pronto(c)) throw new Error("O painel ainda está carregando.");
    const regs = completo ? c.rows.map(r => registroDe(r, true)).filter(Boolean) : locaisParaBanco(c).regs, t = agora();
    regs.forEach(r => { if (!r.atualizado_em) r.atualizado_em = t; });
    const doc = documento(regs.sort((a, b) => a.id < b.id ? -1 : 1));
    if (completo) { doc.completo = true; doc.saneamento = AVISO_COMPLETO; }
    return doc;
  }
  function paginaHtml(doc) {
    const comp_ = !!doc.completo;
    const linhas = doc.registros.map(r => `<tr><td>${esc(r.processo)}${comp_ && sigiloso(r) ? ' <span class="sig">SIGILOSO</span>' : ""}</td><td>${esc(r.classe_judicial || r.Classe)}</td><td>${esc(r.assunto_judicial || r.Assunto_Principal || r.Assunto)}</td><td>${esc(r["data_distribuição"] || r["Data_Distribuição"])}</td><td>${esc(r.tarefa_atual)}</td><td>${esc(r.polo_ativo || r.Polo_Ativo)}</td><td>${esc(r.polo_passivo || r.Polo_Passivo)}</td></tr>`).join("\n");
    const json = JSON.stringify(doc).replace(/</g, "\\u003c");
    return `<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${comp_ ? "Acervo Completo (sigiloso)" : "Acervo Geral"} · Gabinete A</title>
<style>:root{--fundo:#f6f8fa;--papel:#fff;--tinta:#14263c;--suave:#6d7b8a;--linha:#dee3e9;--marca:#1f3d63;--ouro:#d9a441}
@media (prefers-color-scheme:dark){:root{--fundo:#0f1722;--papel:#16212f;--tinta:#e6edf5;--suave:#9fb0c2;--linha:#2a3a4e;--marca:#8fb3e0}}
*{box-sizing:border-box}body{margin:0;background:var(--fundo);color:var(--tinta);font:13px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif}
header{padding:20px 16px 12px;max-width:1400px;margin:auto}h1{margin:0;font-size:20px;color:var(--marca)}p{margin:4px 0;color:var(--suave)}
.barra{position:sticky;top:0;background:var(--fundo);padding:8px 16px;max-width:1400px;margin:auto}
input{width:100%;padding:9px 12px;border:1px solid var(--linha);border-radius:8px;background:var(--papel);color:var(--tinta);font:inherit}
main{max-width:1400px;margin:auto;padding:0 16px 32px;overflow-x:auto}table{width:100%;border-collapse:collapse;background:var(--papel)}
th,td{border-bottom:1px solid var(--linha);padding:6px 8px;text-align:left;vertical-align:top}th{font-size:11px;letter-spacing:.04em;text-transform:uppercase;color:var(--suave);background:var(--papel)}
.sig{display:inline-block;margin-left:4px;padding:1px 6px;border-radius:999px;background:#a14d4d;color:#fff;font-size:10px;font-weight:700;letter-spacing:.04em}
.alerta{margin-top:10px;padding:10px 12px;border-radius:8px;background:#fbeaea;color:#7a2e2e;border:1px solid #e9c3c3;font-weight:600}</style></head>
<body><header><h1>${comp_ ? "Acervo Completo" : "Acervo Geral"} · Gabinete A</h1>
<p>${doc.registros.length} processos · gerado em ${esc(new Date(doc.atualizado_em).toLocaleString("pt-BR"))} · ${esc(doc.saneamento)}</p>
${comp_ ? `<div class="alerta">${doc.registros.filter(sigiloso).length} processo(s) sigiloso(s) incluído(s). Reimportável no Painel Central (Acervo · GitHub › Importar arquivo), que restaura também os sigilosos no seu navegador; ao encaminhar ao GitHub, eles continuam de fora.</div>` : `<p>Este arquivo pode ser reimportado no Painel Central (Acervo · GitHub › Importar arquivo) ou no repositório com <code>python3 scripts/construir.py acervo.html</code>.</p>`}</header>
<div class="barra"><input id="q" placeholder="Filtrar por processo, classe, assunto, tarefa ou parte…" aria-label="Filtrar"></div>
<main><table><thead><tr><th>Processo</th><th>Classe</th><th>Assunto</th><th>Distribuição</th><th>Tarefa atual</th><th>Polo ativo</th><th>Polo passivo</th></tr></thead><tbody id="t">
${linhas}
</tbody></table></main>
<script id="gabA-acervo" type="application/json">${json}<\/script>
<script>(function(){var q=document.getElementById("q"),rows=[].slice.call(document.querySelectorAll("#t tr"));q.addEventListener("input",function(){var v=q.value.toLowerCase();rows.forEach(function(r){r.style.display=!v||r.textContent.toLowerCase().indexOf(v)>=0?"":"none"})})})();<\/script>
</body></html>
`;
  }
  function docDeArquivo(texto, nome) {
    const t = texto.replace(/^﻿/, "");
    if (/^\s*[\[{]/.test(t)) return JSON.parse(t);
    const html = new DOMParser().parseFromString(t, "text/html");
    const s = html.getElementById("gabA-acervo") || html.querySelector('script[type="application/json"][data-schema="gabA.acervo"]');
    if (!s) throw new Error(`${nome}: não encontrei o banco do acervo neste HTML (script#gabA-acervo).`);
    return JSON.parse(s.textContent);
  }
  function escolherArquivo() {
    const inp = document.createElement("input"); inp.type = "file"; inp.accept = ".json,.html,.htm,application/json,text/html";
    inp.addEventListener("change", async () => {
      const f = inp.files && inp.files[0]; if (!f) return;
      try {
        const doc = docDeArquivo(await f.text(), f.name);
        const r = await receber(doc, f.name);
        avisar(r.msg, "ok");
        if ((r.criados || r.atualizados) && autoLigado()) setTimeout(() => encaminhar({ motivo: `O arquivo ${f.name} alterou ${r.criados + r.atualizados} processo(s).` }), 400);
      } catch (e) { avisar("Importação do banco do acervo: " + (e.message || e), "err"); }
    });
    inp.click();
  }

  /* ---------- interface: botão flutuante e painel ---------- */
  const autoLigado = () => { try { return localStorage.getItem(LS_AUTO) !== "0"; } catch (e) { return true; } };
  const css = document.createElement("style");
  css.textContent = `
#acvBtn{position:fixed;right:16px;bottom:16px;z-index:240;display:flex;align-items:center;gap:7px;border:1px solid #1f3d63;background:#1f3d63;color:#fff;border-radius:999px;padding:8px 13px;font:800 10.5px/1 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;letter-spacing:.04em;cursor:pointer;box-shadow:0 4px 14px rgba(20,38,60,.25)}
#acvBtn i{width:8px;height:8px;border-radius:50%;background:#8fa9c0;display:inline-block}#acvBtn i.ok{background:#5fc27e}#acvBtn i.warn{background:#d9a441}#acvBtn i.run{background:#7fb3ff;animation:acvP 1s infinite}
#acvBtn b{background:#d9a441;color:#33240a;border-radius:999px;padding:2px 6px;font-size:9.5px}
@keyframes acvP{50%{opacity:.35}}
#acvPop{position:fixed;right:16px;bottom:58px;z-index:241;width:min(370px,calc(100vw - 32px));background:#fff;color:#14263c;border:1px solid #dee3e9;border-radius:12px;box-shadow:0 18px 50px rgba(20,38,60,.28);padding:15px;font:600 11.5px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
#acvPop h4{margin:0;font-size:9.5px;letter-spacing:.09em;color:#1f3d63}#acvPop .t{font-size:15px;font-weight:850;margin:2px 0 8px}
#acvPop .st{background:#f6f8fa;border:1px solid #edf0f3;border-radius:9px;padding:9px 10px;color:#4c5b6b;font-size:10.5px}
#acvPop .g{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin-top:10px}
#acvPop button{border:1px solid #cfd7e0;background:#fff;color:#14263c;border-radius:8px;padding:8px;font-family:inherit;font-size:10px;font-weight:800;line-height:1.2;letter-spacing:.03em;cursor:pointer}
#acvPop button.acv-pri{background:#d9a441;border-color:#d9a441;color:#33240a}#acvPop button.acv-nav{background:#1f3d63;border-color:#1f3d63;color:#fff}
#acvPop button:disabled{opacity:.5;cursor:wait}#acvPop label{display:flex;gap:7px;align-items:flex-start;margin-top:10px;font-size:10.5px;color:#4c5b6b;cursor:pointer}
#acvPop .nota{margin-top:9px;font-size:9.5px;color:#7e8b99}#acvPop .x{position:absolute;right:10px;top:8px;border:0;padding:4px 7px;background:transparent;font-size:14px}
#acvPop .full{grid-column:1/-1}#acvPop button.acv-sig{border-color:#e9c3c3;color:#7a2e2e;background:#fdf5f5}#acvPop .sub{background:transparent;border-color:transparent;color:#a14d4d;font-weight:700}
.acv-modal{position:fixed;inset:0;z-index:600;background:rgba(20,38,60,.55);display:flex;align-items:center;justify-content:center;padding:16px}
.acv-box{background:#fff;color:#14263c;border-radius:12px;max-width:440px;width:100%;padding:18px 20px;box-shadow:0 18px 50px rgba(0,0,0,.3);font:13px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.acv-box h3{margin:0 0 6px;font-size:15px}.acv-box p{margin:0 0 12px}.acv-box code{font-size:12px}
.acv-box input{width:100%;padding:8px 10px;border:1px solid #c9ced4;border-radius:7px;font:inherit}
.acv-acoes{display:flex;justify-content:flex-end;gap:8px;margin-top:12px}.acv-acoes button{padding:7px 14px;border-radius:7px;border:1px solid #c9ced4;background:#fff;cursor:pointer;font:inherit}.acv-acoes .acv-pri{background:#1f3d63;border-color:#1f3d63;color:#fff}`;
  document.head.appendChild(css);

  let aberto = false;
  const btn = document.createElement("button");
  btn.id = "acvBtn"; btn.type = "button"; btn.title = "Banco do Acervo Geral no GitHub (banco/acervo.json)";
  btn.onclick = () => { aberto = !aberto; desenhar(); };
  const pop = document.createElement("div"); pop.id = "acvPop"; pop.hidden = true; pop.setAttribute("role", "dialog"); pop.setAttribute("aria-label", "Banco do Acervo Geral");

  const dataBr = iso => { try { return iso ? new Date(iso).toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" }) : "—"; } catch (e) { return iso; } };
  function desenhar() {
    const estado = ST.enviando ? "run" : ST.erro ? "warn" : ST.total != null ? "ok" : "";
    btn.innerHTML = `<i class="${estado}"></i>ACERVO · GITHUB${ST.pendentes ? ` <b>${ST.pendentes}</b>` : ""}`;
    pop.hidden = !aberto;
    if (!aberto) return;
    const c = comp(), n = c && Array.isArray(c.rows) ? c.rows.length : 0;
    const situacao = ST.erro ? `Sem leitura do GitHub: ${esc(ST.erro)}.` :
      ST.total == null ? "Lendo banco/acervo.json…" : `<b>${ST.total}</b> processo(s) em banco/acervo.json · versão ${esc(dataBr(ST.versao))}`;
    pop.innerHTML = `<button class="x" type="button" aria-label="Fechar" data-a="fechar">×</button>
      <h4>BANCO DO ACERVO GERAL</h4><div class="t">${GH.dono}/${GH.repo} · ${GH.pasta}/${GH.arquivo}</div>
      <div class="st">${situacao}<br>${n} processo(s) neste painel${ST.pendentes ? ` · <b>${ST.pendentes} alterado(s) desde o último envio</b>` : ""}${ST.ultimoEnvio ? ` · último envio ${esc(dataBr(ST.ultimoEnvio))}` : ""}</div>
      <div class="g">
        <button type="button" data-a="puxar">ATUALIZAR DO GITHUB</button>
        <button type="button" class="acv-nav" data-a="enviar" ${ST.enviando ? "disabled" : ""}>${ST.enviando ? "ENCAMINHANDO…" : "ENCAMINHAR AO GITHUB"}</button>
        <button type="button" class="acv-pri full" data-a="importar">IMPORTAR ARQUIVO (.HTML OU .JSON)</button>
        <button type="button" data-a="json">EXPORTAR ACERVO.JSON</button>
        <button type="button" data-a="html">EXPORTAR ACERVO.HTML</button>
        <button type="button" class="full acv-sig" data-a="htmlc" title="Inclui os processos sigilosos e todos os campos. Fica só no seu computador.">EXPORTAR HTML COMPLETO · COM SIGILOSOS (SÓ LOCAL)</button>
        <button type="button" class="sub full" data-a="substituir" ${ST.enviando ? "disabled" : ""}>Substituir o banco pelo acervo deste painel…</button>
      </div>
      <label><input type="checkbox" data-a="auto" ${autoLigado() ? "checked" : ""}> Encaminhar ao GitHub após cada importação (planilhas Gab A, PJe 2G ou arquivo do banco)</label>
      <div class="nota">Mescla por processo: o banco recebe o que é novo ou mais recente e nada apaga; os controles de trabalho do painel não saem daqui. ${esc(SANEAMENTO)}</div>`;
  }
  pop.addEventListener("click", async e => {
    const a = e.target.closest("[data-a]"); if (!a) return;
    const acao = a.dataset.a;
    if (acao === "fechar") { aberto = false; desenhar(); }
    else if (acao === "puxar") puxar(false);
    else if (acao === "enviar") encaminhar({ motivo: "" });
    else if (acao === "importar") escolherArquivo();
    else if (acao === "json") { try { baixar("acervo.json", serializar(docLocal()), "application/json"); } catch (er) { avisar(er.message, "err"); } }
    else if (acao === "htmlc") { try { const d = docLocal(true); baixar(`acervo-completo-SIGILOSO-${d.versao}.html`, paginaHtml(d), "text/html;charset=utf-8"); avisar(`HTML completo gerado com ${d.registros.length} processo(s), inclusive ${d.registros.filter(sigiloso).length} sigiloso(s). Guarde-o só no seu computador.`, "ok"); } catch (er) { avisar(er.message, "err"); } }
    else if (acao === "html") { try { baixar("acervo.html", paginaHtml(docLocal()), "text/html;charset=utf-8"); } catch (er) { avisar(er.message, "err"); } }
    else if (acao === "substituir") {
      if (window.confirm("Substituir banco/acervo.json pelo acervo deste painel?\n\nProcessos que estão no GitHub mas não neste painel serão retirados do banco. Use só quando este painel tiver o acervo completo.")) encaminhar({ substituir: true, motivo: "" });
    }
  });
  pop.addEventListener("change", e => { if (e.target.dataset.a === "auto") { try { localStorage.setItem(LS_AUTO, e.target.checked ? "1" : "0"); } catch (er) {} } });
  document.addEventListener("keydown", e => { if (e.key === "Escape" && aberto) { aberto = false; desenhar(); } });

  function montar() {
    if (!document.body) return setTimeout(montar, 50);
    document.body.appendChild(btn); document.body.appendChild(pop); desenhar();
  }
  montar();

  /* aguarda o painel terminar de carregar o banco local; depois envolve a importação e lê o GitHub */
  let iniciado = false;
  setInterval(() => {
    const c = comp(); if (!pronto(c)) return;
    envolverImportacao(c);
    if (!iniciado) { iniciado = true; setTimeout(() => puxar(true), 300); }
  }, 400);

  window.__acervoGitHub = { puxar, encaminhar, receber, docLocal, serializar, mesclar, registroDe, sigiloso, paginaHtml, docDeArquivo, estado: ST, GH };
})();
