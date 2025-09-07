import React , { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { DarkModeProvider } from './contexts/DarkModeContext';
import Navbar from './navbar';
import Home from './pages/Home';
import About from './pages/About';
import MapPage from './pages/MapPage';
import FeedbackPage from './pages/FeedbackPage'; // ✅ Import FeedbackPage
import VoiceChatBot from './pages/VoiceChatBot';

const App = () => {
  const [notificationStatus, setNotificationStatus] = useState(null);

  return (
    <DarkModeProvider>
      <Router>
        <Navbar notificationStatus={notificationStatus} />
        <Routes>
          <Route
            path="/"
            element={<Home setNotificationStatus={setNotificationStatus} />}
          />
          <Route path="/about" element={<About />} />
          <Route path="/map" element={<MapPage />} />
          <Route path="/voice-chat-bot" element={<VoiceChatBot />} />
          <Route path="/feedback" element={<FeedbackPage />} /> {/* ✅ Feedback route */}
        </Routes>
      </Router>
    </DarkModeProvider>
  );
};


export default App;
