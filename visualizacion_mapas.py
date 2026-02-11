import pandas as pd
import plotly.express as px
import numpy as np
import os

archivo = "estaciones_viento_con_icao_coords.csv"

if not os.path.exists(archivo):
    print(f"ERROR: No se encuentra {archivo}. Ejecutá primero el script 1.")
    exit()

df = pd.read_csv(archivo)
df = df.dropna(subset=['lat', 'lon', 'viento_promedio'])

if len(df) == 0:
    print("No hay datos con coordenadas y viento válido.")
    exit()

print(f"Graficando {len(df)} estaciones\n")

# Mapa burbujas (tamaño y color por viento)
fig_bubble = px.scatter_mapbox(
    df,
    lat="lat",
    lon="lon",
    size="viento_promedio",
    size_max=30,
    color="viento_promedio",
    hover_name="Estación",
    hover_data={"viento_promedio": ":.1f km/h", "ICAO": True, "Provincia": True},
    color_continuous_scale=px.colors.sequential.YlOrRd,
    zoom=4.2,
    center={"lat": -38.0, "lon": -65.0},
    mapbox_style="open-street-map",
    title="Velocidad media del viento - Estaciones SMN + ICAO (Argentina)"
)

fig_bubble.update_traces(marker=dict(opacity=0.75, allowoverlap=True))
fig_bubble.update_layout(
    margin={"r":0, "t":60, "l":0, "b":0},
    coloraxis_colorbar=dict(title="Viento (km/h)")
)

fig_bubble.show()

"""
Heatmap suavizado sin sesgo de densidad
1) Se promedia el viento por celdas regulares (una muestra por celda)
2) Se aplica KDE con density_mapbox usando ese promedio como intensidad
Así evitamos que zonas con muchas estaciones pesen más por cantidad.
"""

# Tamaño de celda en grados (ajusta suavidad del promedio)
cell_deg = 0.6

lat_min, lon_min = df['lat'].min(), df['lon'].min()
lat_bin = np.floor((df['lat'] - lat_min) / cell_deg).astype(int)
lon_bin = np.floor((df['lon'] - lon_min) / cell_deg).astype(int)
df_cells = df.assign(lat_bin=lat_bin, lon_bin=lon_bin)

agg = df_cells.groupby(['lat_bin', 'lon_bin']).agg(
    mean_viento=("viento_promedio", "mean"),
    estaciones=("viento_promedio", "size")
).reset_index()

# Centro de cada celda (una muestra por celda)
agg['lat'] = lat_min + (agg['lat_bin'] + 0.5) * cell_deg
agg['lon'] = lon_min + (agg['lon_bin'] + 0.5) * cell_deg

# Rango de color basado en los promedios
rc_min = float(agg['mean_viento'].min())
rc_max = float(agg['mean_viento'].max())

fig_heat = px.density_mapbox(
    agg,
    lat="lat",
    lon="lon",
    z="mean_viento",
    radius=50,
    zoom=4.2,
    center={"lat": -38.0, "lon": -65.0},
    mapbox_style="open-street-map",
    color_continuous_scale=px.colors.sequential.Plasma_r,
    range_color=(rc_min, rc_max),
    title="Mapa de calor: Viento promedio (suavizado por celda)"
)

fig_heat.update_layout(margin={"r":0, "t":60, "l":0, "b":0})
fig_heat.show()

print("Mapas abiertos en el navegador.")