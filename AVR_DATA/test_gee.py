import ee

MY_PROJECT_ID = 'avoruby-cash-gee' 

try:
    ee.Initialize(project=MY_PROJECT_ID)
    print("NADI ! GEE m-connecter w m9ad.")
    
    # Test simple : Njbdou l'altitude d Meknès par exemple
    dem = ee.Image('USGS/SRTMGL1_003')
    point = ee.Geometry.Point([-5.55, 33.89]) # Meknès
    val = dem.sample(point, 30).first().get('elevation').getInfo()
    print(f"Altitude de Meknès : {val} mètres.")

except Exception as e:
    print(f"Ba9i chi moshkil : {e}")