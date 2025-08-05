import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './Map.css';
// import Navbar from '../Navbar'; // Removed: Navbar is rendered in App.js

// Fix for default marker icons not showing up in Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

const Map = () => {
  const mapRef = useRef(null); // Create a ref to store the map instance

  useEffect(() => {
    // Check if the map element exists and has a leaflet instance already
    const mapContainer = document.getElementById('map');
    if (mapContainer && mapContainer._leaflet_id) {
      return; // Prevent reinitialization
    }

    // Initialize Map Centered on West Bank
    const map = L.map('map').setView([31.8, 35.3], 10);
    mapRef.current = map; // Store the map instance in the ref

    // Add OpenStreetMap Tile Layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Define West Bank Bounding Box (SW & NE Corners)
    const bounds = L.latLngBounds(
      [31.2, 34.8],  // Southwest corner (lat, lon)
      [32.5, 35.6]   // Northeast corner (lat, lon)
    );

    // Restrict Panning to Bounds
    map.setMaxBounds(bounds);

    // Prevent zooming out too much
    map.setMinZoom(10);

    // Snap back inside bounds when dragging outside
    map.on('drag', function() {
      if (mapRef.current) {
        mapRef.current.panInsideBounds(bounds, { animate: false });
      }
    });

    // Create a beautiful, animated location icon using a base64 encoded SVG
    const svgIcon = `
      <svg width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
        <style>
          @keyframes pulse {
            0% { transform: scale(0.9); opacity: 1; }
            50% { transform: scale(1.1); opacity: 0.7; }
            100% { transform: scale(0.9); opacity: 1; }
          }
          .pin-drop {
            animation: pulse 1.5s infinite ease-in-out;
            transform-origin: center;
          }
        </style>
        <circle class="pin-drop" cx="20" cy="20" r="10" fill="#E74C3C" stroke="#C0392B" stroke-width="2"/>
        <path d="M20 30 C15 30, 10 25, 10 20 C10 15, 20 5, 20 5 C20 5, 30 15, 30 20 C30 25, 25 30, 20 30Z" fill="#E74C3C" stroke="#C0392B" stroke-width="2"/>
        <circle cx="20" cy="18" r="4" fill="#FFFFFF"/>
      </svg>`;
    const locationIcon = L.divIcon({
      className: '',
      html: svgIcon,
      iconSize: [40, 40],
      iconAnchor: [20, 40],
      popupAnchor: [0, -40]
    });

    // Optional: Show User Location Marker
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          // Check if the map still exists before performing operations
          if (mapRef.current) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;

            mapRef.current.setView([lat, lon], 13);
            L.marker([lat, lon], { icon: locationIcon })
              .addTo(mapRef.current)
              .bindPopup('You are here!')
              .openPopup();
          }
        },
        () => {
          console.error('Could not get your location');
        }
      );
    }

    // Handle Click to Add Circle
    let lastCircle = null;
    map.on('click', (e) => {
      if (mapRef.current) {
        const { lat, lng } = e.latlng;

        // Remove previous circle if exists
        if (lastCircle) {
          mapRef.current.removeLayer(lastCircle);
        }

        // Add new circle at clicked position
        lastCircle = L.circle([lat, lng], {
          color: 'red',
          fillColor: '#f03',
          fillOpacity: 0.4,
          radius: 500 // Radius in meters
        }).addTo(mapRef.current);

        // Popup showing coordinates
        lastCircle.bindPopup(`Selected Area:<br>Lat: ${lat.toFixed(5)}, Lng: ${lng.toFixed(5)}`).openPopup();
      }
    });

    // Return a cleanup function to remove the map on unmount
    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null; // Clear the ref
      }
    };

  }, []);

  return (
    <>
      {/* Removed: Navbar is rendered in App.js */}
      <div id="map"></div>
    </>
  );
};

export default Map;
