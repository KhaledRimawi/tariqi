import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import FeedbackPopup from './FeedbackPopup';
import Location from './Location';
import './Home.css';

const Home = () => {
  const [showPopup, setShowPopup] = useState(false);

  // Function to show test notification
  const showTestNotification = () => {
    if (Notification.permission === 'granted') {
      new Notification('🚧 Checkpoint Passed!', {
        body: 'You just passed a checkpoint. Click to give feedback.',
        icon: '/icon.png', // Optional: add your own icon path here
      });
    } else {
      Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
          showTestNotification();
        }
      });
    }
  };

  return (
    <div className="home-container">
      {/* This is the background video for your new design. */}
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

        {/* New test notification button */}
        <button 
          className="feedback-button" 
          style={{ marginTop: '1em', backgroundColor: '#28a745' }} 
          onClick={showTestNotification}
        >
          Show Test Notification
        </button>

        {showPopup && <FeedbackPopup onClose={() => setShowPopup(false)} />}
      </div>
    </div>
  );
};

export default Home;
