"""Ajustes aplicados ao template do Painel Central por montar.py.

Cada ajuste é uma troca exata (antigo -> novo) que precisa casar uma única vez; se o painel mudar e um trecho
não for encontrado, a montagem para e diz qual ajuste falhou, em vez de gerar um painel quebrado.
"""

# ---------------------------------------------------------------------------------------------------------------
# 1. Desempenho: as funções que normalizam nomes de coluna e valores (canon, fieldKey, centralColumn...) são
#    puras e eram recalculadas milhões de vezes ao abrir um acervo grande. Passam a guardar o resultado.
# ---------------------------------------------------------------------------------------------------------------
MEMO = '''function __memo(f, limite) {
  const m = new Map(), lim = limite || 50000;
  return v => {
    const k = v == null ? "" : (typeof v === "string" ? v : String(v));
    let r = m.get(k);
    if (r === undefined && !m.has(k)) { r = f(v); if (m.size >= lim) m.clear(); m.set(k, r); }
    return r;
  };
}
const centralColumn = __memo(c => {'''

DESEMPENHO = [
    ("const centralColumn = c => {", MEMO),
    ('''  return ({"Seleção Prévia":"JULGAMENTO","Sessão Destino":"JULGAMENTO","Status de Julgamento":"JULGAMENTO","Impedimento":"Impedimento / Suspeição","Suspeição":"Impedimento / Suspeição","etiquetas":"Etiquetas"})[c] || c;
};''', '''  return ({"Seleção Prévia":"JULGAMENTO","Sessão Destino":"JULGAMENTO","Status de Julgamento":"JULGAMENTO","Impedimento":"Impedimento / Suspeição","Suspeição":"Impedimento / Suspeição","etiquetas":"Etiquetas"})[c] || c;
});'''),
    ('const selectionColumn = c => ({', 'const selectionColumn = __memo(c => ({'),
    ('''"Mídias":"Outras Peças"})[c] || c;
const SELECAO_REMOVED_COLUMNS''', '''"Mídias":"Outras Peças"})[c] || c);
const SELECAO_REMOVED_COLUMNS'''),
    ('const workflowColumn = c => Object.prototype.hasOwnProperty.call(LEGACY_WORK_COLUMNS,c) ? LEGACY_WORK_COLUMNS[c] : c;',
     'const workflowColumn = __memo(c => Object.prototype.hasOwnProperty.call(LEGACY_WORK_COLUMNS,c) ? LEGACY_WORK_COLUMNS[c] : c);'),
    ('const canon = v => txt(v).normalize("NFD").replace(/[\\u0300-\\u036f]/g, "").toLowerCase().replace(/\\s+/g, " ").trim();',
     'const canon = __memo(v => txt(v).normalize("NFD").replace(/[\\u0300-\\u036f]/g, "").toLowerCase().replace(/\\s+/g, " ").trim(), 200000);'),
    ('const fieldKey = v => {\n  const k = canon(v)', 'const fieldKey = __memo(v => {\n  const k = canon(v)'),
    ('''  return aliases[k] || k;
};
const retiredKeys''', '''  return aliases[k] || k;
});
const retiredKeys'''),
    ('const isRetiredColumn = c => retiredKeys.has(canon(c).replace(/[^a-z0-9]/g, ""));',
     'const isRetiredColumn = __memo(c => retiredKeys.has(canon(c).replace(/[^a-z0-9]/g, "")));'),
    ('const isLegacySectionColumn = c => !txt(c).startsWith("_") && (canon(c) === "secao_competente" || fieldKey(c) === "julgadorcolegiado");',
     'const isLegacySectionColumn = __memo(c => !txt(c).startsWith("_") && (canon(c) === "secao_competente" || fieldKey(c) === "julgadorcolegiado"));'),
    ('const isVisibleColumn = c => txt(c) && !txt(c).startsWith("_") && !isRetiredColumn(c) && !isLegacySectionColumn(c) && workflowColumn(c) === c && !["Impedimento","Suspeição"].includes(c);',
     'const isVisibleColumn = __memo(c => txt(c) && !txt(c).startsWith("_") && !isRetiredColumn(c) && !isLegacySectionColumn(c) && workflowColumn(c) === c && !["Impedimento","Suspeição"].includes(c));'),
    ('const canonKey = v => canon(v).replace(/[_\\s]+/g, " ").trim();',
     'const canonKey = __memo(v => canon(v).replace(/[_\\s]+/g, " ").trim(), 200000);'),
]

