import React from 'react';
import Location from './Location';
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
    </div>
  );
};

export default Home;
