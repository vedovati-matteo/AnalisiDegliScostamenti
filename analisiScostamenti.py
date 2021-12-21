# %%
import pandas as pd
import sqlite3
import functions as fun

conn = sqlite3.connect('dati.db')

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

# volume
volume_costi_b = df_costo_b['quantita'].sum()
volume_costi_c = df_costo_c['quantita'].sum()

volume_ricavi_b = df_ricavi_b['quantita'].sum()
volume_ricavi_c = df_ricavi_c['quantita'].sum()

# mix
mix_costi_b = df_costo_b['quantita'] / volume_costi_b 
mix_costi_c = df_costo_c['quantita'] / volume_costi_c 
mix_ricavi_b = df_ricavi_b['quantita'] / volume_ricavi_b 
mix_ricavi_b = df_ricavi_b['quantita'] / volume_ricavi_b 

# costi unitari
costoU_b = df_costo_b['costo'] / df_costo_b['quantita']
costoU_c = df_costo_c['costo'] / df_costo_c['quantita']
# materiale diretto
mdU_b = df_costo_b['md'] / df_costo_b['quantita']
mdU_c = df_costo_c['md'] / df_costo_c['quantita']
#lavoro diretto
ldU_b = df_costo_b['ld'] / df_costo_b['quantita']
ldU_c = df_costo_c['ld'] / df_costo_c['quantita']

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




# %%

budget = fun.getColonnaGen2(volume_costi_b, mix_costi_b, mdU_b, ldU_b, volume_ricavi_b, mix_ricavi_b, ricaviU_b, df_ricavi_b['valuta'], df_valuta_b)
print(budget)

# %%
