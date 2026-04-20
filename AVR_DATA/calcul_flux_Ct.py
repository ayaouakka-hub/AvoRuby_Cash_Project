import pandas as pd
import numpy as np

# 1. Chargement des données brutes
# On récupère les données météo NASA (Temp/Humidité) et Open-Meteo (Pluie)
df_nasa = pd.read_csv('Dataset_Nasa_2020_2025.csv')
df_pluie = pd.read_csv('Precipitations_OpenMeteo.csv')

# Conversion au format datetime pour le filtrage
df_nasa['Date'] = pd.to_datetime(df_nasa['Date'])
df_pluie['Date'] = pd.to_datetime(df_pluie['Date'])

# 2. Synchronisation temporelle (Période d'étude 2022-2025)
# On restreint l'analyse à l'intervalle commun de 4 ans
df_nasa = df_nasa[(df_nasa['Date'] >= '2022-01-01') & (df_nasa['Date'] <= '2025-12-31')]
df_pluie = df_pluie[(df_pluie['Date'] >= '2022-01-01') & (df_pluie['Date'] <= '2025-12-31')]

# 3. Fusion des datasets (Inner Join)
# On merge par Date et Coordonnées GPS pour aligner les variables
df_final = pd.merge(df_nasa, df_pluie, on=['Date', 'LAT', 'LON'], how='inner')

# Nettoyage : Remplacer les valeurs de pluie manquantes par 0
df_final['Precipitations_mm'] = df_final['Precipitations_mm'].fillna(0)

# 4. Calcul de l'indicateur VPD (Vapor Pressure Deficit)
# Le VPD mesure le stress thermique réel sur la plante (différence de pression de vapeur)
T = df_final['T2M']      # Température moyenne à 2m
RH = df_final['RH2M']    # Humidité relative
 
# Formule de Tetens pour la pression de vapeur à saturation (kPa)
SVP = 0.61078 * np.exp((17.27 * T) / (T + 237.3))
# Pression de vapeur réelle
AVP = SVP * (RH / 100)
# Calcul final du déficit
df_final['VPD'] = (SVP - AVP).round(3)

# 5. Export du Flux Ct final
# Ce fichier contient toutes les variables climatiques synchronisées
df_final.to_csv('AVORUBY_Flux_Ct.csv', index=False)

print(f"Flux Ct généré. Période : {df_final['Date'].min().date()} au {df_final['Date'].max().date()}")
print(f"Nombre total d'observations : {len(df_final)}")
