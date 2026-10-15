"""Acervo Central › Busca · Filtro · Seleção: botão "+ INCLUIR" nos modos TEXTO e LOTE.

- TEXTO: o termo digitado vira um critério fixo da busca (chip em CRITÉRIOS ATIVOS, "busca · …"), que procura em
  todas as colunas visíveis como a busca livre; o campo fica livre para outro termo e os critérios valem juntos.
  Enter no campo faz o mesmo.
- LOTE: os números CNJ colados são ACRESCENTADOS ao lote ativo (APLICAR continua substituindo o lote).
"""

BTN = ("flex:0 0 auto;border:0;cursor:pointer;border-radius:7px;padding:7px 11px;font-weight:900;font-size:10.5px;"
       "background:#d9a441;color:#33240a;white-space:nowrap")

PATCHES = [
    # critério de busca livre (todas as colunas visíveis)
    ("  criterionMatch(r, c) {\n    const originalField=",
     "  criterionMatch(r, c) {\n"
     "    if (c.column === \"__busca__\") { const vals=(c.values||[]).map(canon).filter(Boolean); "
     "const hit=n=>Object.entries(r||{}).some(([k,v])=>isVisibleColumn(k)&&fieldKey(k)!==\"etiquetasoriginais\"&&canon(v).includes(n)); "
     "return !vals.length || (c.combine===\"all\"?vals.every(hit):vals.some(hit)); }\n"
     "    const originalField="),
    ("label: c.grupo ? `tarefa: ${c.grupo} ×` :",
     "label: c.column === \"__busca__\" ? `busca · “${short}” ×` : c.grupo ? `tarefa: ${c.grupo} ×` :"),
    # handlers
    ("      hasBatch: (s.batchProcesses || []).length > 0,",
     "      includeSearch: () => {\n"
     "        const term = txt(s.search);\n"
     "        if (!term) return self.notify(\"Digite um termo para incluir na busca.\", \"warn\");\n"
     "        if (self.criteria.some(c => c.column === \"__busca__\" && (c.values || []).some(v => canon(v) === canon(term)))) { self.setState({ search: \"\" }); return self.notify(`O termo “${term}” já está entre os critérios ativos.`, \"warn\"); }\n"
     "        self.criteria.push({ column: \"__busca__\", op: \"contains\", values: [term], combine: \"any\" });\n"
     "        self.setState({ search: \"\", limit: 60 });\n"
     "        self.notify(`“${term}” incluído na busca — digite outro termo para refinar.`);\n"
     "      },\n"
     "      onSearchKey: e => { if (e.key === \"Enter\") { e.preventDefault(); self.renderVals().includeSearch(); } },\n"
     "      includeBatch: () => {\n"
     "        const raw = String(s.batchInput || \"\");\n"
     "        const found = raw.match(/\\b\\d{7}-\\d{2}\\.\\d{4}\\.\\d\\.\\d{2}\\.\\d{4}\\b/g) || [];\n"
     "        if (!found.length) return self.notify(\"Nenhum número CNJ reconhecido na lista colada.\", \"warn\");\n"
     "        const atual = s.batchProcesses || [], mapa = new Map(atual.map(v => [procId(v), v])), antes = mapa.size;\n"
     "        found.forEach(v => { if (!mapa.has(procId(v))) mapa.set(procId(v), v); });\n"
     "        self.setState({ batchProcesses: [...mapa.values()], batchInput: \"\", limit: 60 });\n"
     "        self.notify(`${mapa.size - antes} processo(s) incluído(s) no lote · ${mapa.size} no total.`);\n"
     "      },\n"
     "      hasBatch: (s.batchProcesses || []).length > 0,"),
    # botões
    ('<input value="{{ search }}" sc-camel-on-input="{{ onSearch }}" placeholder="Buscar em todo o Acervo Central…" style="flex:1;min-width:0;border:0;background:transparent;padding:6px 6px;font-size:12px;font-weight:550;color:#14263c;outline:none">',
     '<input value="{{ search }}" sc-camel-on-input="{{ onSearch }}" sc-camel-on-key-down="{{ onSearchKey }}" placeholder="Buscar em todo o Acervo Central… (Enter inclui o termo como critério)" style="flex:1;min-width:0;border:0;background:transparent;padding:6px 6px;font-size:12px;font-weight:550;color:#14263c;outline:none">'
     '<button sc-camel-on-click="{{ includeSearch }}" title="Incluir o termo como critério da busca (Enter)" style="' + BTN + '">+ INCLUIR</button>'),
    ('<button sc-camel-on-click="{{ applyBatch }}" title="Aplicar lista de processos colada"',
     '<button sc-camel-on-click="{{ includeBatch }}" title="Acrescentar estes processos ao lote ativo" style="' + BTN + '">+ INCLUIR</button>'
     '<button sc-camel-on-click="{{ applyBatch }}" title="Substituir o lote ativo por esta lista"'),
]
