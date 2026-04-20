import ee
import pandas as pd

# Authentification avec Project ID
MY_PROJECT_ID = 'avoruby-cash-gee' 
ee.Initialize(project=MY_PROJECT_ID)

# 1. Définir la liste des barrages stratégiques
# [Nom, Longitude, Latitude]
barrages_list = [
    ['Oued_El_Makhazine', -5.845, 34.938],
    ['Al_Wahda', -5.153, 34.604],
    ['Youssef_Ibn_Tachfine', -9.497, 29.851],
    ['Idriss_1er', -4.665, 34.125]
]

def extract_dam_data(name, lon, lat):
    print(f"Extraction pour le barrage : {name}...")
    roi = ee.Geometry.Point([lon, lat]).buffer(5000) # 5km pour couvrir la cuvette
    
    collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
        .filterBounds(roi) \
        .filterDate('2020-01-01', '2026-01-01') \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 15))

    def calculate_water(image):
        ndwi = image.normalizedDifference(['B3', 'B8']).rename('NDWI')
        water_mask = ndwi.gt(0)
        area = water_mask.multiply(ee.Image.pixelArea())
        stats = area.reduceRegion(reducer=ee.Reducer.sum(), geometry=roi, scale=20)
        return ee.Feature(None, {'Date': image.date().format('YYYY-MM-dd'), 'Surface': stats.get('NDWI')})

    results = collection.map(calculate_water).getInfo()['features']
    
    df = pd.DataFrame([res['properties'] for res in results])
    df['Nom_Barrage'] = name
    return df

# 2. Lancer la boucle sur tous les barrages
all_data = []
for dam in barrages_list:
    df_temp = extract_dam_data(dam[0], dam[1], dam[2])
    all_data.append(df_temp)

# 3. Fusionner et Sauvegarder
df_final_barrages = pd.concat(all_data)
df_final_barrages.to_csv('Dataset_Barrages_Multi.csv', index=False)
print("Safi! Ga3 l'barrages t-sauvegardaw f Dataset_Barrages_Multi.csv")