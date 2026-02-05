import React from 'react';
import { CredentialManager } from '../workflows/CredentialManager';

export const CredentialVaultPanel: React.FC = () => {
  return (
    <div className="command-panel">
      <CredentialManager />
    </div>
  );
};
