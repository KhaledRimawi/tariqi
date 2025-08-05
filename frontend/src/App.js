import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import About from './pages/About';
import Map from './pages/Map';
import Navbar from './navbar'; // <-- Added this import

function App() {
  return (
    <Router>
      <Navbar /> {/* <-- Added this line to render the Navbar */}
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/map" element={<Map />} />
      </Routes>
    </Router>
  );
}

export default App;
