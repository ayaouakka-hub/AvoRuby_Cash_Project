import pandas as pd
import numpy as np

print("--- FUSION NASA & OPEN-METEO ET CALCUL DU VPD ---")

# 1. Charger les deux fichiers
print("Chargement des fichiers...")
df_nasa = pd.read_csv('Dataset_Nasa_2020_2025.csv')
df_pluie = pd.read_csv('Precipitations_OpenMeteo.csv')

df_nasa['Date'] = pd.to_datetime(df_nasa['Date'])
df_pluie['Date'] = pd.to_datetime(df_pluie['Date'])

# 2. La grande fusion
print("Fusion des données en cours...")
df_final = pd.merge(df_nasa, df_pluie, on=['Date', 'LAT', 'LON'], how='inner')

# ==========================================
# ASTUCE PRO : Nettoyage des colonnes en double
# ==========================================
print("Nettoyage des colonnes en double (_x, _y)...")
colonnes_a_supprimer = ['GWETTOP_x', 'T2M_x', 'T2M_y', 'GWETTOP_y']
# On supprime ces colonnes si elles existent
df_final = df_final.drop(columns=[col for col in colonnes_a_supprimer if col in df_final.columns])

# 3. Calcul du VPD (Stress Thermique)
print("Calcul de la formule thermodynamique (VPD)...")

# Tes colonnes exactes
col_temp = 'T2M'   
col_rh = 'RH2M'    

SVP = 0.61078 * np.exp((17.27 * df_final[col_temp]) / (df_final[col_temp] + 237.3))
AVP = SVP * (df_final[col_rh] / 100)
df_final['VPD'] = SVP - AVP

df_final['VPD'] = df_final['VPD'].round(3)

# 4. Sauvegarde finale
fichier_sortie = 'AVORUBY_Dataset_Ct.csv'
df_final.to_csv(fichier_sortie, index=False)

print("\n--- OPÉRATION RÉUSSIE ! ---")
print(f"Ton Flux Environnemental est prêt et nettoyé dans : {fichier_sortie}")