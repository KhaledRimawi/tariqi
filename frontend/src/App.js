import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './navbar';
import Home from './pages/Home';
import About from './pages/About';
import MapPage from './pages/MapPage';
import FeedbackPage from './pages/FeedbackPage'; // ✅ Import FeedbackPage
import VoiceChatBot from './pages/VoiceChatBot';

const App = () => {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/map" element={<MapPage />} />
        <Route path="/voice-chat-bot" element={<VoiceChatBot />} />
        <Route path="/feedback" element={<FeedbackPage />} /> {/* ✅ Feedback route */}
      </Routes>
    </Router>
  );
};


export default App;
