"""Monta as definições dos Modelos-matriz de 28,86% a partir do texto integral dos votos (fontes.json).
Regra: texto do voto sem alteração; somente dados do caso concreto substituídos por {{TIPO_DA_INFORMACAO}}.
Única adaptação formal: o vocativo "Senhores Desembargadores," que abre o 1º parágrafo é omitido,
porque o Modo Matriz já o insere no cabeçalho fixo (evita duplicidade)."""
import json, re
F=json.load(open('src/fontes.json',encoding='utf-8'))
V=lambda p: F[p]['voto']
P01,P02,P03,P04,P05,P06=['5007937-56.2024.4.03.6000','5006675-71.2024.4.03.6000','5001115-51.2024.4.03.6000',
                         '5003454-12.2026.4.03.6000','5003797-42.2025.4.03.6000','5003544-88.2024.4.03.6000']
SUBS=[]   # relatório de substituições
def sub(txt, antigo, novo, onde):
    assert antigo in txt, (onde, antigo)
    SUBS.append({'onde':onde,'original':antigo,'substituido_por':novo})
    return txt.replace(antigo, novo)
def sem_vocativo(t, onde):
    v='Senhores Desembargadores, '
    assert t.startswith(v), t[:40]
    r=t[len(v)].upper()+t[len(v)+1:]
    SUBS.append({'onde':onde,'original':v+t[len(v):len(v)+20]+'…','substituido_por':r[:20]+'… (vocativo omitido: já consta do cabeçalho fixo do Modo Matriz)'})
    return r
def bloco_01(a,b):
    """parágrafos 01.voto[a:b], corrigindo a fusão de [37] (citação do Tema 550 + parágrafo seguinte) pelo voto 03"""
    out=[]
    for i in range(a,b):
        p=V(P01)[i]
        if i==37:
            q1,q2=V(P03)[36],V(P03)[37]; assert p==q1+' '+q2; out+=[q1,q2]
        else: out.append(p)
    return out
def par(pos,titulo,texto,origem): return {'posicao':pos,'titulo':titulo,'texto':texto,'_origem':origem}
defs=[]

# ───────────── H1 · limite territorial afastado · apelação provida (04, 05, 06)
assert V(P06)[4:26]==V(P01)[3:25]==V(P05)[3:25]
tema1433=sem_vocativo(V(P06)[1],'H1 · prelim · Tema 1.433')
prelim_ileg=V(P06)[2]; assert prelim_ileg==V(P04)[2]==V(P05)[1]
honor06=sub(V(P06)[26],'em favor da União','em favor da {{ENTE_EXECUTADO}}','H1 · honor · honorários prejudicados')
presc04=V(P04)[25]; presc05=V(P05)[25]
assert V(P04)[26:28]==V(P05)[26:28]
disp=V(P06)[27]; assert disp==V(P04)[28]==V(P05)[28]
defs.append(dict(arquivo='10-h1-territorial-provida',
 id='par-matriz-2886-territorial-provida',
 nome='28,86% · Limite territorial afastado · apelação da parte exequente provida',
 especie='ApCiv', resultado=disp,
 temas='ACP 0005019-15.1997.4.03.6000; Tema 1.075/STF; Tema 733/STF; Tema 499/STF; ADI 1.576 MC; ARE 1.585.247; AgInt no REsp 1.841.604; AgInt no AREsp 2.993.227; AgInt no AREsp 2.996.314; ApCiv 5005688-98.2025.4.03.6000; Tema 1.433/STJ (ProAfR no REsp 2.234.888)',
 tese='O título da ACP 0005019-15.1997.4.03.6000 não contém limitação territorial; a eficácia erga omnes alcança servidor lotado fora de MS, sem rescisória (Tema 733/STF) e sem incidência do Tema 499/STF; prescrição alegada em contrarrazões remetida à origem.',
 tags='servidor público; 28,86% (acp); limite territorial; ilegitimidade ativa afastada; apelação provida; retorno à origem',
 processosAssociados=f'{P04}; {P05}; {P06}',
 esqueleto={'prelim':[tema1433,prelim_ileg],'jurid':V(P06)[4:25],'concl':[V(P06)[25]],'disp':[disp],'fecho':[V(P06)[28]]},
 paragrafos=[
  par('contro','Controvérsia · só limite territorial',V(P06)[3],P06),
  par('contro','Controvérsia · limite territorial e prescrição',V(P05)[2],P05),
  par('honor','Honorários pedidos pelo ente em contrarrazões · prejudicado',honor06,P06),
  par('complem','Prescrição alegada em contrarrazões · exame remetido à origem (3 parágrafos)',[presc05]+V(P04)[26:28],P05),
  par('complem','Prescrição alegada em contrarrazões, inclusive para habilitação de herdeiros · exame remetido à origem (3 parágrafos)',[presc04]+V(P04)[26:28],P04),
 ]))

