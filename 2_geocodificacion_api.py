import pandas as pd
import requests
import time
import numpy as np   # ← Esto soluciona el error
from functools import lru_cache

# Cargamos el CSV del paso 1
df = pd.read_csv("estaciones_viento_limpio.csv")

# Función con cache y reintentos
@lru_cache(maxsize=200)
def get_lat_lon(icao):
    if pd.isna(icao) or not str(icao).strip():  # maneja NaN y strings vacíos
        return np.nan, np.nan
    
    icao = str(icao).strip().upper()
    url = f"https://iatageo.com/getICAOLatLng/{icao}"
    
    for attempt in range(3):  # 3 reintentos
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                lat = float(data.get('latitude', np.nan))
                lon = float(data.get('longitude', np.nan))
                if not (np.isnan(lat) or np.isnan(lon)):
                    return lat, lon
        except Exception as e:
            print(f"Intento {attempt+1} falló para {icao}: {e}")
        time.sleep(1.5)  # espera para no saturar la API
    
    print(f"No se pudo obtener coordenadas para ICAO: {icao}")
    return np.nan, np.nan

# Aplicamos a la columna ICAO
print("Geocodificando estaciones... (puede tardar si hay muchas)")
df[['lat', 'lon']] = df['ICAO'].apply(lambda x: pd.Series(get_lat_lon(x)))

# Filtramos las que sí tienen coordenadas
df_valid = df.dropna(subset=['lat', 'lon'])
print(f"\nEstaciones con coordenadas válidas: {len(df_valid)} de {len(df)} totales")

# Mostramos un resumen
print("\nEjemplo de estaciones geocodificadas:")
print(df_valid[['Estación', 'ICAO', 'viento_promedio', 'lat', 'lon']].head(10))

# Guardamos el resultado
df.to_csv("estaciones_con_coordenadas.csv", index=False, encoding='utf-8-sig')
df_valid.to_csv("estaciones_con_coordenadas_validas.csv", index=False, encoding='utf-8-sig')

print("\nArchivos guardados. Listo para los mapas en el script 3.")