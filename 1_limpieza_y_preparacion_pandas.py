import pandas as pd
import numpy as np
import requests
from io import StringIO

# URLs
url_smn = "https://gist.githubusercontent.com/jeredeldo/aecbbee1f5afc5c3ff92fda19a89e6d9/raw/ba44c64201be5a24927d3b18ccc90cc84e91d92f/SMN.CSV"
url_icao = "https://gist.githubusercontent.com/jeredeldo/e4d8eba7032bd7ac7178b898d71760dd/raw/284df0cd6853b77b74ab79ac3748f33cf4bedf23/ICAO.csv"

# Descargamos manualmente para controlar encoding y separador
response = requests.get(url_smn)
response.raise_for_status()  # falla si no descarga

# Intentamos leer como TSV con utf-8 (el gist usa utf-8)
try:
    df = pd.read_csv(StringIO(response.text), sep='\t', encoding='utf-8')
    print("Cargado OK con sep='\t' y utf-8")
except Exception as e:
    print("Fallo con utf-8:", e)
    # Fallback: latin-1 (común en datos argentinos viejos)
    df = pd.read_csv(StringIO(response.text), sep='\t', encoding='latin-1')
    print("Cargado con latin-1 fallback")

# Mostramos columnas reales para debug
print("\nColumnas detectadas:", df.columns.tolist())

# Renombramos columnas si vienen con espacios o mal parseadas
df.columns = df.columns.str.strip()  # quita espacios al inicio/fin

# Si por algún motivo no detecta 'Estación', forzamos header manual
if 'Estación' not in df.columns:
    print("¡Header no detectado! Forzando columnas manuales...")
    df = pd.read_csv(StringIO(response.text), sep='\t', encoding='utf-8',
                     names=['Estación', 'Valor Medio de', 'Ene', 'Feb', 'Mar', 'Abr',
                            'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
                     header=0, skiprows=1)  # skip el header original si falla

# Normalizamos nombres de estaciones (minúsculas, espacios extras)
df['Estación'] = df['Estación'].astype(str).str.strip().str.lower().str.replace(r'\s+', ' ', regex=True)

df_icao = pd.read_csv(url_icao, sep=';', encoding='utf-8')
df_icao['Estación'] = df_icao['Estación'].astype(str).str.strip().str.lower().str.replace(r'\s+', ' ', regex=True)

# Debug: mostramos primeras filas
print("\nPrimeras 5 filas de df:")
print(df.head())

# Filtrar solo velocidad del viento
df = df[df['Valor Medio de'].str.contains('Velocidad del Viento', na=False, case=False)]

# Meses correctos (incluye Sep que faltaba)
months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

# Convertir a numérico (S/D → NaN)
for col in months:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Al menos un mes con dato (opcional, pero evita promedios NaN totales)
df = df[df[months].notna().any(axis=1)]

# Promedio anual
df['viento_promedio'] = df[months].mean(axis=1, skipna=True)

# Merge (left join)
df_merged = pd.merge(
    df[['Estación', 'viento_promedio']],
    df_icao[['Estación', 'ICAO']],
    on='Estación',
    how='left'
)

print(f"\nEstaciones encontradas: {len(df_merged)}")
print(f"Con ICAO match: {df_merged['ICAO'].notna().sum()}")
print("\nPrimeras 10 filas del merge:")
print(df_merged.head(10))

# Guardar
df_merged.to_csv("estaciones_viento_limpio.csv", index=False, encoding='utf-8-sig')
print("\nGuardado en: estaciones_viento_limpio.csv")