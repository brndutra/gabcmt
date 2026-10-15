"""Monta painel.html (Painel Central do acervo) a partir da versão baixada do app.

Uso:
    python3 scripts/painel/montar.py [PAINEL_BAIXADO.html] [--saida painel.html]

Sem argumento, usa scripts/painel/original/painel-central.html (a versão baixada do app guardada no repositório).

O app entrega o painel empacotado: um manifesto com os recursos em base64+gzip e um template que só existe depois
que o navegador descompacta tudo (enquanto isso aparece um logotipo gigante com "Unpacking..."). Este script:
  1. aplica os ajustes de scripts/painel/melhorias.py (desempenho, layout, cards de processo);
  2. injeta o módulo scripts/painel/acervo-github.js (banco/acervo.json no GitHub);
  3. grava um HTML DESEMPACOTADO: React, runtime, planilhas e fontes vão embutidos direto, sem etapa de
     descompactação, com uma tela de abertura discreta até o banco local terminar de carregar.
Rode de novo sempre que baixar uma versão nova do painel.
"""
import base64
import gzip
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import melhorias  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
MODULO = Path(__file__).with_name("acervo-github.js")
TITULO = "Painel Central · Acervo, Seleção e Pauta · Gabinete A"


def bloco(fonte, tipo):
    m = re.search(r'<script type="__bundler/%s">(.*?)</script>' % re.escape(tipo), fonte, re.S)
    return m.group(1) if m else None


def js_inline(codigo: str) -> str:
    return "<script>" + codigo.replace("</script", "<\\/script") + "</script>"


ABERTURA_CSS = """<style id="painel-abertura-css">
#painel-abertura{position:fixed;inset:0;z-index:9000;display:grid;place-items:center;background:#eff1f4;transition:opacity .25s ease}
#painel-abertura.saindo{opacity:0;pointer-events:none}
#painel-abertura .pa{display:flex;align-items:center;gap:14px;padding:18px 22px;border-radius:14px;background:#fff;border:1px solid #e3e7ec;box-shadow:0 10px 30px rgba(20,38,60,.08);font-family:'Figtree',system-ui,sans-serif;color:#14263c}
#painel-abertura .pl{width:40px;height:40px;border-radius:11px;background:#d9a441;color:#33240a;display:grid;place-items:center;font-weight:900;font-size:14px}
#painel-abertura b{display:block;font-size:14px;font-weight:850}#painel-abertura span{display:block;font-size:11px;color:#6d7b8a;margin-top:2px}
#painel-abertura .pb{height:3px;width:150px;margin-top:8px;border-radius:9px;background:#e3e7ec;overflow:hidden}
#painel-abertura .pb i{display:block;height:100%;width:40%;border-radius:9px;background:#1f3d63;animation:paMov 1.1s ease-in-out infinite}
@keyframes paMov{0%{transform:translateX(-100%)}100%{transform:translateX(260%)}}
@media(prefers-reduced-motion:reduce){#painel-abertura .pb i{animation:none;width:100%}}
</style>"""
ABERTURA_HTML = """<div id="painel-abertura" role="status" aria-live="polite"><div class="pa"><div class="pl">PC</div><div><b>Painel Central</b><span>Carregando o acervo deste navegador…</span><div class="pb"><i></i></div></div></div></div>
<script>(function(){var el=document.getElementById("painel-abertura");function fim(){if(!el||el.classList.contains("saindo"))return;el.classList.add("saindo");setTimeout(function(){el.style.display="none"},300)}
if(window.__painelPronto)fim();window.addEventListener("painel-pronto",fim);window.addEventListener("error",function(){setTimeout(fim,1500)});setTimeout(fim,45000);})();</script>"""


def inicializacao(recursos: dict) -> str:
    """Recursos que o runtime pede por nome (componentes .dc.html) + captura do HTML para "Baixar HTML configurado"."""
    # "<" escapado: o texto embutido não pode conter "</head>" nem "<body>" literais (o HTML configurado procura esses marcos)
    adds = "".join(f"add({json.dumps(k)},{json.dumps(v).replace('<', chr(92) + 'u003c')},'text/html');" for k, v in recursos.items())
    codigo = (
        "(function(){var R={},B={};function add(id,t,ty){var b=new Blob([t],{type:ty});var u=URL.createObjectURL(b);R[id]=u;B[u]=b}"
        + adds +
        "window.__resources=R;window.__resourceBlobs=B;window.__PANEL_FLAT=true;"
        # elementos criados por script antes do DOMContentLoaded (estilos do runtime, botão do acervo) não entram na cópia
        "var dyn=[],ce=Document.prototype.createElement;Document.prototype.createElement=function(){var e=ce.apply(this,arguments);dyn.push(e);return e};"
        "document.addEventListener('DOMContentLoaded',function(){Document.prototype.createElement=ce;var mv=[];"
        "dyn.forEach(function(e){if(e.parentNode){mv.push([e,e.parentNode,e.nextSibling]);e.parentNode.removeChild(e)}});"
        "var ab=document.getElementById('painel-abertura');if(ab){ab.classList.remove('saindo');ab.style.display=''}"
        "window.__PANEL_FLAT_SOURCE='<!DOCTYPE html>\\n'+document.documentElement.outerHTML;"
        "for(var i=mv.length-1;i>=0;i--){var m=mv[i];m[1].insertBefore(m[0],m[2]&&m[2].parentNode===m[1]?m[2]:null)}dyn=null},{once:true});})();"
    )
    return js_inline(codigo)


