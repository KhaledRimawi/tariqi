import React, { useEffect, useState } from "react";
import FeedbackPopup from "./FeedbackPopup";

const FeedbackNotification  = () => {
  const [showFeedback, setShowFeedback] = useState(false);
  const [previousDistance, setPreviousDistance] = useState(null);
  const [wasClose, setWasClose] = useState(false);

  useEffect(() => {
    // Request notification permission
    if (Notification.permission !== "granted") {
      Notification.requestPermission();
    }

    const watchId = navigator.geolocation.watchPosition(
      async (pos) => {
        const { latitude, longitude } = pos.coords;

        // 1. Get closest checkpoint from backend
        const res = await fetch(
          `http://localhost:5000/api/closest-checkpoint?lat=${latitude}&lon=${longitude}`
        );

        if (!res.ok) {
          console.error("Failed to get closest checkpoint");
          return;
        }

        const checkpoint = await res.json();

        // 2. Calculate distance (in meters)
        const distance = checkpoint.distance_m;

        // 3. Check if within 100m to mark "close"
        if (distance <= 100) {
          setWasClose(true);
        } else if (
          wasClose &&
          previousDistance !== null &&
          distance > previousDistance
        ) {
          // User was close, now distance is increasing → show popup
          setWasClose(false);

          if (Notification.permission === "granted") {
            const notif = new Notification("You passed a checkpoint", {
              body: `You just passed ${checkpoint.checkpoint} in ${checkpoint.city}. Click to give feedback!`,
            });
            notif.onclick = () => {
              window.focus();
              setShowFeedback(true);
            };
          }
        }

        setPreviousDistance(distance);
      },
      (err) => console.error(err),
      { enableHighAccuracy: true }
    );

    return () => navigator.geolocation.clearWatch(watchId);
  }, [wasClose, previousDistance]);

  return (
    <>
      {showFeedback && <FeedbackPopup onClose={() => setShowFeedback(false)} />}
    </>
  );
};

export default FeedbackNotification ;
