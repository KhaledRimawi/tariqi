import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import logo from './assets/LogoFinal.png';
import './Navbar.css';
import AuthButton from './pages/AuthButton';
import NotificationTooltip from "./pages/NotificationTooltip";

const Navbar = ({ notificationStatus }) => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleMenu = () => setIsOpen(!isOpen);

  return (
    <nav className="navbar">
      <div className="navbar-logo">
        <img src={logo} alt="Logo" className="logo" />
          {(notificationStatus === "denied" || notificationStatus === "unsupported") && (
            <NotificationTooltip status={notificationStatus} />
          )}
        </div>
      <div className={`nav-links ${isOpen ? 'open' : ''}`}>
        <li>
          <NavLink to="/" onClick={() => setIsOpen(false)} className={({ isActive }) => isActive ? "active-link" : ""}>
            Home
          </NavLink>
        </li>
        <li>
          <NavLink to="/about" onClick={() => setIsOpen(false)} className={({ isActive }) => isActive ? "active-link" : ""}>
            About
          </NavLink>
        </li>
        <li>
          <NavLink to="/map" onClick={() => setIsOpen(false)} className={({ isActive }) => isActive ? "active-link" : ""}>
            Map
          </NavLink>
        </li>
        <li>
          <NavLink to="/feedback" onClick={() => setIsOpen(false)} className={({ isActive }) => isActive ? "active-link" : ""}>
            Feedback
          </NavLink>
        </li>
        <li>
          <NavLink to="/voice-chat-bot" onClick={() => setIsOpen(false)} className={({ isActive }) => isActive ? "active-link" : ""}>
            Chat Bot
          </NavLink>
        </li>

        <li className="auth-mobile">
          <AuthButton />
        </li>
      </div>

      <div className="hamburger" onClick={toggleMenu}>
        <span></span>
        <span></span>
        <span></span>
      </div>
    </nav>
  );
};

export default Navbar;
