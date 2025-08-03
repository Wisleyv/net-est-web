/**
 * Componente de loading padronizado
 */

import React from 'react';

const Loading = ({ message = 'Carregando...', size = 'medium' }) => {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12',
  };

  return (
    <div className='flex flex-col items-center justify-center p-4'>
      <div
        className={`animate-spin rounded-full border-b-2 border-blue-600 ${sizeClasses[size]}`}
      ></div>
      <p className='mt-2 text-sm text-gray-600'>{message}</p>
    </div>
  );
};

export default Loading;
