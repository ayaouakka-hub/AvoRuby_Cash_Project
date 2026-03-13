# =====================================================
# Script: extraction_ndwi_gee.py
# Projet: AVORUBY CASH v2.0 - Flux Ht (NDWI Sentinel-2)
# Region: Maroc - LAT [27.5-35.5], LON [-7.5/-2.5]
# =====================================================
import ee
import pandas as pd
from datetime import datetime

# --- ETAPE 1 : Authentification (a faire une seule fois) ---
# Commande terminal: earthengine authenticate
ee.Authenticate()
ee.Initialize(project='avoruby-cash-gee')  # Remplace par ton project ID

# --- ETAPE 2 : Charger ta grille de points depuis Ct ---
df_ct = pd.read_csv('AVORUBY_Dataset_Ct.csv')
points = df_ct[['LAT', 'LON']].drop_duplicates().values
print(f"Nombre de points a traiter: {len(points)}")

# --- ETAPE 3 : Fonction de calcul NDWI (Gao 1996) ---
def calcul_ndwi(image):
    """
    NDWI vegetation (stress hydrique interne des plantes)
    Formule: (NIR - SWIR) / (NIR + SWIR)
    Bandes Sentinel-2: B8=NIR (842nm), B11=SWIR (1610nm)
    Valeurs: [-1, 1] -> Plus c'est eleve, plus la plante est hydratee
    """
    ndwi = image.normalizedDifference(['B8', 'B11'])
    return image.addBands(ndwi.rename('NDWI'))

def apply_cloud_mask(image):
    """Masque nuages via bande SCL (Scene Classification Layer)"""
    scl = image.select('SCL')
    # Classes 4 (vegetation), 5 (sol nu), 6 (eau) = pixels valides
    mask = scl.eq(4).Or(scl.eq(5)).Or(scl.eq(6))
    return image.updateMask(mask)

# --- ETAPE 4 : Boucle sur les 18 points de ta grille ---
resultats = []

for lat, lon in points:
    print(f"\nTraitement: LAT={lat}, LON={lon}")
    
    point_geo = ee.Geometry.Point([lon, lat])
    buffer = point_geo.buffer(500)  # Buffer 500m autour du centroide du pixel NASA

    # Collection Sentinel-2 Surface Reflectance (niveau L2A)
    collection = (
        ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
        .filterBounds(buffer)
        .filterDate('2020-01-01', '2025-12-31')
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
        .map(apply_cloud_mask)
        .map(calcul_ndwi)
    )

    # Aggregation mensuelle (NDWI moyen du mois)
    for annee in range(2020, 2026):
        for mois in range(1, 13):
            debut = f'{annee}-{mois:02d}-01'
            # Dernier jour du mois (approximation)
            if mois == 12:
                fin = f'{annee+1}-01-01'
            else:
                fin = f'{annee}-{mois+1:02d}-01'

            img_mois = collection.filterDate(debut, fin).mean()

            try:
                stats = img_mois.reduceRegion(
                    reducer=ee.Reducer.mean(),
                    geometry=buffer,
                    scale=20,          # Resolution bande SWIR Sentinel-2 = 20m
                    maxPixels=1e9,
                    bestEffort=True    # Evite les timeout GEE
                ).getInfo()

                ndwi_val = stats.get('NDWI', None)
                
                resultats.append({
                    'Date': f'{annee}-{mois:02d}-01',
                    'LAT': lat,
                    'LON': lon,
                    'NDWI': round(ndwi_val, 4) if ndwi_val is not None else None,
                    'nb_images': collection.filterDate(debut, fin).size().getInfo()
                })
                print(f"  {annee}-{mois:02d}: NDWI={ndwi_val:.4f}" if ndwi_val else f"  {annee}-{mois:02d}: No data")

            except Exception as e:
                print(f"  Erreur {annee}-{mois:02d}: {e}")
                resultats.append({
                    'Date': f'{annee}-{mois:02d}-01',
                    'LAT': lat, 'LON': lon,
                    'NDWI': None, 'nb_images': 0
                })

# --- ETAPE 5 : Sauvegarde ---
df_ndwi = pd.DataFrame(resultats)
df_ndwi.to_csv('NDWI_Sentinel2.csv', index=False)

print("\n--- TERMINE ! ---")
print(f"Fichier 'NDWI_Sentinel2.csv' cree : {df_ndwi.shape[0]} lignes")
print(f"Couverture nuages (null NDWI): {df_ndwi['NDWI'].isna().sum()} mois sans donnees")
print(df_ndwi.describe())
