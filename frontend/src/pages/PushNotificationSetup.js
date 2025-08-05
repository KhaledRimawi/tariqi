import { useEffect } from 'react';

export default function PushNotificationSetup() {
  useEffect(() => {
    //  Register service worker
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/service_worker.js')
        .then(reg => {
          console.log('✅ Service Worker registered:', reg.scope);
          return navigator.serviceWorker.ready;
        })
        .then(() => {
          askPermissionAndNotify();
        })
        .catch(err => {
          console.error('❌ Service Worker registration failed:', err);
        });
    }

    async function askPermissionAndNotify() {
      if (!("Notification" in window)) {
        alert("This browser does not support notifications.");
        return;
      }

      const permission = await Notification.requestPermission();
      if (permission === "granted") {
        console.log("✅ Notification permission granted.");
        await sendNotificationForClosedCheckpoints();  //  no longer triggers unused warning
      } else {
        console.log("❌ Permission denied");
        alert("Notifications are blocked.");
      }
    }

    // Function that fetches data from API and sends a notification
    async function sendNotificationWithAPIData() {
      try {
        const response = await fetch("http://127.0.0.1:5000/api/data"); // your Flask API endpoint
        const data = await response.json();

        if (data.length > 0) {
          const checkpoint = data[0]; // or pick the most recent one

          const title = "🚨 Checkpoint Alert";
          const options = {
            body: `Location: ${checkpoint.name}\nStatus: ${checkpoint.status}`,
            icon: '/icon.png' 
          };

          new Notification(title, options);
        }
      } catch (error) {
        console.error("Failed to fetch API data or send notification:", error);
      }
    }

async function sendNotificationForClosedCheckpoints() {
  try {
    const response = await fetch("http://127.0.0.1:5000/api/data");
    const data = await response.json();


    // Filter only closed checkpoints in Ramallah
    const filtered = data
      .filter(item => item.city === "رام الله" && item.status.includes("مغلق"))
      .slice(0, 5); //  only first 5 since it keep sending non stop 

    const notified = JSON.parse(localStorage.getItem("notifiedCheckpoints")) || {};

    let newNotified = { ...notified }; // To keep only recent 50 keys later

    for (const item of filtered) {
      const key = `${item.checkpoint}_${item.updatedAt}`;

      if (!notified[key]) {
        const title = "🚫 معبر مغلق - رام الله";
        const options = {
          body: `🔘 المعبر: ${item.checkpoint}\n📍 الحالة: ${item.status}\n🔄 الاتجاه: ${item.direction}\n🕒 ${new Date(item.updatedAt).toLocaleString("ar-EG")}`,
          icon: '/icon.png'
        };
        new Notification(title, options);

        newNotified[key] = true;
      }
    }

    // ✅ Limit to 50 entries to prevent overflow
    const keys = Object.keys(newNotified).slice(-50);
    const trimmed = {};
    for (const k of keys) trimmed[k] = true;

    localStorage.setItem("notifiedCheckpoints", JSON.stringify(trimmed));
  } catch (error) {
    console.error("❌ Failed to fetch or send notifications:", error);
  }
}


  }, []);

  return null;
}


