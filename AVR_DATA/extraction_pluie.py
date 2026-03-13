import pandas as pd
import requests
import time

print("--- DÉMARRAGE DE L'EXTRACTION OPEN-METEO ---")

# 1. On lit ton fichier NASA pour récupérer les points de ta région
df_nasa = pd.read_csv('Dataset_Nasa_2020_2025.csv')

# 2. On extrait toutes les combinaisons uniques de Latitude et Longitude
points_uniques = df_nasa[['LAT', 'LON']].drop_duplicates().values
print(f"Nombre de points géographiques trouvés dans ta région : {len(points_uniques)}")

toutes_les_pluies = []

# 3. Le robot va boucler sur chaque point pour télécharger la pluie
for lat, lon in points_uniques:
    print(f"Téléchargement de la pluie pour Lat: {lat}, Lon: {lon}...")
    
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": "2020-01-01",
        "end_date": "2025-12-31",
        "daily": "precipitation_sum",
        "timezone": "auto"
    }
    
    try:
        # Demande à Open-Meteo
        reponse = requests.get(url, params=params)
        donnees = reponse.json()
        
        # Transformation en tableau pour ce point précis
        df_temp = pd.DataFrame({
            "Date": pd.to_datetime(donnees["daily"]["time"]),
            "Precipitations_mm": donnees["daily"]["precipitation_sum"],
            "LAT": lat,
            "LON": lon
        })
        toutes_les_pluies.append(df_temp)
        
    except Exception as e:
        print(f"Erreur pour le point {lat},{lon} : {e}")
    
    # Pause d'une seconde pour ne pas bloquer l'API gratuite
    time.sleep(1) 

# 4. On rassemble tout et on sauvegarde !
if toutes_les_pluies:
    df_pluie_final = pd.concat(toutes_les_pluies, ignore_index=True)
    df_pluie_final.to_csv('Precipitations_OpenMeteo.csv', index=False)
    print("\n--- TERMINÉ ! ---")
    print("Le fichier 'Precipitations_OpenMeteo.csv' a été créé avec succès.")
else:
    print("Oups, aucune donnée n'a été téléchargée.")