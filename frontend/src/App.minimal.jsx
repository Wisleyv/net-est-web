/**
 * Minimal App.jsx for testing
 */

import React from 'react';

function App() {
  return (
    <div className='min-h-screen bg-gray-50 flex flex-col'>
      <div className='flex-1 max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8 w-full'>
        <div className='mb-8'>
          <h2 className='text-3xl font-bold text-gray-900 mb-2'>
            Sistema de Análise de Tradução Intralinguística
          </h2>
          <p className='text-lg text-gray-600'>
            Ferramenta de análise linguística computacional para identificação e
            classificação de estratégias de simplificação textual.
          </p>
        </div>
        
        <div className='bg-white rounded-lg shadow-sm border p-4'>
          <p>✅ Frontend carregado com sucesso!</p>
          <p>🔧 State Management: Zustand + React Query instalados</p>
          <p>📊 Status: Testando componentes básicos</p>
        </div>
      </div>
    </div>
  );
}

export default App;
