# 💨 Mapa de Estaciones Meteorológicas ICAO — Argentina

Visualización interactiva del **viento promedio 1991-2020** en estaciones meteorológicas argentinas, con datos del Servicio Meteorológico Nacional (SMN) y códigos ICAO.

> **Proyecto Final** — Tecnicatura Universitaria en Programación (TUP)

---

## 📸 ¿Qué hace?

1. Un **script Python** descarga datos del SMN e ICAO, los cruza y genera `data.json`
2. Opcionalmente guarda los datos en **PostgreSQL**
3. Una **app React** muestra los datos en dos mapas interactivos:
   - 🫧 **Burbujas** — Círculos proporcionales al viento, coloreados por intensidad
   - 🌡️ **Heatmap** — Mapa de calor con densidad de viento promedio

Incluye filtrado por código ICAO, nombre de estación o provincia, estadísticas en vivo, panel de detalle por estación con gráfico de barras mensual, y modo claro/oscuro.

---

## 📁 Estructura del proyecto

```
Proyecto_Final_TUP/
├── procesar_csv.py             # Descarga SMN + ICAO, cruza y genera data.json
├── data.json                   # Dataset generado (copia raíz)
│
└── proyecto-mapa-icao/         # App React
    ├── public/
    │   ├── data.json           # Datos que consume la app
    │   └── index.html
    └── src/
        ├── App.js              # Componente principal (mapas + filtros + detalle)
        ├── App.css             # Estilos (tema oscuro / claro)
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

### 2. Script Python (datos)

Instalar dependencias de Python:

```bash
pip install pandas requests sqlalchemy psycopg2-binary
```

**Generar `data.json`** (descarga datos del SMN + ICAO, los cruza y genera el JSON):

```bash
python procesar_csv.py
```

Esto descarga los datos desde GitHub Gists, los cruza por estación, guarda `data.json` tanto en la raíz como en `proyecto-mapa-icao/public/`, y opcionalmente inserta los datos en PostgreSQL.

> 💡 El repositorio ya incluye un `data.json` listo para usar, así que podés saltear este paso si no necesitás actualizar los datos.

### 3. App React (visualización)

```bash
cd proyecto-mapa-icao
npm install --legacy-peer-deps
npm start
```

Abrir **http://localhost:3000** en el navegador.

---

## �️ PostgreSQL (opcional)

El script intenta guardar los datos en PostgreSQL automáticamente. Para que funcione:

1. Crear la base de datos:

```sql
CREATE DATABASE estaciones;
```

2. Editar las credenciales en `procesar_csv.py`:

```python
DB_USER = "postgres"
DB_PASS = "tu_contraseña"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "estaciones"
```

3. Ejecutar el script normalmente:

```bash
python procesar_csv.py
```

Si PostgreSQL no está disponible, el script genera `data.json` de todas formas y muestra un mensaje informativo.

---

## �🗺️ Uso de la app

| Acción | Cómo |
| --- | --- |
| **Filtrar** | Escribí un código ICAO (ej: `SAEZ`), nombre de estación o provincia en la barra de búsqueda |
| **Cambiar mapa** | Usá los tabs **Heatmap** / **Burbujas** |
| **Ver tooltip** | Pasá el mouse sobre una burbuja para ver ICAO, estación, viento y provincia |
| **Ver detalle** | Hacé clic en una burbuja para abrir el panel con datos completos y gráfico mensual |
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
| **Datos** | Python, Pandas, Requests, SQLAlchemy, PostgreSQL |
| **Frontend** | React 18, Leaflet, react-leaflet |
| **Mapas** | OpenStreetMap (tiles via CARTO dark/light) |

---

## � Autores

- **Jeremías Del Do** — [@jeredeldo](https://github.com/jeredeldo)
- **Ezequiel F. Osuna** — [@Ezefosuna](https://github.com/Ezefosuna)

---

## 📝 Licencia

Proyecto académico — Tecnicatura Universitaria en Programación.
