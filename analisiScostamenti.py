# %%
import pandas as pd
pd.options.mode.chained_assignment = None 
import sqlite3
import functions as fun

conn = sqlite3.connect('dati.db')

# %%

articoliSemi_b = pd.read_sql_query("""
	SELECT codicemp, sum(quantitaMP)
	FROM Consumo
	WHERE codicemp IN (SELECT nrarticolo FROM Consumo) AND BC='BUDGET'
	GROUP BY codicemp
""", conn)

articoliSemi_c = pd.read_sql_query("""
	SELECT codicemp, sum(quantitaMP)
	FROM Consumo
	WHERE codicemp IN (SELECT nrarticolo FROM Consumo) AND BC='CONSUNTIVO'
	GROUP BY codicemp
""", conn)



# %% [COSTI]
df = pd.read_sql_query("""
	SELECT ior.nrOrdineProduzione, ior.nrArticolo, ior.BC, ior.tempoRisorsa, cor.costoOrarioRis, ior.quantitaOutput
	FROM Impiego_orario_risorse as ior
	JOIN Costo_orario_risorse as cor ON (ior.risorsa = cor.risorsa AND ior.nrAreaProd = cor.areaProd AND ior.BC = cor.BC)
""", conn)

BCgrouped = df.groupby(df.BC)
df_b = BCgrouped.get_group('BUDGET')
df_c = BCgrouped.get_group('CONSUNTIVO')

df_costo_b = fun.getDfCosto(df_b, conn)
df_costo_c = fun.getDfCosto(df_c, conn)

# %% [RICAVI]
df = pd.read_sql_query("""
	SELECT v.nrArticolo, v.BC, v.quantita, v.importoTot, c.valuta
	FROM Vendita as v
	JOIN Cliente as c ON (v.nrOrigine = c.numeroCliente)
""", conn)

BCgrouped = df.groupby(df.BC)
df_b = BCgrouped.get_group('BUDGET')
df_c = BCgrouped.get_group('CONSUNTIVO')


df_ricavi_b = fun.getDfRicavi(df_b)
df_ricavi_c = fun.getDfRicavi(df_c)

# %% [PREP ANALISI]
#articoli
articoli_c = list(df_costo_b['nrArticolo'])
articoli_v = list(df_ricavi_b['nrArticolo'])

# %%

df_costo_b1 = df_costo_b.copy()
df_costo_c1 = df_costo_c.copy()

# quantita

qta_b = []

for r in df_costo_b.values:
	v = articoliSemi_b.index[articoliSemi_b['codiceMP'] == r[0]].tolist()
	if v:
		q = float(r[4] - articoliSemi_b.iloc[v]['sum(quantitaMP)'])
		if  q >= 0:
			qta_b.append(q)
		else:
			qta_b.append(0)
		
	else:
		qta_b.append(r[4])

qta_c = []

for r in df_costo_c.values:
	v = articoliSemi_c.index[articoliSemi_c['codiceMP'] == r[0]].tolist()
	if v:
		q = float(r[4] - articoliSemi_c.iloc[v]['sum(quantitaMP)'])
		if  q >= 0:
			qta_c.append(q)
		else:
			qta_c.append(0)
		
	else:
		qta_c.append(r[4])

df_costo_b['quantita'] = qta_b
df_costo_c['quantita'] = qta_c

# %%

# volume
volume_costi_b = df_costo_b['quantita'].sum()
volume_costi_c = df_costo_c['quantita'].sum()

volume_ricavi_b = df_ricavi_b['quantita'].sum()
volume_ricavi_c = df_ricavi_c['quantita'].sum()

# mix
mix_costi_b = df_costo_b['quantita'] / volume_costi_b 
mix_costi_c = df_costo_c['quantita'] / volume_costi_c 
mix_ricavi_b = df_ricavi_b['quantita'] / volume_ricavi_b 
mix_ricavi_c = df_ricavi_c['quantita'] / volume_ricavi_c 

# costi unitari
costoU_b = df_costo_b['costo'] / df_costo_b1['quantita']
costoU_c = df_costo_c['costo'] / df_costo_c1['quantita']
# materiale diretto
mdU_b = df_costo_b['md'] / df_costo_b1['quantita']
mdU_c = df_costo_c['md'] / df_costo_c1['quantita']
#lavoro diretto
ldU_b = df_costo_b['ld'] / df_costo_b1['quantita']
ldU_c = df_costo_c['ld'] / df_costo_c1['quantita']