# ---------------------------------------------------------------------------------------------------------------
# 2. Tela Acervo Central: 1ª linha com Assuntos · Classes processuais · Tarefas atuais (larguras proporcionais);
#    2ª linha com Antiguidade do acervo (à esquerda) e Processos por seção (à direita), na mesma altura fixa.
# ---------------------------------------------------------------------------------------------------------------
CSS_ANTIGO = """    .central-stats-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;align-items:stretch;min-width:0}
    .central-stat-card{height:560px;min-height:0;min-width:0;overflow:auto;scrollbar-gutter:stable}"""
CSS_NOVO = """    .central-stats-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;align-items:stretch;min-width:0}
    .central-stat-card{height:460px;min-height:0;min-width:0;overflow:auto;scrollbar-gutter:stable}
    .central-pair-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:14px;align-items:stretch;min-width:0}
    .central-pair-grid>.central-stat-card{height:500px}
    .central-sec-card .sec-table-wrap{max-height:none!important;flex:1;min-height:0}"""
MEDIA_ANTIGA = """    @media(max-width:1350px){.central-stats-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
    @media(max-width:760px){.central-stats-grid{grid-template-columns:minmax(0,1fr)}.central-stat-card{height:480px}}"""
MEDIA_NOVA = """    @media(max-width:1250px){.central-stats-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.central-pair-grid{grid-template-columns:minmax(0,1fr)}}
    @media(max-width:760px){.central-stats-grid{grid-template-columns:minmax(0,1fr)}.central-stat-card,.central-pair-grid>.central-stat-card{height:480px}}"""

INICIO_SECAO = """                        <div style="margin-top:16px;padding-top:14px;border-top:1px solid #e3e7ec">
              <div style="font-size:13px;font-weight:800;color:#14263c;margin-bottom:3px">Processos por seção</div>"""
FIM_SECAO = """                </sc-raw-table>
              </div>
            </div>
"""
INICIO_IDADE = """            <div class="central-stat-card" style="border-radius:14px;background:#fff;border:1px solid #e3e7ec;padding:16px 18px;box-shadow:0 10px 24px rgba(20,38,60,.04);perspective:1200px;min-width:0">"""
FIM_GRADE = '          </div>\n            <div class="central-monthly-card"'
CARD = '<div class="central-stat-card central-sec-card" style="border-radius:14px;background:#fff;border:1px solid #e3e7ec;padding:16px 18px;box-shadow:0 10px 24px rgba(20,38,60,.04);display:flex;flex-direction:column">'


