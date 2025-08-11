// src/navbar.js
import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import logo from './assets/LogoFinal.png'; // Make sure this path is correct
import './Navbar.css';
import FeedbackPopup from './pages/FeedbackPopup';
import ChatUI from './pages/ChatUI';

const Navbar = () => {
  const [showPopup, setShowPopup] = useState(false);
  const [showChatbot, setShowChatbot] = useState(false);

  return (
    <>
      <nav className="navbar" style={{ backgroundColor: '#045d75', color: '#fff', padding: '1rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <div className="navbar-logo">
          <img src={logo} alt="Logo" className="logo" style={{ height: 40 }} />
        </div>
        <ul className="nav-links" style={{ display: 'flex', listStyle: 'none', gap: '1rem', margin: 0, padding: 0 }}>
          <li>
            <NavLink to="/" exact="true" activeclassname="active" style={{ color: '#fff', textDecoration: 'none' }}>Home</NavLink>
          </li>
          <li>
            <NavLink to="/about" activeclassname="active" style={{ color: '#fff', textDecoration: 'none' }}>About</NavLink>
          </li>
          <li>
            <NavLink to="/map" activeclassname="active" style={{ color: '#fff', textDecoration: 'none' }}>Map</NavLink>
          </li>
          <li>
            <NavLink to="/destination-search" activeclassname="active" style={{ color: '#fff', textDecoration: 'none' }}>Destination Search</NavLink>
          </li>
          <li>
            <a
              href="#"
              onClick={e => { e.preventDefault(); setShowChatbot(!showChatbot); }}
              style={{ color: '#fff', textDecoration: 'none' }}
            >
              Chatbot
            </a>
          </li>
          <li>
            <a
              href="#"
              onClick={e => { e.preventDefault(); setShowPopup(true); }}
              style={{ color: '#fff', textDecoration: 'none' }}
            >
              Feedback
            </a>
          </li>
        </ul>
      </nav>

      {/* Feedback popup */}
      {showPopup && <FeedbackPopup onClose={() => setShowPopup(false)} />}

      {/* Chatbot popup */}
      {showChatbot && (
        <div
          style={{
            position: 'fixed',
            bottom: 20,
            right: 20,
            width: 350,
            height: 500,
            backgroundColor: '#fff',
            boxShadow: '0 0 10px rgba(0,0,0,0.3)',
            borderRadius: 10,
            zIndex: 1000,
            overflow: 'hidden',
          }}
        >
          <div style={{ backgroundColor: '#045d75', color: '#fff', padding: '10px', fontWeight: 'bold' }}>
            Chatbot
            <button
              onClick={() => setShowChatbot(false)}
              style={{
                float: 'right',
                background: 'none',
                border: 'none',
                color: '#fff',
                fontSize: '16px',
                cursor: 'pointer',
              }}
            >
              ×
            </button>
          </div>
          <div style={{ padding: '10px', height: 'calc(100% - 40px)', overflowY: 'auto' }}>
            <ChatUI />
          </div>
        </div>
      )}
    </>
  );
};

export default Navbar;
