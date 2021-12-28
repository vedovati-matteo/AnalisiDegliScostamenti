
import pandas as pd
import sqlite3
import numpy as np
from pandas.core.frame import DataFrame
 

def getDfCosto(df, conn):

	costo_OdP_l = []

	for (nrOrdineProduzione, nrArticolo),df_OdP_Art in df.groupby(["nrOrdineProduzione", "nrArticolo"]):
		#per ogni articolo in ogni OdP(Ordine di Produzione) calcolo il costo (materie prime + lavorazione) e la quantità
		#poi sommo costi e quantià per ogni articolo (senza dividere per ordini di produzione)
		
		costo = (df_OdP_Art['tempoRisorsa'] * df_OdP_Art['costoOrarioRis']).sum()
		ld = (df_OdP_Art['tempoRisorsa'] * df_OdP_Art['costoOrarioRis']).sum()
		quantita = df_OdP_Art['quantitaOutput'].max()
		
		df_consumi = pd.read_sql_query("""
			SELECT *
			FROM Consumo
			WHERE nrDocumento="{0}" AND nrArticolo="{1}"
		""".format(nrOrdineProduzione, nrArticolo), conn)
		
		costo += df_consumi['importoTot'].sum()
		md = df_consumi['importoTot'].sum()

		costo_OdP_l.append([nrOrdineProduzione, nrArticolo, costo, md, ld, quantita])

	df_costo_OdP = pd.DataFrame(costo_OdP_l, columns=['nrOrdineProduzione', 'nrArticolo', 'costo', 'md', 'ld', 'quantita'])

	costo_l = []

	for (nrArticolo),df_Art in df_costo_OdP.groupby("nrArticolo"):
		
		costo = df_Art['costo'].sum()
		md = df_Art['md'].sum()
		ld = df_Art['ld'].sum()
		quantita = df_Art['quantita'].sum()

		costo_l.append([nrArticolo, costo, md, ld, quantita])

	df_costo = pd.DataFrame(costo_l, columns=['nrArticolo', 'costo', 'md', 'ld', 'quantita'])

	return df_costo

def getDfRicavi(df):
	#per ogni articolo trovo quanto ne ho venduto e quanto è il guadagno totale
	ricavi_l = []

	for (nrArticolo),df_Art in df.groupby('nrArticolo'):
			
		ricavo = df_Art['importoTot'].sum()
		quantita = df_Art['quantita'].sum()
		valuta = df_Art['valuta'].iloc[0]

		ricavi_l.append([nrArticolo, ricavo, quantita, valuta])

	df_ricavi = pd.DataFrame(ricavi_l, columns=['nrArticolo', 'ricavo', 'quantita', 'valuta'])

	return df_ricavi

def getColonnaGen(volumeC, mixC, mdU, ldU, volumeV, mixV, ricaviU, valutaType, valuta):

	volumeMixC = volumeC * mixC
	mdMix = volumeMixC * mdU
	ldMix = volumeMixC * ldU

	MD = mdMix.sum()
	LD = ldMix.sum()

	volumeMixV = volumeV * mixV
	rMix = volumeMixV * ricaviU / list(valuta['tassoCambio'].iloc[valutaType - 1])

	R = rMix.sum()

	return [round(MD, 2), round(LD, 2), round(LD + MD, 2), round(R, 2), round(R - LD - MD, 2)]

def getScostamentoMix(articoli, mix_b, mix_c):
	
	df_mix = pd.DataFrame(list(zip(articoli, round(mix_b * 100, 3), round(mix_c * 100 - mix_b * 100, 3), round(mix_c * 100, 3))), columns=['nrArticolo','budget', 'scostamento', 'consuntivo'])
	return df_mix.sort_values(by='scostamento', key=abs, ascending=False)

def getScostamentoMDeLD(articoli, b, c, q):
	df = pd.DataFrame(list(zip(articoli, q, round(q*(c-b), 2), round(b, 2), round(c - b, 2), round(c, 2))), columns=['nrArticolo','quantita', 'scostamento', 'budgetU', 'scostamentoU', 'consuntivoU'])
	return df.sort_values(by='scostamento', key=abs, ascending=False)

def getScostamentoCosti(articoli, b_md, c_md, b_ld, c_ld):
	df = pd.DataFrame(list(zip(articoli, round(c_md - b_md, 2), round(c_ld - b_ld, 2))), columns=['nrArticolo','md', 'ld'])
	return df

