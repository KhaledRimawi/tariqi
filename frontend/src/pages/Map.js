import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './Map.css';
import * as topojson from 'topojson-client';
import palestineTopoJson from '../assets/palestine.topo.json';

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

  const getStatusColor = (status) => {
    switch (status) {
      case 'مغلق': case 'مسكر': case 'مكهرب': return 'red';
      case 'مفتوح': case 'سالك': case 'بحري': return 'green';
      case 'ازمة': case 'مزدحم': return 'orange';
      default: return 'gray';
    }
  };

  useEffect(() => {
    const fetchCheckpoints = async () => {
      try {
        const response = await fetch('http://127.0.0.1:5000/api/checkpoints/merged');

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const mergedCheckpoints = await response.json();
        
        setCheckpoints(mergedCheckpoints);
      } catch (error) {
        console.error("Could not fetch checkpoints:", error);
      }
    };
    fetchCheckpoints();
  }, []);

  useEffect(() => {
    if (mapRef.current) return;
    const map = L.map('map').setView([31.9, 35.2], 8);
    mapRef.current = map;
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OpenStreetMap contributors' }).addTo(map);

    const bounds = L.latLngBounds([31.2, 34.8], [32.5, 35.6]);
    const palestineGeoJSON = topojson.feature(palestineTopoJson, palestineTopoJson.objects.collection);
    L.geoJSON(palestineGeoJSON, { style: { color: "#FF0000", weight: 3, opacity: 1, fillOpacity: 0 }}).addTo(map);

    map.setMaxBounds(bounds);
    map.setMinZoom(8);
    map.on('drag', function() { if (mapRef.current) { mapRef.current.panInsideBounds(bounds, { animate: false }); }});
    return () => { if (mapRef.current) { mapRef.current.remove(); mapRef.current = null; }};
  }, []);

  useEffect(() => {
    if (!mapRef.current || checkpoints.length === 0) return;
    checkpointMarkersRef.current.forEach(marker => mapRef.current.removeLayer(marker));
    checkpointMarkersRef.current = [];
    checkpoints.forEach(checkpoint => {
      if (checkpoint.lat && checkpoint.lng) {
        const checkpointColor = getStatusColor(checkpoint.status);
        const checkpointSvgIcon = `<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="10" fill="${checkpointColor}" stroke="#FFF" stroke-width="2"/><text x="12" y="16" font-family="Arial" font-size="10" fill="#FFF" text-anchor="middle">${checkpoint.checkpoint_name ? checkpoint.checkpoint_name.charAt(0) : '?'}</text></svg>`;
        const checkpointIcon = L.divIcon({ className: '', html: checkpointSvgIcon, iconSize: [24, 24], iconAnchor: [12, 12], popupAnchor: [0, -12] });
        const marker = L.marker([checkpoint.lat, checkpoint.lng], { icon: checkpointIcon })
          .addTo(mapRef.current)
          .bindPopup(`<b>${checkpoint.checkpoint_name || 'N/A'}</b><br>Status: ${checkpoint.status || 'N/A'}<br>Direction: ${checkpoint.direction || 'N/A'}`);
        checkpointMarkersRef.current.push(marker);
      }
    });
  }, [checkpoints, mapRef.current]);

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