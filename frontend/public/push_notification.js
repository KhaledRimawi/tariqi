
// Immediately register the service worker
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('./service_worker.js')
    .then(registration => {
      console.log("✅ Service Worker registered:", registration.scope);
      // Wait until it's active before continuing
      return navigator.serviceWorker.ready;
    })
    .then(() => {
      requestNotificationPermission(); // Ask immediately on load
    })
    .catch(error => {
      console.error("❌ Service Worker registration failed:", error);
    });
} else {
  alert("Service Workers are not supported in this browser.");
}

//  Ask for notification permission and act accordingly
async function requestNotificationPermission() {
  if (!("Notification" in window)) {
    alert("This browser does not support notifications.");
    return;
  }

  const permission = await Notification.requestPermission();

  if (permission === "granted") {
    console.log("✅ Notification permission granted.");
    simulateBarrierAlert(); // Use mock location
  } else {
    console.log("❌ Notification permission denied.");
    alert("Notifications are blocked. You won’t receive alerts.");
  }
}

/// Hard coded (mock data example)

//  Simulate nearby barrier detection
async function simulateBarrierAlert() {
  const mockLocation = { lat: 31.7683, lng: 35.2137 };
  const alertData = checkNearbyBarriers(mockLocation);

  if (alertData && Notification.permission === "granted") {
    const registration = await navigator.serviceWorker.ready;
    if (registration.active) {
      registration.active.postMessage(alertData);
    } else {
      console.error("⚠️ Service worker not active.");
    }
  }
}

// Fake location logic
function checkNearbyBarriers(location) {
  if (location.lat === 31.7683) {
    return {
      title: "🚧 Barrier Nearby",
      body: "A roadblock is 200m away from your current location!"
    };
  }
  return null;
}

