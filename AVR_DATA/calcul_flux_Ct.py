import pandas as pd
import numpy as np
from pathlib import Path

# Path robuste : le dossier où se trouve ce script
BASE_DIR = Path(__file__).resolve().parent

print("--- FUSION NASA & OPEN-METEO + CALCUL DU VPD ---")

# 1. Chargement
print("Chargement des fichiers...")
df_nasa  = pd.read_csv(BASE_DIR / 'Dataset_Nasa_2020_2025.csv')
df_pluie = pd.read_csv(BASE_DIR / 'Precipitations_OpenMeteo.csv')

df_nasa['Date']  = pd.to_datetime(df_nasa['Date'])
df_pluie['Date'] = pd.to_datetime(df_pluie['Date'])

print(f"  NASA  : {df_nasa.shape}, colonnes = {list(df_nasa.columns)}")
print(f"  Pluie : {df_pluie.shape}, colonnes = {list(df_pluie.columns)}")

# 2. Fusion
# ⚙ Choix du type de jointure :
#   - 'inner'  : garde seulement les points (Date,LAT,LON) présents dans les 2 datasets
#                (= ~18 points car la grille pluie est très restreinte)
#   - 'outer'  : garde tous les points (NaN sur la pluie là où elle n'existe pas)
#   - 'left'   : garde tous les points NASA, NaN sur la pluie si absente
# → Change simplement la valeur de TYPE_FUSION ci-dessous selon ton besoin.
TYPE_FUSION = 'inner'

print(f"\nFusion ({TYPE_FUSION} join) en cours...")
df_final = pd.merge(df_nasa, df_pluie, on=['Date', 'LAT', 'LON'], how=TYPE_FUSION)
print(f"  Résultat : {df_final.shape}")

# Option : remplir les NaN de pluie par 0 (pluie absente = pas de précipitation)
# Décommente la ligne suivante si tu veux ce comportement
# df_final['Precipitations_mm'] = df_final['Precipitations_mm'].fillna(0)

# 3. Vérification des colonnes attendues
colonnes_requises = ['T2M', 'RH2M', 'GWETTOP', 'ALLSKY_SFC_SW_DWN', 'Precipitations_mm']
manquantes = [c for c in colonnes_requises if c not in df_final.columns]
if manquantes:
    print(f"⚠ Colonnes manquantes : {manquantes}")
    print(f"   Colonnes disponibles : {list(df_final.columns)}")

# 4. Calcul du VPD (Vapor Pressure Deficit = stress thermique)
# Formule de Tetens : SVP = 0.61078 * exp(17.27*T / (T+237.3))   en kPa
print("\nCalcul du VPD...")
T  = df_final['T2M']
RH = df_final['RH2M']
SVP = 0.61078 * np.exp((17.27 * T) / (T + 237.3))   # Saturation Vapor Pressure
AVP = SVP * (RH / 100)                              # Actual Vapor Pressure
df_final['VPD'] = (SVP - AVP).round(3)

# Alerte si VPD n'a pas pu être calculé partout
nb_nan_vpd = df_final['VPD'].isna().sum()
if nb_nan_vpd > 0:
    print(f"  ⚠ {nb_nan_vpd} lignes avec VPD=NaN (T2M ou RH2M manquant)")

# 5. Sauvegarde
fichier_sortie = BASE_DIR / 'AVORUBY_Dataset_Ct.csv'
df_final.to_csv(fichier_sortie, index=False)

print(f"\n--- TERMINÉ ---")
print(f"Fichier : {fichier_sortie}")
print(f"Shape   : {df_final.shape}")
print(f"Période : {df_final['Date'].min().date()} → {df_final['Date'].max().date()}")
print(f"NaN par colonne :\n{df_final.isna().sum()}")
