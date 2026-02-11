# 💨 Mapa de Estaciones Meteorológicas ICAO — Argentina

Visualización interactiva del **viento promedio anual** en estaciones meteorológicas argentinas, con datos del Servicio Meteorológico Nacional (SMN) y códigos ICAO.

> **Proyecto Final** — Tecnicatura Universitaria en Programación (TUP)

---

## 📸 ¿Qué hace?

1. **Scripts Python** descargan datos del SMN e ICAO, los cruzan y generan un dataset limpio
2. El dataset se guarda como **CSV** y opcionalmente en **PostgreSQL**
3. Una **app React** muestra los datos en dos mapas interactivos:
   - 🫧 **Burbujas** — Círculos proporcionales al viento, coloreados por intensidad
   - 🌡️ **Heatmap** — Mapa de calor con densidad de viento promedio

Incluye filtrado por código ICAO, nombre de estación o provincia, y estadísticas en vivo.

---

## 📁 Estructura del proyecto

```
Proyecto_Final_TUP/
├── limpieza_pandas.py          # Descarga, limpia y cruza datos SMN + ICAO
├── procesar_csv.py             # Genera data.json para la app React
├── visualizacion_mapas.py      # Mapas con Plotly (standalone, sin React)
├── estaciones_viento_con_icao_coords.csv  # Dataset generado
│
└── proyecto-mapa-icao/         # App React
    ├── public/
    │   ├── data.json           # Datos que consume la app
    │   └── index.html
    └── src/
        ├── App.js              # Componente principal (mapa + filtros)
        ├── App.css             # Estilos (tema oscuro)
        ├── index.js            # Entry point
        └── index.css           # Estilos globales
```

---

## 🛠️ Requisitos previos

| Herramienta   | Versión mínima |
| ------------- | -------------- |
| **Node.js**   | 16+            |
| **npm**       | 8+             |
| **Python**    | 3.9+           |
| **PostgreSQL**| 12+ *(opcional)* |

---

## 🚀 Instalación y uso

### 1. Clonar el repositorio

```bash
git clone https://github.com/jeredeldo/Proyecto_Final_TUP.git
cd Proyecto_Final_TUP
```

### 2. Scripts Python (datos)

Instalar dependencias de Python:

```bash
pip install pandas numpy requests sqlalchemy psycopg2-binary
```

**Generar el dataset** (descarga datos del SMN + ICAO y los cruza):

```bash
python limpieza_pandas.py
```

Esto genera `estaciones_viento_con_icao_coords.csv` y, si tenés PostgreSQL configurado, guarda los datos en la tabla `estaciones`.

**Generar `data.json`** para la app React:

```bash
python procesar_csv.py
```

Esto crea `data.json`. Copialo a la carpeta de la app:

```bash
cp data.json proyecto-mapa-icao/public/data.json
```

> 💡 El repositorio ya incluye un `data.json` listo para usar, así que podés saltear este paso si no necesitás actualizar los datos.

### 3. App React (visualización)

```bash
cd proyecto-mapa-icao
npm install --legacy-peer-deps
npm start
```

Abrir **http://localhost:3000** en el navegador.

---

## 🗄️ PostgreSQL (opcional)

Si querés guardar los datos en una base de datos PostgreSQL:

1. Crear la base de datos:

```sql
CREATE DATABASE estaciones;
```

2. Editar las credenciales en `limpieza_pandas.py`:

```python
DB_USER = "postgres"
DB_PASS = "tu_contraseña"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "estaciones"
```

3. Ejecutar el script:

```bash
python limpieza_pandas.py
```

---

## 🗺️ Uso de la app

| Acción | Cómo |
| --- | --- |
| **Filtrar** | Escribí un código ICAO (ej: `SAEZ`), nombre de estación o provincia en la barra de búsqueda |
| **Cambiar mapa** | Usá los tabs **Heatmap** / **Burbujas** |
| **Ver datos** | Pasá el mouse sobre una burbuja para ver ICAO, estación, viento y provincia |
| **Zoom** | Scroll o botones +/- del mapa |
| **Limpiar filtro** | Botón "Limpiar" o borrá el texto |

---

## 📊 Fuentes de datos

- **SMN** — Servicio Meteorológico Nacional: valores medios de velocidad del viento por estación
- **ICAO** — Códigos de estaciones con coordenadas geográficas (latitud, longitud, altura)

---

## 🧰 Tecnologías

| Capa | Stack |
| --- | --- |
| **Datos** | Python, Pandas, SQLAlchemy, PostgreSQL |
| **Frontend** | React 18, Leaflet, react-leaflet, leaflet.heat |
| **Mapas** | OpenStreetMap (tiles via CARTO dark) |

---

## 👤 Autor

**Jerónimo Deldo** — [@jeredeldo](https://github.com/jeredeldo)

---

## 📝 Licencia

Proyecto académico — Tecnicatura Universitaria en Programación.
