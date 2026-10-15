"""Importa as exportações do Construtor de Minutas (schemas gabA.*) para a pasta banco/ do repositório, sem duplicar.

Uso:
    python3 scripts/banco/importar.py ARQUIVO.json|ARQUIVO.html [...] [--substituir]

- Cada arquivo é reconhecido pelo campo "schema" (gabA.normas, gabA.precedentes, gabA.modelos...), não pelo nome,
  e vai para banco/<nome>.json (ex.: gabA.normas → banco/normas.json).
- Sem --substituir, os registros são MESCLADOS com o que já está em banco/: o mesmo id é atualizado, ids novos
  são acrescentados, nada é apagado.
- Com --substituir, a exportação passa a ser a fotografia oficial daquele banco (registros que saíram do app saem
  também do repositório).
- Em ambos os casos não há duplicatas: além do id, cada banco tem uma chave natural (ex.: número do processo e
  espécie nos precedentes; sigla nas normas). Dois registros com a mesma chave natural e ids diferentes são
  reduzidos a um, prevalecendo o que veio por último, e o descarte é informado.
- Acervo (gabA.acervo, exportado pelo Painel Central como acervo.json ou acervo.html): chave natural é o número
  do processo; vale a versão mais recente de cada processo (campo atualizado_em). O saneamento é refeito aqui:
  celulares, telefones, e-mails e CPF são removidos (o repositório é público). Processos sigilosos entram: as
  informações sigilosas já vêm mascaradas (###) na planilha de origem.
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
    "acervo": "Acervo geral de processos do gabinete (Painel Central), saneado: sem celulares, e-mails e CPF",
}
SANEAMENTO = ("Sem celulares, telefones, e-mails e CPF (repositório público). Processos sigilosos incluídos: "
              "as informações sigilosas já vêm mascaradas (###) na planilha de origem.")
SENSIVEL = re.compile(r"celular|telefone|fone|whats|e-?mail|cpf", re.I)
SIGILO_CAMPO = re.compile(r"sigil|segredo", re.I)
NAO = re.compile(r"^(0|n[aã]o|n|false|p[uú]blico|-)$", re.I)
SIM = re.compile(r"^(sim|s|true|1|x)$", re.I)


def sigiloso(r):
    if SIM.match(str(r.get("Consta_Acervo_Sigiloso") or "").strip()):
        return True
    for k, v in r.items():
        if SIGILO_CAMPO.search(k) and not k.lower().startswith("consta_acervo"):
            v = str(v or "").strip()
            if v and not NAO.match(v):
                return True
    return False


def sanear_acervo(regs):
    """Retira campos pessoais (celular, telefone, e-mail, CPF); garante id = acv-<20 dígitos>."""
    limpos, fora = [], []
    for r in regs:
        proc = str(r.get("processo") or r.get("Processo") or "").strip()
        dig = re.sub(r"\D", "", proc)
        if len(dig) < 15:
            fora.append(("sem processo", proc or "?"))
            continue
        o = {"id": "acv-" + dig, "processo": proc}
        o.update({k: v for k, v in r.items() if k not in ("id", "processo", "Processo") and not k.startswith("_")
                  and not SENSIVEL.search(k) and str(v if v is not None else "").strip() != ""})
        if "atualizado_em" in o:
            o["atualizado_em"] = o.pop("atualizado_em")
        limpos.append(o)
    return limpos, fora


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
    if nome == "acervo":
        d = re.sub(r"\D", "", str(r.get("processo") or ""))
        return ("proc", d) if d else None
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
        if nome == "acervo" and r.get("id") in por_id:  # acervo: prevalece a versão mais recente do processo
            atual = base[por_id[r["id"]]]
            if str(r.get("atualizado_em") or "") < str(atual.get("atualizado_em") or ""):
                continue
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
    if nome == "acervo":  # um processo por linha: diffs legíveis e arquivo menor (mesmo formato do Painel Central)
        obj = {**{k: v for k, v in obj.items() if k != "registros"}, "saneamento": SANEAMENTO, "registros": regs}
        cab = [f"  {json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)}" for k, v in obj.items() if k != "registros"]
        linhas = ["    " + json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in regs]
        texto = "{\n" + ",\n".join(cab) + ',\n  "registros": [\n' + ",\n".join(linhas) + ("\n" if linhas else "") + "  ]\n}\n"
        (BANCO / "acervo.json").write_text(texto, encoding="utf-8")
        return
    (BANCO / f"{nome}.json").write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ler_exportacao(arq):
    """JSON gabA.* ou HTML com o banco embutido (<script id="gabA-acervo" type="application/json">)."""
    texto = Path(arq).read_text(encoding="utf-8").lstrip("\ufeff")
    if texto.lstrip()[:1] in "[{":
        return json.loads(texto)
    m = re.search(r'<script[^>]*id="gabA-(\w+)"[^>]*>(.*?)</script>', texto, re.S)
    if not m:
        sys.exit(f"{arq}: HTML sem banco embutido (script#gabA-acervo)")
    return json.loads(m.group(2))


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
    linhas += ["", "Para atualizar: exporte cada banco no app e rode `python3 scripts/construir.py ARQUIVOS.json`.",
               "", "O acervo (`acervo.json`) é atualizado pelo próprio Painel Central (`painel.html`): cada importação de planilha "
               "é encaminhada ao GitHub. Também aceita `python3 scripts/construir.py acervo.html` (ou `acervo.json`) exportado do painel. "
               "Saneamento: sem celulares, telefones, e-mails e CPF; os sigilosos entram, já mascarados (###) na origem."]
    (BANCO / "README.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")


def importar(arquivos, substituir=False):
    resumo = []
    lotes = []
    for arq in arquivos:
        obj = ler_exportacao(arq)
        nome = nome_do_schema(obj, arq)
        if nome == "paradigmas":  # exportação conjunta: separa em precedentes e modelos (um banco para cada)
            for alvo, tipo in (("precedentes", "Precedente"), ("modelos", "Modelo")):
                regs = [r for r in obj["registros"] if (r.get("tipo") or "Precedente") == tipo]
                if regs:
                    lotes.append((alvo, {**obj, "schema": f"gabA.{alvo}", "registros": regs}))
        elif nome == "acervo":
            regs, fora = sanear_acervo(obj["registros"])
            if fora:
                print(f"acervo: {len(fora)} registro(s) sem número de processo ignorado(s)")
            lotes.append((nome, {**obj, "registros": regs}))
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