def reorganizar_cards(t: str) -> str:
    def um(trecho, nome, desde=0):
        i = t.find(trecho, desde)
        if i < 0 or t.find(trecho, i + 1) >= 0 and nome != "fim":
            raise SystemExit(f"melhorias/layout: trecho '{nome}' não encontrado uma única vez — o painel mudou.")
        return i
    for a, b, nome in ((CSS_ANTIGO, CSS_NOVO, "css"), (MEDIA_ANTIGA, MEDIA_NOVA, "media")):
        if t.count(a) != 1:
            raise SystemExit(f"melhorias/layout: {nome} não encontrado")
        t = t.replace(a, b)
    # 1) retira "Processos por seção" de dentro do card Assuntos
    i = um(INICIO_SECAO, "seção")
    j = t.find(FIM_SECAO, i) + len(FIM_SECAO)
    secao = t[i:j]
    t = t[:i] + t[j:]
    corpo = secao[len(INICIO_SECAO.split("\n")[0]) + 1:]          # sem a div de separação (margem/borda superior)
    corpo = corpo[:corpo.rfind("            </div>\n")]             # sem o fechamento dessa div
    corpo = corpo.replace('<div style="border:1px solid #e3e7ec;border-radius:10px;overflow:auto;max-height:300px">',
                          '<div class="sec-table-wrap" style="border:1px solid #e3e7ec;border-radius:10px;overflow:auto;max-height:300px">', 1)
    card_secao = "            " + CARD + "\n" + corpo + "            </div>\n"
    # 2) retira o card Antiguidade do acervo da grade de quatro colunas
    k = um(INICIO_IDADE, "antiguidade")
    fim = um(FIM_GRADE, "fim", k)
    idade = t[k:fim].rstrip() + "\n"
    t = t[:k] + t[fim:]
    # 3) nova linha logo depois da grade: Antiguidade (esquerda) · Processos por seção (direita)
    fim = um(FIM_GRADE, "fim")
    par = "          </div>\n          <div class=\"central-pair-grid\">\n" + idade + card_secao + "          "
    return t[:fim] + par + t[fim:]


# ---------------------------------------------------------------------------------------------------------------
# 3. Cards de processo do Acervo Central: ao abrir, mostram só os CONTROLES DE TRABALHO que existem na planilha
#    da Seleção Prévia (elaboração, registros, regularidade, parecer, alegações, contrarrazões, voto, julgamento).
#    Etiquetas, sigilo, partes e dados do processo continuam na visão em planilha e na própria Seleção Prévia.
# ---------------------------------------------------------------------------------------------------------------
CAMPOS_SELECAO = ('const PRE_CARD_WORK = ["Observações","Regularidade","Intercorrências","Tempestividade","Preparo",'
                  '"Impedimento / Suspeição","Representação","ID da Procuração","MPF","MPF - Custos Legis",'
                  '"ID do Parecer MPF","Alegações","Contrarrazões Ausentes","Prelim.","Descrição das Contrarrazões","Outras Peças",'
                  '"Voto","JULGAMENTO","Sessões","Tema","META","Dificuldade","Item (Pauta de Julgamento)"];')
CARDS = [
    ("const WORK_LEAD_COLUMNS = [", CAMPOS_SELECAO + "\nconst WORK_LEAD_COLUMNS = ["),
    ('hasTagsCell: open && (detailCols.includes("Etiquetas") || detailCols.includes("etiquetas")),', "hasTagsCell: false,"),
    ('draftCells: open ? ["SERVIDOR","MINUTADO"].filter(c => detailCols.includes(c)).map(c => this.cell(i,c)) : [],',
     'draftCells: open ? ["SERVIDOR","MINUTADO"].map(c => this.cell(i,c)) : [],'),
    ('reviewCells: open ? ["CORRETOR","CORRIGIDO","LIBERADO"].filter(c => detailCols.includes(c)).map(c => this.cell(i,c)) : [],',
     'reviewCells: open ? ["CORRETOR","CORRIGIDO","LIBERADO"].map(c => this.cell(i,c)) : [],'),
    ("workCells: open ? workCols.filter(c => !WORK_LEAD_COLUMNS.includes(c)).map(c => this.cell(i,c)) : [],",
     "workCells: open ? PRE_CARD_WORK.map(c => this.cell(i,c)) : [],"),
    ("hasWork: open && detailCols.some(c => WORK_COLUMNS.has(c)),", "hasWork: open,"),
    ("hasSigilo: open && detailCols.some(c => sigiloSet.has(c)),", "hasSigilo: false,"),
    ("hasParties: open && detailCols.some(c => partySet.has(c)),", "hasParties: false,"),
    ("details: open ? detailCols.filter(c => !WORK_COLUMNS.has(c) && !sigiloSet.has(c) && !partySet.has(c) && !specialSet.has(c)).map(c => this.cell(i,c)) : []",
     "details: []"),
]

