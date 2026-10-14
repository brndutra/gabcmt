"""Converte os votos-fonte de 28,86% (ACP 0005019-15.1997.4.03.6000) em três modelos-matriz no padrão atual do app:
estrutura padrão v2 (Abertura · Fundamentação · Caso · Resolução · Encerramento), um parágrafo por cartão,
posição + versão para alternativas, opcional por parágrafo, citações marcadas, variáveis automáticas @ e campos de caso {{ }}.
Texto dos votos preservado; só mudam: vocativo inicial (já no cabeçalho fixo), dados do caso concreto (→ {{ }}) e
dados que o app já possui (→ @).

Entrada: votos.json (texto extraído dos PDFs do PJe pelos scripts da pasta anterior; não versionado, pois o repositório é público).
Saída: modelos-2886.json no formato gabA.modelos, para scripts/construir.py ou para a importação do app."""
import json, re, sys
from pathlib import Path

AQUI = Path(__file__).parent
V = json.load(open(AQUI / 'votos.json', encoding='utf-8'))
BANCO = json.load(open(AQUI.parents[2] / 'banco' / 'modelos.json', encoding='utf-8'))
ANT = {r['id']: r for r in BANCO['registros']}

EST_PADRAO = [
    ('admiss', 'Abertura', 'Admissibilidade', True, 'Conheço do {{recurso interposto}}, por preenchidos os pressupostos de admissibilidade.'),
    ('tutela', 'Abertura', 'Tutela recursal', True, 'Quanto ao pedido de tutela recursal, {{análise da tutela}}.'),
    ('prelim', 'Abertura', 'Preliminares', True, 'Cabe examinar, inicialmente, a preliminar de {{preliminar}}. {{fundamentação e conclusão da preliminar}}'),
    ('contro', 'Abertura', 'Controvérsias', True, 'A controvérsia envolve discutir se {{controvérsia}}.'),
    ('jurid', 'Fundamentação', 'Moldura jurídica', True, '{{regime jurídico aplicável}}'),
    ('citnorma', 'Fundamentação', 'Citação normativa', False, '{{dispositivo normativo}}'),
    ('citjur', 'Fundamentação', 'Citação jurisprudencial', False, '{{trecho do precedente}}'),
    ('desenv', 'Fundamentação', 'Desenvolvimento', True, '{{desenvolvimento da fundamentação}}'),
    ('fatos', 'Caso', 'Introdução do caso', True, 'Na espécie, {{situação concreta}}.'),
    ('provas', 'Caso', 'Análise fática/probatória', True, 'O documento de ID {{ID do documento}} registra {{conteúdo da prova}}.'),
    ('aplic', 'Caso', 'Aplicação do direito', True, '{{aplicação do direito aos fatos comprovados}}'),
    ('concl', 'Resolução', 'Conclusão', True, 'Assim, {{conclusão sobre a controvérsia}}.'),
    ('provid', 'Resolução', 'Providências e determinações', True, '{{providências e determinações}}'),
    ('consec', 'Encerramento', 'Consectários e custas', True, '{{tratamento dos consectários e custas}}'),
    ('honor', 'Encerramento', 'Honorários', True, '{{tratamento dos honorários}}'),
    ('disp', 'Encerramento', 'Dispositivo', False, 'Ante o exposto, {{resultado do recurso}}.'),
    ('fecho', 'Encerramento', 'Fecho', False, 'É como voto.'),
]
CIT_TIPO = {'citnorma': 'norma', 'citjur': 'juris'}


def sem_vocativo(t):
    return t[len('Senhores Desembargadores, '):][:1].upper() + t[len('Senhores Desembargadores, ') + 1:] if t.startswith('Senhores Desembargadores, ') else t


def ref_citacao(t):
    m = re.match(r'^(.{10,200}?):\s*[“"]', t)
    return m.group(1) if m else ''


