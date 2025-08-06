import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import About from './pages/About';
import Map from './pages/Map';
import Navbar from './navbar'; // <-- Added this import
import PushNotificationSetup from './pages/PushNotificationSetup';
import CheckpointCard from './cards/CheckpointCard';


function App() {
  return (
    <Router>
      <Navbar /> {/* <-- Added this line to render the Navbar */}
      <PushNotificationSetup />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/map" element={<Map />} />
      </Routes>
      <CheckpointCard/>
    </Router>
  );
}

export default App;
