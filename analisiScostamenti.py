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

# valuta
df_valuta = pd.read_sql_query("""
	SELECT *
	FROM Valuta
""", conn)

BCgrouped = df_valuta.groupby(df_valuta.BC)
df_valuta_b = BCgrouped.get_group('BUDGET')
df_valuta_c = BCgrouped.get_group('CONSUNTIVO')




# %%
