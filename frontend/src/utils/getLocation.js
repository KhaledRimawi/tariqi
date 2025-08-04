const getLocation = () => {
  return new Promise((resolve, reject) => {
    if (!('geolocation' in navigator)) {
      reject(new Error('Geolocation is not supported by this browser.'));
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const loc = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        };
        resolve(loc);
      },
      (error) => {
        reject(new Error('Error retrieving location: ' + error.message));
      }
    );
  });
};

export default getLocation;
