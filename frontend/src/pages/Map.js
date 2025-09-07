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

  const getStatusColor = (status) => {
    switch (status) {
      case 'مغلق': case 'مسكر': case 'مكهرب': case 'اغلاق': case 'إغلاق': return 'red';
      case 'مفتوح': case 'سالك': case 'بحري': case 'فتح': case 'فاتح': return 'green';
      case 'ازمة': case 'أزمة': case 'مزدحم': case 'ازدحام': case 'إزدحام': return 'orange';
      case 'حاجز/تفتيش': case 'تفتيش': case 'حاجز': return 'yellow';
      default: return 'gray';
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
      const checkpointColor = getStatusColor(cp.entry?.status || cp.exit?.status);

      const checkpointSvgIcon = `
        <svg width="24" height="24" xmlns="http://www.w3.org/2000/svg">
          <circle cx="12" cy="12" r="10" fill="${checkpointColor}" stroke="#FFF" stroke-width="2"/>
          <text x="12" y="16" font-family="Arial" font-size="10" fill="#FFF" text-anchor="middle">
            ${cp.checkpoint_name.charAt(0)}
          </text>
        </svg>`;

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

      marker.bindTooltip(hoverCard, {
        className: 'checkpoint-tooltip-card',
        direction: 'top',
        offset: [0, -14],
        sticky: true,
        opacity: 1,
        permanent: false
      });

      checkpointMarkersRef.current.push(marker);
    });
  }, [checkpoints]);

  // Updated effect for adding the user's location with a red professional icon
  useEffect(() => {
    if (!mapRef.current) return;

    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition((position) => {
        const { latitude, longitude } = position.coords;
        const userLatLng = [latitude, longitude];

        // Create a custom SVG icon for the user's location with a red fill
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
