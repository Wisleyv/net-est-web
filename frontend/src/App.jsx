/**
 * NET-EST Text Simplification Analysis System
 * Enhanced for strategy detection and visual analysis
 */

import React, { useState, useEffect } from 'react';
import './App.css'; // Ensure global styles (including strategy marker highlight) are applied
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Components
import EnhancedTextInput from './components/EnhancedTextInput';
import AboutCredits from './components/AboutCredits';
import useAppStore from './stores/useAppStore.js';
import useAnnotationStore from './stores/useAnnotationStore.js';
import AnnotationTimeline from './components/dashboard/AnnotationTimeline.jsx';
import AuditSearchPanel from './components/dashboard/AuditSearchPanel.jsx';

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
  const enableFeedbackActions = useAppStore(s => s.config.enableFeedbackActions);
  const { exportAnnotations } = useAnnotationStore();

  // Dev-only flag: enable feedback actions during development/testing.
  // Also provide a compatibility alias window.ENABLE_FEEDBACK_FLAG for convenience.
  useEffect(() => {
    const env = (typeof import.meta !== 'undefined' && import.meta.env) ? import.meta.env : {};
    const isNonProd = !!(env && (env.DEV || env.MODE === 'test'));

    if (typeof window !== 'undefined' && isNonProd) {
      // Dev diagnostics: log initial flag state
      try {
        // eslint-disable-next-line no-console
        console.log('[NET-EST][dev] ENABLE_FEEDBACK diagnostics', {
          VITE_ENABLE_FEEDBACK: env?.VITE_ENABLE_FEEDBACK,
          VITE_DISABLE_FEEDBACK: env?.VITE_DISABLE_FEEDBACK,
          existingWindowFlag: typeof window.__ENABLE_FEEDBACK_FLAG__,
        });
      } catch {}
      // Provide a readable/writable alias without underscores for convenience in DevTools
      try {
        if (!Object.getOwnPropertyDescriptor(window, 'ENABLE_FEEDBACK_FLAG')) {
          Object.defineProperty(window, 'ENABLE_FEEDBACK_FLAG', {
            get() { return window.__ENABLE_FEEDBACK_FLAG__; },
            set(v) { window.__ENABLE_FEEDBACK_FLAG__ = v; },
            configurable: true,
          });
        }
      } catch (_) {
        // no-op: defining property can fail in some hardened contexts; safe to ignore in dev
      }

      // Auto-enable in dev unless explicitly disabled via VITE_DISABLE_FEEDBACK === 'true'
      const explicitlyDisabled = env && env.VITE_DISABLE_FEEDBACK === 'true';
      const explicitlyEnabled = env && env.VITE_ENABLE_FEEDBACK === 'true';
      const shouldEnable = !explicitlyDisabled && (explicitlyEnabled || window.__ENABLE_FEEDBACK_FLAG__ !== false);

      if (shouldEnable) {
        window.__ENABLE_FEEDBACK_FLAG__ = true;
        const st = useAppStore.getState();
        if (!st?.config?.enableFeedbackActions) {
          useAppStore.setState({ config: { ...st.config, enableFeedbackActions: true } });
        }
        try {
          // eslint-disable-next-line no-console
          console.log('[NET-EST][dev] Feedback actions enabled:', {
            windowFlag: window.__ENABLE_FEEDBACK_FLAG__,
            enableFeedbackActions: useAppStore.getState().config.enableFeedbackActions,
          });
        } catch {}
      }

      // Dev helpers: expose methods to inspect/toggle flag at runtime
      try {
        window.NET_EST = window.NET_EST || {};
        window.NET_EST.getStore = () => useAppStore.getState();
        window.NET_EST.enableFeedback = () => {
          window.__ENABLE_FEEDBACK_FLAG__ = true;
          const st = useAppStore.getState();
          useAppStore.setState({ config: { ...st.config, enableFeedbackActions: true } });
          // eslint-disable-next-line no-console
          console.log('[NET-EST][dev] enableFeedback ->', useAppStore.getState().config.enableFeedbackActions);
        };
        window.NET_EST.disableFeedback = () => {
          window.__ENABLE_FEEDBACK_FLAG__ = false;
          const st = useAppStore.getState();
          useAppStore.setState({ config: { ...st.config, enableFeedbackActions: false } });
          // eslint-disable-next-line no-console
          console.log('[NET-EST][dev] disableFeedback ->', useAppStore.getState().config.enableFeedbackActions);
        };
      } catch {}
    }
  }, []);

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
                backgroundColor: currentView === 'input' || currentView === 'results' ? '#2563eb' : '#e2e8f0', // darker blue for contrast
                color: currentView === 'input' || currentView === 'results' ? '#ffffff' : '#2d3748',
                border: '2px solid transparent',
                borderRadius: '0.5rem',
                cursor: 'pointer',
                fontSize: '0.875rem',
                fontWeight: '600',
                transition: 'all 0.2s ease',
                outline: 'none'
              }}
              onFocus={(e) => { e.currentTarget.style.borderColor = '#1d4ed8'; }}
              onBlur={(e) => { e.currentTarget.style.borderColor = 'transparent'; }}
              aria-current={currentView === 'input' || currentView === 'results' ? 'page' : undefined}
            >
              📝 Análise de Textos
            </button>
            <button
              onClick={() => setCurrentView('about')}
              style={{
                padding: '0.625rem 1.25rem',
                backgroundColor: currentView === 'about' ? '#2563eb' : '#e2e8f0',
                color: currentView === 'about' ? '#ffffff' : '#2d3748',
                border: '2px solid transparent',
                borderRadius: '0.5rem',
                cursor: 'pointer',
                fontSize: '0.875rem',
                fontWeight: '600',
                transition: 'all 0.2s ease',
                outline: 'none'
              }}
              onFocus={(e) => { e.currentTarget.style.borderColor = '#1d4ed8'; }}
              onBlur={(e) => { e.currentTarget.style.borderColor = 'transparent'; }}
              aria-current={currentView === 'about' ? 'page' : undefined}
            >
              ℹ️ Sobre
            </button>
            {enableFeedbackActions && (
              <div style={{ display:'flex', gap:'0.5rem' }} aria-label="Exportar anotações">
                <button
                  onClick={() => exportAnnotations('jsonl')}
                  style={{ padding:'0.625rem 1.0rem', background:'#805ad5', color:'#fff', border:'none', borderRadius:'0.5rem', cursor:'pointer', fontSize:'0.75rem' }}
                  aria-label="Exportar anotações em JSONL"
                >Export JSONL</button>
                <button
                  onClick={() => exportAnnotations('csv')}
                  style={{ padding:'0.625rem 1.0rem', background:'#6b46c1', color:'#fff', border:'none', borderRadius:'0.5rem', cursor:'pointer', fontSize:'0.75rem' }}
                  aria-label="Exportar anotações em CSV"
                >Export CSV</button>
              </div>
            )}
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
          {/* Phase 4a Timeline (client-derived) */}
          {enableFeedbackActions && enableFeedbackActions && enableFeedbackActions && null}
          {enableFeedbackActions && enableFeedbackActions && null}
          {/** separate flag for timeline */}
          {useAppStore.getState().config.enableTimelineView && (
            <div style={{ marginTop:'2rem' }}>
              <AnnotationTimeline />
            </div>
          )}
          {useAppStore.getState().config.enableAuditSearch && (
            <div style={{ marginTop:'2rem' }}>
              <AuditSearchPanel />
            </div>
          )}
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
