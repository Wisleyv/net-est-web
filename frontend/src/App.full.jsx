/**
 * Aplicação principal NET-EST
 * Integração com Zustand + React Query para gerenciamento de estado
 */

import React, { useEffect } from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { AlertTriangle, CheckCircle, RefreshCw } from 'lucide-react';

// Components
import Header from './components/layout/Header';
import Footer from './components/layout/Footer';
import Loading from './components/common/Loading';
import ErrorMessage from './components/common/ErrorMessage';
import TextInput from './components/TextInput';
import ProcessedTextDisplay from './components/ProcessedTextDisplay';
import SemanticAlignment from './components/SemanticAlignment';

// Hooks and Services
import { queryClient } from './hooks/queryClient';
import { useHealthCheck } from './hooks/useHealthQueries';

// Stores
import useAppStore from './stores/useAppStore';
import useSessionStore from './stores/useSessionStore';
import useAnalysisStore from './stores/useAnalysisStore';

// Styles
import './App.css';

// Main App Component
function AppContent() {
  // Global State
  const {
    currentPhase,
    loading,
    globalError,
    systemHealthy,
    systemStatus,
    navigateToPhase,
    clearGlobalError,
    resetApp,
  } = useAppStore();

  // Session State
  const { startSession, sessionActive } = useSessionStore();

  // Analysis State
  const { resetCurrentAnalysis } = useAnalysisStore();

  // Health Check Query
  const { isLoading: healthLoading, error: healthError } = useHealthCheck({
    refetchInterval: 60000, // Check every minute
  });

  // Initialize session on mount
  useEffect(() => {
    if (!sessionActive) {
      startSession();
    }
  }, [sessionActive, startSession]);

  // Navigation Handlers
  const handleTextProcessed = (data) => {
    if (import.meta.env.DEV) {
      // eslint-disable-next-line no-console
      console.log('Text processed:', data);
    }
    navigateToPhase('processed');
  };

  const handleContinueToAlignment = (data) => {
    if (import.meta.env.DEV) {
      // eslint-disable-next-line no-console
      console.log('Continue to alignment with:', data);
    }
    navigateToPhase('alignment');
  };

  const handleError = (errorMessage) => {
    if (import.meta.env.DEV) {
      // eslint-disable-next-line no-console
      console.error('App error:', errorMessage);
    }
    // Error is handled by global state in hooks
  };

  const handleReturnToInput = () => {
    resetCurrentAnalysis();
    navigateToPhase('input');
    clearGlobalError();
  };

  const handleResetApp = () => {
    resetCurrentAnalysis();
    resetApp();
  };

  // System Status Indicator
  const SystemStatus = () => (
    <div className='mb-6 bg-white rounded-lg shadow-sm border p-4'>
      <div className='flex items-center justify-between'>
        <div className='flex items-center space-x-3'>
          {healthLoading ? (
            <RefreshCw className='w-5 h-5 text-blue-500 animate-spin' />
          ) : systemHealthy ? (
            <CheckCircle className='w-5 h-5 text-green-500' />
          ) : (
            <AlertTriangle className='w-5 h-5 text-red-500' />
          )}
          <div>
            <span className='font-medium text-gray-900'>
              Status do Sistema: {systemHealthy ? 'Operacional' : 'Verificando...'}
            </span>
            {systemStatus && (
              <p className='text-sm text-gray-500'>
                Última verificação: {new Date(systemStatus.timestamp).toLocaleTimeString('pt-BR')}
              </p>
            )}
          </div>
        </div>
        {healthError && (
          <span className='text-sm text-red-600'>
            Falha na verificação
          </span>
        )}
      </div>
    </div>
  );

  // Phase Progress Indicator
  const PhaseProgress = () => (
    <div className='mb-6 bg-white rounded-lg shadow-sm border p-4'>
      <div className='flex items-center justify-between'>
        <div className='flex items-center space-x-4'>
          <div
            className={`flex items-center ${currentPhase === 'input' ? 'text-blue-600' : currentPhase === 'processed' || currentPhase === 'alignment' ? 'text-green-600' : 'text-gray-400'}`}
          >
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${currentPhase === 'input' ? 'bg-blue-100' : currentPhase === 'processed' || currentPhase === 'alignment' ? 'bg-green-100' : 'bg-gray-100'}`}
            >
              {currentPhase === 'input' ? '1' : '✓'}
            </div>
            <span className='ml-2 font-medium'>Entrada de Texto</span>
          </div>

          <div className='w-8 border-t border-gray-300'></div>

          <div
            className={`flex items-center ${currentPhase === 'processed' ? 'text-blue-600' : currentPhase === 'alignment' ? 'text-green-600' : 'text-gray-400'}`}
          >
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${currentPhase === 'processed' ? 'bg-blue-100' : currentPhase === 'alignment' ? 'bg-green-100' : 'bg-gray-100'}`}
            >
              {currentPhase === 'processed' ? '2' : currentPhase === 'alignment' ? '✓' : '2'}
            </div>
            <span className='ml-2 font-medium'>Alinhamento Semântico</span>
          </div>
        </div>

        {(currentPhase === 'processed' || currentPhase === 'alignment') && (
          <button
            onClick={handleResetApp}
            className='text-sm text-blue-600 hover:text-blue-800 font-medium'
          >
            Reiniciar Análise
          </button>
        )}
      </div>
    </div>
  );

  return (
    <div className='min-h-screen bg-gray-50 flex flex-col'>
      <Header />

      <main className='flex-1 max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8 w-full'>
        <div className='mb-8'>
          <h2 className='text-3xl font-bold text-gray-900 mb-2'>
            Sistema de Análise de Tradução Intralinguística
          </h2>
          <p className='text-lg text-gray-600'>
            Ferramenta de análise linguística computacional para identificação e
            classificação de estratégias de simplificação textual.
          </p>
        </div>

        <SystemStatus />
        <PhaseProgress />

        {/* Global Error Display */}
        {globalError && (
          <div className='mb-6'>
            <ErrorMessage 
              error={globalError} 
              onDismiss={clearGlobalError}
            />
          </div>
        )}

        {/* Loading Overlay */}
        {loading && (
          <div className='mb-6'>
            <Loading message="Processando..." />
          </div>
        )}

        {/* Phase Content */}
        <div className='space-y-6'>
          {currentPhase === 'input' && (
            <TextInput
              onTextProcessed={handleTextProcessed}
              onError={handleError}
            />
          )}

          {currentPhase === 'processed' && (
            <ProcessedTextDisplay
              onContinueToAlignment={handleContinueToAlignment}
              onReturnToInput={handleReturnToInput}
              onError={handleError}
            />
          )}

          {currentPhase === 'alignment' && (
            <SemanticAlignment
              onReturnToInput={handleReturnToInput}
              onError={handleError}
            />
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}

// App with Providers
function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
      {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
    </QueryClientProvider>
  );
}

export default App;
