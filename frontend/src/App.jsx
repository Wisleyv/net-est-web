/**
 * NET-EST Text Simplification Analysis System
 * Enhanced for strategy detection and visual analysis
 */

import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Components
import EnhancedTextInput from './components/EnhancedTextInput';
import AboutCredits from './components/AboutCredits';

// React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      staleTime: 5 * 60 * 1000,
      cacheTime: 10 * 60 * 1000,
    },
  },
});

// Error Boundary Component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(_error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
          <h1 style={{ color: 'red' }}>🚨 Erro na Aplicação</h1>
          <details style={{ whiteSpace: 'pre-wrap' }}>
            <summary>Detalhes do Erro</summary>
            {this.state.error && this.state.error.toString()}
            <br />
            {this.state.errorInfo.componentStack}
          </details>
          <button 
            onClick={() => window.location.reload()}
            style={{ 
              padding: '10px 20px', 
              backgroundColor: '#dc3545', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Recarregar Página
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// Main Application Component
function MainApp() {
  const [currentView, setCurrentView] = useState('input');

  const handleTextProcessed = (_result) => {
    // Analysis completed successfully
    // The EnhancedTextInput component handles the display
  };

  const handleError = (_error) => {
    // Error handling is managed by the EnhancedTextInput component
    // This could be extended to show app-level notifications if needed
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'about':
        return <AboutCredits onBack={() => setCurrentView('input')} />;
      default:
        return (
          <EnhancedTextInput
            onTextProcessed={handleTextProcessed}
            onError={handleError}
          />
        );
    }
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      {/* Header */}
      <div style={{ 
        backgroundColor: 'rgba(255, 255, 255, 0.95)', 
        backdropFilter: 'blur(10px)',
        padding: '1rem 2rem',
        boxShadow: '0 2px 20px rgba(0, 0, 0, 0.1)',
        borderBottom: '1px solid rgba(0, 0, 0, 0.1)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ 
              margin: 0, 
              color: '#2d3748',
              fontSize: '1.5rem',
              fontWeight: '600'
            }}>
              🌐 NET-EST - Análise de Estratégias de Simplificação Textual
            </h1>
            <p style={{ 
              margin: '0.25rem 0 0 0', 
              color: '#4a5568',
              fontSize: '0.875rem'
            }}>
              Sistema de análise comparativa para tradução intralingual
            </p>
          </div>
          
          {/* Navigation Buttons */}
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button
              onClick={() => setCurrentView('input')}
              style={{
                padding: '0.625rem 1.25rem',
                backgroundColor: currentView === 'input' || currentView === 'results' ? '#3182ce' : '#e2e8f0',
                color: currentView === 'input' || currentView === 'results' ? 'white' : '#4a5568',
                border: 'none',
                borderRadius: '0.5rem',
                cursor: 'pointer',
                fontSize: '0.875rem',
                fontWeight: '500',
                transition: 'all 0.2s ease'
              }}
            >
              � Análise de Textos
            </button>
            <button
              onClick={() => setCurrentView('about')}
              style={{
                padding: '0.625rem 1.25rem',
                backgroundColor: currentView === 'about' ? '#3182ce' : '#e2e8f0',
                color: currentView === 'about' ? 'white' : '#4a5568',
                border: 'none',
                borderRadius: '0.5rem',
                cursor: 'pointer',
                fontSize: '0.875rem',
                fontWeight: '500',
                transition: 'all 0.2s ease'
              }}
            >
              ℹ️ Sobre
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div style={{ padding: '2rem' }}>
        <div style={{ 
          backgroundColor: 'white', 
          borderRadius: '12px', 
          padding: '2rem',
          boxShadow: '0 4px 25px rgba(0, 0, 0, 0.1)'
        }}>
          {renderCurrentView()}
        </div>
      </div>
    </div>
  );
}

// Main App Wrapper with Providers
function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <MainApp />
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;

/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
*/
