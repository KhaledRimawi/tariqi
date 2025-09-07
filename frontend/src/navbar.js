import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import logo from './assets/LogoFinal.png';
import './Navbar.css';
import AuthButton from './pages/AuthButton';
import NotificationTooltip from "./pages/NotificationTooltip";

const Navbar = ({ notificationStatus }) => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleMenu = () => setIsOpen(!isOpen);

  // Close menu when clicking outside or on link
  useEffect(() => {
    const handleClickOutside = (event) => {
      const navbar = document.querySelector('.navbar');
      if (navbar && !navbar.contains(event.target)) {
        setIsOpen(false);
      }
    };

    const handleEscape = (event) => {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden'; // Prevent background scroll
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  const handleLinkClick = () => {
    setIsOpen(false);
  };

  return (
    <nav className="navbar">
      <div className="navbar-logo">
        <NavLink to="/" onClick={handleLinkClick}>
          <img src={logo} alt="Logo" className="logo" />
        </NavLink>
        {(notificationStatus === "denied" || notificationStatus === "unsupported") && (
          <NotificationTooltip status={notificationStatus} />
        )}
      </div>
      
      <ul className={`nav-links ${isOpen ? 'open' : ''}`}>
        <li>
          <NavLink 
            to="/" 
            onClick={handleLinkClick} 
            className={({ isActive }) => isActive ? "active-link" : ""}
          >
            Home
          </NavLink>
        </li>
        <li>
          <NavLink 
            to="/map" 
            onClick={handleLinkClick} 
            className={({ isActive }) => isActive ? "active-link" : ""}
          >
            Map
          </NavLink>
        </li>
        <li>
          <NavLink 
            to="/feedback" 
            onClick={handleLinkClick} 
            className={({ isActive }) => isActive ? "active-link" : ""}
          >
            Feedback
          </NavLink>
        </li>
        <li>
          <NavLink 
            to="/voice-chat-bot" 
            onClick={handleLinkClick} 
            className={({ isActive }) => isActive ? "active-link" : ""}
          >
            Chat Bot
          </NavLink>
        </li>
        <li>
          <NavLink 
            to="/about" 
            onClick={handleLinkClick} 
            className={({ isActive }) => isActive ? "active-link" : ""}
          >
            About
          </NavLink>
        </li>
        <li className="auth-mobile">
          <AuthButton />
        </li>
      </ul>

      <div className={`hamburger ${isOpen ? 'active' : ''}`} onClick={toggleMenu}>
        <span></span>
        <span></span>
        <span></span>
      </div>
    </nav>
  );
};

export default Navbar;