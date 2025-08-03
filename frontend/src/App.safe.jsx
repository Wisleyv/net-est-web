/**
 * App.jsx - Error Boundary Version
 */

import React from 'react';

// Error Boundary Component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
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
            <summary>Detalhes do erro (clique para expandir)</summary>
            <p><strong>Erro:</strong> {this.state.error && this.state.error.toString()}</p>
            <p><strong>Stack:</strong> {this.state.errorInfo.componentStack}</p>
          </details>
          <button 
            onClick={() => window.location.reload()} 
            style={{ 
              padding: '10px 20px', 
              background: '#007bff', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px',
              cursor: 'pointer',
              marginTop: '10px'
            }}
          >
            🔄 Recarregar Página
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// Simple App Component
function SimpleApp() {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif', minHeight: '100vh', background: '#f5f5f5' }}>
      <header style={{ background: 'white', padding: '20px', borderRadius: '8px', marginBottom: '20px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <h1 style={{ color: '#333', margin: '0 0 10px 0' }}>
          🎯 Sistema de Análise de Tradução Intralinguística
        </h1>
        <p style={{ color: '#666', margin: '0' }}>
          Ferramenta de análise linguística computacional para identificação e classificação de estratégias de simplificação textual.
        </p>
      </header>

      <main style={{ background: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <div style={{ background: '#e8f5e8', padding: '15px', borderRadius: '6px', marginBottom: '20px' }}>
          <h2 style={{ color: '#2d5a2d', margin: '0 0 10px 0' }}>✅ Status da Aplicação</h2>
          <ul style={{ margin: '0', color: '#2d5a2d' }}>
            <li>✅ React carregado e funcionando</li>
            <li>✅ HTML e CSS aplicados corretamente</li>
            <li>✅ Estado de desenvolvimento: Phase 2.B.1 State Management</li>
            <li>⚠️ State Management em processo de teste</li>
          </ul>
        </div>

        <div style={{ background: '#f8f9fa', padding: '15px', borderRadius: '6px' }}>
          <h3 style={{ margin: '0 0 10px 0' }}>🚧 Desenvolvimento em Progresso</h3>
          <p style={{ margin: '0' }}>
            Esta versão está sendo testada para identificar problemas com as importações do state management (Zustand + React Query).
            Se você está vendo esta mensagem, significa que o React está funcionando corretamente.
          </p>
        </div>
      </main>
    </div>
  );
}

// Main App with Error Boundary
function App() {
  return (
    <ErrorBoundary>
      <SimpleApp />
    </ErrorBoundary>
  );
}

export default App;