def montar(origem: Path, saida: Path):
    fonte = origem.read_text(encoding="utf-8")
    manifesto, tpl, ext = bloco(fonte, "manifest"), bloco(fonte, "template"), bloco(fonte, "ext_resources")
    if not manifesto or not tpl:
        sys.exit(f"{origem}: não é o HTML empacotado do Painel Central (faltam manifest/template)")
    manifesto, template = json.loads(manifesto), json.loads(tpl)
    ext = json.loads(ext) if ext else []
    if "__painelCentralComponent" not in template:
        sys.exit(f"{origem}: o template não contém o Painel Central (__painelCentralComponent)")
    if "function __memo(" in template:
        sys.exit(f"{origem}: este painel já foi montado; use o original baixado do app")

    def conteudo(uuid):
        e = manifesto[uuid]
        d = base64.b64decode(e["data"])
        return (gzip.decompress(d) if e.get("compressed") else d), e["mime"]

    # 1. ajustes e módulo do acervo
    template = melhorias.aplicar(template)
    js = MODULO.read_text(encoding="utf-8")
    if "</script" in js.lower():
        sys.exit("acervo-github.js não pode conter </script>")
    fim = template.rfind("</body>")
    template = template[:fim] + '<script id="acervo-github">\n' + js + "</script>\n" + template[fim:]

    # 2. recursos embutidos no lugar dos identificadores do manifesto
    por_id = {e["id"]: e["uuid"] for e in ext}
    react = conteudo(por_id["https://unpkg.com/react@18.3.1/umd/react.production.min.js"])[0].decode()
    react_dom = conteudo(por_id["https://unpkg.com/react-dom@18.3.1/umd/react-dom.production.min.js"])[0].decode()
    componentes = {k: conteudo(u)[0].decode() for k, u in por_id.items() if k.endswith(".dc.html")}
    for uuid in manifesto:
        if uuid not in template:
            continue
        dados, mime = conteudo(uuid)
        tag = f'<script src="{uuid}"></script>'
        if tag in template:
            template = template.replace(tag, js_inline(dados.decode()))
        else:
            template = template.replace(uuid, f"data:{mime};base64,{base64.b64encode(dados).decode()}")
    restantes = [u for u in manifesto if u in template]
    if restantes:
        sys.exit(f"recursos não resolvidos no template: {restantes}")

    # 3. cabeçalho: título, inicialização, React antes do runtime; abertura no início do corpo
    corpo = re.search(r"<body[^>]*>", template)      # antes de embutir textos que também contêm "<body>"
    template = template[:corpo.end()] + "\n" + ABERTURA_HTML + "\n" + template[corpo.end():]
    cab = re.search(r"<head[^>]*>", template)
    template = (template[:cab.end()] + f"\n<title>{TITULO}</title>\n" + inicializacao(componentes) + "\n"
                + js_inline(react) + "\n" + js_inline(react_dom) + "\n" + ABERTURA_CSS + "\n" + template[cab.end():])
    template = re.sub(r"<html(?=[\s>])", '<html style="background:#eff1f4"', template, count=1)   # sem clarão branco na abertura
    if not template.lstrip().lower().startswith("<!doctype"):
        template = "<!DOCTYPE html>\n" + template
    saida.write_text(template, encoding="utf-8")
    rel = saida.relative_to(RAIZ) if saida.is_relative_to(RAIZ) else saida
    print(f"{rel}: {len(template.encode()):,} bytes · desempacotado · ajustes e módulo do acervo aplicados")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0].startswith("-"):
        args = [str(Path(__file__).parent / "original" / "painel-central.html"), *args]
    saida = RAIZ / "painel.html"
    if "--saida" in args:
        saida = Path(args[args.index("--saida") + 1]).resolve()
    montar(Path(args[0]), saida)
