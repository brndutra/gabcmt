"""Diálogo "Banco do Acervo Geral" — reúne num só lugar o que estava espalhado:

- a página Importar / atualizar inteira (planilha principal, importação em lote, suplementares Sigilosos e PJe 2G,
  registro e download dos arquivos importados, regras do merge);
- as exportações do bloco OPERAÇÕES da barra lateral (Excel completo e acervo sem controles);
- a sincronização com banco/acervo.json no GitHub (renderizada por acervo-github.js no espaço #acv-gh-slot);
- os avisos e as ocorrências de importação, que antes ficavam atrás, na página.

Na barra lateral, o bloco OPERAÇÕES dá lugar a um único botão que abre o diálogo; o botão flutuante
ACERVO · GITHUB também o abre.
"""

LIMPAR_SOLTO = ('<button sc-camel-on-click="{{ openClearDialog }}" disabled="{{ storageBusy }}" title="Limpar dados deste painel no navegador" '
                'style="grid-column:1/-1;border:1px solid rgba(255,255,255,.16);border-radius:10px;background:transparent;color:#e5b3b3;padding:8px;cursor:pointer">⌫</button>')

SEC = "border-radius:10px;background:#fff;border:1px solid #e3e7ec;box-shadow:0 10px 26px rgba(20,38,60,.04)"
EXP_CARD = "display:flex;flex-direction:column;align-items:flex-start;gap:4px;border:1px solid #dee3e9;border-radius:10px;background:#fafbfc;padding:13px 14px;text-align:left;cursor:pointer;color:#14263c"

BOTAO_LATERAL = """      <div style="font-size:8.5px;font-weight:850;letter-spacing:.11em;color:#8fa9c0;padding:0 8px 7px">ACERVO</div>
      <div style="display:grid;gap:4px">
        <button sc-camel-on-click="{{ goImport }}" title="Importar, atualizar, exportar e sincronizar com o GitHub" style="display:flex;align-items:center;gap:9px;border:1px solid {{ importNavBorder }};cursor:pointer;border-radius:10px;padding:10px 11px;font-weight:750;font-size:11.5px;background:{{ importNavBg }};color:{{ importNavFg }};text-align:left"><span style="width:18px;text-align:center">⛁</span><span style="display:grid;gap:1px"><span>Banco do Acervo Geral</span><span style="font-size:8.5px;font-weight:700;opacity:.75">importar · exportar · GitHub</span></span></button>
      </div>"""


