import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './Map.css';
import * as topojson from 'topojson-client';
import palestineTopoJson from '../assets/palestine.topo.json';
import { formatCheckpointTime } from "../utils/timeFormat";
 
// Fix for default marker icons not showing up in Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});
 
const Map = () => {
  const mapRef = useRef(null);
  const checkpointMarkersRef = useRef([]);
  const userMarkerRef = useRef(null);
  const [checkpoints, setCheckpoints] = useState([]);
  const REFRESH_MS = Number(process.env.REACT_APP_MAP_REFRESH_MS) || 30000;
  const AGO_MINUTES = Number(process.env.REACT_APP_MAP_AGO_MINUTES) || 90;
  const userPopupTimerRef = useRef(null);

  const getStatusColor = (status) => {
    switch (status) {
      case 'مغلق': case 'مسكر': case 'مكهرب': case 'اغلاق': case 'إغلاق': return 'red';
      case 'مفتوح': case 'سالك': case 'بحري': case 'فتح': case 'فاتح': return 'green';
      case 'ازمة': case 'أزمة': case 'مزدحم': case 'ازدحام': case 'إزدحام': return 'orange';
      case 'حاجز/تفتيش': case 'تفتيش': case 'حاجز': return 'yellow';
      default: return 'gray';
    }
  };
const buildSplitMarkerSVG = ({entryColor, exitColor, label, size = 24}) => {
  const r = size / 2;      
  const innerR = r - 2;    
  const same = entryColor === exitColor;
 
  if (same) {
    return `
<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" xmlns="http://www.w3.org/2000/svg">
  <circle cx="${r}" cy="${r}" r="${innerR}" fill="${entryColor}" />
  <circle cx="${r}" cy="${r}" r="${innerR}" fill="none" stroke="#FFF" stroke-width="2"/>
  <text x="${r}" y="${r + 4}" font-family="Arial" font-size="10" fill="#FFF" text-anchor="middle">${label}</text>
</svg>`;
  }
 
  return `
<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <clipPath id="cp">
      <circle cx="${r}" cy="${r}" r="${innerR}"/>
    </clipPath>
  </defs>
  <g clip-path="url(#cp)">
    <rect x="0" y="0" width="${r}" height="${size}" fill="${entryColor}"/>
    <rect x="${r}" y="0" width="${r}" height="${size}" fill="${exitColor}"/>
  </g>
  <circle cx="${r}" cy="${r}" r="${innerR}" fill="none" stroke="#FFF" stroke-width="2"/>
  <text x="${r}" y="${r + 4}" font-family="Arial" font-size="10" fill="#FFF" text-anchor="middle">${label}</text>
</svg>`;
};
 
 
const ensureRoomForTooltip = (map, latlng, estW = 260, estH = 180, margin = 16) => {
  const p = map.latLngToContainerPoint(latlng);
  const size = map.getSize();
 
  let dx = 0;
  let dy = 0;
 
  const needTop = estH + margin - p.y;              
  const needBottom = estH + margin - (size.y - p.y);  
 
  if (needTop > 0 && needBottom <= 0) {
    dy += needTop;          
  } else if (needBottom > 0 && needTop <= 0) {
    dy -= needBottom;        
  }
 
  const needLeft = estW / 2 + margin - p.x;
  const needRight = estW / 2 + margin - (size.x - p.x);
 
  if (needLeft > 0 && needRight <= 0) {
    dx += needLeft;          
  } else if (needRight > 0 && needLeft <= 0) {
    dx -= needRight;          
  }
 
  if (dx !== 0 || dy !== 0) {
    map.panBy([dx, dy], { animate: true, duration: 0.2 });
  }
};
 
  const formatTime = (isoString) => {
    if (!isoString) return 'N/A';
    try {
      return new Date(isoString).toLocaleString(undefined, {
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit', second: '2-digit',
        hour12: false
      });
    } catch {
      return isoString;
    }
  };
 
  useEffect(() => {
    let timerId;
 
    const load = async () => {
      try {
        const base = process.env.REACT_APP_BACKEND_URL;
        const response = await fetch(`${base}/api/checkpoints/query?top=5000&with_location=true`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        const list = Array.isArray(data?.results) ? data.results : [];
        const filtered = list.filter(p => Number.isFinite(p.lat) && Number.isFinite(p.lng));
 
        // Merge new data with old data
        setCheckpoints(prev => {
          const merged = { ...Object.fromEntries(prev.map(cp => [cp._id || cp.checkpoint_name, cp])) };
 
          filtered.forEach(cp => {
            const key = cp._id || cp.checkpoint_name;
            const old = merged[key];
 
            if (!old || new Date(cp?.message_date?.$date || 0) > new Date(old?.message_date?.$date || 0)) {
              merged[key] = cp; // Update if the data is newer
            }
          });
 
          return Object.values(merged);
        });
 
      } catch (error) {
        console.error("Could not fetch checkpoints:", error);
 
      }
    };
 
    load();
    timerId = setInterval(load, REFRESH_MS);
    return () => clearInterval(timerId);
  }, []);
 
 
  useEffect(() => {
    if (mapRef.current) return;
    const map = L.map('map', { zoomControl: false }).setView([31.9, 35.2], 8);
 
    L.control.zoom({ position: 'topleft' }).addTo(map);
 
const legend = L.control({ position: 'topleft' });
legend.onAdd = function () {
  const div = L.DomUtil.create('div', 'legend-control');
 
div.innerHTML = `
  <button class="legend-btn" aria-label="Legend" title="Legend">?</button>
  <div class="legend-tooltip tidy" dir="rtl">
    <ul class="legend-list">
      <li><span class="dot" style="background:#28a745"></span><span>مفتوح </span></li>
      <li><span class="dot" style="background:#dc3545"></span><span>مغلق </span></li>
      <li><span class="dot" style="background:#fd7e14"></span><span>ازدحام</span></li>
      <li><span class="dot" style="background:#ffc107"></span><span>تفتيش /حاجز </span></li>
      <li><span class="dot" style="background:#6c757d"></span><span>غير معروف</span></li>
      <li>
        <span class="split-circle">
          <span class="half left" style="background:#28a745"></span>
          <span class="half right" style="background:#dc3545"></span>
        </span>
        <span> دخول/خروج مختلفتان في الحالة</span>
      </li>
    </ul>
  </div>
`;

  L.DomEvent.disableClickPropagation(div);
  L.DomEvent.disableScrollPropagation(div);
 
  return div;
};
    legend.addTo(map);
    mapRef.current = map;
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OpenStreetMap contributors' }).addTo(map);
 
    const bounds = L.latLngBounds([31.2, 34.8], [32.5, 35.6]);
    const palestineGeoJSON = topojson.feature(palestineTopoJson, palestineTopoJson.objects.collection);
    L.geoJSON(palestineGeoJSON, { style: { color: "#FF0000", weight: 3, opacity: 1, fillOpacity: 0 } }).addTo(map);
 
    map.setMaxBounds(bounds);
    map.setMinZoom(8);
    map.on('drag', function () { if (mapRef.current) { mapRef.current.panInsideBounds(bounds, { animate: false }); } });
    return () => { if (mapRef.current) { mapRef.current.remove(); mapRef.current = null; } };
  }, []);
 
  // Card Display (Enter/Exit)
  useEffect(() => {
    if (!mapRef.current) return;
 
    checkpointMarkersRef.current.forEach(marker => mapRef.current.removeLayer(marker));
    checkpointMarkersRef.current = [];
 
    if (checkpoints.length === 0) return;
 
    const grouped = {};
    checkpoints.forEach(cp => {
      const key = cp.checkpoint_name || "—";
      const dir = cp.direction || "";
      const rawTime = cp?.message_date?.$date || null;
 
      const { absolute, relative } = formatCheckpointTime(rawTime);
      const statusBlock = {
        status: cp.status || "—",
        time: relative || "—",
        rawTime: rawTime,
        lat: cp.lat,
        lng: cp.lng
      };
 
      if (!grouped[key]) grouped[key] = { checkpoint_name: key, entry: null, exit: null, lat: cp.lat, lng: cp.lng };
 
      if (["الداخل", "دخول", "الدخول", "داخل"].includes(dir)) {
        if (!grouped[key].entry || new Date(rawTime) > new Date(grouped[key].entry.rawTime)) grouped[key].entry = statusBlock;
      } else if (["الخارج", "خروج", "الخروج", "خارج"].includes(dir)) {
        if (!grouped[key].exit || new Date(rawTime) > new Date(grouped[key].exit.rawTime)) grouped[key].exit = statusBlock;
      } else if (dir === "الاتجاهين") {
        grouped[key].entry = statusBlock;
        grouped[key].exit = statusBlock;
      } else {
        if (!grouped[key].entry) grouped[key].entry = statusBlock;
        else if (!grouped[key].exit) grouped[key].exit = statusBlock;
      }
    });
 
    Object.values(grouped).forEach(cp => {
      let entryColor = getStatusColor(cp.entry?.status || "");
      let exitColor  = getStatusColor(cp.exit?.status  || "");
 
      if (entryColor === "gray" && exitColor !== "gray") entryColor = exitColor;
      if (exitColor === "gray" && entryColor !== "gray") exitColor = entryColor;
      if (entryColor === "gray" && exitColor === "gray") {
        entryColor = exitColor = "gray";
      }
 
      const checkpointSvgIcon = buildSplitMarkerSVG({
        entryColor,
        exitColor,
        label: (cp.checkpoint_name || " ").charAt(0),
        size: 24
      });
 
      const checkpointIcon = L.divIcon({
        className: '',
        html: checkpointSvgIcon,
        iconSize: [24, 24],
        iconAnchor: [12, 12],
        popupAnchor: [0, -12]
      });
 
      const marker = L.marker([cp.lat, cp.lng], { icon: checkpointIcon }).addTo(mapRef.current);
 
      const hoverCard = `
        <div class="checkpoint-hover-card" dir="rtl">
          <div class="cp-title"><b>${cp.checkpoint_name}</b></div>
 
          <div class="cp-block cp-entry">
            <div><b>الدخول</b></div>
            <div><b>الحالة:</b> ${cp.entry?.status || "—"}</div>
            <div><b>الوقت:</b> ${cp.entry?.time || "—"}</div>
          </div>
 
          <div class="cp-block cp-exit">
            <div><b>الخروج</b></div>
            <div><b>الحالة:</b> ${cp.exit?.status || "—"}</div>
            <div><b>الوقت:</b> ${cp.exit?.time || "—"}</div>
          </div>
        </div>
      `;
 
const tt = marker.bindTooltip(hoverCard, {
  className: 'checkpoint-tooltip-card',
  direction: 'auto',   
  offset: [0, -14],     
  sticky: true,
  opacity: 1,
  permanent: false
}).getTooltip();

marker.on('tooltipopen', (e) => {
  const map = mapRef.current;
  if (!map) return;

  const p = map.latLngToContainerPoint(e.target.getLatLng());
  const sz = map.getSize();
  const t  = e.target.getTooltip();
  const edge = 120;       
  if (p.y < edge)            { t.options.direction = 'bottom'; t.options.offset = [0, 14];  }
  else if (p.y > sz.y-edge)  { t.options.direction = 'top';    t.options.offset = [0, -14]; }
  else if (p.x < edge)       { t.options.direction = 'right';  t.options.offset = [14, 0];  }
  else if (p.x > sz.x-edge)  { t.options.direction = 'left';   t.options.offset = [-14, 0]; }
  t.update();
});
 
 
      checkpointMarkersRef.current.push(marker);
    });
 
  }, [checkpoints]);
 
  useEffect(() => {
    if (!mapRef.current) return;
 
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition((position) => {
        const { latitude, longitude } = position.coords;
        const userLatLng = [latitude, longitude];
 
        const userSvgIcon = `
          <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path fill="#FF0000" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5S10.62 6.5 12 6.5s2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
            <circle cx="12" cy="9" r="2" fill="#fff"/>
          </svg>`;
 
        const userIcon = L.divIcon({
          className: 'user-marker-icon',
          html: userSvgIcon,
          iconSize: [24, 24],
          iconAnchor: [12, 24],
          popupAnchor: [0, -24]
        });
 
        if (userMarkerRef.current) {
          userMarkerRef.current.setLatLng(userLatLng);
        } else {
          userMarkerRef.current = L.marker(userLatLng, { icon: userIcon }).addTo(mapRef.current)
            .bindPopup("Your Current Location").openPopup();
            if (userPopupTimerRef.current) clearTimeout(userPopupTimerRef.current);
            userPopupTimerRef.current = setTimeout(() => {
              if (userMarkerRef.current) userMarkerRef.current.closePopup();
            }, 2000);
        }
 
        mapRef.current.setView(userLatLng, 12);
      }, (error) => {
        console.error("Error getting user location:", error);
      });
    } else {
      console.log("Geolocation is not supported by your browser.");
    }
  }, [mapRef.current]);
 
  return (<div id="map"></div>);
};
 
export default Map;
 
 