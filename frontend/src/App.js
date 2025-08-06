import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import About from './pages/About';
import Map from './pages/Map';
<<<<<<< HEAD
import Navbar from './navbar';
import CheckpointCard from './cards/CheckpointCard';
=======
import Navbar from './navbar'; // <-- Added this import
import PushNotificationSetup from './pages/PushNotificationSetup';

>>>>>>> 478f82dfa51db472ef847ff1505bb74f20d20350

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