# ---------------------------------------------------------------------------------------------------------------
# 4. Abertura: avisa quando o banco local terminou de carregar (a tela de carregamento some nesse momento).
# ---------------------------------------------------------------------------------------------------------------
ABERTURA = [
    ("componentDidMount() { window.__painelCentralComponent = this; this.loadDB(false); }",
     "componentDidMount() { window.__painelCentralComponent = this; Promise.resolve(this.loadDB(false)).catch(() => {}).finally(() => { window.__painelPronto = true; window.dispatchEvent(new Event(\"painel-pronto\")); }); }"),
]

# ---------------------------------------------------------------------------------------------------------------
# 5. Versão desempacotada: "Baixar HTML configurado" passa a funcionar também sem o empacotador.
# ---------------------------------------------------------------------------------------------------------------
HTML_PLANO = [
    ("""  sessionHtmlSource() {
    const source=window.__PANEL_BUNDLE_SOURCE;""",
     r"""  sessionHtmlSource() {
    if(window.__PANEL_FLAT_SOURCE){
      const seed={...this.portableConfig(),storageKey:'PainelCentralConfigurado_'+Date.now()+'_'+Math.random().toString(36).slice(2)};
      const seedText=JSON.stringify(seed).replace(/</g,'\\u003c');
      const t=window.__PANEL_FLAT_SOURCE.replace(/<script id="panel-config-seed" type="application\/json">[\s\S]*?<\/script>/,'');
      return t.replace('</head>','<script id="panel-config-seed" type="application/json">'+seedText+'<\/script></head>');
    }
    const source=window.__PANEL_BUNDLE_SOURCE;"""),
]

# ---------------------------------------------------------------------------------------------------------------
# 1b. Desempenho de tela: o verso do card Antiguidade (tempo na tarefa) e as Listas específicas desenhavam todas as
#     linhas mesmo ocultos — com 3.000 processos, dezenas de milhares de elementos. Passam a desenhar só quando abertos.
# ---------------------------------------------------------------------------------------------------------------
DESEMPENHO_TELA = [
    ("taskAgeRows:taskAge.list,", "taskAgeRows:s.ageReversed ? taskAge.list : [],"),
    ("});return {label,count:rows.length,empty:!rows.length,rows:rows.map(r=>({proc:r.Processo,",
     "});const open=!!(self._specOpen&&self._specOpen.has(label));"
     "return {label,count:rows.length,empty:!rows.length,open,"
     "toggle:e=>{const el=e&&e.currentTarget,o=el?!!el.open:!open;if(o===open)return;(self._specOpen||(self._specOpen=new Set()))[o?\"add\":\"delete\"](label);self.refresh();},"
     "rows:(open?rows:[]).map(r=>({proc:r.Processo,"),
    ('<sc-for list="{{ specificClasses }}" as="g"><details style="border:1px solid #dce4ed;border-radius:9px;margin-bottom:7px;overflow:hidden">',
     '<sc-for list="{{ specificClasses }}" as="g"><details open="{{ g.open }}" sc-camel-on-toggle="{{ g.toggle }}" style="border:1px solid #dce4ed;border-radius:9px;margin-bottom:7px;overflow:hidden">'),
]

