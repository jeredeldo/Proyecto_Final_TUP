import pandas as pd
import json
import unicodedata
from io import StringIO
import requests

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

# ── Cargar fuentes ──────────────────────────────────────────────────────────
url_smn = "https://gist.githubusercontent.com/jeredeldo/80943d8e022f58e387d578b4e75ea680/raw/315aaf51efd7844a347f73d7449183cf9c0393cc/SMN.CSV"
url_icao = "https://gist.githubusercontent.com/jeredeldo/571645d80a42dfb098c217529266a327/raw/36574b070a8d5e236559696cd54685bb69483723/ICAO.CSV"

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

print("Cargando ICAO...")
df_icao = pd.read_csv(url_icao, sep=';', encoding='utf-8')
df_icao['Estación_norm'] = df_icao['Estación'].apply(normalize_station)
df_icao = df_icao.rename(columns={'Altura': 'Altura_m'})

# ── Merge ───────────────────────────────────────────────────────────────────
cols_wind = ['Estación', 'Estación_norm', 'viento_promedio'] + months
df_merged = pd.merge(
    df_wind[cols_wind],
    df_icao[['Estación_norm', 'ICAO', 'lat', 'lon', 'Altura_m', 'Provincia']],
    on='Estación_norm',
    how='left'
)
df_merged = df_merged.drop(columns=['Estación_norm'])
df_merged = df_merged.dropna(subset=['lat', 'lon', 'viento_promedio'])
df_merged = df_merged[df_merged['ICAO'].notna() & (df_merged['ICAO'].str.strip() != '')]
df_merged = df_merged.drop_duplicates(subset=['ICAO', 'lat', 'lon'])

# ── Construir JSON con datos mensuales ──────────────────────────────────────
records = []
for _, row in df_merged.iterrows():
    rec = {
        'ICAO': row['ICAO'],
        'Estación': row['Estación'],
        'viento_promedio': round(row['viento_promedio'], 2),
        'lat': row['lat'],
        'lon': row['lon'],
        'Altura_m': row['Altura_m'] if pd.notna(row['Altura_m']) else None,
        'Provincia': row['Provincia'],
        'mensual': {}
    }
    for m in months:
        val = row[m]
        rec['mensual'][m] = round(val, 2) if pd.notna(val) else None
    records.append(rec)

# Guardar en ambas ubicaciones
for path in ["data.json", "proyecto-mapa-icao/public/data.json"]:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

print(f"Guardado {len(records)} estaciones con datos mensuales en data.json")