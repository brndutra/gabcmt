"""Converte um acórdão do catálogo TRF3 para o registro do Banco de Paradigmas (CMText, schema gabA.paradigmas v1),
seguindo o padrão dos precedentes curados: id par-<processo>, assunto do catálogo do app, sessão = data do julgamento
(DD/MM/AAAA), data = publicação (AAAA-MM-DD), marcadores em minúsculas separados por "; "."""
import json
import re
import unicodedata
from pathlib import Path

BASE = Path(__file__).parent
_ASS = {a["nome"] for a in json.loads((BASE / "ref" / "assuntos.json").read_text(encoding="utf-8"))}
_CURADOS = json.loads((BASE / "ref" / "banco-atual.json").read_text(encoding="utf-8"))

# (padrão no cabeçalho da ementa, assunto do catálogo do app) — a primeira regra que casar vence
REGRAS_ASSUNTO = [
    (r"28[,.]86|ACP 0005019", "Índice de 28,86% Lei 8.622/1993 e 8.627/1993"),
    (r"PENS[ÃA]O POR MORTE.*(RURAL|SEGURAD[OA] ESPECIAL)|(RURAL|SEGURAD[OA] ESPECIAL).*PENS[ÃA]O POR MORTE",
     "Rural (Pensão por Morte (Art. 74/9))"),
    (r"PENS[ÃA]O POR MORTE", "Pensão por Morte (Art. 74/9)"),
    (r"SAL[ÁA]RIO[- ]MATERNIDADE", "Salário-Maternidade (Art. 71/73)"),
    (r"AUX[ÍI]LIO[- ]ACIDENTE", "Auxílio-Acidente (Art. 86)"),
    (r"PRESTA[ÇC][ÃA]O CONTINUADA|BENEF[ÍI]CIO ASSISTENCIAL|\bLOAS\b|\bBPC\b", "Benefício Assistencial (Art. 203,V CF/88)"),
    (r"H[ÍI]BRIDA", "Híbrida (Art. 48/106)"),
    (r"APOSENTADORIA (POR IDADE )?RURAL|IDADE RURAL|TRABALHADOR(A)? RURAL|SEGURAD[OA] ESPECIAL", "Rural (Art. 48/51)"),
    (r"APOSENTADORIA ESPECIAL", "Aposentadoria Especial (Art. 57/8)"),
    (r"ATIVIDADE ESPECIAL|TEMPO ESPECIAL|TEMPO DE SERVI[ÇC]O ESPECIAL|CONVERS[ÃA]O DE TEMPO",
     "Averbação/Cômputo/Conversão de tempo de serviço especial"),
    (r"TEMPO DE CONTRIBUI[ÇC][ÃA]O", "Aposentadoria por Tempo de Contribuição (Art. 55/6)"),
    (r"BENEF[ÍI]CIO POR INCAPACIDADE|AUX[ÍI]LIO[- ]DOEN[ÇC]A|APOSENTADORIA POR INVALIDEZ|AUX[ÍI]LIO POR INCAPACIDADE|"
     r"INCAPACIDADE (TOTAL|PARCIAL|TEMPOR[ÁA]RIA|PERMANENTE|LABORA)|ASSIST[ÊE]NCIA PERMANENTE DE TERCEIROS",
     "Benefício por Incapacidade"),
    (r"INCOMPET[ÊE]NCIA ABSOLUTA|COMPET[ÊE]NCIA DA JUSTI[ÇC]A", "Competência da Justiça Federal"),
    (r"\bPASEP\b", "PASEP"),
    (r"FERROVI[ÁA]RI", "Complementação de Benefício/Ferroviário"),
]
REGRAS_ASSUNTO = [(re.compile(p), a) for p, a in REGRAS_ASSUNTO if a in _ASS]
CLASSES = re.compile(r"^(Embargos de Declara[çc][ãa]o|Embargos Infringentes|Apela[çc][ãa]o|Remessa Necess[áa]ria|Agravo( de Instrumento| Interno)?|"
                     r"Recurso( Inominado| Especial| Extraordin[áa]rio)?|Mandado de Seguran[çc]a|A[çc][ãa]o Civil P[úu]blica|Procedimento Comum)$", re.I)
