import pandas as pd
import glob
import os
import numpy as np
# 1. Le dossier qui contient tes paramètres (puisque ton script est dans AVR_DATA)
chemin_base = 'Nasa_Power'

# 2. Fonction pour lire et empiler toutes les années d'un dossier
def empiler_annees(nom_dossier):
    print(f"Traitement du dossier : {nom_dossier}...")
    
    # Construire le chemin vers le dossier spécifique (ex: Nasa_Power/All Sky)
    chemin_dossier = os.path.join(chemin_base, nom_dossier)
    
    # Trouver tous les fichiers .csv dans ce dossier
    fichiers_csv = glob.glob(os.path.join(chemin_dossier, "*.csv"))
    
    if not fichiers_csv:
        print(f"ATTENTION: Aucun fichier CSV trouvé dans {chemin_dossier}")
        return None

    liste_dataframes = []
    for fichier in fichiers_csv:
        try:
            # Note: Les fichiers NASA POWER ont souvent un texte d'explication au début.
            # Si le code donne une erreur ici, essaie de remplacer cette ligne par :
            # df = pd.read_csv(fichier, skiprows=14) 
            # (Remplace 14 par le vrai nombre de lignes de texte avant le tableau dans ton CSV)
            df = pd.read_csv(fichier, skiprows=9)
            liste_dataframes.append(df)
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier {fichier}: {e}")
        
    # On rassemble toutes les années en un seul grand tableau
    df_complet = pd.concat(liste_dataframes, ignore_index=True)
    return df_complet

# 3. Empiler les données pour chaque paramètre
print("--- DÉBUT DE LA PRÉPARATION DES DONNÉES ---")
df_as = empiler_annees('All Sky')
df_rh = empiler_annees('Humidite')
df_sw = empiler_annees('Humidité du sol')
df_tm = empiler_annees('Température')

# 4. Fusionner les 4 grands tableaux ensemble
print("\n--- FUSION DES PARAMÈTRES EN COURS ---")
cles_fusion = ['YEAR', 'DOY', 'LAT', 'LON']

# Fusion étape par étape
df_final = pd.merge(df_as, df_rh, on=cles_fusion, how='inner')
df_final = pd.merge(df_final, df_sw, on=cles_fusion, how='inner')
df_final = pd.merge(df_final, df_tm, on=cles_fusion, how='inner')

df_final = pd.merge(df_final, df_tm, on=cles_fusion, how='inner')

# ========================================================
# --- NOUVELLE ÉTAPE : NETTOYAGE ET FORMATAGE ---
# ========================================================
print("\n--- NETTOYAGE DES DONNÉES EN COURS ---")

# A. Transformer YEAR et DOY en une vraie date (ex: 2021-01-15)
df_final['Date'] = pd.to_datetime(df_final['YEAR'] * 1000 + df_final['DOY'], format='%Y%j')

# B. Remplacer les valeurs aberrantes de la NASA (-999.0) par du "vide" (NaN)
df_final = df_final.replace(-999.0, np.nan)

# C. Supprimer définitivement les colonnes YEAR et DOY
df_final = df_final.drop(columns=['YEAR', 'DOY'])

# D. Réorganiser les colonnes pour mettre 'Date' tout au début du tableau
colonnes_ordre = ['Date'] + [col for col in df_final.columns if col != 'Date']
df_final = df_final[colonnes_ordre]

# ======================
# 5. Sauvegarder le résultat final
fichier_sortie = 'Dataset_Nasa_2020_2025.csv'
df_final.to_csv(fichier_sortie, index=False)
print(f"\n--- TERMINÉ ! ---")
print(f"Le fichier final '{fichier_sortie}' a été créé avec succès dans AVR_DATA.")
