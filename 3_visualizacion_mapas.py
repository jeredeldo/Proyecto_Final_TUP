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

# Mapa de burbujas con tamaño FIJO (igual para todas)
fig_bubble = px.scatter_mapbox(
    df,
    lat="lat",
    lon="lon",
    # NO usamos size= aquí → lo quitamos o lo ponemos en None para no variar
    # size="viento_promedio",  # ← comentado o eliminado
    color="viento_promedio",  # Seguimos coloreando por valor (opcional)
    hover_name="Estación",
    hover_data={"viento_promedio": ":.2f", "ICAO": True},
    color_continuous_scale=px.colors.sequential.OrRd,
    zoom=3.5,
    center={"lat": -38.4, "lon": -63.6},
    mapbox_style="open-street-map",
    title="Ubicación de estaciones de medición de viento - Argentina (tamaño fijo)"
)

# ¡Esto es lo clave! Tamaño fijo en píxeles para TODOS los markers
fig_bubble.update_traces(
    marker=dict(
        size=12,          # Tamaño fijo en píxeles (ajustá: 8-15 suele verse bien en mapas)
        opacity=0.8,      # Un poco transparente para no tapar mucho
        allowoverlap=True # Permite superposición si hay estaciones muy cercanas
    )
)

# Opcional: si querés que el color siga indicando el valor, pero tamaño no
# (ya lo hace por defecto con color=)

fig_bubble.update_layout(
    margin={"r":0, "t":60, "l":0, "b":0},
    # Opcional: agrandar un poco el título o agregar leyenda clara
    title_font_size=20
)

fig_bubble.show()

# Mapa de densidad (este queda igual, ya que no usa burbujas individuales)
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
    title="Zonas con mayor intensidad promedio de viento (heatmap)"
)

fig_density.update_layout(margin={"r":0, "t":60, "l":0, "b":0})
fig_density.show()

print("Mapas abiertos en tu navegador. ¡Listo!")