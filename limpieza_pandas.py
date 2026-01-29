import pandas as pd
import numpy as np
import requests
from io import StringIO
import unicodedata

def normalize_station(name):
    if pd.isna(name) or not name:
        return ''
    name = str(name).strip().lower()
    name = ''.join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')
    to_remove = ['aero', 'obs', 'observatorio', 'b.a.', '*', '(mza)', 'del rio seco', 'del río seco', 'base', 'u n', 'internacional']
    for item in to_remove:
        name = name.replace(item, '')
    name = name.replace('  ', ' ').strip()
    return name

# URLs nuevas
url_smn = "https://gist.githubusercontent.com/jeredeldo/80943d8e022f58e387d578b4e75ea680/raw/315aaf51efd7844a347f73d7449183cf9c0393cc/SMN.CSV"
url_icao = "https://gist.githubusercontent.com/jeredeldo/571645d80a42dfb098c217529266a327/raw/36574b070a8d5e236559696cd54685bb69483723/ICAO.CSV"

# ── SMN: velocidad viento + promedio ────────────────────────────────────────
print("Cargando SMN...")
df_smn = pd.read_csv(url_smn, sep='\t', encoding='utf-8')
df_smn.columns = df_smn.columns.str.strip()
df_smn['Estación_norm'] = df_smn['Estación'].apply(normalize_station)

df_wind = df_smn[df_smn['Valor Medio de'].str.contains('Velocidad del Viento', na=False, case=False)].copy()

months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
for col in months:
    df_wind[col] = pd.to_numeric(df_wind[col], errors='coerce')

df_wind = df_wind[df_wind[months].notna().any(axis=1)]
df_wind['viento_promedio'] = df_wind[months].mean(axis=1, skipna=True)
print(f"Estaciones con datos de viento: {len(df_wind)}")

# ── ICAO nuevo: ya viene con lat/lon decimal ────────────────────────────────
print("\nCargando ICAO nuevo (con coordenadas)...")
df_icao = pd.read_csv(url_icao, sep=';', encoding='utf-8')
df_icao['Estación_norm'] = df_icao['Estación'].apply(normalize_station)

# Renombrar columnas para consistencia
df_icao = df_icao.rename(columns={
    'lat': 'lat',
    'lon': 'lon',
    'Altura': 'Altura_m'
})

print(f"Estaciones ICAO cargadas: {len(df_icao)}")
print("Ejemplo ICAO:")
print(df_icao[['Estación', 'Estación_norm', 'ICAO', 'lat', 'lon']].head(10))

# ── Merge por nombre normalizado ────────────────────────────────────────────
df_merged = pd.merge(
    df_wind[['Estación', 'Estación_norm', 'viento_promedio']],
    df_icao[['Estación_norm', 'ICAO', 'lat', 'lon', 'Altura_m', 'Provincia']],
    on='Estación_norm',
    how='left'
)

df_merged = df_merged.drop(columns=['Estación_norm'])

print(f"\nTotal merged: {len(df_merged)}")
print(f"Con ICAO y coordenadas: {df_merged['ICAO'].notna().sum()}")

print("\nPrimeras 15 filas:")
print(df_merged.head(15))

# Guardar
df_merged.to_csv("estaciones_viento_con_icao_coords.csv", index=False, encoding='utf-8-sig')
print("\nGuardado en: estaciones_viento_con_icao_coords.csv")