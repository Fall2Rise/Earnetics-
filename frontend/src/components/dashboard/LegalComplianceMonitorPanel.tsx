import React from 'react';
import { LegalContractsPanel } from './LegalContractsPanel';
import { TaxDeskPanel } from './TaxDeskPanel';
import { AssetsSafetyPanel } from './AssetsSafetyPanel';
import { LawLibraryPanel } from './LawLibraryPanel';

export const LegalComplianceMonitorPanel: React.FC = () => {
  return (
    <div className="panel-stack">
      <div className="command-panel">
        <LegalContractsPanel />
      </div>
      <div className="command-panel">
        <TaxDeskPanel />
      </div>
      <div className="command-panel">
        <AssetsSafetyPanel />
      </div>
      <div className="command-panel">
        <LawLibraryPanel />
      </div>
    </div>
  );
};