def articoloFinale(num_Articolo, tabella_valute_budget, tabella_valute_consuntivo, tabella_costi_budget,
	tabella_costi_consuntivo, tabella_vendite_budget, tabella_vendite_consuntivo, filtrata = False):
	#passami articolo e tabelle costi e vendite (sia per budget e consuntivo) e ti ritorno specifiche
	if not filtrata:
		tabella_costi_budget = filtroArticolo(num_Articolo, tabella_costi_budget)
		tabella_costi_consuntivo = filtroArticolo(num_Articolo, tabella_costi_consuntivo)
		tabella_vendite_budget = filtroArticolo(num_Articolo, tabella_vendite_budget)
		tabella_vendite_consuntivo = filtroArticolo(num_Articolo, tabella_vendite_consuntivo)

	#costi budget
	q_prodotta_budget = tabella_costi_budget['quantita'].sum()
	md_unitario_budget = tabella_costi_budget['md'].sum() / q_prodotta_budget
	ld_unitario_budget = tabella_costi_budget['ld'].sum() / q_prodotta_budget

	
	#ricavi budget
	q_venduta_budget = tabella_vendite_budget['quantita'].sum()
	prezzo_unitario_budget = (tabella_vendite_budget['ricavo'].sum() / q_venduta_budget) / tabella_valute_budget[tabella_valute_budget.codiceValuta == tabella_vendite_budget['valuta'].iloc[0]]['tassoCambio'].iloc[0]


	#costi consuntivo
	q_prodotta_consuntivo = tabella_costi_consuntivo['quantita'].sum()
	md_unitario_consuntivo = tabella_costi_consuntivo['md'].sum() / q_prodotta_consuntivo
	ld_unitario_consuntivo = tabella_costi_consuntivo['ld'].sum() / q_prodotta_consuntivo

	
	#ricavi consuntivo
	q_venduta_consuntivo = tabella_vendite_consuntivo['quantita'].sum()
	prezzo_unitario_consuntivo = (tabella_vendite_consuntivo['ricavo'].sum() / q_venduta_consuntivo) / tabella_valute_consuntivo[tabella_valute_consuntivo.codiceValuta == tabella_vendite_consuntivo['valuta'].iloc[0]]['tassoCambio'].iloc[0]


	return ((md_unitario_budget,
	ld_unitario_budget,
	q_prodotta_budget, 
	(md_unitario_budget + ld_unitario_budget) * q_prodotta_budget, #costo_totale_budget
	prezzo_unitario_budget,
	q_venduta_budget, 
	prezzo_unitario_budget * q_venduta_budget,  #ricavi_tot_budget
	prezzo_unitario_budget * q_venduta_budget - (md_unitario_budget + ld_unitario_budget) * q_prodotta_budget),

	(md_unitario_consuntivo,
	ld_unitario_consuntivo,
	q_prodotta_consuntivo,
	(md_unitario_consuntivo + ld_unitario_consuntivo) * q_prodotta_consuntivo, #costo_totale_consuntivo
	prezzo_unitario_consuntivo,
	q_venduta_consuntivo, 
	prezzo_unitario_consuntivo * q_venduta_consuntivo, #ricavi_tot_consuntivo
	prezzo_unitario_consuntivo * q_venduta_consuntivo - (md_unitario_consuntivo + ld_unitario_consuntivo) * q_prodotta_consuntivo
	))

def filtroArticolo (num_Articolo, tabella):
	return tabella[tabella.nrArticolo == num_Articolo]

def getValutaName (n_valuta):
	if n_valuta == 1:
		return 'EURO'
	if n_valuta == 2:
		return 'DOLLAR'
	if n_valuta == 3:
		return 'YEN'
	return 'NO VALUTA'

def getCliente(numArticolo, df):
	return df.query("nrArticolo == '{0}'".format(numArticolo))['numeroCliente'].iloc[0]


def getValuta(numArticolo, df_ricavi):
	return getValutaName(df_ricavi[df_ricavi.nrArticolo == numArticolo]['valuta'].iloc[0])


