import pandas as pd
import numpy as np
import requests

# URL del archivo
url_smn = "https://gist.githubusercontent.com/pablo27207/4019b9e58671a9ea3f9c9daf13c7c4ae/raw/e77b9306d8c4d3deee66a5278df9be8b173f0996/SMN.CSV"

# Descargamos el contenido
response = requests.get(url_smn)
if response.status_code != 200:
    print("Error al descargar:", response.status_code)
    exit()

# Separamos en líneas
lines = response.text.splitlines()

# Lista para guardar los datos
data = []

# Meses (para nombrar columnas)
months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

# Procesamos línea por línea
for line in lines[1:]:  # saltamos la primera línea (encabezado)
    if not line.strip():
        continue
    
    # Separamos por tabs o múltiples espacios
    parts = [p.strip() for p in line.split('\t') if p.strip()]  # mejor con tab
    if len(parts) < 3:
        parts = [p.strip() for p in line.split()]  # fallback a espacios
    
    if len(parts) < 14:  # estación + variable + 12 meses mínimo
        continue
    
    estacion = parts[0].replace(' OBS.', '').replace(' AERO', '').strip()
    variable = parts[1].strip()
    
    # Los 12 valores mensuales están en parts[2:14]
    valores_str = parts[2:14]
    if len(valores_str) != 12:
        continue
    
    valores = []
    for v in valores_str:
        if v == 'S/D' or v == '':
            valores.append(np.nan)
        else:
            try:
                valores.append(float(v))
            except ValueError:
                valores.append(np.nan)
    
    # Guardamos una fila por variable-estación
    fila = {'Estacion': estacion, 'Variable': variable}
    fila.update({mes: val for mes, val in zip(months, valores)})
    data.append(fila)

# Creamos el DataFrame
df = pd.DataFrame(data)

# Mostramos resultados
print("Estaciones únicas encontradas:", df['Estacion'].unique())
print("\nForma del DataFrame:", df.shape)
print("\nPrimeras 10 filas:")
print(df.head(10))

# Opcional: pivot para tener variables como columnas (multi-column)
df_pivot = df.pivot(index='Estacion', columns='Variable', values=months)
print("\nVista pivot (multi-column):")
print(df_pivot.head())

# Guardar a CSV limpio si querés
# df.to_csv('datos_smn_limpios.csv', index=False)