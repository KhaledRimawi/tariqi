self.addEventListener('message', event => {
  const data = event.data;
  self.registration.showNotification(data.title, {
    body: data.body,
    icon: "https://cdn-icons-png.flaticon.com/512/595/595067.png"
  });
});