_CAT = []
for _a in json.loads((BASE / "ref" / "assuntos.json").read_text(encoding="utf-8")):
    if _a.get("ativo") is False:
        continue
    for _t in [_a["nome"], *(_a.get("sinonimos") or [])]:
        _base = re.sub(r"\s*\(.*?\)\s*", " ", _t).strip()
        for _k in {_base, *[p.strip() for p in re.split(r"\s*/\s*", _base)]}:
            if len(_k) >= 9 and not re.search(r"[–—]", _k) and not CLASSES.match(_k):
                _CAT.append((_a["nome"], _k))


def assunto_catalogo(cab):
    alvo = " " + re.sub(r"[^a-z0-9%]+", " ", unicodedata.normalize("NFD", cab).encode("ascii", "ignore").decode().lower()) + " "
    achados = [(len(k), nome) for nome, k in _CAT
               if " " + re.sub(r"[^a-z0-9%]+", " ", unicodedata.normalize("NFD", k).encode("ascii", "ignore").decode().lower()).strip() + " " in alvo]
    return max(achados)[1] if achados else ""

SIGLAS = {"STJ", "STF", "TNU", "TRF3", "TRF-3", "INSS", "CPC", "CF", "ACP", "MP", "EC", "LOAS", "BPC", "RMI", "DIB", "DII",
          "DER", "DCB", "CNIS", "PIS", "PASEP", "COFINS", "FGTS", "SUS", "INPC", "IPCA-E", "SELIC", "OAB", "FUNASA", "CDA",
          "CTN", "IN", "RFFSA", "IBAMA", "INCRA", "DNIT", "ANTT", "CEF", "UFMS", "TJMS", "MS", "SP", "RPV", "ITR", "IRPF",
          "ADI", "RE", "RESP", "EDCL", "PPP", "LTCAT", "EPI", "CTPS", "CADÚNICO", "FUNAI", "CLT", "JEF"}
GENERICOS = re.compile(
    r"^(DIREITO\b.*|APELA[ÇC][ÃA]O( C[ÍI]VEL)?|REMESSA NECESS[ÁA]RIA( E APELA[ÇC][ÃA]O)?|APELA[ÇC][ÃA]O E REMESSA NECESS[ÁA]RIA|"
    r"RECURSO (DES)?PROVIDO|APELA[ÇC][ÃA]O (PARCIALMENTE )?(DES)?PROVIDA|(PARCIAL )?(DES)?PROVIMENTO|HONOR[ÁA]RIOS RECURSAIS|"
    r"N[ÃA]O CONHECIMENTO|APELA[ÇC][ÃA]O N[ÃA]O CONHECIDA|APELA[ÇC][ÃA]O PREJUDICADA|EMBARGOS (DE DECLARA[ÇC][ÃA]O )?REJEITADOS|"
    r"SENTEN[ÇC]A (MANTIDA|REFORMADA)|PROVIMENTO PARCIAL)$")


def _norm(s):
    return unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode().lower().strip()


def frase(seg):
    """Converte trecho em caixa alta para caixa de frase, preservando siglas, números e Temas/Súmulas."""
    palavras = seg.lower().split()
    out = []
    for i, w in enumerate(palavras):
        nucleo = re.sub(r"[^\wÀ-ú\-]", "", w)
        if nucleo.upper() in SIGLAS:
            w = w.replace(nucleo, nucleo.upper().replace("CADÚNICO", "CadÚnico").replace("RESP", "REsp").replace("EDCL", "EDcl"))
        elif re.fullmatch(r"[ivxl]+", nucleo) and len(nucleo) <= 4 and i > 0:
            w = w.upper()
        elif nucleo in ("tema", "temas", "súmula", "súmulas", "lei", "leis", "decreto"):
            w = w.capitalize()
        elif nucleo == "união" and not (i + 1 < len(palavras) and palavras[i + 1].startswith("est")):
            w = w.capitalize()
        elif nucleo in ("fazenda", "nacional") and "fazenda nacional" in seg.lower():
            w = w.capitalize()
        out.append(w)
    txt = " ".join(out)
    txt = re.sub(r"/(stj|stf|tnu)\b", lambda m: "/" + m.group(1).upper(), txt)
    return txt[:1].upper() + txt[1:]


