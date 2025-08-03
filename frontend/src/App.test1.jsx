/**
 * App.jsx - Step by step reconstruction
 */

import React from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

// Basic test component
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
          <p>✅ React Query imports funcionando!</p>
          <p>🔧 Próximo passo: testar QueryClient</p>
        </div>
      </div>
    </div>
  );
}

export default App;
