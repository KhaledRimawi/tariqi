// src/navbar.js
import React from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav style={{
      padding: '1rem',
      backgroundColor: '#045d75',
      color: '#fff',
      display: 'flex',
      gap: '1rem'
    }}>
      <Link to="/" style={{ color: '#fff', textDecoration: 'none' }}>Home</Link>
      <Link to="/about" style={{ color: '#fff', textDecoration: 'none' }}>About</Link>
      <Link to="/map" style={{ color: '#fff', textDecoration: 'none' }}>Map</Link> {/* <-- New link */}
    </nav>
  );
};

export default Navbar;