def segmentos(cabecalho):
    return [s.strip() for s in re.split(r"\.\s+|\.$", cabecalho) if s.strip()]


def secao(e, inicio, fins):
    m = re.search(inicio, e, re.I)
    if not m:
        return ""
    resto = e[m.end():]
    corte = min([f.start() for p in fins for f in [re.search(p, resto, re.I)] if f] + [len(resto)])
    return resto[:corte].strip(" :\n")


def sem_numero(t):
    return re.sub(r"^\s*\d+(\.\d+)?\s*\.\s*", "", t.strip())


def primeira_frase(t, limite=240):
    t = sem_numero(t).replace("\n", " ")
    m = re.search(r"^(.{40,}?[^\d\s§º.]\.)(\s|$)", t)
    f = m.group(1) if m else t
    return f if len(f) <= limite else f[:limite].rsplit(" ", 1)[0] + "…"


GERAL = re.compile(r"^(A concess[ãa]o|O benef[íi]cio|Os benef[íi]cios|Nos termos|O artigo|Conforme|A legisla[çc][ãa]o|A jurisprud[êe]ncia|"
                   r"Segundo|De acordo|O aux[íi]lio|A aposentadoria|A pens[ãa]o por morte exige|Para a concess[ãa]o|A carência|"
                   r"Embora o laudo|O laudo pericial judicial n[ãa]o vincula)", re.I)
DECISIVO = re.compile(r"\b(no caso|na esp[ée]cie|in casu|caso concreto|n[ãa]o se|deve(m)? ser|imp[õo]e-se|afasta-se|rejeita-se|"
                      r"mant[ée]m-se|reconhece-se|n[ãa]o comprov|comprovad|inviabiliza|autoriza|n[ãa]o h[áa])\b", re.I)


def escolher_tese(itens):
    """Prefere o item das razões que aplica a regra ao caso; evita a premissa normativa genérica."""
    if not itens:
        return ""
    melhor, nota_max = itens[0], -9
    for pos, it in enumerate(itens):
        t = sem_numero(it)
        nota = (2 if DECISIVO.search(t[:400]) else 0) - (3 if GERAL.match(t) else 0) + pos * 0.2
        if nota >= nota_max:
            melhor, nota_max = it, nota
    return primeira_frase(melhor)


def marcador(seg):
    t = frase(seg)
    t = t if t[:2].isupper() else t[:1].lower() + t[1:]
    return re.sub(r"/(stj|stf|tnu)\b", lambda m: "/" + m.group(1).upper(), t)


def iso(br):
    m = re.search(r"(\d{2})/(\d{2})/(\d{4})", br or "")
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else ""


