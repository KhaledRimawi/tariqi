import React, { useState } from 'react';
import { Link } from 'react-router-dom'; // Import Link
import FeedbackPopup from './FeedbackPopup';
import Location from './Location';
import './Home.css';

const Home = () => {
  const [showPopup, setShowPopup] = useState(false);

  return (
    <div className="home-container">
      <video className="background-video" src="/background.mp4" autoPlay loop muted></video>

      <div className="home-content">
        <h1>Welcome to AI Navigation Palestine</h1>
        <p>Your guide to the Holy Land</p>

        <Location />

        {/* Add a button or link to navigate to the new map page */}
        <Link to="/map" className="map-button">
          Show Checkpoints Map
        </Link>

        <button className="feedback-button" onClick={() => setShowPopup(true)}>Give Feedback</button>

        {showPopup && <FeedbackPopup onClose={() => setShowPopup(false)} />}
      </div>
    </div>
  );
};

export default Home;