# ---------------------------------------------------------------------------------------------------------------
# 7. Diálogo Configurações Globais: barra com título e botão Fechar; Esc e clique fora também fecham.
# ---------------------------------------------------------------------------------------------------------------
DIALOGO = [
    ('<div role="dialog" aria-modal="true" aria-label="Configurações Globais" style="position:fixed;inset:0;z-index:500;background:rgba(20,38,60,.55);display:grid;place-items:center;padding:16px"><iframe id="global-config-frame" title="Configurações Globais" style="width:min(1560px,98vw);height:95vh;border:1px solid #dce4ec;border-radius:14px;background:#fff;box-shadow:0 12px 60px #14263c45"></iframe></div>',
     '<div role="dialog" aria-modal="true" aria-label="Configurações Globais" sc-camel-on-click="{{ closeDialogBackdrop }}" style="position:fixed;inset:0;z-index:500;background:rgba(20,38,60,.55);display:grid;place-items:center;padding:16px">'
     '<div style="display:flex;flex-direction:column;width:min(1560px,98vw);height:95vh;border:1px solid #dce4ec;border-radius:14px;background:#fff;box-shadow:0 12px 60px #14263c45;overflow:hidden">'
     '<div style="flex:0 0 auto;display:flex;align-items:center;justify-content:space-between;gap:12px;padding:8px 10px 8px 16px;background:#1f3d63;color:#fff">'
     '<div style="font-size:12px;font-weight:850;letter-spacing:.06em">CONFIGURAÇÕES GLOBAIS</div>'
     '<button sc-camel-on-click="{{ closeDialog }}" title="Fechar (Esc)" aria-label="Fechar configurações" style="display:inline-flex;align-items:center;gap:6px;border:1px solid rgba(255,255,255,.35);border-radius:8px;background:rgba(255,255,255,.1);color:#fff;padding:6px 12px;font-size:11px;font-weight:850;letter-spacing:.04em;cursor:pointer">FECHAR <span aria-hidden="true" style="font-size:14px;line-height:1">×</span></button>'
     '</div>'
     '<iframe id="global-config-frame" title="Configurações Globais" sc-camel-on-load="{{ dialogFrameLoad }}" style="flex:1 1 auto;width:100%;min-height:0;border:0;background:#fff"></iframe></div></div>'),
    ("openDialog: () => self.setState({ dialog: true }), closeDialog: () => self.setState({ dialog: false }),",
     "openDialog: () => self.setState({ dialog: true }), closeDialog: () => self.setState({ dialog: false }), closeDialogBackdrop: e => { if (e && e.target === e.currentTarget) self.setState({ dialog: false }); }, dialogFrameLoad: e => { try { const w = e.target.contentWindow; if (w && !w.__escFecha) { w.__escFecha = true; w.addEventListener('keydown', ev => { if (ev.key === 'Escape') self.setState({ dialog: false }); }); } } catch (_) {} },"),
    ("componentDidMount() { window.__painelCentralComponent = this; Promise",
     "componentDidMount() { window.__painelCentralComponent = this; if (!this.__escFecha) { this.__escFecha = e => { if (e.key === \"Escape\" && this.state.dialog) this.setState({ dialog: false }); }; window.addEventListener(\"keydown\", this.__escFecha); } Promise"),
]

import triagem  # noqa: E402  (aba Triagem Processual e escaninhos)
import banco_dialogo  # noqa: E402  (diálogo Banco do Acervo Geral)
import busca_incluir  # noqa: E402  (botão + INCLUIR na busca)

AJUSTES = [("desempenho", DESEMPENHO), ("desempenho-tela", DESEMPENHO_TELA), ("cards", CARDS), ("abertura", ABERTURA), ("html-plano", HTML_PLANO), ("dialogo", DIALOGO), ("triagem", triagem.PATCHES), ("busca", busca_incluir.PATCHES)]