class Modelo:
    def __init__(self, sigla):
        self.sigla, self.top, self.base, self.pars = sigla, {}, {}, []
        self.ordem = {}
        self.extra = []  # tópicos próprios: (id, grupo, título, depois_de)

    def topico(self, tid, titulo=None, ativo=True, base=None, livres=None, grupo=None, depois=None, opcional=True):
        self.top[tid] = dict(titulo=titulo, ativo=ativo, livres=livres, opcional=opcional)
        if base is not None:
            self.base[tid] = base
        if grupo:
            self.extra.append((tid, grupo, titulo, depois))

    def par(self, tid, texto, titulo='', opcional=False, versao=None, mesma=False, cit='', citTipo='', citRef=''):
        if not mesma:
            self.ordem[tid] = self.ordem.get(tid, 0) + 1
        o = self.ordem[tid]
        p = dict(id=f'mp-2886{self.sigla}-{tid}-{o:02d}{versao or "a"}', posicao=tid, ordem=o, versao=versao or 'a',
                 titulo=titulo, texto=texto, opcional=opcional)
        if cit:
            p.update(cit=cit, citTipo=citTipo or 'juris', citRef=citRef)
        assert '\n' not in texto, (tid, titulo)
        self.pars.append(p)
        return p

    def esqueleto(self):
        T, o = [], {'_estrutura': 'padrao'}
        for tid, g, tit, livres, txt in EST_PADRAO:
            cfg = self.top.get(tid, {})
            t = dict(id=tid, titulo=cfg.get('titulo') or tit, opcional=cfg.get('opcional', True),
                     livres=cfg['livres'] if cfg.get('livres') is not None else livres, grupo=g)
            if tid in CIT_TIPO:
                t.update(tipo='cit', citTipo=CIT_TIPO[tid], citRef='')
            T.append(t)
            o[tid] = dict(texto=self.base.get(tid, '' if any(p['posicao'] == tid for p in self.pars) else txt),
                          ativo=bool(cfg.get('ativo', False)) if cfg else False)
            fila = [tid]
            while fila:
                ant = fila.pop(0)
                for eid, eg, etit, dep in self.extra:
                    if dep == ant:
                        c = self.top[eid]
                        T.append(dict(id=eid, titulo=etit, opcional=c.get('opcional', True), livres=True, grupo=eg))
                        o[eid] = dict(texto=self.base.get(eid, ''), ativo=bool(c.get('ativo', True)))
                        fila.append(eid)
        o['_topicos'] = T
        return o


# ---------------------------------------------------------------- blocos comuns
def bloco_territorial(m, v, ini, tid='jurid'):
    """22 parágrafos idênticos em cinco votos: pedidos da ACP → título → Tema 1.075 → Tema 733 → Tema 499 → precedentes → conclusão"""
    T = v[ini:ini + 22]
    tit = ['Pedidos da ACP · introdução', 'Pedidos da ACP · transcrição (1/3)', 'Pedidos da ACP · transcrição (2/3)',
           'Pedidos da ACP · transcrição (3/3)', 'Pedidos sem limitação territorial', 'Aditamento do MPF · órgãos sem restrição geográfica',
           'Título executivo sem restrição geográfica', 'Sentença · artigo 16 da LACP (Lei 9.494/1997)', 'Tema 1.075/STF',
           'Redação original do artigo 16 da LACP', 'Desnecessidade de rescisória (Tema 733/STF)', 'Tema 499/STF · objeção',
           'Substituição × representação processual', 'AgInt no REsp 1.841.604', 'Abrangência pelo pedido (AgInt no AREsp 2.996.314)',
           'ARE 1.585.247 · instância final', 'ADI 1.576 MC superada', 'Eficácia erga omnes nacional',
           'Jurisprudência · introdução', 'AgInt no AREsp 2.993.227', 'ApCiv 5005688-98.2025.4.03.6000', 'Conclusão · legitimidade ativa']
    for i, (t, ti) in enumerate(zip(T, tit)):
        if i in (1, 2, 3):
            m.par(tid, t, ti, cit='direta', citTipo='outros')
        elif i in (13, 19, 20):
            m.par(tid, t, ti, cit='direta', citTipo='juris', citRef=ref_citacao(t))
        else:
            m.par(tid, t, ti)


