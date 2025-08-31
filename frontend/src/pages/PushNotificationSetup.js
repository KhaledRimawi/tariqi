import { useEffect  } from 'react';
import getLocation from '../utils/getLocation';

export default function PushNotificationSetup({ setNotificationStatus })  {
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
        setNotificationStatus("unsupported");
        return;
      }

      const permission = await Notification.requestPermission();
      if (permission === "granted") {
        console.log("✅ Notification permission granted.");
        setNotificationStatus("granted");
        await notifyNearbyCheckpoints();   
      } else {
        console.log("❌ Permission denied");
        setNotificationStatus("denied");
      } 
    }

async function notifyNearbyCheckpoints() {
  try {
    const position = await getLocation();
    const userLat = position.latitude;
    const userLng = position.longitude;

    console.log("📍 Sending user location to backend:", userLat, userLng);

    const res = await fetch(
      `${process.env.REACT_APP_BACKEND_URL}/api/near_location?latitude=${userLat}&longitude=${userLng}`
    );

    const data = await res.json();
    console.log("✅ Nearby checkpoints received:", data);

    const reg = await navigator.serviceWorker.getRegistration();
    if (!reg) return;

    if (data.count > 0) {
      for (const cp of data.checkpoints) {
        const title = "🚧 نقطة تفتيش قريبة منك";
        const options = {
          body: `🔘 المعبر: ${cp.checkpoint}\n📍 المدينة: ${cp.city}\n📡 الحالة: ${cp.status || "غير معروف"}\n🧭 الاتجاه: ${cp.direction || "غير معروف"}\n📏 البعد: ${cp.distance_km} كم\n🕒 ${new Date(cp.updatedAt).toLocaleString("ar-EG")}`,
          requireInteraction: true
        };
        reg.showNotification(title, options);
      }
    } else {
      reg.showNotification("🚫 لا توجد نقاط تفتيش قريبة", {
        body: "📍 لم يتم العثور على نقاط تفتيش ضمن موقعك الحالي.",
        requireInteraction: true
      });
    }
  } catch (err) {
    console.error("❌ Error in notifyNearbyCheckpoints:", err);
  }
}


  }, []);
  return null;
}