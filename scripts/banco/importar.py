"""Importa as exportações do Construtor de Minutas (schemas gabA.*) para a pasta banco/ do repositório, sem duplicar.

Uso:
    python3 scripts/banco/importar.py ARQUIVO.json [ARQUIVO.json ...] [--substituir]

- Cada arquivo é reconhecido pelo campo "schema" (gabA.normas, gabA.precedentes, gabA.modelos...), não pelo nome,
  e vai para banco/<nome>.json (ex.: gabA.normas → banco/normas.json).
- Sem --substituir, os registros são MESCLADOS com o que já está em banco/: o mesmo id é atualizado, ids novos
  são acrescentados, nada é apagado.
- Com --substituir, a exportação passa a ser a fotografia oficial daquele banco (registros que saíram do app saem
  também do repositório).
- Em ambos os casos não há duplicatas: além do id, cada banco tem uma chave natural (ex.: número do processo e
  espécie nos precedentes; sigla nas normas). Dois registros com a mesma chave natural e ids diferentes são
  reduzidos a um, prevalecendo o que veio por último, e o descarte é informado.
- Ao final, atualiza as referências usadas pelo catálogo (scripts/catalogo/ref/banco-atual.json e assuntos.json)
  e grava banco/README.md com as contagens.
"""
import hashlib
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
BANCO = RAIZ / "banco"
REF = RAIZ / "scripts" / "catalogo" / "ref"
PROC = re.compile(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}")

DESCR = {
    "precedentes": "Precedentes curados do Banco de Paradigmas",
    "modelos": "Modelos do Banco de Paradigmas, inclusive os antigos modelos-matriz (hoje unificados)",
    "paragrafos": "Parágrafos-modelo do gestor de parágrafos",
    "normas": "Catálogo de normas (siglas, aliases e forma por extenso)",
    "jurisprudencia": "Jurisprudência de referência (temas, súmulas, precedentes qualificados)",
    "assuntos": "Catálogo de assuntos (TPU/CNJ, seções e sinônimos)",
    "redacao": "Padrão de redação: conectivos, verbos, preferências, correções e alertas",
}


def sem_acento(s):
    return unicodedata.normalize("NFD", str(s or "")).encode("ascii", "ignore").decode().lower().strip()


def chave_natural(nome, r):
    """Identidade do registro independente do id; None quando o banco não tem chave natural confiável."""
    if nome == "precedentes" and r.get("tipo", "Precedente") == "Precedente":
        p = PROC.search(r.get("processo") or "")
        return ("proc", p.group(0), sem_acento(r.get("especie"))[:4]) if p else None
    if nome == "normas":
        return ("sigla", sem_acento(r.get("sigla") or r.get("nome")))
    if nome == "assuntos":
        return ("nome", sem_acento(r.get("nome")))
    if nome == "jurisprudencia":
        return ("ref", re.sub(r"\s+", " ", sem_acento(r.get("referencia"))))
    if nome == "paragrafos":
        t = re.sub(r"\s+", " ", sem_acento(r.get("texto")))
        return ("texto", hashlib.sha1(t.encode()).hexdigest()) if t else None
    return None


def nome_do_schema(obj, arq):
    s = str(obj.get("schema", ""))
    if not s.startswith("gabA.") or not isinstance(obj.get("registros"), list):
        sys.exit(f"{arq}: não é uma exportação gabA.* com a lista 'registros'")
    return s.split(".", 1)[1]


def mesclar(nome, atuais, novos, substituir):
    base = [] if substituir else list(atuais)
    por_id = {r["id"]: i for i, r in enumerate(base)}
    descartes = []
    for r in novos:
        if not r.get("id"):
            descartes.append(("sem id", r.get("processo") or r.get("nome") or r.get("titulo") or "?"))
            continue
        if r["id"] in por_id:
            base[por_id[r["id"]]] = r
        else:
            por_id[r["id"]] = len(base)
            base.append(r)
    # chave natural: o último registro prevalece
    vistos, final = {}, []
    for r in base:
        k = chave_natural(nome, r)
        if k and k in vistos:
            antigo = final[vistos[k]]
            descartes.append((antigo["id"], f"mesma chave que {r['id']}"))
            final[vistos[k]] = r
            continue
        if k:
            vistos[k] = len(final)
        final.append(r)
    # ids repetidos não sobram, mas confere
    assert len({r["id"] for r in final}) == len(final)
    return sorted(final, key=lambda r: str(r["id"])), descartes


