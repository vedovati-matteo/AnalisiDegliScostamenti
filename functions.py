
import pandas as pd
import sqlite3
import numpy as np
 

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
	
	df_mix = pd.DataFrame(list(zip(articoli, mix_b, mix_c - mix_b, mix_c)), columns=['nrArticolo','budget', 'scostamento', 'consuntivo'])
	return df_mix.sort_values(by='scostamento', key=abs, ascending=False)

def getScostamentoMDeLD(articoli, b, c, q):
	df = pd.DataFrame(list(zip(articoli, q, round(q*(c-b), 2), b, round(c - b, 2), c)), columns=['nrArticolo','quantita', 'scostamento', 'budgetU', 'scostamentoU', 'consuntivoU'])
	return df.sort_values(by='scostamento', key=abs, ascending=False)

