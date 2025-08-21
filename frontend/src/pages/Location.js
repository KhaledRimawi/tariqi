import React, { useEffect, useState } from 'react';
import getLocation from '../utils/getLocation';

const Location = () => {
  const [location, setLocation] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    getLocation()
      .then((loc) => {
        setLocation(loc);
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