def converter(r, periodo_busca):
    e = r["ementa"]
    cab = e.split("\n", 1)[0].strip()
    segs = segmentos(cab)
    ramo = next((s for s in segs if s.startswith("DIREITO")), "")
    especificos = [s for s in segs if not GENERICOS.match(s)]
    assunto = next((a for rx, a in REGRAS_ASSUNTO if rx.search(cab)), "")
    assunto_origem = "regra" if assunto else ""
    if not assunto:
        caso = secao(e, r"I\.\s*Caso em exame", [r"\nII\."]).upper()
        assunto = next((a for rx, a in REGRAS_ASSUNTO if rx.search(caso)), "")
        assunto_origem = "regra" if assunto else ""
    if not assunto:
        assunto = assunto_catalogo(cab)
        assunto_origem = "sugerido" if assunto else ""
    sigla = (r.get("classe") or "").split(" - ")[0].strip()
    edcl = bool(re.search(r"EMBARGOS DE DECLARA[ÇC][ÃA]O", cab))
    classe_nome = (r.get("classe") or "").split(" - ", 1)[-1].strip()
    dispositivo = secao(e, r"IV\.\s*Dispositivo( e tese)?", [r"\n_{3,}", r"\n-{3,}", r"\nDispositivos? relevantes?", r"\nTese"])
    disp_txt = sem_numero(dispositivo.split("\n")[0]) if dispositivo else ""
    resultado = re.split(r",\s*(?=honor)|;\s*(?=honor)", disp_txt, flags=re.I)[0].rstrip(". ") + "." if disp_txt else ""
    hon = re.search(r"(honor[áa]rios[^.;]*)", disp_txt, re.I)
    razoes = secao(e, r"III\.\s*Raz[õo]es de decidir", [r"\nIV\.\s*Dispositivo"])
    itens = [i for i in re.split(r"\n(?=\d+\.)", razoes) if i.strip()]
    tese = escolher_tese(itens)
    prel = re.findall(r"(?:preliminar(?:es)?|nulidade)\s+(?:de\s+|da\s+|do\s+|por\s+)([^.;,\n]{6,80})", e, re.I)
    tags = [marcador(s) for s in especificos if len(s) <= 48][:4]
    pub_iso = iso(r.get("pub"))
    pub_br = re.search(r"\d{2}/\d{2}/\d{4}", r.get("pub") or "")
    reg = {
        "id": "par-" + re.sub(r"[^a-z0-9]+", "-", _norm(r["processo"])).strip("-"),
        "processo": r["processo"],
        "tipo": "Precedente",
        "pronunciamento": "Voto",
        "especie": "EDcl" if edcl else sigla,
        "classe": classe_nome.title() if classe_nome else "",
        "classeSigla": sigla,
        "primeiroGrau": "",
        "parteNotavel": "",
        "papelNotavel": "",
        "assunto": assunto,
        "temas": r.get("temas", ""),
        "especificidadesTags": "; ".join(dict.fromkeys(tags)),
        "causaPedir": "",
        "tese": tese,
        "fundamentacao": ". ".join(frase(s) for s in especificos) + ("." if especificos else ""),
        "especificidades": "Ementa integral extraída da pesquisa de jurisprudência do TRF3; inteiro teor não juntado. "
                           "Registro bruto: conferir assunto, tese e marcadores antes de usar como paradigma.",
        "preliminares": "; ".join(dict.fromkeys(p.strip() for p in prel[:3])),
        "honorarios": (hon.group(1)[:1].upper() + hon.group(1)[1:].rstrip(" .") + ".") if hon else "",
        "resultado": resultado,
        "sessao": r.get("julg", ""),
        "fonte": f"Pesquisa de Jurisprudência TRF3 — relator Carlos Muta, publicação de {periodo_busca}. "
                 f"Acórdão publicado em {pub_br.group(0) if pub_br else '—'}.",
        "data": pub_iso,
        "processosAssociados": "",
        "formatoModelo": "",
        "nomeModelo": "",
        "textoModelo": "",
        "esqueletoModelo": "",
        "paragrafosModelo": "",
        # campos novos propostos para a integração (aceitos pelo catálogo compartilhado, que guarda JSON livre)
        "ementaIntegral": e,
        "ementaCabecalho": cab,
        "ramoDireito": ramo.title().replace(" E ", " e ").replace(" Do ", " do ").replace(" Da ", " da "),
        "dispositivosCitados": r.get("dispositivos", ""),
        "jurisprudenciaCitada": r.get("jurisprudencia", ""),
        "orgaoJulgador": r.get("orgao", ""),
        "assuntoOrigem": assunto_origem,
        "statusCuradoria": "bruto",
        "urlFonte": "",
    }
    return reg


def no_banco(processo, especie=""):
    """Registro do banco para o mesmo processo e o mesmo tipo de recurso (EDcl separado da apelação)."""
    regs = _CURADOS.get(_norm(processo)) or []
    ed = especie.upper().startswith("ED")
    for b in regs:
        if b["tipo"] == "Modelo" or (b.get("especie", "").upper().startswith("ED")) == ed:
            return b
    return None
