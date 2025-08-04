/**
 * ErrorTestComponent.jsx - Component for testing ErrorBoundary functionality
 */

import React, { useState } from 'react';

const ErrorTestComponent = () => {
  const [shouldError, setShouldError] = useState(false);

  if (shouldError) {
    // This will throw an error and be caught by ErrorBoundary
    throw new Error('Test error: This is a deliberate error for testing ErrorBoundary!');
  }

  return (
    <div style={{ 
      padding: '20px', 
      margin: '10px 0', 
      border: '2px dashed #ff6b6b', 
      borderRadius: '8px',
      backgroundColor: '#fff5f5'
    }}>
      <h3>🧪 Error Boundary Test Component</h3>
      <p>This component is for testing error handling functionality.</p>
      <button
        onClick={() => setShouldError(true)}
        style={{
          padding: '10px 20px',
          backgroundColor: '#ff6b6b',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
          fontSize: '14px',
          fontWeight: 'bold'
        }}
      >
        💥 Trigger Error (Test ErrorBoundary)
      </button>
      <p style={{ fontSize: '12px', color: '#666', marginTop: '10px' }}>
        Click the button above to test the ErrorBoundary component.
      </p>
    </div>
  );
};

export default ErrorTestComponent;
