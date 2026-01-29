import pandas as pd
import plotly.express as px
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
    color_continuous_scale=px.colors.sequential.OrRd_r,
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

# Heatmap de intensidad
fig_heat = px.density_mapbox(
    df,
    lat="lat",
    lon="lon",
    z="viento_promedio",
    radius=45,
    zoom=4.2,
    center={"lat": -38.0, "lon": -65.0},
    mapbox_style="open-street-map",
    color_continuous_scale=px.colors.sequential.Hot_r,
    title="Mapa de calor: Zonas con mayor viento promedio"
)

fig_heat.update_layout(margin={"r":0, "t":60, "l":0, "b":0})
fig_heat.show()

print("Mapas abiertos en el navegador.")