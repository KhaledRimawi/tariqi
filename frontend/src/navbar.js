import React from 'react';
import { NavLink } from 'react-router-dom';
import logo from './assets/LogoFinal.png';
import './Navbar.css';

const Navbar = () => {
  return (
    <nav className="navbar">
      <div className="navbar-logo">
        <img src={logo} alt="Logo" className="logo" />
      </div>
      <ul className="nav-links">
        <li>
          <NavLink to="/" className={({ isActive }) => isActive ? "active-link" : ""}>
            Home
          </NavLink>
        </li>
        <li>
          <NavLink to="/about" className={({ isActive }) => isActive ? "active-link" : ""}>
            About
          </NavLink>
        </li>
        <li>
          <NavLink to="/map" className={({ isActive }) => isActive ? "active-link" : ""}>
            Map
          </NavLink>
        </li>
        <li>
          <NavLink to="/destination-search" className={({ isActive }) => isActive ? "active-link" : ""}>
            Destination Search
          </NavLink>
        </li>
        <li>
          <NavLink to="/feedback" className={({ isActive }) => isActive ? "active-link" : ""}>
            Feedback
          </NavLink>
        </li>
        <li>
          <NavLink to="/voice-chat-bot" className={({ isActive }) => isActive ? "active-link" : ""}>
            Chat Bot
          </NavLink>
        </li>
      </ul>
    </nav>
  );
};

export default Navbar;
