

// src/components/Navbar.js

import React from 'react';
import { Link } from 'react-router-dom';
import ThemeToggle from './ThemeToggle';

const Navbar = () => {
  return (
    <nav className="bg-blue-600 text-white p-4 flex justify-between items-center">
      <div className="text-xl font-bold">
        <Link to="/">FlairLabs Real Estate</Link>
      </div>
      <div className="flex items-center space-x-4">
        {/* <Link to="/">Home</Link>
        <Link to="/broker-details">Broker Details</Link> */}
        <ThemeToggle />
      </div>
    </nav>
  );
};

export default Navbar;