def bloco_acordo(m, v):
    """voto 01 (5007937): parágrafos 25–46, com a citação do Tema 550 separada da introdução do Tema 1.102"""
    tid = 'acordo'
    A = v[25:47]
    t37 = A[12]
    k = t37.index('No tocante ao segundo grupo')
    seq = [
        (A[0], 'Fundamento da sentença · acordo administrativo', {}),
        (A[1], 'Retrospecto · MP 1.704/1998 e prorrogações', {}),
        (A[2], 'MP 1.962-33/2000 · documento do SIAPE', {}),
        (A[3], 'Acordo individual × transação com homologação', {}),
        (A[4], 'MP 2.169-43/2001 · introdução', {}),
        (A[5], 'MP 2.169-43/2001 · art. 6º', dict(cit='direta', citTipo='norma', citRef='MP 2.169-43/2001, art. 6º')),
        (A[6], 'MP 2.169-43/2001 · supressão', dict(cit='direta', citTipo='norma', citRef='MP 2.169-43/2001')),
        (A[7], 'MP 2.169-43/2001 · art. 7º, caput', dict(cit='direta', citTipo='norma', citRef='MP 2.169-43/2001, art. 7º')),
        (A[8], 'MP 2.169-43/2001 · art. 7º, § 1º', dict(cit='direta', citTipo='norma', citRef='MP 2.169-43/2001, art. 7º, § 1º')),
        (A[9], 'MP 2.169-43/2001 · art. 7º, § 2º', dict(cit='direta', citTipo='norma', citRef='MP 2.169-43/2001, art. 7º, § 2º')),
        (A[10], 'Duas situações distintas', {}),
        (A[11], 'Primeiro grupo · Tema 550/STJ', {}),
        (t37[:k].strip(), 'Tema 550/STJ · tese', dict(cit='direta', citTipo='juris', citRef='')),
        (t37[k:].strip(), 'Segundo grupo · Tema 1.102/STJ', {}),
        (A[13], 'Tema 1.102/STJ · tese I', dict(cit='direta', citTipo='juris', citRef='')),
        (A[14], 'Tema 1.102/STJ · tese II', dict(cit='direta', citTipo='juris', citRef='')),
        (A[15], 'Tema 1.102/STJ no contexto das MPs', {}),
        (A[16], 'Transação até 19/05/1999 e homologação a qualquer tempo', {}),
        (A[17], 'Homologação judicial e coisa julgada', {}),
        (A[18], 'Litígio judicial não provado', {}),
        (A[19], 'Fichas do SIAPE comprovam acordo individual', {}),
        (A[20], 'Inadequação da via (revisão ou cobrança do acordo)', {}),
        (A[21], 'Anuência e renúncia · jurisprudência da Corte', {}),
    ]
    for t, ti, kw in seq:
        m.par(tid, t, ti, **kw)


def honorarios(m, variante_h3=False):
    if variante_h3:
        a = ('Pela sucumbência recursal, a parte exequente deve suportar condenação adicional (artigo 85, § 11, CPC), no equivalente a '
             '@HONORARIOS_PERCENTUAL_ADICIONAL, à sucumbência fixada na sentença pelo decaimento na instância de origem, observada a '
             'gratuidade de justiça concedida (artigo 98, § 3º, do CPC).')
    else:
        a = ('Pela sucumbência recursal, a parte exequente deve suportar condenação adicional (artigo 85, § 11, CPC), no equivalente a '
             '@HONORARIOS_PERCENTUAL_ADICIONAL, a ser acrescido ao fixado na origem, observada a gratuidade de justiça concedida '
             '(artigo 98, § 3º, do CPC).')
    b = a.replace(', observada a gratuidade de justiça concedida (artigo 98, § 3º, do CPC).', '.')
    m.par('honor', '@HONORARIOS_PARAGRAFO', 'Automático · calculado pelo app com os dados da sentença e do recurso', versao='a')
    m.par('honor', a, 'Majoração · com gratuidade', opcional=True, versao='b', mesma=True)
    m.par('honor', b, 'Majoração · sem gratuidade', opcional=True, versao='c', mesma=True)


