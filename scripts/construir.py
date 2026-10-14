"""Reconstrói tudo o que o repositório publica, a partir das exportações do app e da base de acórdãos.

Uso:
    python3 scripts/construir.py [EXPORTAÇÕES.json ...] [--substituir]

Etapas:
  1. importa as exportações para banco/ (scripts/banco/importar.py), sem duplicar;
  2. regenera o catálogo de acórdãos (scripts/catalogo/acumular.py), marcando o que já consta do banco;
  3. monta catalogo-trf3/<assunto>/<tema>.json só com o que ainda NÃO está no banco (scripts/catalogo/organizar.py);
  4. regrava o index.html.
Assim, cada precedente aparece uma única vez: ou em banco/precedentes.json (curado, lido pelo construtor.html),
ou no catálogo bruto de acórdãos do TRF3 (catalogo-trf3/), à espera de curadoria.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CAT = RAIZ / "scripts" / "catalogo"


def rodar(*cmd):
    r = subprocess.run([sys.executable, *map(str, cmd)], capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode:
        sys.exit(r.stderr)


def main(args):
    arquivos = [a for a in args if not a.startswith("--")]
    if arquivos:
        rodar(RAIZ / "scripts" / "banco" / "importar.py", *arquivos, *[a for a in args if a.startswith("--")])
    shutil.copy(RAIZ / "catalogo-trf3" / "acordaos.jsonl", CAT / "acordaos.jsonl")
    try:
        rodar(CAT / "acumular.py")
    finally:
        (CAT / "acordaos.jsonl").unlink(missing_ok=True)
    rodar(CAT / "organizar.py", CAT / "catalogo-agrupado.json", RAIZ / "catalogo-trf3")

    html = (CAT / "tabela-acordaos-carlos-muta.html").read_text(encoding="utf-8")
    fim_titulo = html.index("</title>") + 8
    cab, corpo = html[:fim_titulo], html[fim_titulo:]
    antigo = ("if(!dl){mostrarJson(txt);msg('O download não está disponível nesta visualização. "
              "Copie o JSON abaixo e salve como precedentes.json.',true);return}")
    novo = ("if(!dl){const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([txt],{type:'application/json'}));"
            "a.download='precedentes.json';document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove()},800);"
            "msg(`precedentes.json com ${n} registro(s). No app, abra o Banco de Paradigmas › Precedentes › Importar JSON.`);return}")
    corpo = corpo.replace(antigo, novo)
    j = corpo.index("</style>") + 8
    (RAIZ / "index.html").write_text(
        '<!doctype html>\n<html lang="pt-BR">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        + cab + "\n" + corpo[:j] + "\n</head>\n<body>\n" + corpo[j:] + "\n</body>\n</html>\n", encoding="utf-8")
    print("index.html regravado")


if __name__ == "__main__":
    main(sys.argv[1:])