# ───────────── H2 · limite territorial afastado + acordo administrativo (SIAPE) · desprovida (01, 03)
assert V(P03)[2:36]==V(P01)[3:37] and V(P03)[38:47]==V(P01)[38:47] and V(P03)[48]==V(P01)[48]
fatos=sub(V(P01)[47],'(ID 388960832)','(ID {{ID_FICHAS_FINANCEIRAS}})','H2 · fatos · fichas financeiras')
fatos03=sub(V(P03)[47],'(ID’s\xa0385140944, 385140957, 385140958, 385140959 e 385140960)','(ID’s\xa0{{IDS_FICHAS_FINANCEIRAS}})','H2 · fatos · fichas financeiras (vários IDs)')
assert fatos.replace('(ID {{ID_FICHAS_FINANCEIRAS}})','')==fatos03.replace('(ID’s\xa0{{IDS_FICHAS_FINANCEIRAS}})','')
contro03=sem_vocativo(V(P03)[1],'H2 · contro · voto 03')
disp03=sub(V(P03)[62],'recurso adesivo da FUNASA','recurso adesivo da {{ENTE_EXECUTADO}}','H2 · disp · recurso adesivo')
grat=V(P03)[51:61]
defs.append(dict(arquivo='20-h2-acordo-siape-desprovida',
 id='par-matriz-2886-acordo-administrativo-desprovida',
 nome='28,86% · Legitimidade reconhecida, mas acordo administrativo (fichas SIAPE) · apelação desprovida',
 especie='ApCiv', resultado=V(P01)[51],
 temas='ACP 0005019-15.1997.4.03.6000; Tema 1.075/STF; Tema 733/STF; Tema 499/STF; ADI 1.576 MC; ARE 1.585.247; MP 1.704/1998; MP 1.962-33/2000; MP 2.169-43/2001, arts. 6º e 7º; Tema 550/STJ; Tema 1.102/STJ; Tema 1.178/STJ; ADC 80',
 tese='Afastada a limitação territorial, o registro de pagamentos da vantagem nas fichas financeiras do SIAPE comprova acordo individual e impede nova cobrança em cumprimento individual da sentença coletiva (Temas 550 e 1.102/STJ).',
 tags='servidor público; 28,86% (acp); limite territorial; acordo administrativo; fichas financeiras SIAPE; apelação desprovida; honorários recursais',
 processosAssociados=f'{P01}; {P03}',
 esqueleto={'jurid':bloco_01(3,47),'fatos':[fatos],'aplic':[V(P01)[48]],'honor':[V(P01)[50]],'fecho':[V(P01)[52]]},
 paragrafos=[
  par('contro','Controvérsia · “No caso, a controvérsia…”',V(P01)[2],P01),
  par('contro','Controvérsia · “A controvérsia…” (abertura direta)',contro03,P03),
  par('concl','Conclusão · “Em suma, embora a parte exequente seja legitimada…”',V(P01)[49],P01),
  par('concl','Conclusão · “Afigura-se, pois, correta a solução…”',V(P03)[49],P03),
  par('consec','Litigância de má-fé pedida em contrarrazões · afastada',V(P03)[50],P03),
   par('consec',f'Gratuidade impugnada por critério objetivo · Tema 1.178/STJ e ADC 80 ({len(grat)} parágrafos)',grat,P03),
  par('disp','Dispositivo · desprovimento',V(P01)[51],P01),
  par('disp','Dispositivo · desprovimento da apelação e do recurso adesivo do ente',disp03,P03),
 ]))