def contar_vars(m):
    txt = ' '.join([p['texto'] for p in m.pars] + list(m.base.values()))
    return sorted(set(re.findall(r'@[A-Z][A-Z0-9_]*(?:\[\d+\])?(?:\.[A-Z_]+)?', txt))), sorted(set(re.findall(r'\{\{([^{}]+)\}\}', txt)))


# ---------------------------------------------------------------- H1 · limite territorial afastado · provida
def h1():
    m = Modelo('t')
    v4, v3544, v5 = V['5003454'], V['5003544'], V['5003797']
    m.topico('prelim', 'Preliminares', ativo=True)
    m.par('prelim', sem_vocativo(v3544[1]), 'Tema 1.433/STJ · sem sobrestamento')
    m.par('prelim', v4[2], 'Ilegitimidade ativa em contrarrazões · remetida ao mérito')
    m.topico('contro', 'Controvérsias', ativo=True)
    m.par('contro', v3544[3], 'Só limite territorial', versao='a')
    m.par('contro', v5[2], 'Limite territorial e prescrição', opcional=True, versao='b', mesma=True)
    m.topico('jurid', 'Limite territorial da coisa julgada (Tema 1.075/STF)', ativo=True, opcional=False)
    bloco_territorial(m, V['5007937'], 3)
    m.topico('prescr', 'Prescrição alegada em contrarrazões · exame na origem', ativo=False, grupo='Fundamentação', depois='desenv')
    m.par('prescr', v5[25], 'Alegação · prazo quinquenal', opcional=True, versao='a')
    m.par('prescr', v4[25], 'Alegação · prazo quinquenal e habilitação de herdeiros', opcional=True, versao='b', mesma=True)
    m.par('prescr', v4[26], 'Necessidade de contraditório e prova na origem', opcional=True)
    m.par('prescr', v4[27], 'Ampla defesa · não supressão de instância', opcional=True)
    m.topico('honor', 'Honorários', ativo=True)
    m.par('honor', v3544[26].replace('em favor da União', 'em favor @REU_DE'), 'Honorários pedidos pelo ente em contrarrazões · prejudicado', opcional=True)
    m.topico('disp', 'Dispositivo', ativo=True, base=v4[28])
    m.topico('fecho', 'Fecho', ativo=True, base='É como voto.')
    return m


# ---------------------------------------------------------------- H2 · acordo administrativo (SIAPE) · desprovida
def h2():
    m = Modelo('a')
    v1, v3 = V['5007937'], V['5001115']
    m.topico('contro', 'Controvérsias', ativo=True)
    m.par('contro', v1[2], 'Limite territorial e acordo administrativo · “No caso, …”', versao='a')
    m.par('contro', sem_vocativo(v3[1]), 'Limite territorial e acordo administrativo · abertura direta', opcional=True, versao='b', mesma=True)
    m.topico('jurid', 'Limite territorial da coisa julgada (Tema 1.075/STF)', ativo=True)
    bloco_territorial(m, v1, 3)
    m.topico('acordo', 'Acordo administrativo e transação (MP 2.169-43/2001; Temas 550 e 1.102/STJ)', ativo=True, opcional=False,
             grupo='Fundamentação', depois='desenv')
    bloco_acordo(m, v1)
    m.topico('fatos', 'Fichas financeiras do SIAPE', ativo=True)
    f1 = v1[47].replace('(ID 388960832)', '(ID {{ID das fichas financeiras}})')
    f2 = re.sub(r'\(ID’s\s[^)]*\)', '(ID’s {{IDs das fichas financeiras}})', v3[47])
    assert '{{' in f1 and '{{' in f2
    m.par('fatos', f1, 'Rubrica do 28,86% nas fichas · um ID', versao='a')
    m.par('fatos', f2, 'Rubrica do 28,86% nas fichas · vários IDs', opcional=True, versao='b', mesma=True)
    m.par('fatos', v1[48], 'Presunção de legitimidade · adesão à composição administrativa')
    m.topico('concl', 'Conclusão', ativo=True)
    m.par('concl', v1[49], 'Legitimada, mas sem título para o valor transacionado', versao='a')
    m.par('concl', v3[49], 'Solução da origem correta', opcional=True, versao='b', mesma=True)
    m.topico('mafe', 'Litigância de má-fé pedida em contrarrazões', ativo=False, grupo='Resolução', depois='provid')
    m.par('mafe', v3[50], 'Sanção processual afastada', opcional=True)
    m.topico('gratuid', 'Gratuidade judiciária · recurso adesivo do ente (Tema 1.178/STJ; ADC 80)', ativo=False, grupo='Resolução', depois='mafe')
    g = v3[51:61]
    g[0] = g[0] if g[0].endswith('.') else g[0] + '.'
    tits = ['Revisão sem contraditório e por critério objetivo', 'Alegação · remuneração acima de parâmetro objetivo',
            'Tema 1.178/STJ · vedação de critério objetivo', 'Teses · introdução', 'Tema 1.178/STJ · tese i', 'Tema 1.178/STJ · tese ii',
            'Tema 1.178/STJ · tese iii', 'Parâmetros objetivos apenas suplementares', 'Caso concreto · só critério objetivo',
            'ADC 80 · modulação ex nunc']
    for i, (t, ti) in enumerate(zip(g, tits)):
        m.par('gratuid', t, ti, opcional=True, **(dict(cit='direta', citTipo='juris', citRef='') if i in (4, 5, 6) else {}))
    m.topico('honor', 'Honorários recursais', ativo=True)
    honorarios(m)
    m.topico('disp', 'Dispositivo', ativo=True, livres=True)
    m.par('disp', v1[51], 'Desprovimento da apelação', versao='a')
    m.par('disp', v3[62].replace('ao recurso adesivo da FUNASA', 'ao recurso adesivo @REU_DE'), 'Desprovimento da apelação e do recurso adesivo do ente',
          opcional=True, versao='b', mesma=True)
    m.topico('fecho', 'Fecho', ativo=True, base='É como voto.')
    return m


