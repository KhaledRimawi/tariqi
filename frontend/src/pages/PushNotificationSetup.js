import { useEffect } from 'react';
import getLocation from '../utils/getLocation';

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
        await notifyNearbyCheckpoints(); 
        await sendNotificationForClosedCheckpoints();
        
      } else {
        console.log("❌ Permission denied");
        alert("Notifications are blocked.");
      }
    }

async function sendNotificationForClosedCheckpoints() {
  try {
    const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/data/show`);
    const data = await response.json();

    // Show first 3 items just to make sure notifications work
    const sampleData = data.slice(0, 3); // Remove this line later

    for (const item of sampleData) {
      const title = `🚧 تنبيه حول حاجز ${item.checkpoint_name}`;
      const options = {
        body: `🔘 المعبر: ${item.checkpoint_name}
📍 المدينة: ${item.city_name}
📊 الحالة: ${item.status}
🔄 الاتجاه: ${item.direction || "غير معروف"}
🕒 ${new Date(item.message_date).toLocaleString("ar-EG")}`,
        icon: '/icon.png',
      };

      // Use Service Worker to show the notification
      const reg = await navigator.serviceWorker.getRegistration();
      if (reg) {
        reg.showNotification(title, options);
      }
    }
  } catch (error) {
    console.error("❌ Failed to fetch or send notifications:", error);
  }
}


async function notifyNearbyCheckpoints() {
  try {
    const position = await getLocation();
    const userLat = position.latitude;
    const userLng = position.longitude;
    

    console.log("📍 Sending user location to backend:", userLat, userLng);

    const res = await fetch("http://127.0.0.1:5000/api/near_location", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        latitude: userLat,
        longitude: userLng
      })
    });

    const nearbyCheckpoints = await res.json();
    console.log("✅ Nearby checkpoints received:", nearbyCheckpoints);

    const reg = await navigator.serviceWorker.getRegistration();
    if (!reg) {
      console.warn("⚠️ No service worker registration found");
      return;
    }

    if (nearbyCheckpoints.length > 0) {
      for (const cp of nearbyCheckpoints) {
        const title = "🚧 نقطة تفتيش قريبة منك";
        const options = {
          body: `🔘 المعبر: ${cp.checkpoint}\n📍 المدينة: ${cp.city}\n📡 الحالة: ${cp.status || "غير معروف"}\n🧭 الاتجاه: ${cp.direction || "غير معروف"}\n📏 البعد: ${cp.distance_km} كم\n🕒 ${new Date(cp.updatedAt).toLocaleString("ar-EG")}`,
          requireInteraction: true

        };

        console.log("📣 Triggering notification:", title, options);
        reg.showNotification(title, options);
      }
    } else {
      console.log("ℹ️ No nearby checkpoints found. Sending fallback notification.");

      reg.showNotification("🚫 لا توجد نقاط تفتيش قريبة", {
        body: "📍 لم يتم العثور على نقاط تفتيش ضمن موقعك الحالي.",
        requireInteraction: true,
      });
    }
  } catch (err) {
    console.error("❌ Error in notifyNearbyCheckpoints:", err);
  }
}


  }, []);

  return null;
}


