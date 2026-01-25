import pandas as pd
import requests
import time
import numpy as np
from functools import lru_cache
import unicodedata

# Normalización de nombres (igual que antes)
def normalize_name(name):
    if pd.isna(name):
        return ''
    name = str(name).strip().lower()
    name = ''.join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')
    for suf in [' aero', ' obs', ' obs.', ' b.a.', ' del rio seco', ' del río seco', ' (mza)', ' base']:
        name = name.replace(suf, '')
    name = name.strip().replace('  ', ' ')
    return name

# Cargar CSV principal
df = pd.read_csv("estaciones_viento_limpio.csv")

# Cargar Gist con ICAO (¡esto llena los nulls!)
print("Cargando ICAO desde Gist...")
url_gist = "https://gist.githubusercontent.com/jeredeldo/e4d8eba7032bd7ac7178b898d71760dd/raw/284df0cd6853b77b74ab79ac3748f33cf4bedf23/ICAO.csv"
df_gist = pd.read_csv(url_gist, sep=';')  # Separador es ';'

# Crear dict: nombre normalizado → ICAO
icao_dict = {}
for _, row in df_gist.iterrows():
    estacion_raw = str(row.get('Estación', '')).strip()  # Columna 'Estación'
    icao = str(row.get('ICAO', '')).strip().upper()
    if icao and estacion_raw:
        norm = normalize_name(estacion_raw)
        icao_dict[norm] = icao

print(f"ICAO cargados desde Gist: {len(icao_dict)}")

# Cargar SMN para fallback coords (si iatageo falla)
print("Cargando SMN...")
df_smn = pd.read_html("http://db.at.fcen.uba.ar/station/location_data")[0]
smn_dict_icao = {}
smn_dict_name = {}
for _, row in df_smn.iterrows():
    icao = str(row.get('OACI', '')).strip().upper()
    name_norm = normalize_name(row.get('Localidad', ''))
    lat = float(row.get('Lat.[gr] [min]', np.nan))
    lon = float(row.get('Lon.[gr] [min]', np.nan))
    if not np.isnan(lat) and not np.isnan(lon):
        if icao:
            smn_dict_icao[icao] = (lat, lon)
        if name_norm:
            smn_dict_name[name_norm] = (lat, lon)

# Función: llenar ICAO si null, luego obtener coords
@lru_cache(maxsize=200)
def get_icao_and_coords(icao_orig, estacion):
    icao = str(icao_orig).strip().upper() if not pd.isna(icao_orig) else ''
    estacion_norm = normalize_name(estacion)
    
    # Llenar ICAO si está vacío, desde Gist
    if not icao and estacion_norm in icao_dict:
        icao = icao_dict[estacion_norm]
        print(f"Llenado ICAO para '{estacion}' ({estacion_norm}): {icao}")
    
    # Obtener coords con ICAO (prefer iatageo)
    if icao:
        try:
            r = requests.get(f"https://iatageo.com/getICAOLatLng/{icao}", timeout=10)
            if r.status_code == 200:
                data = r.json()
                lat = float(data.get('latitude', np.nan))
                lon = float(data.get('longitude', np.nan))
                if not np.isnan(lat) and not np.isnan(lon):
                    print(f"Coords desde iatageo ({icao}): {lat}, {lon}")
                    return icao, lat, lon
        except Exception as e:
            print(f"Error iatageo para {icao}: {e}")
    
    # Fallback SMN
    if icao in smn_dict_icao:
        lat, lon = smn_dict_icao[icao]
        print(f"Coords desde SMN ICAO {icao}: {lat}, {lon}")
        return icao, lat, lon
    if estacion_norm in smn_dict_name:
        lat, lon = smn_dict_name[estacion_norm]
        print(f"Coords desde SMN nombre '{estacion_norm}': {lat}, {lon}")
        return icao, lat, lon
    
    print(f"No coords para '{estacion}' (ICAO: {icao})")
    return icao, np.nan, np.nan

# Aplicar
print("Procesando estaciones...")
results = df.apply(lambda row: get_icao_and_coords(row['ICAO'], row['Estación']), axis=1)
df[['ICAO', 'lat', 'lon']] = pd.DataFrame(results.tolist(), index=df.index)

# Limpiar y guardar
df['ICAO'] = df['ICAO'].replace('', np.nan).fillna('No encontrado')  # Opcional: si aún null, pon texto
df_valid = df.dropna(subset=['lat', 'lon'])
print(f"Válidas: {len(df_valid)} / {len(df)}")

df.to_csv("estaciones_con_coordenadas.csv", index=False, encoding='utf-8-sig')
df_valid.to_csv("estaciones_con_coordenadas_validas.csv", index=False, encoding='utf-8-sig')
print("¡Listo! CSV actualizado sin ICAO null (o muy pocos).")