// public/service_worker.js

self.addEventListener('install', (event) => {
  console.log('✅ Service Worker installed');
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  console.log('✅ Service Worker activated');
  return self.clients.claim();
});

self.addEventListener('message', (event) => {
  const { title, body } = event.data;

  if (!title || !body) {
    console.warn("⚠️ Missing title or body in SW message");
    return;
  }

  console.log("📩 SW received message:", title);

  self.registration.showNotification(title, {
    body,
    icon: "LogoFinal.png", // Make sure this file exists in /public
  });
});