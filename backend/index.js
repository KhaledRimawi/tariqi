const express = require('express');
const app = express();
const PORT = 5000;

// Middleware to parse JSON bodies
app.use(express.json());

// Define routes
app.get('/', (req, res) => {
  res.send('Welcome to the backend Home Page');
});

app.get('/about', (req, res) => {
  res.send('About the backend');
});

//  Add location receiving route
app.post('/api/location', (req, res) => {
  const { latitude, longitude } = req.body;
  console.log(`Received location: Lat ${latitude}, Long ${longitude}`);
  res.json({ message: 'Location received successfully', received: { latitude, longitude } });
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

app.post('/api/feedback', (req, res) => {
  const { message } = req.body;
  console.log('Feedback received:', message);
  res.json({ status: 'success', message: 'Thank you for your feedback!' });
});