# ---------------------------------------------------------------- H3 · ilegitimidade (sindicato com ação anterior) · desprovida
def h3():
    m = Modelo('s')
    v = V['5006675']
    m.topico('admiss', 'Admissibilidade · conhecimento parcial', ativo=True)
    m.par('admiss', sem_vocativo(v[1]), 'Conhecimento parcial · questão não tratada na sentença; fundamento não impugnado')
    m.topico('contro', 'Exceções da coisa julgada na ACP', ativo=True)
    m.par('contro', v[2], 'Hipóteses excluídas pela própria coisa julgada')
    t3 = v[3].replace('o Sindicato dos Trabalhadores Federais em Seguridade e Seguro Social no Estado do Rio de Janeiro (SINDSPREV/RJ), por meio da Ação 0023278-37.1995.4.02.5101',
                      'o {{nome e sigla do sindicato}}, por meio da Ação {{nº da ação coletiva do sindicato}}')
    assert '{{' in t3
    m.par('contro', t3, 'Ação coletiva do sindicato com o mesmo objeto')
    m.topico('jurid', 'Litispendência e limites subjetivos da coisa julgada coletiva', ativo=True)
    for i, ti in [(4, 'Sem litispendência entre execução individual e coletiva do mesmo título'), (5, 'Neste sentido'),
                  (6, 'ApCiv 5001464-12.2024.4.03.6111'), (7, 'Identidade de partes pelos beneficiários (STJ)'), (8, 'REsp 2.018.707'),
                  (9, 'Limites objetivos e subjetivos do título'), (10, 'A propósito'), (11, 'REsp 2.163.451')]:
        if i in (6, 8, 11):
            m.par('jurid', v[i], ti, cit='direta', citTipo='juris', citRef=ref_citacao(v[i]))
        else:
            m.par('jurid', v[i], ti)
    m.topico('aplic', 'Servidor representado por sindicato com ação anterior', ativo=True)
    m.par('aplic', v[12], 'Não se trata de opção entre ação individual e coletiva')
    t13 = (v[13].replace('representado pelo SINDSPREV/RJ', 'representado pelo {{sigla do sindicato}}')
                .replace('a ação coletiva 0023278-37.1995.4.02.5101, em 25/09/1995', 'a ação coletiva {{nº da ação coletiva do sindicato}}, em {{data do ajuizamento da ação do sindicato}}')
                .replace('ACP 0005019-15.1997.403.6000', 'ACP 0005019-15.1997.4.03.6000'))
    assert t13.count('{{') == 3
    m.par('aplic', t13, 'Ação do sindicato anterior à ACP · escolha do título')
    m.par('aplic', v[14], 'Coisa julgada já excluiu servidores representados')
    t15 = (v[15].replace('ação coletiva 0023278-37.1995.4.02.5101', 'ação coletiva {{nº da ação coletiva do sindicato}}')
                .replace('categoria profissional de trabalhadores em instituições de saúde, trabalho e previdência social, com vínculo federal direto, indireto e funcional, lotados no Estado do Rio de Janeiro',
                         'categoria profissional de {{categoria e base territorial representadas pelo sindicato}}')
                .replace('a categoria funcional do apelante (ID 376094580, f. 38)', 'a categoria funcional @RECORRENTE_DE (ID {{ID e folha do documento}})'))
    assert t15.count('{{') == 3 and '@RECORRENTE_DE' in t15
    m.par('aplic', t15, 'Categoria da parte abrangida pelo sindicato')
    m.par('aplic', v[16], 'Sem direito de escolher o título mais favorável')
    m.topico('concl', 'Conclusão', ativo=True)
    m.par('concl', v[17], 'Pretensão recursal desprovida')
    m.topico('honor', 'Honorários recursais', ativo=True)
    honorarios(m, variante_h3=True)
    m.topico('disp', 'Dispositivo', ativo=True, base=v[19])
    m.topico('fecho', 'Fecho', ativo=True, base='É como voto.')
    return m


