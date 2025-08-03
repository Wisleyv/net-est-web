/**
 * Fresh App.jsx - Debugging version
 */

import React from 'react';

console.log('App.jsx loading...');

function App() {
  console.log('App component rendering...');
  
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ color: 'blue' }}>🚀 NET-EST Frontend Debug</h1>
      <div style={{ background: '#f0f0f0', padding: '10px', margin: '10px 0' }}>
        <p>✅ React está funcionando</p>
        <p>✅ Component está renderizando</p>
        <p>⏰ Timestamp: {new Date().toLocaleTimeString()}</p>
      </div>
    </div>
  );
}

console.log('App.jsx loaded successfully');

export default App;
