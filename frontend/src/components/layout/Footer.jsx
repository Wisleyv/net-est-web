/**
 * Footer da aplicação
 */

import React from 'react';

const Footer = () => {
  return (
    <footer className='bg-gray-50 border-t mt-auto'>
      <div className='max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8'>
        <div className='flex justify-between items-center text-sm text-gray-600'>
          <div>
            <p>© 2025 NET-EST - Núcleo de Estudos de Tradução UFRJ</p>
          </div>
          <div className='flex space-x-4'>
            <span>MIT License</span>
            <span>•</span>
            <span>Politécnico de Leiria (PT)</span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