def gravar(nome, regs, origem):
    BANCO.mkdir(exist_ok=True)
    obj = {"schema": f"gabA.{nome}", "schema_versao": origem.get("schema_versao", 1),
           "versao": origem.get("versao", date.today().isoformat()),
           "atualizado_em": origem.get("atualizado_em", date.today().isoformat()), "registros": regs}
    (BANCO / f"{nome}.json").write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def carregar(nome):
    f = BANCO / f"{nome}.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {"registros": []}


def atualizar_referencias():
    """banco-atual.json: processo → registros do banco que o citam (para o catálogo não repetir o que já está curado).
    assuntos.json: lista de assuntos do app usada para classificar os acórdãos."""
    curados = {}
    for nome in ("precedentes", "modelos"):
        for r in carregar(nome)["registros"]:
            procs = set(PROC.findall(r.get("processo") or "")) | set(PROC.findall(r.get("processosAssociados") or ""))
            for p in procs:
                item = {"tipo": r.get("tipo", "Precedente"), "id": r["id"], "especie": r.get("especie", ""),
                        "sessao": r.get("sessao", "")}
                lista = curados.setdefault(sem_acento(p), [])
                if all(x["id"] != r["id"] for x in lista):
                    lista.append(item)
    REF.mkdir(parents=True, exist_ok=True)
    (REF / "banco-atual.json").write_text(json.dumps(curados, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    ass = carregar("assuntos")["registros"]
    if ass:
        (REF / "assuntos.json").write_text(json.dumps(ass, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return len(curados)


def leia_me():
    linhas = ["# Banco do Construtor de Minutas", "",
              "Exportações dos bancos do app, importadas por `scripts/banco/importar.py` (sem duplicatas: por id e por chave natural).", "",
              "| Arquivo | Conteúdo | Registros | Versão |", "|---|---|---:|---|"]
    for f in sorted(BANCO.glob("*.json")):
        o = json.loads(f.read_text(encoding="utf-8"))
        nome = f.stem
        linhas.append(f"| [`{f.name}`]({f.name}) | {DESCR.get(nome, o.get('schema', ''))} | {len(o['registros'])} | {o.get('versao', '')} |")
    linhas += ["", "Para atualizar: exporte cada banco no app e rode `python3 scripts/construir.py ARQUIVOS.json`."]
    (BANCO / "README.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")


def importar(arquivos, substituir=False):
    resumo = []
    lotes = []
    for arq in arquivos:
        obj = json.loads(Path(arq).read_text(encoding="utf-8"))
        nome = nome_do_schema(obj, arq)
        if nome == "paradigmas":  # exportação conjunta: separa em precedentes e modelos (um banco para cada)
            for alvo, tipo in (("precedentes", "Precedente"), ("modelos", "Modelo")):
                regs = [r for r in obj["registros"] if (r.get("tipo") or "Precedente") == tipo]
                if regs:
                    lotes.append((alvo, {**obj, "schema": f"gabA.{alvo}", "registros": regs}))
        else:
            lotes.append((nome, obj))
    for nome, obj in lotes:
        atual = carregar(nome)
        antes = len(atual["registros"])
        regs, desc = mesclar(nome, atual["registros"], obj["registros"], substituir)
        gravar(nome, regs, obj)
        resumo.append((nome, len(obj["registros"]), antes, len(regs), desc))
    n = atualizar_referencias()
    leia_me()
    for nome, rec, antes, depois, desc in resumo:
        print(f"{nome}: {rec} recebidos · {antes} antes · {depois} agora" + (f" · {len(desc)} descartados" if desc else ""))
        for d in desc[:10]:
            print("   descartado:", *d)
    print(f"referências do catálogo: {n} processos já presentes no banco")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    importar(args, "--substituir" in sys.argv)
