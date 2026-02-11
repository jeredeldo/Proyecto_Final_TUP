import React, { useState, useEffect, useMemo } from 'react';
import { MapContainer, TileLayer, CircleMarker, Tooltip, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './App.css';

/* ─── Paleta de colores compartida (misma para burbujas y heatmap) ─── */
const COLOR_STOPS = [
  { v: 0,  r: 66,  g: 133, b: 244 },
  { v: 8,  r: 0,   g: 188, b: 212 },
  { v: 13, r: 76,  g: 175, b: 80  },
  { v: 18, r: 255, g: 193, b: 7   },
  { v: 22, r: 255, g: 87,  b: 34  },
  { v: 28, r: 211, g: 47,  b: 47  },
];

function windColor(speed) {
  if (speed <= COLOR_STOPS[0].v)
    return `rgb(${COLOR_STOPS[0].r},${COLOR_STOPS[0].g},${COLOR_STOPS[0].b})`;
  if (speed >= COLOR_STOPS[COLOR_STOPS.length - 1].v) {
    const s = COLOR_STOPS[COLOR_STOPS.length - 1];
    return `rgb(${s.r},${s.g},${s.b})`;
  }
  for (let i = 0; i < COLOR_STOPS.length - 1; i++) {
    if (speed >= COLOR_STOPS[i].v && speed <= COLOR_STOPS[i + 1].v) {
      const t = (speed - COLOR_STOPS[i].v) / (COLOR_STOPS[i + 1].v - COLOR_STOPS[i].v);
      const r = Math.round(COLOR_STOPS[i].r + t * (COLOR_STOPS[i + 1].r - COLOR_STOPS[i].r));
      const g = Math.round(COLOR_STOPS[i].g + t * (COLOR_STOPS[i + 1].g - COLOR_STOPS[i].g));
      const b = Math.round(COLOR_STOPS[i].b + t * (COLOR_STOPS[i + 1].b - COLOR_STOPS[i].b));
      return `rgb(${r},${g},${b})`;
    }
  }
  return `rgb(${COLOR_STOPS[0].r},${COLOR_STOPS[0].g},${COLOR_STOPS[0].b})`;
}

function windColorRGB(speed) {
  if (speed <= COLOR_STOPS[0].v) return COLOR_STOPS[0];
  if (speed >= COLOR_STOPS[COLOR_STOPS.length - 1].v) return COLOR_STOPS[COLOR_STOPS.length - 1];
  for (let i = 0; i < COLOR_STOPS.length - 1; i++) {
    if (speed >= COLOR_STOPS[i].v && speed <= COLOR_STOPS[i + 1].v) {
      const t = (speed - COLOR_STOPS[i].v) / (COLOR_STOPS[i + 1].v - COLOR_STOPS[i].v);
      return {
        r: Math.round(COLOR_STOPS[i].r + t * (COLOR_STOPS[i + 1].r - COLOR_STOPS[i].r)),
        g: Math.round(COLOR_STOPS[i].g + t * (COLOR_STOPS[i + 1].g - COLOR_STOPS[i].g)),
        b: Math.round(COLOR_STOPS[i].b + t * (COLOR_STOPS[i + 1].b - COLOR_STOPS[i].b)),
      };
    }
  }
  return COLOR_STOPS[0];
}

/* ─── HeatmapLayer con IDW (misma paleta que burbujas, sin acumulación) ─── */
function HeatmapLayer({ points }) {
  const map = useMap();
  useEffect(() => {
    if (!points?.length || !map) return;

    /* Interpolación IDW: para cada píxel calcula la velocidad
       de viento ponderada por la distancia inversa a cada estación.
       power=2 → interpolación suave y regional */
    function idw(lat, lon) {
      let sumW = 0, sumV = 0, closest = Infinity;
      for (const p of points) {
        const dlat = lat - p.lat;
        const dlon = (lon - p.lon) * Math.cos(lat * Math.PI / 180);
        const d2 = dlat * dlat + dlon * dlon;
        const d = Math.sqrt(d2);
        if (d < 0.05) return { wind: p.viento_promedio, dist: d };
        const w = 1 / d2; // power=2
        sumW += w;
        sumV += w * p.viento_promedio;
        if (d < closest) closest = d;
      }
      return { wind: sumV / sumW, dist: closest };
    }

    /* Bounds amplios para que bordes queden fuera del viewport */
    const southLat = -66, northLat = -18;
    const westLon = -80, eastLon = -38;
    const bounds = [[southLat, westLon], [northLat, eastLon]];
    const W = 400, H = 500;
    const lonRange = eastLon - westLon;

    /* Funciones Mercator para corregir la proyección */
    const toMerc = (lat) => Math.log(Math.tan(Math.PI / 4 + (lat * Math.PI) / 360));
    const fromMerc = (my) => (2 * Math.atan(Math.exp(my)) - Math.PI / 2) * 180 / Math.PI;
    const mercNorth = toMerc(northLat);
    const mercSouth = toMerc(southLat);

    const canvas = document.createElement('canvas');
    canvas.width = W;
    canvas.height = H;
    const ctx = canvas.getContext('2d');
    const imgData = ctx.createImageData(W, H);

    for (let y = 0; y < H; y++) {
      /* Convertir pixel y → lat usando Mercator (no lineal) */
      const t = y / H;
      const mercY = mercNorth - t * (mercNorth - mercSouth);
      const lat = fromMerc(mercY);
      for (let x = 0; x < W; x++) {
        const lon = westLon + (x / W) * lonRange;
        const { wind, dist } = idw(lat, lon);
        const c = windColorRGB(wind);
        const idx = (y * W + x) * 4;
        let alpha;
        if (dist < 1) alpha = 175;
        else if (dist < 3.5) alpha = Math.round(175 * Math.pow(1 - (dist - 1) / 2.5, 2));
        else alpha = 0;
        imgData.data[idx]     = c.r;
        imgData.data[idx + 1] = c.g;
        imgData.data[idx + 2] = c.b;
        imgData.data[idx + 3] = alpha;
      }
    }
    ctx.putImageData(imgData, 0, 0);

    /* Blur suave para transiciones */
    const smooth = document.createElement('canvas');
    smooth.width = W;
    smooth.height = H;
    const sCtx = smooth.getContext('2d');
    sCtx.filter = 'blur(10px)';
    sCtx.drawImage(canvas, 0, 0);
    sCtx.filter = 'blur(5px)';
    sCtx.globalAlpha = 0.55;
    sCtx.drawImage(canvas, 0, 0);
    sCtx.filter = 'none';
    sCtx.globalAlpha = 0.4;
    sCtx.drawImage(canvas, 0, 0);
    sCtx.globalAlpha = 1.0;

    const overlay = L.imageOverlay(smooth.toDataURL(), bounds, { opacity: 0.82 }).addTo(map);
    return () => map.removeLayer(overlay);
  }, [points, map]);
  return null;
}

/* ─── BubbleLayer ─── */
function BubbleLayer({ stations }) {
  return (
    <>
      {stations.map((station, idx) => {
        const color = windColor(station.viento_promedio);
        return (
          <CircleMarker
            key={`${station.ICAO}-${idx}`}
            center={[station.lat, station.lon]}
            radius={Math.max(5, Math.sqrt(station.viento_promedio) * 2.2)}
            fillColor={color}
            color="rgba(255,255,255,0.8)"
            weight={1.5}
            opacity={1}
            fillOpacity={0.82}
          >
            <Tooltip direction="top" offset={[0, -8]}>
              <div style={{ fontSize: 13, lineHeight: 1.5 }}>
                <strong style={{ fontSize: 14 }}>{station.ICAO}</strong><br />
                {station.Estación}<br />
                <span style={{ color, fontWeight: 700 }}>{station.viento_promedio.toFixed(1)} km/h</span><br />
                <em style={{ color: '#888' }}>{station.Provincia}</em>
              </div>
            </Tooltip>
          </CircleMarker>
        );
      })}
    </>
  );
}

/* ─── App ─── */
function App() {
  const [data, setData] = useState([]);
  const [filter, setFilter] = useState('');
  const [activeFilter, setActiveFilter] = useState('');
  const [mapType, setMapType] = useState('bubble');

  useEffect(() => {
    fetch(process.env.PUBLIC_URL + '/data.json')
      .then((r) => r.json())
      .then((json) => setData(json))
      .catch((err) => console.error('Error cargando data.json:', err));
  }, []);

  const normalize = (str) =>
    str?.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '') ?? '';

  const filteredData = useMemo(() => {
    const term = normalize(activeFilter.trim());
    if (!term) return data;
    return data.filter(
      (s) =>
        normalize(s.ICAO).includes(term) ||
        normalize(s.Estación).includes(term) ||
        normalize(s.Provincia).includes(term)
    );
  }, [data, activeFilter]);

  const stats = useMemo(() => {
    if (!filteredData.length) return { min: '0', max: '0', avg: '0' };
    const winds = filteredData.map((d) => d.viento_promedio);
    return {
      min: Math.min(...winds).toFixed(1),
      max: Math.max(...winds).toFixed(1),
      avg: (winds.reduce((a, b) => a + b, 0) / winds.length).toFixed(1),
    };
  }, [filteredData]);

  const applyFilter = () => setActiveFilter(filter);
  const resetFilter = () => { setFilter(''); setActiveFilter(''); };

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <span className="header-icon">&#x1F4A8;</span>
        <div>
          <h1 className="header-title">Estaciones Meteorológicas ICAO</h1>
          <p className="header-sub">Viento promedio anual — Argentina</p>
        </div>
      </header>

      {/* Controls */}
      <div className="controls-panel">
        <div className="controls-row">
          <input
            className="search-input"
            type="text"
            placeholder="Buscar por ICAO, estación o provincia..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && applyFilter()}
          />
          <button className="btn btn-primary" onClick={applyFilter}>Filtrar</button>
          <button className="btn btn-secondary" onClick={resetFilter}>Limpiar</button>
        </div>

        <div className="controls-row controls-bottom">
          <div className="tabs">
            <button
              className={`tab ${mapType === 'heatmap' ? 'tab-active' : ''}`}
              onClick={() => setMapType('heatmap')}
            >
              🌡️ Heatmap
            </button>
            <button
              className={`tab ${mapType === 'bubble' ? 'tab-active' : ''}`}
              onClick={() => setMapType('bubble')}
            >
              🫧 Burbujas
            </button>
          </div>

          <div className="stat-chips">
            <span className="chip">{filteredData.length} estaciones</span>
            <span className="chip chip-blue">Min: {stats.min} km/h</span>
            <span className="chip chip-green">Prom: {stats.avg} km/h</span>
            <span className="chip chip-red">Max: {stats.max} km/h</span>
          </div>
        </div>
      </div>

      {/* Map */}
      <div className="map-wrapper">
        <MapContainer
          center={[-38, -65]}
          zoom={5}
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            attribution='&copy; CARTO'
          />
          {mapType === 'heatmap' && <HeatmapLayer points={filteredData} />}
          {mapType === 'bubble' && <BubbleLayer stations={filteredData} />}
        </MapContainer>

        {/* Legend — misma paleta para ambos mapas */}
        <div className="legend">
          <strong>Viento (km/h)</strong>
          <div className="legend-items">
            {[
              { label: '0',   color: '#4285f4' },
              { label: '8',   color: '#00bcd4' },
              { label: '13',  color: '#4caf50' },
              { label: '18',  color: '#ffc107' },
              { label: '22',  color: '#ff5722' },
              { label: '27+', color: '#d32f2f' },
            ].map((s) => (
              <div key={s.label} className="legend-item">
                <span className="legend-swatch" style={{ background: s.color }} />
                <span>{s.label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="app-footer">
        Datos: Servicio Meteorológico Nacional (SMN) — Proyecto Final TUP
      </footer>
    </div>
  );
}

export default App;