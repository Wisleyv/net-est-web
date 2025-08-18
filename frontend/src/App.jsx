/**
 * NET-EST Text Simplification Analysis System
 * Enhanced for strategy detection and visual analysis
 */

import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Components
import DualTextInputComponent from './components/DualTextInputComponent';
import AboutCredits from './components/AboutCredits';
import SentenceAlignmentPlaceholder from './components/SentenceAlignmentPlaceholder';
import ComparativeResultsDisplay from './components/ComparativeResultsDisplay';
import ComparativeAnalysisService from './services/comparativeAnalysisService';

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
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isAnalysing, setIsAnalysing] = useState(false);

  const handleTextProcessed = async (analysisData) => {
    // Called by DualTextInputComponent when user submits analysisData
    setIsAnalysing(true);
    try {
      // Call the ComparativeAnalysisService to run the analysis on the backend
      const result = await ComparativeAnalysisService.performComparativeAnalysis(analysisData);
      // Raw log (may show live object)
      console.log('Comparative analysis result (raw):', result);
      // Snapshot the object to avoid later mutation / inspect nested shape
      try {
        console.log('Comparative analysis result (JSON):', JSON.parse(JSON.stringify(result)));
      } catch (e) {
        console.warn('Failed to stringify comparative analysis result for snapshot:', e);
      }
      setAnalysisResult(result);
      // Switch to results view so the UI can display outcome
      setCurrentView('results');
    } catch (err) {
      console.error('Failed to perform comparative analysis', err);
      // Keep user on input view on failure (could be enhanced to show notifications)
      setCurrentView('input');
    } finally {
      setIsAnalysing(false);
    }
  };

  const handleError = (_error) => {
    // Error handling is managed by the EnhancedTextInput component
    // This could be extended to show app-level notifications if needed
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'about':
        return <AboutCredits onBack={() => setCurrentView('input')} />;
      case 'results':
        return (
          <ComparativeResultsDisplay
            analysisResult={analysisResult}
            onExport={async (format) => {
              const id = analysisResult?.id || analysisResult?.analysis_id || analysisResult?.analysisId;
              if (!id) throw new Error('Missing analysis id for export');
              return ComparativeAnalysisService.exportAnalysis(id, format);
            }}
            isExporting={isAnalysing}
          />
        );
      default:
        return (
          <>
            <DualTextInputComponent
              onComparativeAnalysis={handleTextProcessed}
              className=""
            />
            <SentenceAlignmentPlaceholder />
          </>
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
              📊 Análise de Textos
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
