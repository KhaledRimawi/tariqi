import React from 'react'; 
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import About from './pages/About';
import Map from './pages/Map';
import Navbar from './navbar';

function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/map" element={<Map />} /> {/* <-- added */}
      </Routes>
    </Router>
  );
}

export default App;
