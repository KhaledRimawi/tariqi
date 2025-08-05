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
                        <h1>About Our Project</h1>
                        <p>
                            Our project is dedicated to providing an **AI-powered navigation solution for Palestine**. By leveraging cutting-edge technology, we are creating a tool that is not only functional and user-friendly but also helps you explore the rich history and culture of the region with a modern and intuitive interface.
                        </p>
                        <p>
                            We believe in the power of technology to connect people with their heritage and to make travel more accessible and meaningful.
                        </p>
                    </div>
                </div>
            </div>
        </>
    );
};

export default About;