def aplicar(t: str) -> str:
    def uma(trecho, nome, desde=0):
        i = t.find(trecho, desde)
        if i < 0:
            raise SystemExit(f"banco_dialogo: '{nome}' não encontrado — o painel mudou; revise o ajuste.")
        return i

    # 1) handlers: o "Importar / atualizar" passa a abrir o diálogo
    antigo = 'goImport: () => self.setState({ tab: "import" }),'
    if t.count(antigo) != 1:
        raise SystemExit("banco_dialogo: goImport não encontrado")
    t = t.replace(antigo, 'goImport: () => self.setState({ acervoDialog: true }),\n      acervoDialogOpen: !!s.acervoDialog, closeAcervo: () => self.setState({ acervoDialog: false }), closeAcervoBackdrop: e => { if (e && e.target === e.currentTarget) self.setState({ acervoDialog: false }); },')
    for a, b in (('importNavBg: s.tab === "import" ? "#d9a441"', 'importNavBg: s.acervoDialog ? "#d9a441"'),
                 ('importNavFg: s.tab === "import" ? "#33240a"', 'importNavFg: s.acervoDialog ? "#33240a"'),
                 ('importNavBorder: s.tab === "import" ? "#d9a441"', 'importNavBorder: s.acervoDialog ? "#d9a441"')):
        if t.count(a) != 1:
            raise SystemExit(f"banco_dialogo: {a[:30]} não encontrado")
        t = t.replace(a, b)

    # 2) barra lateral recolhida: um ícone só (abre o diálogo)
    i = uma('<button sc-camel-on-click="{{ goImport }}" title="Importar / atualizar"', "ícone importar")
    t = t[:i] + t[i:].replace('title="Importar / atualizar"', 'title="Banco do Acervo Geral — importar, exportar, GitHub"', 1)
    i = t.find('>⇧</button>', i)
    t = t[:i] + '>⛁</button>' + t[i + len('>⇧</button>'):]
    j = uma('<button sc-camel-on-click="{{ exportAll }}" title="Exportar Excel completo" style="display:grid;place-items:center;height:44px', "ícone exportar")
    t = t[:j] + t[t.index('</button>', j) + 9:]

    # 3) barra lateral expandida: bloco OPERAÇÕES → botão único
    k = uma('      <div style="font-size:8.5px;font-weight:850;letter-spacing:.11em;color:#8fa9c0;padding:0 8px 7px">OPERAÇÕES</div>', "OPERAÇÕES")
    m = uma('<div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:16px">', "estatísticas", k)
    t = t[:k] + BOTAO_LATERAL + "\n\n      " + t[m:]

    # 4) página Importar / atualizar → diálogo
    ini = uma('<sc-if value="{{ isImport }}" hint-placeholder-val="{{ false }}">', "página importar")
    fim = uma('\n    <sc-if value="{{ isCentral }}" hint-placeholder-val="{{ true }}">', "fim da página importar", ini)
    bloco = t[ini:fim].rstrip()
    corpo = bloco[bloco.index(">") + 1: bloco.rindex("</sc-if>")]
    corpo = corpo.replace(LIMPAR_SOLTO, "")                         # botões ⌫ soltos dentro dos cartões de arquivo
    corpo = corpo.replace("animation:riseIn .18s ease", "")
    q = uma('<sc-if value="{{ hasImportIssues }}">', "ocorrências")
    ocorrencias = t[q: t.index("</sc-if>", q) + 8]
    aviso = ('<sc-if value="{{ hasNotice }}" hint-placeholder-val="{{ false }}"><div style="display:flex;align-items:center;justify-content:space-between;gap:12px;border-radius:9px;padding:11px 14px;font-size:12px;font-weight:600;background:{{ noticeBg }};color:{{ noticeFg }}">'
             '<span>{{ noticeMsg }}</span><button sc-camel-on-click="{{ clearNotice }}" style="border:0;background:transparent;color:inherit;font-size:15px;font-weight:800;cursor:pointer">×</button></div></sc-if>')
    dialogo = f"""<sc-if value="{{{{ acervoDialogOpen }}}}" hint-placeholder-val="{{{{ false }}}}">
      <div role="dialog" aria-modal="true" aria-label="Banco do Acervo Geral" sc-camel-on-click="{{{{ closeAcervoBackdrop }}}}" style="position:fixed;inset:0;z-index:245;background:rgba(20,38,60,.55);display:grid;place-items:center;padding:16px">
       <div style="display:flex;flex-direction:column;width:min(1180px,97vw);max-height:94vh;border-radius:14px;background:#eff1f4;overflow:hidden;box-shadow:0 24px 70px rgba(20,38,60,.35)">
        <div style="flex:0 0 auto;display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px 14px 12px 18px;background:linear-gradient(135deg,#1f3d63,#16304e);color:#fff">
          <div style="min-width:0"><div style="font-size:10px;font-weight:900;letter-spacing:.1em;color:#e9c46a">BANCO DO ACERVO GERAL</div><div style="font-size:15px;font-weight:850;margin-top:2px">brndutra/gabcmt · banco/acervo.json</div><div style="font-size:10.5px;color:#cddbe8;margin-top:2px">{{{{ statRows }}}} processo(s) neste navegador · importar planilhas, exportar e sincronizar com o GitHub</div></div>
          <button sc-camel-on-click="{{{{ closeAcervo }}}}" title="Fechar (Esc)" aria-label="Fechar o Banco do Acervo Geral" style="flex:0 0 auto;display:inline-flex;align-items:center;gap:6px;border:1px solid rgba(255,255,255,.35);border-radius:8px;background:rgba(255,255,255,.1);color:#fff;padding:7px 12px;font-size:11px;font-weight:850;letter-spacing:.04em;cursor:pointer">FECHAR <span aria-hidden="true" style="font-size:14px;line-height:1">×</span></button>
        </div>
        <div style="flex:1 1 auto;min-height:0;overflow:auto;padding:14px;display:grid;gap:14px;align-content:start">
          {aviso}
          {ocorrencias}
          <div style="display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,.75fr);gap:14px" class="acv-dlg-topo">
            <section style="{SEC};padding:16px 18px">
              <div style="font-size:9.5px;font-weight:900;letter-spacing:.09em;color:#1f3d63">GITHUB · BANCO COMPARTILHADO</div>
              <div style="font-size:14px;font-weight:850;color:#14263c;margin-top:3px">Sincronização com banco/acervo.json</div>
              <div id="acv-gh-slot" style="margin-top:10px"></div>
            </section>
            <section style="{SEC};padding:16px 18px;display:grid;gap:9px;align-content:start">
              <div><div style="font-size:9.5px;font-weight:900;letter-spacing:.09em;color:#1f3d63">EXPORTAR</div><div style="font-size:14px;font-weight:850;color:#14263c;margin-top:3px">Planilhas do acervo</div></div>
              <button sc-camel-on-click="{{{{ exportAll }}}}" style="{EXP_CARD}"><span style="font-size:11.5px;font-weight:850">⇩ Exportar XLSX completo</span><span style="font-size:10px;color:#6d7b8a;line-height:1.4">Acervo Central, Seleção Prévia, pauta e estatísticas, com os controles de trabalho.</span></button>
              <button sc-camel-on-click="{{{{ exportWithoutControls }}}}" disabled="{{{{ storageBusy }}}}" style="{EXP_CARD}"><span style="font-size:11.5px;font-weight:850">⇩ Exportar acervo sem controles</span><span style="font-size:10px;color:#6d7b8a;line-height:1.4">Todos os processos e dados processuais, inclusive colunas ocultas, sem os controles de trabalho.</span></button>
              <button sc-camel-on-click="{{{{ openClearDialog }}}}" disabled="{{{{ storageBusy }}}}" style="justify-self:start;border:1px solid #ecc9c9;border-radius:8px;background:#fff;color:#a64f35;padding:7px 11px;font-size:10px;font-weight:850;cursor:pointer">⌫ Limpar dados deste navegador…</button>
            </section>
          </div>
{corpo}
        </div>
       </div>
      </div>
    </sc-if>"""
    return t[:ini] + dialogo + t[fim:]


CSS = "    @media(max-width:900px){.acv-dlg-topo{grid-template-columns:minmax(0,1fr)!important}}\n"
