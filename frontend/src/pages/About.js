import React from 'react';
// import Navbar from '../Navbar'; // Removed: Navbar is rendered in App.js
import './About.css';
import logo from '../assets/LogoFinal.png'; // Import your logo image

const About = () => {
    return (
        <>
            {/* Removed: Navbar is rendered in App.js */}
            <div className="about-container">
                <div className="about-card animated-card">
                    {/* The src now uses your imported logo file */}
                    <img src={logo} alt="SmartNav Palestine Logo" className="about-image" />
                    <div className="about-content">
                        <p>
                            Tariqi is an AI-powered app that shows live checkpoint status in Palestine, with a map of all checkpoints, user feedback, and a chatbot to answer your questions instantly.
                        </p>
                    </div>
                </div>
            </div>
        </>
    );
};

export default About;
