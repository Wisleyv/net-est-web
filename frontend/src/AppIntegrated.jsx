/**
 * Enhanced Main App Component - Phase 2.B.3 Implementation
 * Integrates all components with centralized error handling and state management
 */

import React, { useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { Toaster } from 'react-hot-toast';

// Enhanced components with React Query integration
import TextInputFieldIntegrated from './components/TextInputFieldIntegrated';
import SemanticAlignmentIntegrated from './components/SemanticAlignmentIntegrated';
import ProcessedTextDisplayIntegrated from './components/ProcessedTextDisplayIntegrated';

// Common components
import ErrorBoundary from './components/common/ErrorBoundary';
import NotificationCenter from './components/common/NotificationCenter';

// Stores and hooks
import useAnalysisStore from './stores/useAnalysisStore';
import useAppStore from './stores/useAppStore';
import useErrorHandler from './hooks/useErrorHandler';

// Services
import { healthAPI } from './services/api';

// Styles
import './App.css';

// React Query client configuration
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,
    },
    mutations: {
      retry: 1,
    },
  },
});

const AppContent = () => {
  // Global state
  const { 
    currentAnalysis, 
    alignmentResult, 
    isProcessing,
    initializeAnalysis,
    resetAnalysis
  } = useAnalysisStore();
  
  const { 
    notifications, 
    isOnline,
    setOnlineStatus
  } = useAppStore();

  // Error handling
  const { handleError, handleSuccess } = useErrorHandler();

  // Initialize app and check health
  useEffect(() => {
    const initializeApp = async () => {
      try {
        // Check backend health
        await healthAPI.check();
        handleSuccess('Conectado ao servidor com sucesso!');
        
        // Initialize analysis session
        initializeAnalysis();
        
      } catch (error) {
        handleError(error, {
          component: 'App',
          operation: 'inicializar aplicação',
          showNotification: true
        });
      }
    };

    initializeApp();
  }, [initializeAnalysis, handleError, handleSuccess]);

  // Monitor online status
  useEffect(() => {
    const handleOnline = () => setOnlineStatus(true);
    const handleOffline = () => setOnlineStatus(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [setOnlineStatus]);

  // Handle text processing completion
  const handleTextProcessingComplete = (result) => {
    console.log('Text processing completed:', result);
    // Additional processing logic can be added here
  };

  // Handle alignment completion
  const handleAlignmentComplete = (result) => {
    console.log('Alignment completed:', result);
    // Additional alignment logic can be added here
  };

  // Handle text editing from ProcessedTextDisplay
  const handleTextEdit = (editedText) => {
    // You could implement text editing logic here
    // For example, create a new analysis with the edited text
    console.log('Text edited:', editedText);
  };

  // Clear all analysis data
  const handleResetAnalysis = () => {
    resetAnalysis();
    handleSuccess('Análise resetada com sucesso!');
  };

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">NET</span>
                </div>
                <div>
                  <h1 className="text-xl font-semibold text-gray-900">
                    NET - Núcleo de Estudos Textuais
                  </h1>
                  <p className="text-sm text-gray-600">
                    Sistema de Simplificação Textual e Alinhamento Semântico
                  </p>
                </div>
              </div>
              
              <div className="flex items-center gap-3">
                {/* Online Status Indicator */}
                <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs ${
                  isOnline 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  <div className={`w-2 h-2 rounded-full ${
                    isOnline ? 'bg-green-500' : 'bg-red-500'
                  }`} />
                  {isOnline ? 'Online' : 'Offline'}
                </div>

                {/* Reset Button */}
                {(currentAnalysis || alignmentResult) && (
                  <button
                    onClick={handleResetAnalysis}
                    disabled={isProcessing}
                    className="px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Nova Análise
                  </button>
                )}
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="space-y-8">
            
            {/* Phase 2.B.3 Notice */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-white text-xs font-bold">✓</span>
                </div>
                <div>
                  <h3 className="font-medium text-blue-900">Fase 2.B.3 - Implementação Concluída</h3>
                  <p className="text-sm text-blue-800 mt-1">
                    Sistema integrado com tratamento centralizado de erros, React Query para gerenciamento de estado assíncrono, 
                    e componentes modulares independentes. Todos os componentes agora utilizam hooks centralizados e 
                    notificações unificadas.
                  </p>
                </div>
              </div>
            </div>

            {/* Input Section */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                1. Entrada de Dados
              </h2>
              <TextInputFieldIntegrated
                label="Digite ou carregue seu texto"
                placeholder="Cole seu texto aqui ou carregue um arquivo para processamento..."
                onProcessingComplete={handleTextProcessingComplete}
                className="w-full"
              />
            </div>

            {/* Semantic Alignment Section */}
            {currentAnalysis && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  2. Alinhamento Semântico
                </h2>
                <SemanticAlignmentIntegrated
                  inputText={currentAnalysis.originalText}
                  onAlignmentComplete={handleAlignmentComplete}
                  className="w-full"
                />
              </div>
            )}

            {/* Results Section */}
            {(currentAnalysis || alignmentResult) && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  3. Resultados
                </h2>
                <ProcessedTextDisplayIntegrated
                  showComparison={!!alignmentResult}
                  showStatistics={true}
                  allowEdit={true}
                  onTextEdit={handleTextEdit}
                  className="w-full"
                />
              </div>
            )}

            {/* Empty State */}
            {!currentAnalysis && !alignmentResult && !isProcessing && (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">📝</span>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Bem-vindo ao NET
                </h3>
                <p className="text-gray-600 max-w-md mx-auto">
                  Comece digitando ou carregando um texto para realizar a simplificação textual 
                  e alinhamento semântico automatizado.
                </p>
              </div>
            )}
          </div>
        </main>

        {/* Footer */}
        <footer className="mt-16 bg-white border-t border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="flex flex-col md:flex-row justify-between items-center gap-4">
              <div className="text-sm text-gray-600">
                © 2025 NET - Núcleo de Estudos Textuais. Desenvolvido para pesquisa acadêmica.
              </div>
              <div className="flex items-center gap-4 text-sm text-gray-500">
                <span>Versão: 2.B.3</span>
                <span>•</span>
                <span>Fase: Integração Frontend-Backend</span>
                <span>•</span>
                <span className="flex items-center gap-1">
                  {isProcessing && (
                    <>
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
                      Processando...
                    </>
                  )}
                </span>
              </div>
            </div>
          </div>
        </footer>

        {/* Notification Center */}
        <NotificationCenter />

        {/* React Query DevTools (only in development) */}
        {import.meta.env.DEV && (
          <ReactQueryDevtools initialIsOpen={false} />
        )}
      </div>
    </ErrorBoundary>
  );
};

const App = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          className: 'text-sm',
        }}
      />
    </QueryClientProvider>
  );
};

export default App;
