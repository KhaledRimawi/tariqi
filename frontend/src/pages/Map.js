import React, { useEffect } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

const Map = () => {
  useEffect(() => {
    const mapContainer = document.getElementById('map');
    if (mapContainer._leaflet_id) {
      return; // Prevent reinitialization
    }

    // Initialize Map Centered on West Bank
    const map = L.map('map').setView([31.8, 35.3], 10);

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
      map.panInsideBounds(bounds, { animate: false });
    });

    // Optional: Show User Location Marker
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lat = position.coords.latitude;
          const lon = position.coords.longitude;

          map.setView([lat, lon], 13);
          L.marker([lat, lon])
            .addTo(map)
            .bindPopup('You are here!')
            .openPopup();
        },
        () => {
          alert('Could not get your location');
        }
      );
    }

    // Handle Click to Add Circle
    let lastCircle = null;
    map.on('click', (e) => {
      const { lat, lng } = e.latlng;

      // Remove previous circle if exists
      if (lastCircle) {
        map.removeLayer(lastCircle);
      }

      // Add new circle at clicked position
      lastCircle = L.circle([lat, lng], {
        color: 'red',
        fillColor: '#f03',
        fillOpacity: 0.4,
        radius: 500 // Radius in meters
      }).addTo(map);

      // Popup showing coordinates
      lastCircle.bindPopup(`Selected Area:<br>Lat: ${lat.toFixed(5)}, Lng: ${lng.toFixed(5)}`).openPopup();
    });

  }, []);

  return (
    <div id="map" style={{
      height: 'calc(100vh - 64px)',  // Adjust based on Navbar height
      width: '100%'
    }}></div>
  );
};

export default Map;
