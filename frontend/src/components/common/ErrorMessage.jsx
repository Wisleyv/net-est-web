/**
 * Componente de erro padronizado
 */

import React from 'react';

const ErrorMessage = ({ error, onRetry }) => {
  const getErrorMessage = error => {
    if (error.response?.data?.detail) {
      return error.response.data.detail;
    }
    if (error.message) {
      return error.message;
    }
    return 'Ocorreu um erro inesperado';
  };

  return (
    <div className='bg-red-50 border border-red-200 rounded-lg p-4'>
      <div className='flex'>
        <div className='flex-shrink-0'>
          <span className='text-red-400'>❌</span>
        </div>
        <div className='ml-3'>
          <h3 className='text-sm font-medium text-red-800'>Erro no Sistema</h3>
          <div className='mt-2 text-sm text-red-700'>
            <p>{getErrorMessage(error)}</p>
          </div>
          {onRetry && (
            <div className='mt-4'>
              <button
                onClick={onRetry}
                className='bg-red-100 text-red-800 px-3 py-1 rounded text-sm hover:bg-red-200'
              >
                Tentar Novamente
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ErrorMessage;
