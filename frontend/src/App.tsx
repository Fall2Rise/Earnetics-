import React from 'react';
import { CommandCenter } from './components/layout/CommandCenter';
import { ErrorBoundary } from './components/ErrorBoundary';

function App() {
  return (
    <div style={{ width: '100vw', height: '100vh', margin: 0, padding: 0, overflow: 'hidden' }}>
      <ErrorBoundary>
        <CommandCenter />
      </ErrorBoundary>
    </div>
  );
}

export default App;
