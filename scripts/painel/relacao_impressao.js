  /* versão de impressão da relação simplificada: A4 retrato, sem margens de página, até 2 folhas (fonte ajustada) */
  relImprimirHtml(rows, titulo, sub, itemHead) {
    const esc = v => String(v == null ? "" : v).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
    const vazio = v => !txt(v) || txt(v) === "—";
    const conta = k => rows.filter(r => (r.ind || []).some(b => b.k === k)).length;
    const nImp = rows.filter(r => /⚠/.test(r.observacoes || "")).length, nMeta = conta("meta");
    const agora = new Date(), gerado = agora.toLocaleDateString("pt-BR") + " · " + agora.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
    const rotItem = itemHead === "ITEM" ? "Item" : "Item de pauta";
    // blocos: cabeçalho de grupo (assunto; AI e ED em blocos próprios ao final) + linhas
    const grupoDe = r => r.grupo === "ed" ? "Embargos de declaração" : r.grupo === "ai" ? "Agravos de instrumento" : (vazio(r.assunto) ? "Assunto não informado" : r.assunto);
    const blocos = []; let atual = null;
    rows.forEach(r => { const g = grupoDe(r); if (!atual || atual.g !== g) { atual = { g, tipo: r.grupo || "", rows: [] }; blocos.push(atual); } atual.rows.push(r); });
    const curtaMeta = t => { const m = /meta\s*(\d+[a-z]?)/i.exec(t); return m ? "META " + m[1].toUpperCase() : t; };
    const linha = (r, k) => {
      const obs = vazio(r.observacoes) ? "" : String(r.observacoes).split("\n").map(o => o.trim()).filter(Boolean).map(o => /^⚠/.test(o) ? `<span class="alerta">⚠ ${esc(o.replace(/^⚠\s*/, ""))}</span>` : `<span>${esc(o.replace(/^•\s*/, ""))}</span>`).join("");
      const tema = vazio(r.tema) ? "" : `<b>${esc(r.tema)}</b>`, espec = vazio(r.especificidades) ? "" : `<i>${esc(r.especificidades)}</i>`;
      const assuntoExtra = r.grupo && !vazio(r.assunto) ? `<i class="ass">${esc(r.assunto)}</i>` : "";
      return `<div class="rw${k % 2 ? " par" : ""}${r.grupo ? " g-" + r.grupo : ""}"><div class="c-item">${esc(r.item)}</div><div class="c-proc">${esc(r.processo)}</div><div class="c-ind">${(r.ind || []).map(b => `<span class="b b-${b.k}" title="${esc(b.k === "meta" ? b.s : b.t)}">${esc(b.k === "meta" ? curtaMeta(b.s) : b.s)}</span>`).join("")}</div><div class="c-tema">${tema || assuntoExtra || espec ? [tema, assuntoExtra, espec].filter(Boolean).join("") : '<span class="tr">—</span>'}</div><div class="c-obs">${obs || '<span class="tr">—</span>'}</div></div>`;
    };
    let k = 0;
    const corpo = blocos.map(b => `<div class="gh${b.tipo ? " gh-" + b.tipo : ""}" data-g="${esc(b.g)}"><span class="gt">${esc(b.g)}</span><span class="gn">${b.rows.length} processo${b.rows.length > 1 ? "s" : ""} · ${esc(b.rows[0].item)}${b.rows.length > 1 ? "–" + esc(b.rows[b.rows.length - 1].item) : ""}</span></div>` + b.rows.map(r => linha(r, k++)).join("")).join("");
    const chip = (n, rot, cls) => `<span class="kpi ${cls || ""}"><b>${n}</b>${rot}</span>`;
    const metaTipos = new Map(); rows.forEach(r => (r.ind || []).filter(x => x.k === "meta").forEach(x => metaTipos.set(x.s, (metaTipos.get(x.s) || 0) + 1)));
    const n1 = rows.filter(r => r.pend1).length, nEd = conta("ed");
    const resumo = [chip(rows.length, rows.length === 1 ? "processo" : "processos"), chip(n1, "1º julgamento", "k-1j"), chip(nEd, "ED", "k-ed"),
      chip(nMeta, "com meta" + (metaTipos.size ? ": " + [...metaTipos.entries()].sort((x, y) => x[0].localeCompare(y[0], "pt-BR", { numeric: true })).map(([t, n]) => `${esc(t)} (${n})`).join(" · ") : ""), "k-meta")].join("");
    const colhead = `<div class="ch"><div>${itemHead === "ITEM" ? "Item" : "Item"}</div><div>Processo</div><div>Ind.</div><div>Tema · especificidade</div><div>Observações</div></div>`;
    const layout = () => {
      const fonte = document.getElementById("fonte"), paginas = document.getElementById("paginas"), status = document.getElementById("status");
      const banda = fonte.querySelector(".banda"), legenda = fonte.querySelector(".legenda"), corrente = fonte.querySelector(".corrente"), ch = fonte.querySelector(".ch"), rodape = fonte.querySelector(".rodape");
      const itens = [...fonte.querySelector(".lista").children];
      const oficina = document.createElement("div"); oficina.className = "oficina"; document.body.append(oficina);
      // monta folhas reais: acrescenta linha a linha e abre nova folha quando a área útil transborda (medição exata, com margens e quebras)
      const montar = kf => {
        oficina.replaceChildren(); const folhas = [];
        const nova = () => {
          const pg = document.createElement("section"); pg.className = "pg"; pg.style.setProperty("--k", kf);
          const doc = document.createElement("div"); doc.className = "doc";
          const topo = folhas.length ? [corrente.cloneNode(true)] : [banda.cloneNode(true), legenda.cloneNode(true)];
          const lista = document.createElement("div"); lista.className = "lista";
          doc.append(...topo, ch.cloneNode(true), lista); pg.append(doc, rodape.cloneNode(true)); oficina.append(pg);
          const f = { pg, doc, lista }; folhas.push(f); return f;
        };
        const cheia = f => { const u = f.lista.lastElementChild; return !!u && u.getBoundingClientRect().bottom > f.doc.getBoundingClientRect().bottom - 4; }; // folga de 4px p/ diferenças de renderização na impressão
        let f = nova(), grupo = null;
        for (let i = 0; i < itens.length; i++) {
          const el = itens[i].cloneNode(true), ehGrupo = el.classList.contains("gh");
          if (ehGrupo) grupo = itens[i];
          f.lista.append(el);
          if (!cheia(f)) continue;
          el.remove();
          const mover = [el], ult = f.lista.lastElementChild;
          if (!ehGrupo && ult && ult.classList.contains("gh")) { ult.remove(); mover.unshift(ult); }
          if (!f.lista.children.length) { mover.forEach(x => f.lista.append(x)); continue; }
          f = nova();
          if (!mover[0].classList.contains("gh") && grupo) { const gh = grupo.cloneNode(true); gh.querySelector(".gt").textContent += " (cont.)"; f.lista.append(gh); }
          mover.forEach(x => f.lista.append(x));
        }
        folhas.forEach((x, k) => x.pg.querySelectorAll(".pn").forEach(n => n.textContent = `folha ${k + 1}/${folhas.length}`));
        return folhas;
      };
      let kf = 1, folhas = montar(1);
      if (folhas.length > 1) {
        let lo = 0.3, hi = 1;
        for (let n = 0; n < 12; n++) { const m = (lo + hi) / 2; if (montar(m).length <= 1) lo = m; else hi = m; }
        if (lo >= 0.86) kf = lo;
        else if (folhas.length > 2) { lo = 0.3; hi = 1; for (let n = 0; n < 12; n++) { const m = (lo + hi) / 2; if (montar(m).length <= 2) lo = m; else hi = m; } kf = lo; }
        folhas = montar(kf);
      }
      paginas.replaceChildren(...folhas.map(x => x.pg)); oficina.remove();
      status.textContent = `${folhas.length} folha(s) A4 · retrato · sem margens · fonte ${Math.round(kf * 100)}%`;
    };
    const css = `
      *{box-sizing:border-box;margin:0;padding:0}
      @page{size:A4 portrait;margin:0}
      html,body{font-family:"Segoe UI",Inter,"Helvetica Neue",Arial,sans-serif;color:#1d2733;background:#fff;-webkit-print-color-adjust:exact;print-color-adjust:exact}
      .barra{position:sticky;top:0;z-index:2;display:flex;align-items:center;gap:12px;padding:9px 14px;background:#0f2a47;color:#dfe8f2;font-size:12px}
      .barra button{border:0;border-radius:7px;background:#d9a441;color:#2b1d05;padding:8px 14px;font-weight:800;letter-spacing:.04em;cursor:pointer}
      #fonte{display:none}
      .pg{position:relative;width:210mm;height:296.5mm;padding:4mm 4.5mm 0;overflow:hidden;background:#fff;break-after:page;page-break-after:always}
      .pg:last-child{break-after:auto;page-break-after:auto}
      .oficina{position:absolute;left:-10000px;top:0;visibility:hidden}
      .doc{height:calc(296.5mm - 4mm - 7.5mm);overflow:hidden;font-size:calc(9.4px * var(--k,1));line-height:1.25}
      .banda{display:flex;align-items:center;gap:.4em .9em;flex-wrap:nowrap;padding:.38em .75em;overflow:hidden;border-radius:.5em;background:linear-gradient(120deg,#0f2a47,#1f3d63 70%,#2a5180);color:#fff;margin-bottom:.35em}
      .banda .tit{display:flex;align-items:baseline;gap:.6em;min-width:0}
      .banda .sobre{font-size:.72em;letter-spacing:.14em;text-transform:uppercase;color:#d9a441;font-weight:800;white-space:nowrap}
      .banda h1{font-size:1.32em;line-height:1.1;font-weight:800;white-space:nowrap}
      .banda .meta{margin-left:auto;text-align:right;font-size:.76em;color:#c9d6e4;white-space:nowrap}
      .banda .meta b{color:#fff}
      .kpis{display:flex;flex-wrap:nowrap;gap:.3em;min-width:0;overflow:hidden;margin-left:auto}.legenda{display:none!important}.kpi.k-1j b{color:#ffe08a}
      .kpi{display:inline-flex;align-items:baseline;gap:.3em;padding:.12em .55em;border-radius:99px;background:rgba(255,255,255,.12);font-size:.8em;color:#dfe8f2;white-space:nowrap}
      .kpi b{font-size:1.15em;color:#fff}
      .kpi.k-ed b{color:#ffc978}.kpi.k-agint b{color:#d6c2ff}.kpi.k-ai b{color:#a9d2ff}.kpi.k-meta b{color:#9be2b6}.kpi.k-imp b{color:#ff9f9f}
      .legenda{font-size:.74em;color:#55657a;display:flex;flex-wrap:wrap;gap:.2em .9em;align-items:center;padding:0 .2em .35em}
      .legenda .b{margin-right:.25em}
      .corrente{display:flex;justify-content:space-between;align-items:baseline;padding:0 .2em .3em;border-bottom:2px solid #1f3d63;margin-bottom:.3em;font-size:.92em}
      .corrente b{color:#1f3d63;font-weight:800}.corrente span{color:#6b7a8c;font-size:.9em}
      .ch,.rw{display:grid;grid-template-columns:3.2em 14.6em 5.2em minmax(0,1.2fr) minmax(0,1fr);column-gap:.7em;align-items:baseline}
      .ch{padding:.35em .5em;font-size:.74em;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:#5c6b7e;border-bottom:1px solid #c9d3df}
      .ch div:first-child{text-align:center}
      .gh{display:flex;justify-content:space-between;align-items:baseline;margin-top:.4em;padding:.26em .5em .24em;border-left:.32em solid #1f3d63;background:#eef3f8;break-after:avoid}
      .gh .gt{font-weight:800;color:#1f3d63;font-size:1.02em}
      .gh .gn{font-size:.8em;color:#5c6b7e;font-weight:600}
      .gh-ai{border-left-color:#2563a8;background:#e8f2fd}.gh-ai .gt{color:#1d4f86}
      .gh-ed{border-left-color:#b26a00;background:#fff3e0}.gh-ed .gt{color:#8a5200}
      .rw{padding:.26em .5em;border-bottom:1px solid #e6ebf1;break-inside:avoid}
      .rw.par{background:#fafbfd}
      .c-item{text-align:center;font-weight:800;font-size:1.08em;color:#1f3d63;font-variant-numeric:tabular-nums}
      .c-proc{font-weight:700;letter-spacing:-.01em;white-space:nowrap;font-variant-numeric:tabular-nums;font-size:1.02em}
      .c-ind{display:flex;flex-wrap:wrap;gap:.2em;align-self:start;padding-top:.05em}
      .c-tema,.c-obs{min-width:0;overflow-wrap:anywhere}
      .c-tema b{font-weight:650;color:#24384f}.c-tema i{font-style:normal;color:#6b7a8c;font-size:.94em}.c-tema i.ass{color:#40566e}
      .c-tema b+i::before{content:" — ";color:#a3afbd}.c-tema i+i::before{content:" · ";color:#a3afbd}
      .c-obs span{color:#2f3d4d}.c-obs span+span::before{content:" · ";color:#a3afbd;font-weight:400}
      .c-obs span.alerta{color:#a12626;font-weight:700}.c-obs span.alerta::after{content:""}
      .tr{color:#b3bdc9}
      .b{display:inline-block;padding:.08em .42em;border-radius:.35em;font-size:.78em;font-weight:800;letter-spacing:.02em;line-height:1.3;border:1px solid;white-space:nowrap;max-width:100%;overflow:hidden;text-overflow:ellipsis}
      .b-ed{background:#fff0d6;border-color:#e0a24a;color:#7a4700}.b-agint{background:#f0e8ff;border-color:#a888e0;color:#4b2a8c}
      .b-ai{background:#e3f0ff;border-color:#7fb0e6;color:#1d4f86}.b-meta{background:#e0f6e8;border-color:#7cc89a;color:#17643a}
      .rodape{position:absolute;left:4.5mm;right:4.5mm;bottom:2.2mm;height:4.2mm;display:flex;justify-content:space-between;align-items:flex-end;font-size:7px;color:#8a97a6;border-top:1px solid #e3e8ee;padding-top:.4mm;white-space:nowrap;overflow:hidden}
      @media screen{body{background:#dfe4ea}#paginas{display:flex;flex-direction:column;align-items:center;gap:10px;padding:14px 0 30px}.pg{box-shadow:0 2px 14px rgba(15,42,71,.18)}}
      @media print{.barra{display:none!important}#paginas{padding:0}.pg{box-shadow:none}}`;
    const html = `<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8"><title>${esc(titulo)}</title><style>${css}</style></head><body>
      <div class="barra"><button onclick="window.print()">IMPRIMIR / SALVAR COMO PDF</button><span id="status">diagramando…</span></div>
      <div id="paginas"></div>
      <div id="fonte">
        <div class="banda"><h1>${esc(itemHead === "ITEM" ? titulo : "Pauta · " + titulo)}</h1><div class="kpis">${resumo}</div></div>
<div class="legenda"></div>
        <div class="corrente"><b>${esc(titulo)}</b><span class="pn"></span></div>
        ${colhead}
        <div class="lista">${corpo}</div>
        <div class="rodape"><span>${esc(sub || "")} · ${rows.length} processo(s) · ${esc(gerado)}</span><span class="pn"></span></div>
      </div>
      <script>(${layout.toString()})();window.addEventListener("beforeprint",function(){});<\/script></body></html>`;
    const w = window.open("", "_blank");
    if (!w) return this.notify("O navegador bloqueou a nova janela. Permita pop-ups para abrir a versão de impressão.", "warn");
    w.document.open(); w.document.write(html); w.document.close();
    this.notify("Versão de impressão aberta — A4, sem margens, pronta para imprimir ou salvar como PDF.");
  }