# ---------------------------------------------------------------- registros
REFS_J = {
    't': ['AgInt no REsp 1.841.604, Rel. Min. MAURO CAMPBELL, DJe de 27/4/2020', 'AgInt no AREsp 2.996.314, Rel. Min. TEODORO SILVA SANTOS, DJEN de 17/3/2026',
          'ARE 1.585.247, Rel. Min. DIAS TOFFOLI, DJE de 19/02/2026', 'AgInt no AREsp 2.993.227, Rel. Min. TEODORO SILVA SANTOS, DJEN de 25/3/2026',
          'ApCiv 5005688-98.2025.4.03.6000, Rel. Des. Fed. ANTONIO MORIMOTO, DJEN de 19/12/2025', 'RE 1.101.937 (Tema 1.075/STF)', 'Tema 733/STF',
          'RE 612.043 (Tema 499/STF)', 'ADI 1.576 MC', 'ProAfR no REsp 2.234.888 (Tema 1.433/STJ), Rel. Min. AFRÂNIO VILELA, julgado em 05/05/2026'],
    's': ['ApCiv 5001464-12.2024.4.03.6111, Rel. Des. Fed. JOSE CARLOS FRANCISCO, DJEN 15/04/2026', 'REsp 2.018.707, Rel. Min. MOURA RIBEIRO, DJEN 9/2/2025',
          'REsp 2.163.451, Rel. Min. TEODORO SILVA SANTOS, DJEN 24/4/2026'],
}
REFS_J['a'] = REFS_J['t'][:9] + ['REsp 1.318.315 (Tema 550/STJ)', 'REsp 1.925.194 (Tema 1.102/STJ)',
                                 'ApCiv 5008922-59.2023.4.03.6000, Rel. Des. Fed. RENATA LOTUFO, DJEN de 05/11/2025',
                                 'ApCiv 5008102-06.2024.4.03.6000, Rel. Des. Fed. CARLOS FRANCISCO, DJEN de 15/04/2026', 'Tema 1.178/STJ', 'ADC 80, Rel. p/ acórdão Min. GILMAR MENDES']
REFS_D = {
    't': ['Lei 7.347/1985, art. 16', 'Lei 9.494/1997, art. 2º-A', 'CPC, art. 535, § 8º', 'Lei 8.078/1990, art. 93, II', 'Decreto 20.910/1932', 'Súmula 150/STF'],
    'a': ['Lei 7.347/1985, art. 16', 'Lei 9.494/1997, art. 2º-A', 'CPC, art. 535, § 8º', 'MP 2.169-43/2001, arts. 6º e 7º', 'MP 1.962-33/2000, art. 7º, § 2º',
          'CPC, art. 487, III, b', 'CPC, art. 99, § 2º', 'CPC, art. 85, § 11', 'CPC, art. 98, § 3º'],
    's': ['CPC, art. 85, § 11', 'CPC, art. 98, § 3º'],
}


