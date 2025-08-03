import React from 'react';
import './About.css';
import image from '../assets/image.jpg'; // You can replace this with a nice SVG illustration

function About() {
  return (
    <div className="about-container">
      <div className="about-content">
        <div className="about-image">
          <img src={image} alt="About Us" />
        </div>
        <div className="about-text">
          <h1>Welcome to AI Navigation Palestine</h1>
          <p>
            We are committed to revolutionizing the way people travel across Palestine by leveraging cutting-edge artificial intelligence and smart technology. Our mission is to provide safe, efficient, and context-aware navigation solutions tailored to the unique geography and cultural landscape of Palestine. Through real-time traffic analysis, offline capabilities, and community-driven insights, we empower individuals and communities to explore their surroundings with confidence and ease. Join us on this journey to smarter, more connected travel.
          </p>
        </div>
      </div>
    </div>
  );
}

export default About;