# ───────────── H3 · ilegitimidade ativa · categoria representada por sindicato com ação coletiva anterior (02)
v=V(P02)
conhec=sem_vocativo(v[1],'H3 · admiss · conhecimento parcial')
f3=v[3]
f3=sub(f3,'o Sindicato dos Trabalhadores Federais em Seguridade e Seguro Social no Estado do Rio de Janeiro (SINDSPREV/RJ)','o {{NOME_DO_SINDICATO}} ({{SIGLA_DO_SINDICATO}})','H3 · contro · sindicato')
f3=sub(f3,'Ação 0023278-37.1995.4.02.5101','Ação {{NUMERO_DA_ACAO_COLETIVA_DO_SINDICATO}}','H3 · contro · ação do sindicato')
a13=v[13]
a13=sub(a13,'pelo SINDSPREV/RJ','pelo {{SIGLA_DO_SINDICATO}}','H3 · aplic · sindicato')
a13=sub(a13,'ação coletiva 0023278-37.1995.4.02.5101, em 25/09/1995','ação coletiva {{NUMERO_DA_ACAO_COLETIVA_DO_SINDICATO}}, em {{DATA_DE_AJUIZAMENTO_DA_ACAO_DO_SINDICATO}}','H3 · aplic · ação e data do sindicato')
a15=v[15]
a15=sub(a15,'ação coletiva 0023278-37.1995.4.02.5101','ação coletiva {{NUMERO_DA_ACAO_COLETIVA_DO_SINDICATO}}','H3 · aplic · ação do sindicato')
a15=sub(a15,'trabalhadores em instituições de saúde, trabalho e previdência social, com vínculo federal direto, indireto e funcional, lotados no Estado do Rio de Janeiro','{{CATEGORIA_PROFISSIONAL_REPRESENTADA_E_BASE_TERRITORIAL_DO_SINDICATO}}','H3 · aplic · categoria do sindicato')
a15=sub(a15,'(ID 376094580, f. 38)','(ID {{ID_DOCUMENTO}}, f. {{FOLHA}})','H3 · aplic · prova da categoria')
defs.append(dict(arquivo='30-h3-sindicato-desprovida',
 id='par-matriz-2886-ilegitimidade-acao-sindical',
 nome='28,86% · Ilegitimidade ativa · categoria representada por sindicato com ação coletiva anterior · apelação desprovida',
 especie='ApCiv', resultado=v[19],
 temas='ACP 0005019-15.1997.4.03.6000; limites subjetivos da coisa julgada; litispendência em ação coletiva; REsp 2.018.707; REsp 2.163.451; ApCiv 5001464-12.2024.4.03.6111',
 tese='A própria coisa julgada da ACP 0005019-15.1997.4.03.6000 exclui servidor representado por sindicato que ajuizou antes ação com o mesmo objeto; não há direito de escolher o título mais favorável.',
 tags='servidor público; 28,86% (acp); ilegitimidade ativa; ação coletiva de sindicato; limites subjetivos da coisa julgada; conhecimento parcial; apelação desprovida',
 processosAssociados=P02,
 esqueleto={'admiss':[conhec],'contro':[v[2],f3],'jurid':v[4:12],'aplic':[v[12],a13,v[14],a15,v[16]],'concl':[v[17]],'honor':[v[18]],'disp':[v[19]],'fecho':[v[20]]},
 paragrafos=[]))
json.dump({'variante_fatos_varios_ids':fatos03,'defs':defs,'substituicoes':SUBS},open('defs.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
for d in defs: print(d['id'], {k:len(x) for k,x in d['esqueleto'].items()}, len(d['paragrafos']),'parágrafos-matriz')
print(len(SUBS),'substituições')
