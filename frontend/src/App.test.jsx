/**
 * Minimal App.jsx for testing
 */

import React from 'react';

function App() {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
        <h1 className="text-2xl font-bold text-center text-blue-600 mb-4">
          NET-EST System
        </h1>
        <p className="text-gray-600 text-center">
          Phase 2.B.1 State Management Integration
        </p>
        <div className="mt-6 text-center">
          <div className="inline-block px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
            System Status: Online
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
