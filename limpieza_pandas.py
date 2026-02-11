import pandas as pd
import numpy as np
import requests
from io import StringIO
import unicodedata
import sqlalchemy
from sqlalchemy import create_engine, text

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

# Imprimir versiones para depuración
print(f"Iniciando... (Pandas: {pd.__version__}, SQLAlchemy: {sqlalchemy.__version__})")

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

# ── Guardar en PostgreSQL ───────────────────────────────────────────────────
# TODO: Ajustá estos valores según tu configuración de PostgreSQL
DB_USER = "postgres"
DB_PASS = "postgres" # <--- Cambiá esto por tu contraseña real
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "estaciones" # <--- Asegurate de crear esta base de datos primero

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

try:
    print(f"\nGuardando datos en PostgreSQL ({DB_NAME})...")
    engine = create_engine(DATABASE_URL)

    # Crear tabla y insertar datos usando SQL raw (compatible con Pandas 3.0 + SQLAlchemy 2.0)
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS estaciones"))
        conn.execute(text("""
            CREATE TABLE estaciones (
                "Estación" TEXT,
                viento_promedio DOUBLE PRECISION,
                "ICAO" TEXT,
                lat DOUBLE PRECISION,
                lon DOUBLE PRECISION,
                "Altura_m" DOUBLE PRECISION,
                "Provincia" TEXT
            )
        """))
        for _, row in df_merged.iterrows():
            conn.execute(text("""
                INSERT INTO estaciones ("Estación", viento_promedio, "ICAO", lat, lon, "Altura_m", "Provincia")
                VALUES (:est, :viento, :icao, :lat, :lon, :alt, :prov)
            """), {
                "est": row.get("Estación"),
                "viento": row.get("viento_promedio"),
                "icao": row.get("ICAO"),
                "lat": row.get("lat"),
                "lon": row.get("lon"),
                "alt": row.get("Altura_m"),
                "prov": row.get("Provincia"),
            })
    print(f"¡Éxito! Tabla 'estaciones' creada con {len(df_merged)} filas.")
except Exception as e:
    print(f"\nNo se pudo guardar en la base de datos: {e}")
    if "multiple values for argument 'schema'" in str(e):
        print("ERROR DE COMPATIBILIDAD: Pandas no se lleva bien con SQLAlchemy 2.0 en este entorno.")
        print("SOLUCIÓN RÁPIDA: Instalá una versión anterior de SQLAlchemy.")
        print("Ejecutá: pip install \"sqlalchemy<2.0\"")
    else:
        print("Recordá instalar: pip install sqlalchemy psycopg2-binary")
        print(f"Y crear la base de datos '{DB_NAME}' en tu servidor PostgreSQL.")
