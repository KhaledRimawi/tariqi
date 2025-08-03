import React from 'react';

const Home = () => {
  return (
    <div style={{ padding: '2rem', textAlign: 'center' }}>
      <h1>Welcome to the Smart Navigation Assistant</h1>
      <p>Explore how AI helps navigate Palestine safely and efficiently.</p>

      <video width="100%" height="auto" autoPlay loop muted controls>
        <source src="/location.mp4" type="video/mp4" />
        Your browser does not support the video tag.
      </video>
    </div>
  );
};

export default Home;
