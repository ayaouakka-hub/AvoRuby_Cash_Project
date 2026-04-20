import pandas as pd

# 1. Chargement des fichiers sources (Output de GEE)
df_ndwi = pd.read_csv('NDWI_Sentinel2.csv')
df_barrages = pd.read_csv('Dataset_Barrages_Multi.csv')

# Formatage des dates
df_ndwi['Date'] = pd.to_datetime(df_ndwi['Date'])
df_barrages['Date'] = pd.to_datetime(df_barrages['Date'])

# 2. Aggrégation spatiale
# On calcule la moyenne du NDWI sur les 18 points pour avoir une tendance globale
df_ndwi_daily = df_ndwi.groupby('Date')['NDWI'].mean().reset_index()

# Somme de la surface d'eau pour l'ensemble des barrages suivis
df_barrages_daily = df_barrages.groupby('Date')['Surface'].sum().reset_index()

# 3. Alignement temporel (Période d'étude 2022-2025)
# On crée une timeline continue pour synchroniser avec les autres flux
full_range = pd.date_range(start='2022-01-01', end='2025-12-31', freq='D')
master_ht = pd.DataFrame({'Date': full_range})

# 4. Fusion des Dataframes
master_ht = master_ht.merge(df_ndwi_daily, on='Date', how='left')
master_ht = master_ht.merge(df_barrages_daily, on='Date', how='left')

# 5. Gestion des gaps (Revenance satellite de 5 jours)
# Interpolation linéaire pour transformer la donnée discrète en série temporelle continue
master_ht['NDWI'] = master_ht['NDWI'].interpolate(method='linear')
master_ht['Surface'] = master_ht['Surface'].interpolate(method='linear')

# Backfill et Forwardfill pour les valeurs aux limites
master_ht = master_ht.ffill().bfill()

# 6. Export du Flux Ht final
master_ht.to_csv('AVORUBY_Flux_Ht.csv', index=False)

print("Génération du fichier AVORUBY_Flux_Ht.csv terminée.")