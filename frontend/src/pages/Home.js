import React from 'react';
import { useState } from 'react';
import FeedbackPopup from './FeedbackPopup';
import Location from './Location'; 

const Home = () => {
  const [showPopup, setShowPopup] = useState(false);

  return (
    <div style={{ padding: '2rem', textAlign: 'center' }}>
      <h1>Welcome to the Smart Navigation Assistant</h1>
      <p>Explore how AI helps navigate Palestine safely and efficiently.</p>

      {/* Show location info */}
      <Location />

      {/* Feedback button */}
      <button onClick={() => setShowPopup(true)}>Give Feedback</button>

      {/* Feedback popup */}
      {showPopup && <FeedbackPopup onClose={() => setShowPopup(false)} />}

      <video width="100%" height="auto" autoPlay loop muted controls>
        <source src="/location.mp4" type="video/mp4" />
        Your browser does not support the video tag.
      </video>
    </div>
  );
};

export default Home;
