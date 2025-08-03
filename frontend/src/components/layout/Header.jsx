/**
 * Header da aplicação
 */

import React from 'react';
import AboutCredits from '../AboutCredits';

const Header = () => {
  return (
    <header className='bg-white shadow-sm border-b'>
      <div className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'>
        <div className='flex justify-between items-center py-4'>
          <div className='flex items-center'>
            <h1 className='text-2xl font-bold text-gray-900'>NET-EST</h1>
            <span className='ml-2 text-sm text-gray-500'>v1.0</span>
          </div>

          <div className='flex items-center space-x-4'>
            <span className='text-sm text-gray-600'>
              Núcleo de Estudos de Tradução - UFRJ
            </span>
            <AboutCredits />
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
