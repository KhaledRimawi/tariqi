import React, { useState } from 'react';
import FeedbackPopup from './FeedbackPopup';
import Location from './Location';
import './Home.css';
// The Navbar is imported and rendered in App.js, so it's not needed here.
// import Navbar from '../navbar';

const Home = () => {
  const [showPopup, setShowPopup] = useState(false);

  return (
    // The component must return a single parent element.
    <div className="home-container">

      {/* IMPORTANT: The Navbar is rendered ONCE in App.js at the very top of your application.
          Do NOT render it again here, otherwise it will be duplicated and mispositioned
          due to the centering styles of .home-container. */}

      {/* This is the background video for your new design. */}
      <video className="background-video" src="/background.mp4" autoPlay loop muted></video>

      {/* This container holds the content that sits on top of the video */}
      <div className="home-content">
        <h1>Welcome to AI Navigation Palestine</h1>
        <p>Your guide to the Holy Land</p>

        {/* The location and feedback components are placed inside the content div */}
        <Location />

        {/* Feedback button */}
        <button className="feedback-button" onClick={() => setShowPopup(true)}>Give Feedback</button>

        {/* Feedback popup */}
        {showPopup && <FeedbackPopup onClose={() => setShowPopup(false)} />}
      </div>
    </div>
  );
};

export default Home;
