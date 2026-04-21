import pandas as pd
import glob
import os
import numpy as np
from pathlib import Path

# Path robuste : le dossier où se trouve ce script
BASE_DIR = Path(__file__).resolve().parent
chemin_base = BASE_DIR / 'Nasa_Power'


def empiler_annees(nom_dossier, colonne_attendue):
    """
    Lit tous les CSV d'un sous-dossier NASA Power et les empile.
    
    colonne_attendue : nom de la variable attendue (ex: 'ALLSKY_SFC_SW_DWN')
        Si le fichier contient plus de colonnes que prévu (bug NASA/téléchargement),
        on ne garde QUE LAT, LON, YEAR, DOY + la colonne attendue.
    """
    print(f"Traitement du dossier : {nom_dossier}...")
    chemin_dossier = chemin_base / nom_dossier
    fichiers_csv = glob.glob(str(chemin_dossier / "*.csv"))

    if not fichiers_csv:
        print(f"  ATTENTION : Aucun CSV trouvé dans {chemin_dossier}")
        return None

    liste_dfs = []
    for fichier in fichiers_csv:
        try:
            df = pd.read_csv(fichier, skiprows=9)
            # Garder uniquement les colonnes attendues (évite les doublons T2M/GWETTOP)
            colonnes_base = ['LAT', 'LON', 'YEAR', 'DOY']
            if colonne_attendue in df.columns:
                df = df[colonnes_base + [colonne_attendue]]
            else:
                print(f"  ⚠ {os.path.basename(fichier)} : colonne '{colonne_attendue}' absente. "
                      f"Colonnes trouvées : {list(df.columns)}")
                continue
            liste_dfs.append(df)
        except Exception as e:
            print(f"   Erreur sur {os.path.basename(fichier)} : {e}")

    if not liste_dfs:
        return None

    df_complet = pd.concat(liste_dfs, ignore_index=True)
    # Dédoublonner au cas où il y aurait des fichiers redondants
    df_complet = df_complet.drop_duplicates(subset=['LAT', 'LON', 'YEAR', 'DOY'])
    print(f"  {len(df_complet)} lignes, colonnes = {list(df_complet.columns)}")
    return df_complet


print("--- DÉBUT DE LA PRÉPARATION DES DONNÉES ---")
df_as = empiler_annees('All Sky',         'ALLSKY_SFC_SW_DWN')
df_rh = empiler_annees('Humidite',        'RH2M')
df_sw = empiler_annees('Humidité du sol', 'GWETTOP')
df_tm = empiler_annees('Température',     'T2M')

# Vérification : tous les DataFrames doivent être chargés
for nom, df in [('All Sky', df_as), ('Humidite', df_rh),
                ('Humidité du sol', df_sw), ('Température', df_tm)]:
    if df is None:
        raise SystemExit(f" Impossible de continuer : '{nom}' vide.")

print("\n--- FUSION DES PARAMÈTRES EN COURS ---")
cles_fusion = ['YEAR', 'DOY', 'LAT', 'LON']

# IMPORTANT : on passe en 'outer' pour garder tous les points spatiaux,
# puis on drop les NaN à la fin si on veut un jeu complet.
# Pour ton usage agricole tu veux probablement garder le max d'info -> outer + dropna final optionnel.
df_final = pd.merge(df_as, df_rh, on=cles_fusion, how='outer')
df_final = pd.merge(df_final, df_sw, on=cles_fusion, how='outer')
df_final = pd.merge(df_final, df_tm, on=cles_fusion, how='outer')
print(f"  Après fusion : {len(df_final)} lignes, colonnes = {list(df_final.columns)}")

print("\n--- NETTOYAGE DES DONNÉES ---")
# A. Date à partir de YEAR + DOY
df_final['Date'] = pd.to_datetime(
    df_final['YEAR'].astype(int) * 1000 + df_final['DOY'].astype(int),
    format='%Y%j'
)
# B. Remplacer -999 par NaN
df_final = df_final.replace(-999.0, np.nan)
# C. Supprimer YEAR / DOY
df_final = df_final.drop(columns=['YEAR', 'DOY'])
# D. Réorganiser
colonnes_ordre = ['Date', 'LAT', 'LON'] + \
                 [c for c in df_final.columns if c not in ('Date', 'LAT', 'LON')]
df_final = df_final[colonnes_ordre]
# E. Trier par Date puis LAT/LON pour un fichier propre
df_final = df_final.sort_values(['Date', 'LAT', 'LON']).reset_index(drop=True)

# Optionnel : si tu veux SEULEMENT les points où TOUTES les variables existent
# df_final = df_final.dropna(subset=['ALLSKY_SFC_SW_DWN', 'RH2M', 'GWETTOP', 'T2M'])

fichier_sortie = BASE_DIR / 'Dataset_Nasa_2020_2025.csv'
df_final.to_csv(fichier_sortie, index=False)

print(f"\n--- TERMINÉ ---")
print(f"Fichier : {fichier_sortie}")
print(f"Shape   : {df_final.shape}")
print(f"Période : {df_final['Date'].min()} → {df_final['Date'].max()}")
print(f"NaN par colonne :\n{df_final.isna().sum()}")
