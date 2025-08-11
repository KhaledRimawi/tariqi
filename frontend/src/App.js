import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './navbar';
import Home from './pages/Home';
import About from './pages/About';
import MapPage from './pages/MapPage';
import DestinationSearch from './pages/DestinationSearch';

const App = () => {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/map" element={<MapPage />} />
        <Route path="/destination-search" element={<DestinationSearch />} />
      </Routes>
    </Router>
  );
};

export default App;