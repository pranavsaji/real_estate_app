// src/components/Footer.js

import React from 'react';

const Footer = () => {
  return (
    <footer className="bg-blue-600 text-white p-4 text-center">
      © {new Date().getFullYear()} FlairLabs Real Estate. All rights reserved.
    </footer>
  );
};

export default Footer;

