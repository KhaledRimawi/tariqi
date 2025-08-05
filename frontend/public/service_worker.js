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
  self.registration.showNotification(title, {
    body,
    icon: '/logo192.png', // use your app icon here
  });
});
