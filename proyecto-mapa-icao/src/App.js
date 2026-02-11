import React, { useState, useEffect, useMemo } from 'react';
import { MapContainer, TileLayer, CircleMarker, Tooltip, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet.heat';
import './App.css';

/* ─── Color por velocidad de viento ─── */
function windColor(speed) {
  const stops = [
    { v: 0, r: 66, g: 133, b: 244 },
    { v: 8, r: 0, g: 188, b: 212 },
    { v: 13, r: 76, g: 175, b: 80 },
    { v: 18, r: 255, g: 193, b: 7 },
    { v: 22, r: 255, g: 87, b: 34 },
    { v: 28, r: 211, g: 47, b: 47 },
  ];
  if (speed <= stops[0].v) return `rgb(${stops[0].r},${stops[0].g},${stops[0].b})`;
  if (speed >= stops[stops.length - 1].v) {
    const s = stops[stops.length - 1];
    return `rgb(${s.r},${s.g},${s.b})`;
  }
  for (let i = 0; i < stops.length - 1; i++) {
    if (speed >= stops[i].v && speed <= stops[i + 1].v) {
      const t = (speed - stops[i].v) / (stops[i + 1].v - stops[i].v);
      const r = Math.round(stops[i].r + t * (stops[i + 1].r - stops[i].r));
      const g = Math.round(stops[i].g + t * (stops[i + 1].g - stops[i].g));
      const b = Math.round(stops[i].b + t * (stops[i + 1].b - stops[i].b));
      return `rgb(${r},${g},${b})`;
    }
  }
  return '#1e88e5';
}

/* ─── HeatmapLayer ─── */
function HeatmapLayer({ points }) {
  const map = useMap();
  useEffect(() => {
    if (!points?.length || !map) return;
    const maxWind = Math.max(...points.map((p) => p.viento_promedio));
    const heatPoints = points.map((p) => [p.lat, p.lon, p.viento_promedio / maxWind]);
    const heatLayer = L.heatLayer(heatPoints, {
      radius: 35, blur: 25, maxZoom: 12, minOpacity: 0.35,
      gradient: { 0.0: '#313695', 0.2: '#4575b4', 0.35: '#74add1', 0.5: '#abd9e9', 0.6: '#fee090', 0.7: '#fdae61', 0.85: '#f46d43', 1.0: '#a50026' },
    }).addTo(map);
    return () => map.removeLayer(heatLayer);
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

  const filteredData = useMemo(() => {
    const term = activeFilter.trim().toLowerCase();
    if (!term) return data;
    return data.filter(
      (s) =>
        s.ICAO?.toLowerCase().includes(term) ||
        s.Estación?.toLowerCase().includes(term) ||
        s.Provincia?.toLowerCase().includes(term)
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

        {/* Legend */}
        <div className="legend">
          <strong>Viento (km/h)</strong>
          <div className="legend-items">
            {[
              { label: '0', color: '#313695' },
              { label: '8', color: '#4575b4' },
              { label: '13', color: '#fee090' },
              { label: '18', color: '#fdae61' },
              { label: '22', color: '#f46d43' },
              { label: '27+', color: '#a50026' },
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