def registro(rid, m, nome_obs):
    r = dict(ANT[rid])
    pars = m.pars
    juris = []
    for ref in REFS_J[m.sigla]:
        tx = next((p['texto'] for p in pars if p.get('citRef') == ref), '')
        juris.append(dict(ref=ref, texto=tx))
    disp = [dict(ref=d, texto='') for d in REFS_D[m.sigla]]
    ats, campos = contar_vars(m)
    r.update(
        esqueletoModelo=json.dumps(m.esqueleto(), ensure_ascii=False),
        paragrafosModelo=json.dumps(pars, ensure_ascii=False),
        jurisprudenciaRelevante=json.dumps(juris, ensure_ascii=False),
        jurisprudenciaCitada='; '.join(j['ref'] for j in juris),
        dispositivosRelevantes=json.dumps(disp, ensure_ascii=False),
        dispositivosCitados='; '.join(d['ref'] for d in disp),
        fundamentacao='Texto integral dos votos-fonte, sem alteração redacional, em estrutura padrão (Abertura · Fundamentação · Caso · Resolução · Encerramento): um parágrafo por cartão, alternativas como versões da mesma posição, citações marcadas.',
        especificidades=(f'{nome_obs} Variáveis automáticas (@, preenchidas pelo app): {", ".join(ats) or "nenhuma"}. '
                         f'Campos do caso ({{{{ }}}}, preenchidos na Minuta): {"; ".join(campos) or "nenhum"}.'),
        statusCuradoria='curado',
        fonte=r['fonte'].replace('Modelo-matriz gerado em 13/10/2026.', 'Modelo-matriz gerado em 13/10/2026 e convertido ao padrão atual (estrutura v2, @ e {{ }}) em 14/10/2026.'),
    )
    return r


if __name__ == '__main__':
    M = [('par-matriz-2886-territorial-provida', h1(), 'Entram por padrão: as duas preliminares (Tema 1.433/STJ e ilegitimidade em contrarrazões, removíveis) e a controvérsia “só limite territorial” (troque pela versão com prescrição quando for o caso). Marque os parágrafos de “Prescrição” quando alegada em contrarrazões e o de honorários prejudicados quando o ente os tiver pedido.'),
         ('par-matriz-2886-acordo-administrativo-desprovida', h2(), 'Entram por padrão: abertura “No caso, a controvérsia…”, fichas com um ID, conclusão “Em suma…”, honorários automáticos e desprovimento simples; troque as versões conforme o caso (vários IDs, “correta a solução da origem”, majoração redigida, desprovimento também do recurso adesivo). Marque os parágrafos de “Litigância de má-fé” e “Gratuidade” quando suscitadas.'),
         ('par-matriz-2886-ilegitimidade-acao-sindical', h3(), 'Preencha os dados do sindicato e da ação coletiva anterior (campos em destaque na Minuta). Honorários automáticos por padrão; há versões redigidas com e sem gratuidade.')]
    regs = [registro(rid, m, obs) for rid, m, obs in M]
    out = {'schema': 'gabA.modelos', 'schema_versao': 1, 'versao': '2.3.0', 'atualizado_em': '2026-10-14',
           'descricao': 'Modelos-matriz 28,86% (ACP 0005019-15.1997.4.03.6000) no padrão atual do app', 'registros': regs}
    dest = Path(sys.argv[1] if len(sys.argv) > 1 else AQUI / 'modelos-2886.json')
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for (rid, m, _), r in zip(M, regs):
        ats, campos = contar_vars(m)
        e = json.loads(r['esqueletoModelo'])
        print(rid, '·', len(m.pars), 'parágrafos ·', sum(1 for t in e['_topicos'] if e[t['id']]['ativo']), 'tópicos ativos ·', ats, campos)
