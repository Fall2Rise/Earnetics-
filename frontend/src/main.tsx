import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { ErrorBoundary } from './components/ErrorBoundary';
import './styles/index.css';

console.log('[Main] Starting React app initialization...');

const rootElement = document.getElementById('root');
if (!rootElement) {
  console.error('[Main] Root element not found!');
  throw new Error('Root element not found');
}

console.log('[Main] Root element found, creating React root...');

try {
  const root = ReactDOM.createRoot(rootElement);
  console.log('[Main] React root created, rendering app...');
  
  root.render(
    <React.StrictMode>
      <ErrorBoundary>
        <App />
      </ErrorBoundary>
    </React.StrictMode>,
  );
  
  console.log('[Main] App rendered successfully');
} catch (error) {
  console.error('[Main] Failed to render app:', error);
  rootElement.innerHTML = `
    <div style="padding: 2rem; color: white; font-family: Inter, sans-serif;">
      <h1>Rendering Error</h1>
      <p>Failed to render the React app. Check the console for details.</p>
      <pre style="background: rgba(0,0,0,0.5); padding: 1rem; border-radius: 0.5rem; overflow: auto;">
        ${error instanceof Error ? error.stack : String(error)}
      </pre>
    </div>
  `;
}
