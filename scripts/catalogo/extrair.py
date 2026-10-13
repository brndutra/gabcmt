"""Lê a saída persistida de get_page_text, extrai o lote entre <<INI>> e <<FIM>>,
grava lotes/pagina-NN.json para cada página e atualiza o catálogo (acumular.py).
Uso: python3 extrair.py <arquivo-tool-result>"""
import json
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).parent
blocos = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
texto = "".join(b.get("text", "") for b in blocos if isinstance(b, dict))
ini, fim = texto.find("<<INI>>"), texto.find("<<FIM>>")
if ini < 0 or fim < 0:
    sys.exit(f"marcadores não encontrados (ini={ini}, fim={fim}); leitura truncada")
paginas = json.loads(texto[ini + 7:fim])
(BASE / "lotes").mkdir(exist_ok=True)
gravados = []
for pg in paginas:
    dados = pg["itens"]
    dest = BASE / "lotes" / f"pagina-{pg['p']:02d}.json"
    dest.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    gravados.append(str(dest))
    julgs = sorted(d["julg"][6:] + d["julg"][3:5] + d["julg"][:2] for d in dados if d.get("julg"))
    print(f"página {pg['p']}: {len(dados)} acórdãos, {sum(1 for d in dados if not d.get('ementa'))} sem ementa, "
          f"julgados {julgs[0] if julgs else '?'}…{julgs[-1] if julgs else '?'}")
print(subprocess.run([sys.executable, str(BASE / "acumular.py"), *gravados], capture_output=True, text=True).stdout.strip())