# ---------------------------------------------------------------------------------------------------------------
# 6. Seleção Prévia › Planejamento da sessão (01 · Marcos em uma linha; 02 · simulador com metas dinâmicas).
#    A página de planejamento é texto dentro da página da Seleção Prévia, que vai compactada dentro do painel.
# ---------------------------------------------------------------------------------------------------------------
def ajustar_planejamento(template: str) -> str:
    import base64, gzip, json
    import planejamento
    marca = 'const b=Uint8Array.from(atob("'
    i = template.find(marca)
    if i < 0 or template.find(marca, i + 1) >= 0 and "__PRE_PANEL_HTML" not in template[i:i + 4000000]:
        raise SystemExit("melhorias/planejamento: página da Seleção Prévia não encontrada.")
    ini = i + len(marca)
    fim = template.index('"', ini)
    pre = gzip.decompress(base64.b64decode(template[ini:fim])).decode("utf-8")
    if "window.__PRE_PANEL_HTML" not in template[fim:fim + 400]:
        raise SystemExit("melhorias/planejamento: o primeiro bloco compactado não é a Seleção Prévia.")
    alvo = pre.find("Planejamento da sessão · Marcos e Simulador")
    k = pre.rfind('const source="', 0, alvo)
    if alvo < 0 or k < 0:
        raise SystemExit("melhorias/planejamento: página de planejamento não encontrada na Seleção Prévia.")
    k += len("const source=")
    texto, fim_txt = json.JSONDecoder().raw_decode(pre, k)
    novo = planejamento.aplicar(texto)
    cod = json.dumps(novo, ensure_ascii=False).replace("</", "<\\/")
    pre = pre[:k] + cod + pre[fim_txt:]
    # painel compacto da Seleção Prévia (layout da prévia sobre os dados reais; visão clássica preservada)
    from pathlib import Path
    pasta = Path(__file__).parent
    css = (pasta / "selecao_compacta.css").read_text(encoding="utf-8")
    js = (pasta / "selecao_compacta.js").read_text(encoding="utf-8").replace("</script", "<\\/script")
    # sem clarão: antes de qualquer pintura, as camadas legadas ficam ocultas e a página só aparece após o 1º desenho
    guarda = ("<style id=\"sp2-guarda\">#selection-planning-frame{display:none!important}"
              "html:not(.sp2-classico) #controle-pauta-root{display:none!important}"
              "html:not(.sp2-pronto) body{visibility:hidden}</style>"
              "<script>setTimeout(function(){var h=document.documentElement;if(!h.classList.contains('sp2-pronto'))"
              "h.classList.add('sp2-pronto','sp2-classico');},5000);</script>")
    fim_head = pre.find("</head>")
    if fim_head < 0:
        raise SystemExit("melhorias/planejamento: </head> não encontrado na Seleção Prévia.")
    pre = pre[:fim_head] + guarda + pre[fim_head:]
    fim_body = pre.rindex("</body>")
    pre = pre[:fim_body] + "<style id=\"sp2-css\">" + css + "</style><script>" + js + "</script>" + pre[fim_body:]
    b64 = base64.b64encode(gzip.compress(pre.encode("utf-8"), 9)).decode()
    return template[:ini] + b64 + template[fim:]


def ajustar_configuracoes(template: str) -> str:
    """Configurações Globais (outro HTML compactado): injeta a aba única "Gabinete", só leitura (config_gabinete.js)."""
    import base64, gzip
    from pathlib import Path
    i = template.find("frame=document.getElementById('global-config-frame')")
    ini = template.rfind('atob("', 0, i) + len('atob("')
    if i < 0 or ini < len('atob("'):
        raise SystemExit("melhorias/configuracoes: página das Configurações Globais não encontrada.")
    fim = template.index('"', ini)
    html = gzip.decompress(base64.b64decode(template[ini:fim])).decode("utf-8")
    if "installGlobalConfigBridge" not in html:
        raise SystemExit("melhorias/configuracoes: o bloco compactado não é o das Configurações Globais.")
    js = (Path(__file__).parent / "config_gabinete.js").read_text(encoding="utf-8").replace("</script", "<\\/script")
    k = html.rindex("</body>")
    html = html[:k] + "<script>" + js + "</script>" + html[k:]
    b64 = base64.b64encode(gzip.compress(html.encode("utf-8"), 9)).decode()
    return template[:ini] + b64 + template[fim:]


def aplicar(template: str) -> str:
    template = reorganizar_cards(template)
    template = ajustar_configuracoes(template)
    template = ajustar_planejamento(template)
    template = banco_dialogo.aplicar(template)
    ancora = "    .central-stats-stack{display:grid;gap:14px;min-width:0}"
    template = template.replace(ancora, banco_dialogo.CSS + ancora, 1)
    for grupo, trocas in AJUSTES:
        for i, (antigo, novo) in enumerate(trocas, 1):
            n = template.count(antigo)
            if n != 1:
                raise SystemExit(f"melhorias/{grupo} #{i}: trecho encontrado {n} vez(es) — o painel mudou; revise o ajuste.\n{antigo[:160]}")
            template = template.replace(antigo, novo)
    return template