# ricavi unitari
ricaviU_b = df_ricavi_b['ricavo'] / df_ricavi_b['quantita']
ricaviU_c = df_ricavi_c['ricavo'] / df_ricavi_c['quantita']

# valuta
df_valuta = pd.read_sql_query("""
	SELECT *
	FROM Valuta
""", conn)

BCgrouped = df_valuta.groupby(df_valuta.BC)
df_valuta_b = BCgrouped.get_group('BUDGET')
df_valuta_c = BCgrouped.get_group('CONSUNTIVO')




# %% [pagina iniziale]

budget = fun.getColonnaGen(volume_costi_b, mix_costi_b, mdU_b, ldU_b, volume_ricavi_b, mix_ricavi_b, ricaviU_b, df_ricavi_b['valuta'], df_valuta_b)
mix_std = fun.getColonnaGen(volume_costi_c, mix_costi_b, mdU_b, ldU_b, volume_ricavi_c, mix_ricavi_b, ricaviU_b, df_ricavi_b['valuta'], df_valuta_b)
mix_eff = fun.getColonnaGen(volume_costi_c, mix_costi_c, mdU_b, ldU_b, volume_ricavi_c, mix_ricavi_c, ricaviU_b, df_ricavi_b['valuta'], df_valuta_b)
consuntivo = fun.getColonnaGen(volume_costi_c, mix_costi_c, mdU_c, ldU_c, volume_ricavi_c, mix_ricavi_c, ricaviU_c, df_ricavi_c['valuta'], df_valuta_c)

tabellaScostamenti = (budget, mix_std, mix_eff, consuntivo)

# %% [scostamento volumi]
volumi = ((int(volume_costi_b), int(volume_costi_c)),(int(volume_ricavi_b), int(volume_ricavi_c)))
delta_volumi = (round(mix_std[2] - budget[2], 2), round(mix_std[3] - budget[3], 2))

# %% [scostamento mix]
# costi
mix_scostamento_c = fun.getScostamentoMix(articoli_c, mix_costi_b, mix_costi_c)
delta_mix_c = round(mix_eff[2] - mix_std[2], 2)
# -- grafico

# vendite
mix_scostamento_v = fun.getScostamentoMix(articoli_v, mix_ricavi_b, mix_ricavi_c)
delta_mix_v = round(mix_eff[3] - mix_std[3], 2)
# -- grafico

# %% [scostamento costo MD e LD]
md_scostamento = fun.getScostamentoMDeLD(articoli_c, mdU_b, mdU_c, df_costo_c['quantita'])
delta_md = round(consuntivo[0] - mix_eff[0], 2)
# -- grafico

ld_scostamento = fun.getScostamentoMDeLD(articoli_c, ldU_b, ldU_c, df_costo_c['quantita'])
delta_ld = round(consuntivo[1] - mix_eff[1], 2)
# -- grafico
delta_costi = round(delta_md + delta_ld, 2)
costi_scostamento = fun.getScostamentoCosti(articoli_c, mdU_b, mdU_c, ldU_b, ldU_c)
# -- grafico condiviso MD e LD ?

# %% [valuta / prezzo vendita]
valuta_scostamento, ricavi_scostamento = fun.getScostamentoValuta(articoli_v, ricaviU_b, ricaviU_c, df_ricavi_c['quantita'], df_ricavi_c['valuta'], df_valuta_b, df_valuta_c)
# -- grafico
mix_eff_valutaC = round(valuta_scostamento[0][2] + valuta_scostamento[1][2] + valuta_scostamento[2][2], 2)

delta_valuta = round(mix_eff_valutaC - mix_eff[3], 2)

delta_ricavi = round(consuntivo[3] -  mix_eff_valutaC, 2)
# %% [selezione di articoli specifici]
artScost = fun.getScostamenti(df_costo_b1, df_costo_c1, df_ricavi_b, df_ricavi_c, df_valuta_b, df_valuta_c)

df_articoli = pd.read_sql_query("""
SELECT v.nrArticolo, c.numeroCliente
FROM Vendita as v
JOIN Cliente as c ON (v.nrOrigine = c.numeroCliente)"""
, conn)




# %%