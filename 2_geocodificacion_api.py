import pandas as pd
import requests
import time
import numpy as np
from functools import lru_cache
import unicodedata

# Función para normalizar nombres (quita tildes, lower, remueve sufijos comunes)
def normalize_name(name):
    if pd.isna(name):
        return ''
    name = str(name).strip().lower()
    # Quitar acentos/tildes
    name = ''.join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')
    # Remover sufijos comunes y variaciones
    for suf in [' aero', ' obs', ' obs.', ' b.a.', ' del rio seco', ' del río seco', ' (mza)', ' base']:
        name = name.replace(suf, '')
    name = name.strip().replace('  ', ' ')  # limpia espacios extra
    return name

# Cargamos el CSV
df = pd.read_csv("estaciones_viento_limpio.csv")

# Cargamos tabla SMN
print("Cargando lista oficial de estaciones SMN...")
url_smn = "http://db.at.fcen.uba.ar/station/location_data"
df_smn = pd.read_html(url_smn)[0]

print("Columnas SMN:", df_smn.columns.tolist())

# Diccionarios
smn_dict_icao = {}
smn_dict_name = {}
for _, row in df_smn.iterrows():
    icao = str(row.get('OACI', '')).strip().upper()
    name_raw = str(row.get('Localidad', '')).strip()
    name_norm = normalize_name(name_raw)
    lat = row.get('Lat.[gr] [min]', np.nan)
    lon = row.get('Lon.[gr] [min]', np.nan)
    try:
        lat = float(lat)
        lon = float(lon)
        if not (np.isnan(lat) or np.isnan(lon)):
            if icao:
                smn_dict_icao[icao] = (lat, lon)
            if name_norm:
                smn_dict_name[name_norm] = (lat, lon)  # key normalizada
                # Opcional: agregar variaciones extras si querés
                if 'quiaca' in name_norm:
                    smn_dict_name['la quiaca'] = (lat, lon)
                if 'villa maria' in name_norm:
                    smn_dict_name['villa maria del rio seco'] = (lat, lon)
    except:
        pass

print(f"Estaciones SMN: {len(smn_dict_icao)} ICAO, {len(smn_dict_name)} nombres normalizados.")

# Función principal
@lru_cache(maxsize=200)
def get_lat_lon(icao, estacion):
    icao_str = str(icao).strip().upper() if not pd.isna(icao) else ''
    estacion_raw = str(estacion).strip()
    estacion_norm = normalize_name(estacion_raw)
    
    print(f"Procesando: ICAO='{icao_str}', Estación raw='{estacion_raw}' → norm='{estacion_norm}'")
    
    if not icao_str and not estacion_norm:
        return np.nan, np.nan
    
    # 1. iatageo si hay ICAO
    if icao_str:
        url = f"https://iatageo.com/getICAOLatLng/{icao_str}"
        for attempt in range(3):
            try:
                r = requests.get(url, timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    lat = float(data.get('latitude', np.nan))
                    lon = float(data.get('longitude', np.nan))
                    if not (np.isnan(lat) or np.isnan(lon)):
                        print(f"Éxito iatageo {icao_str}: {lat}, {lon}")
                        return lat, lon
            except Exception as e:
                print(f"Fallo intento {attempt+1} iatageo {icao_str}: {e}")
            time.sleep(1.5)
    
    # 2. SMN por ICAO
    if icao_str in smn_dict_icao:
        lat, lon = smn_dict_icao[icao_str]
        print(f"Éxito SMN ICAO {icao_str}: {lat}, {lon}")
        return lat, lon
    
    # 3. SMN por nombre normalizado (exacto)
    if estacion_norm in smn_dict_name:
        lat, lon = smn_dict_name[estacion_norm]
        print(f"Éxito SMN nombre '{estacion_norm}': {lat}, {lon}")
        return lat, lon
    
    # 4. Intentos parciales si no exacto (opcional, descomenta si faltan pocas)
    # for key in smn_dict_name:
    #     if estacion_norm in key or key in estacion_norm:
    #         lat, lon = smn_dict_name[key]
    #         print(f"Éxito parcial nombre '{key}' para '{estacion_norm}': {lat}, {lon}")
    #         return lat, lon
    
    print(f"Falló: ICAO '{icao_str}' / Estación norm '{estacion_norm}'")
    return np.nan, np.nan

# Aplicar
print("\nGeocodificando...")
df[['lat', 'lon']] = df.apply(lambda row: pd.Series(get_lat_lon(row['ICAO'], row['Estación'])), axis=1)

df_valid = df.dropna(subset=['lat', 'lon'])
print(f"\nVálidas: {len(df_valid)} de {len(df)}")

print("\nEjemplo:")
print(df_valid[['Estación', 'ICAO', 'viento_promedio', 'lat', 'lon']].head(10))

df.to_csv("estaciones_con_coordenadas.csv", index=False, encoding='utf-8-sig')
df_valid.to_csv("estaciones_con_coordenadas_validas.csv", index=False, encoding='utf-8-sig')
print("Guardado.")