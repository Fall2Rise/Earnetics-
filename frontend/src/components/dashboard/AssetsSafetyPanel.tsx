import React, { useCallback, useEffect, useState } from 'react';
import { fetchAssets, fetchAssetAlerts, Asset, AssetAlert } from '../../api/headOfficeApi';

export const AssetsSafetyPanel: React.FC = () => {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [alerts, setAlerts] = useState<AssetAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [assetsData, alertsData] = await Promise.all([
        fetchAssets(),
        fetchAssetAlerts(),
      ]);
      setAssets(assetsData);
      setAlerts(alertsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load assets');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
    const interval = setInterval(loadData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [loadData]);

  if (loading && assets.length === 0) {
    return (
      <div className="command-panel">
        <div className="panel-header">
          <h2>Assets + Safety Radar</h2>
        </div>
        <div className="panel-content">Loading...</div>
      </div>
    );
  }

  const activeAlerts = alerts.filter(a => a.status === 'active');

  return (
    <div className="command-panel command-panel--full">
      <div className="panel-header">
        <h2>Assets + Safety Radar</h2>
        <button onClick={loadData} className="btn-secondary" disabled={loading}>
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>
      {error && <div className="panel-error">{error}</div>}
      <div className="panel-content panel-content--split">
        <div className="assets-section">
          <h3>Asset Inventory ({assets.length})</h3>
          {assets.length === 0 ? (
            <p className="empty-state">No assets found</p>
          ) : (
            <div className="asset-list">
              {assets.map((asset) => (
                <div key={asset.id} className={`asset-item criticality-${asset.criticality}`}>
                  <div className="asset-header">
                    <strong>{asset.name}</strong>
                    <span className={`criticality-badge criticality-${asset.criticality}`}>
                      {asset.criticality}
                    </span>
                  </div>
                  <div className="asset-meta">
                    <span>Category: {asset.category}</span>
                    <span>Owner: {asset.owner}</span>
                    {asset.value !== undefined && (
                      <span>Value: ${asset.value.toFixed(2)}</span>
                    )}
                  </div>
                  {asset.description && <p>{asset.description}</p>}
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="alerts-section">
          <h3>Safety Alerts ({activeAlerts.length})</h3>
          {activeAlerts.length === 0 ? (
            <p className="empty-state">No active alerts</p>
          ) : (
            <div className="alert-list">
              {activeAlerts.map((alert) => (
                <div key={alert.id} className={`alert-item severity-${alert.severity}`}>
                  <div className="alert-header">
                    <strong>{alert.alert_type}</strong>
                    <span className={`severity-badge severity-${alert.severity}`}>
                      {alert.severity}
                    </span>
                  </div>
                  <p>{alert.message}</p>
                  <div className="alert-meta">
                    <span>Asset: {alert.asset_id}</span>
                    <span>Triggered: {new Date(alert.triggered_at).toLocaleString()}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
