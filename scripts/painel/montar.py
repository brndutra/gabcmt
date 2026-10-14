"""Monta painel.html (Painel Central do acervo) com o módulo do banco do acervo no GitHub.

Uso:
    python3 scripts/painel/montar.py PAINEL_BAIXADO.html [--saida painel.html]

O Painel Central é um HTML empacotado (manifesto + template). Este script injeta no template o módulo
scripts/painel/acervo-github.js, que liga o Acervo Central a banco/acervo.json:
  - ao abrir, o painel lê o banco e mescla no Acervo Central;
  - cada importação de planilha (ou de um acervo.html/acervo.json) atualiza o banco no GitHub.
Rode de novo sempre que baixar uma versão nova do painel: a injeção anterior é substituída, não duplicada.
"""
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
MODULO = Path(__file__).with_name("acervo-github.js")
TITULO = "Painel Central · Acervo, Seleção e Pauta · Gabinete A"
RX_TEMPLATE = re.compile(r'(<script type="__bundler/template">)(.*?)(</script>)', re.S)
RX_INJECAO = re.compile(r'<script id="acervo-github">.*?</script>\n?', re.S)


def montar(origem: Path, saida: Path):
    fonte = origem.read_text(encoding="utf-8")
    m = RX_TEMPLATE.search(fonte)
    if not m:
        sys.exit(f"{origem}: não é o HTML empacotado do Painel Central (falta __bundler/template)")
    template = json.loads(m.group(2))
    if "__painelCentralComponent" not in template:
        sys.exit(f"{origem}: o template não contém o Painel Central (__painelCentralComponent)")
    js = MODULO.read_text(encoding="utf-8")
    if "</script" in js.lower():
        sys.exit("acervo-github.js não pode conter </script>")
    template = RX_INJECAO.sub("", template)
    fim = template.rfind("</body>")
    if fim < 0:
        sys.exit("template sem </body>")
    template = template[:fim] + '<script id="acervo-github">\n' + js + "</script>\n" + template[fim:]
    codificado = json.dumps(template, ensure_ascii=False).replace("</script", "<\\/script")
    fonte = fonte[:m.start(2)] + codificado + fonte[m.end(2):]
    fonte = re.sub(r"<title>Bundled Page</title>", f"<title>{TITULO}</title>", fonte, count=1)
    saida.write_text(fonte, encoding="utf-8")
    print(f"{saida.relative_to(RAIZ) if saida.is_relative_to(RAIZ) else saida}: {len(fonte):,} bytes · módulo do acervo injetado")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0].startswith("-"):
        sys.exit(__doc__)
    saida = RAIZ / "painel.html"
    if "--saida" in args:
        saida = Path(args[args.index("--saida") + 1]).resolve()
    montar(Path(args[0]), saida)
