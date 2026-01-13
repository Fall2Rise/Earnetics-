import React, { useCallback, useEffect, useState } from 'react';
import {
  fetchContracts,
  getContract,
  scanContract,
  getSignatureRecommendation,
  Contract,
  ContractScanResult,
} from '../../api/headOfficeApi';

export const LegalContractsPanel: React.FC = () => {
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [selectedContract, setSelectedContract] = useState<Contract | null>(null);
  const [scanResult, setScanResult] = useState<ContractScanResult | null>(null);
  const [signatureRec, setSignatureRec] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [scanning, setScanning] = useState(false);

  const loadContracts = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchContracts();
      setContracts(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load contracts');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadContracts();
    const interval = setInterval(loadContracts, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [loadContracts]);

  const handleSelectContract = async (id: string) => {
    try {
      const contract = await getContract(id);
      setSelectedContract(contract);
      setScanResult(null);
      setSignatureRec(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load contract');
    }
  };

  const handleScanContract = async (contractId: string) => {
    try {
      setScanning(true);
      setError(null);
      const result = await scanContract(contractId);
      setScanResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to scan contract');
    } finally {
      setScanning(false);
    }
  };

  const handleGetSignature = async (contractId: string) => {
    try {
      setError(null);
      const result = await getSignatureRecommendation(contractId);
      setSignatureRec(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get signature recommendation');
    }
  };

  if (loading && contracts.length === 0) {
    return (
      <div className="command-panel">
        <div className="panel-header">
          <h2>Legal + Contracts</h2>
        </div>
        <div className="panel-content">Loading...</div>
      </div>
    );
  }

  return (
    <div className="command-panel command-panel--full">
      <div className="panel-header">
        <h2>Legal + Contracts</h2>
        <button onClick={loadContracts} className="btn-secondary" disabled={loading}>
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>
      {error && <div className="panel-error">{error}</div>}
      <div className="panel-content panel-content--split">
        <div className="contract-list">
          <h3>Contracts ({contracts.length})</h3>
          {contracts.length === 0 ? (
            <p className="empty-state">No contracts found</p>
          ) : (
            <ul className="contract-items">
              {contracts.map((contract) => (
                <li
                  key={contract.id}
                  className={`contract-item ${selectedContract?.id === contract.id ? 'selected' : ''}`}
                  onClick={() => handleSelectContract(contract.id)}
                >
                  <div className="contract-item-header">
                    <strong>{contract.title}</strong>
                    <span className={`status-badge status-${contract.status}`}>
                      {contract.status}
                    </span>
                  </div>
                  <div className="contract-item-meta">
                    <span>Party: {contract.party_name}</span>
                    <span>Counterparty: {contract.counterparty}</span>
                    <span>Type: {contract.contract_type}</span>
                  </div>
                  {contract.value !== undefined && (
                    <div className="contract-item-value">Value: ${contract.value.toFixed(2)}</div>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>

        {selectedContract && (
          <div className="contract-details">
            <h3>{selectedContract.title}</h3>
            <div className="detail-section">
              <h4>Contract Info</h4>
              <p><strong>Party:</strong> {selectedContract.party_name}</p>
              <p><strong>Counterparty:</strong> {selectedContract.counterparty}</p>
              <p><strong>Type:</strong> {selectedContract.contract_type}</p>
              <p><strong>Status:</strong> {selectedContract.status}</p>
              <p><strong>Version:</strong> {selectedContract.version}</p>
              {selectedContract.value !== undefined && (
                <p><strong>Value:</strong> ${selectedContract.value.toFixed(2)}</p>
              )}
              {selectedContract.expiry_date && (
                <p><strong>Expiry:</strong> {selectedContract.expiry_date}</p>
              )}
            </div>

            <div className="contract-actions">
              <button
                onClick={() => handleScanContract(selectedContract.id)}
                className="btn-primary"
                disabled={scanning}
              >
                {scanning ? 'Scanning...' : 'Scan for Loopholes'}
              </button>
              <button
                onClick={() => handleGetSignature(selectedContract.id)}
                className="btn-secondary"
              >
                Get Signature Recommendation
              </button>
            </div>

            {scanResult && (
              <div className="scan-result">
                <h4>Scan Result</h4>
                <div className={`risk-level risk-${scanResult.risk_level}`}>
                  Risk Level: <strong>{scanResult.risk_level.toUpperCase()}</strong>
                </div>
                <div className="scan-summary">
                  <h5>Executive Summary</h5>
                  <p>{scanResult.executive_summary}</p>
                </div>
                {Object.keys(scanResult.risk_map).length > 0 && (
                  <div className="risk-map">
                    <h5>Risk Map</h5>
                    <ul>
                      {Object.entries(scanResult.risk_map).map(([category, level]) => (
                        <li key={category} className={`risk-${level}`}>
                          <strong>{category}:</strong> {level}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {scanResult.missing_items_checklist.length > 0 && (
                  <div className="missing-items">
                    <h5>Missing Items Checklist</h5>
                    <ul>
                      {scanResult.missing_items_checklist.map((item, idx) => (
                        <li key={idx}>{item}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {signatureRec && (
              <div className="signature-recommendation">
                <h4>Signature Recommendation</h4>
                <pre>{JSON.stringify(signatureRec, null, 2)}</pre>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
