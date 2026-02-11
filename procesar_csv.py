import pandas as pd
import json

# Carga tu CSV (cambia la ruta si es necesario)
df = pd.read_csv("estaciones_viento_con_icao_coords.csv")  # o pega el contenido directamente como antes

# Limpieza básica
df = df.dropna(subset=['lat', 'lon', 'viento_promedio'])
df = df[df['ICAO'].notna() & (df['ICAO'].str.strip() != '')]
df = df.drop_duplicates(subset=['ICAO', 'lat', 'lon'])  # evita duplicados

# Selecciona solo las columnas útiles
data = df[['ICAO', 'Estación', 'viento_promedio', 'lat', 'lon', 'Provincia']].to_dict(orient='records')

# Guarda como JSON
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Guardado {len(data)} estaciones válidas en data.json")