import React from 'react';
import Location from './Location';
import PushNotificationSetup from './PushNotificationSetup';
import './Home.css';


const Home = () => {
  return (
    <div className="home-container">
      <video className="background-video" src="/background.mp4" autoPlay loop muted></video>
      <div className="home-overlay"></div>

      <div className="home-content">
        <h1>Welcome to AI Navigation Palestine</h1>
        <p>Your guide to the Holy Land</p>

        <Location />
      </div>
      {/* Notification setup */}
      <PushNotificationSetup />
    </div>
  );
};

export default Home;
