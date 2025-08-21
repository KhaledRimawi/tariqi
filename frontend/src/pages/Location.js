import React, { useEffect, useState } from 'react';
import getLocation from '../utils/getLocation';

const Location = () => {
  const [location, setLocation] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    getLocation()
      .then((loc) => {
        setLocation(loc);

        // Send to backend
        fetch(`${process.env.REACT_APP_BACKEND_URL}/api/location`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(loc),
        })
          .then((res) => res.json())
          .then((data) => {
            console.log('Location sent to backend:', data);
          })
          .catch((err) => {
            console.error('Error sending location:', err);
          });
      })
      .catch((err) => {
        setError(err.message);
      });
  }, []);
  if (error) return <p style={{ color: 'red' }}>{error}</p>;

  return (
    <div>
      {location ? (
        <p>
          Your location: Latitude {location.latitude}, Longitude {location.longitude}
        </p>
      ) : (
        <p>Getting your location...</p>
      )}
    </div>
  );
};

export default Location;
