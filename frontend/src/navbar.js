import React from 'react';
import { NavLink } from 'react-router-dom';
import logo from './assets/LogoFinal.png'; // Make sure this path is correct
import './Navbar.css';

const Navbar = () => {
    return (
        <nav className="navbar">
            <div className="navbar-logo">
                <img src={logo} alt="Logo" className="logo" />
            </div>
            <ul className="nav-links">
                <li>
                    <NavLink to="/" exact activeClassName="active">Home</NavLink>
                </li>
                <li>
                    <NavLink to="/about" activeClassName="active">About</NavLink>
                </li>
                <li>
                    <NavLink to="/map" activeClassName="active">Map</NavLink>
                </li>
                <li>
                    <NavLink to="/destination-search" activeClassName="active">Destination Search</NavLink>
                </li>
            </ul>
        </nav>
    );
};

export default Navbar;