def getScostamenti(df_costo_b, df_costo_c, df_ricavi_b, df_ricavi_c, df_valuta_b, df_valuta_c):

	ricavi_b = df_ricavi_b.copy()
	ricavi_b['ricavo'] = ricavi_b['ricavo'] / list(df_valuta_b['tassoCambio'].iloc[ricavi_b['valuta']-1])

	ricavi_c = df_ricavi_c.copy()
	ricavi_c['ricavo'] = ricavi_c['ricavo'] / list(df_valuta_c['tassoCambio'].iloc[ricavi_c['valuta']-1])

	a = pd.merge(df_costo_b, ricavi_b, on = 'nrArticolo')[['nrArticolo','costo','ricavo']]
	b = pd.merge(df_costo_c, ricavi_c, on = 'nrArticolo')[['nrArticolo','costo','ricavo']]
	c = pd.merge(a,b, on='nrArticolo')
	data = pd.DataFrame(zip( list(c['nrArticolo']), list(round((c['costo_x'] - c['costo_y']) + (c['ricavo_y'] - c['ricavo_x']), 2))),columns=['nrArticolo','scostamento'])

	return data.sort_values("scostamento", key = abs, ascending=False)

def getScostamentoValuta(articoli, ricaviU_b, ricaviU_c, quantita, tipoValuta, valuta_b, valuta_c):
	
	df = pd.DataFrame(zip(articoli, ricaviU_b, ricaviU_c, quantita, tipoValuta), columns=['articolo','rU_b', 'rU_c', 'qta', 'valType'])

	valGroup = df.groupby(df.valType)
	df_euro = valGroup.get_group(1)
	df_dollar = valGroup.get_group(2)
	df_yen = valGroup.get_group(3)

	ricavi_euro_b = df_euro['rU_b'] * df_euro['qta'] / valuta_b['tassoCambio'].iloc[0]
	ricavi_euro_c = df_euro['rU_b'] * df_euro['qta'] / valuta_c['tassoCambio'].iloc[0]
	
	ricavi_dollar_b = df_dollar['rU_b'] * df_dollar['qta'] / valuta_b['tassoCambio'].iloc[1]
	ricavi_dollar_c = df_dollar['rU_b'] * df_dollar['qta'] / valuta_c['tassoCambio'].iloc[1]

	ricavi_yen_b = df_yen['rU_b'] * df_yen['qta'] / valuta_b['tassoCambio'].iloc[2]
	ricavi_yen_c = df_yen['rU_b'] * df_yen['qta'] / valuta_c['tassoCambio'].iloc[2]

	risValuta = ((round(ricavi_euro_b.sum(), 2), round(ricavi_euro_c.sum() - ricavi_euro_b.sum(), 2), round(ricavi_euro_c.sum(), 2)),
		(round(ricavi_dollar_b.sum(), 2), round(ricavi_dollar_c.sum() - ricavi_dollar_b.sum(), 2), round(ricavi_dollar_c.sum(), 2)),
		(round(ricavi_yen_b.sum(), 2), round(ricavi_yen_c.sum() - ricavi_yen_b.sum(), 2), round(ricavi_yen_c.sum(), 2)))

	df_euro['ricaviU_b'] = round(df_euro['rU_b'] / valuta_c['tassoCambio'].iloc[0], 2)
	df_dollar['ricaviU_b'] = round(df_dollar['rU_b'] / valuta_c['tassoCambio'].iloc[1], 2)
	df_yen['ricaviU_b'] = round(df_yen['rU_b'] / valuta_c['tassoCambio'].iloc[2], 2)

	df_euro['ricaviU_c'] = round(df_euro['rU_c'] / valuta_c['tassoCambio'].iloc[0], 2)
	df_dollar['ricaviU_c'] = round(df_dollar['rU_c'] / valuta_c['tassoCambio'].iloc[1], 2)
	df_yen['ricaviU_c'] = round(df_yen['rU_c'] / valuta_c['tassoCambio'].iloc[2], 2)

	df_ricavi = pd.concat([df_euro, df_dollar, 	df_yen])
	df_ricavi = df_ricavi.drop(columns=['rU_b', 'rU_c', 'valType'])

	df_ricavi['ricaviU_scost'] = round(df_ricavi['ricaviU_c'] - df_ricavi['ricaviU_b'], 2)
	df_ricavi['ricavi_scost'] = round(df_ricavi['ricaviU_scost'] * df_ricavi['qta'], 2)

	df_sorted = df_ricavi.sort_values('ricavi_scost', key=abs, ascending=False)[['articolo', 'qta', 'ricavi_scost', 'ricaviU_b', 'ricaviU_scost', 'ricaviU_c']]

	return risValuta, df_sorted


