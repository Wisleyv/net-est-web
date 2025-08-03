/**
 * Enhanced App.jsx - Phase 2.B.5 Dual Input Architecture - Fully Restored & Working
 */

import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Components
import DualTextInputComponent from './components/DualTextInputComponent';
import ComparativeResultsDisplay from './components/ComparativeResultsDisplay';

// Services
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
  const [analysisHistory, setAnalysisHistory] = useState([]);

  // Real API integration function
  const handleComparativeAnalysis = async (analysisData) => {
    // Call the backend service
    const result = await ComparativeAnalysisService.performComparativeAnalysis(analysisData);
    
    // Store result and switch to results view
    setAnalysisResult(result);
    setAnalysisHistory(prev => [result, ...prev]);
    setCurrentView('results');
    
    return result;
  };

  const handleBackToInput = () => {
    setCurrentView('input');
    setAnalysisResult(null);
  };

  const handleViewHistory = () => {
    // Future enhancement - for now just go back to input
    setCurrentView('input');
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'results':
        return (
          <ComparativeResultsDisplay
            analysisResult={analysisResult}
            onBack={handleBackToInput}
            onNewAnalysis={handleBackToInput}
          />
        );
      case 'about':
        return (
          <div>
            <h2>📖 About NET-EST</h2>
            <p>Phase 2.B.5 Dual Input Architecture - Fully Functional!</p>
            <button onClick={() => setCurrentView('input')}>Back to Input</button>
          </div>
        );
      default:
        return (
          <DualTextInputComponent
            onComparativeAnalysis={handleComparativeAnalysis}
            analysisHistory={analysisHistory}
            onViewHistory={handleViewHistory}
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
        boxShadow: '0 2px 20px rgba(0, 0, 0, 0.1)'
      }}>
        <h1 style={{ margin: 0, color: '#2d3748' }}>
          🌐 NET-EST - Análise Comparativa de Simplificação Textual
        </h1>
        <p style={{ margin: '0.5rem 0 0 0', color: '#4a5568' }}>
          Phase 2.B.5 - Dual Input Architecture - Fully Restored & Functional ✅
        </p>
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
