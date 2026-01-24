import pandas as pd
import plotly.express as px
import os

print("Iniciando visualización de mapas...\n")

# Verificamos que exista el archivo
archivo = "estaciones_con_coordenadas.csv"
if not os.path.exists(archivo):
    print(f"ERROR → No se encuentra el archivo: {archivo}")
    print("Ejecutá primero el script 2 (geocodificación)")
    exit()

df = pd.read_csv(archivo)

# Quitamos filas sin coordenadas (por seguridad)
df = df.dropna(subset=['lat', 'lon'])

if len(df) == 0:
    print("No hay estaciones con coordenadas válidas. Revisá el script 2.")
    exit()

print(f"→ Vamos a graficar {len(df)} estaciones con coordenadas\n")

# Mapa de burbujas
fig_bubble = px.scatter_mapbox(
    df,
    lat="lat",
    lon="lon",
    size="viento_promedio",
    color="viento_promedio",
    hover_name="Estación",
    hover_data={"viento_promedio": ":.2f", "ICAO": True},
    color_continuous_scale=px.colors.sequential.OrRd,
    size_max=55,
    zoom=3.5,
    center={"lat": -38.4, "lon": -63.6},
    mapbox_style="open-street-map",
    title="Velocidad promedio del viento - Argentina"
)

fig_bubble.update_layout(margin={"r":0, "t":60, "l":0, "b":0})
fig_bubble.show()

# Mapa de densidad / intensidad
fig_density = px.density_mapbox(
    df,
    lat="lat",
    lon="lon",
    z="viento_promedio",
    hover_name="Estación",
    radius=40,
    zoom=3.5,
    center={"lat": -38.4, "lon": -63.6},
    mapbox_style="open-street-map",
    color_continuous_scale=px.colors.sequential.Hot,
    title="Zonas con mayor intensidad promedio de viento"
)

fig_density.update_layout(margin={"r":0, "t":60, "l":0, "b":0})
fig_density.show()

print("Mapas abiertos en tu navegador. ¡Listo!")