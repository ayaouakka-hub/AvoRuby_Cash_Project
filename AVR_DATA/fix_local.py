import pandas as pd
import numpy as np

# 1. Chargement du fichier original (celui qui a le gap)
print("Chargement du fichier source...")
df = pd.read_csv('AVORUBY_Flux_Ct.csv')
df['Date'] = pd.to_datetime(df['Date'])
df['MonthDay'] = df['Date'].dt.strftime('%m-%d')
df['Year'] = df['Date'].dt.year

# 2. Isolation de 2024 et calcul de la moyenne (2022, 2023, 2025)
df_2024 = df[df['Year'] == 2024].copy()
df_others = df[df['Year'] != 2024].copy()

print("Application de l'imputation climatologique pour 2024...")
# On groupe par jour/mois + coordonnées pour garder la précision spatiale
climatology = df_others.groupby(['MonthDay', 'LAT', 'LON'])[['T2M', 'RH2M', 'ALLSKY_SFC_SW_DWN']].mean().reset_index()

# 3. Remplissage des NaNs
df_2024 = df_2024.drop(columns=['T2M', 'RH2M', 'ALLSKY_SFC_SW_DWN', 'VPD'])
df_2024 = df_2024.merge(climatology, on=['MonthDay', 'LAT', 'LON'], how='left')

# 4. Recalcul du VPD (Indispensable pour la cohérence)
print("Recalcul des indicateurs de stress (VPD)...")
T = df_2024['T2M']
RH = df_2024['RH2M']
SVP = 0.61078 * np.exp((17.27 * T) / (T + 237.3))
AVP = SVP * (RH / 100)
df_2024['VPD'] = (SVP - AVP).round(3)

# 5. Fusion et Sauvegarde finale
df_final = pd.concat([df_others, df_2024]).sort_values(['Date', 'LAT', 'LON'])
df_final = df_final.drop(columns=['MonthDay', 'Year'])

# C'EST ICI QUE LE FICHIER SE CRÉE SUR TON PC
df_final.to_csv('AVORUBY_Dataset_Ct_Final.csv', index=False)

print("---")
print("✅ TERMINÉ : Le fichier 'AVORUBY_Dataset_Ct_Final.csv' a été généré.")
print(f"✅ Taille du fichier : {len(df_final)} lignes.")