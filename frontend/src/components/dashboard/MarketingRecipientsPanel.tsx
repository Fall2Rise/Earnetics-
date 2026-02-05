import React, { useState, useEffect } from 'react';
import { leadManagementApi, MarketingRecipient } from '../../api/leadManagementApi';

export const MarketingRecipientsPanel: React.FC = () => {
  const [recipients, setRecipients] = useState<MarketingRecipient[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRecipients();
    loadStats();
    const interval = setInterval(() => {
      loadRecipients();
      loadStats();
    }, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadRecipients = async () => {
    try {
      setLoading(true);
      const data = await leadManagementApi.getMarketingRecipients({ limit: 500 });
      setRecipients(data.recipients);
    } catch (error) {
      console.error('Failed to load recipients:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const data = await leadManagementApi.getMarketingRecipientsStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  return (
    <div className="command-panel">
      <div className="panel-header">
        <h2>📧 Marketing Campaign Recipients</h2>
        <div className="panel-controls">
          <button className="btn btn-sm" onClick={loadRecipients}>Refresh</button>
        </div>
      </div>

      {stats && (
        <div className="stats-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '1rem' }}>
          <div className="stat-card">
            <div className="stat-value">{stats.total_campaigns}</div>
            <div className="stat-label">Total Campaigns</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.total_sent}</div>
            <div className="stat-label">Total Sent</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.engagement?.opened?.unique_count || 0}</div>
            <div className="stat-label">Unique Opens</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.engagement?.clicked?.unique_count || 0}</div>
            <div className="stat-label">Unique Clicks</div>
          </div>
        </div>
      )}

      <div className="table-container" style={{ maxHeight: '600px', overflowY: 'auto' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Email</th>
              <th>Campaign</th>
              <th>Sent At</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={4} style={{ textAlign: 'center', padding: '2rem' }}>Loading recipients...</td>
              </tr>
            ) : recipients.length === 0 ? (
              <tr>
                <td colSpan={4} style={{ textAlign: 'center', padding: '2rem' }}>No recipients found</td>
              </tr>
            ) : (
              recipients.map((recipient, idx) => (
                <tr key={`${recipient.email}-${recipient.campaign_id}-${idx}`}>
                  <td>{recipient.email}</td>
                  <td>
                    <span className="badge">{recipient.campaign_name || recipient.campaign_subject || `Campaign #${recipient.campaign_id}`}</span>
                  </td>
                  <td>{new Date(recipient.sent_at).toLocaleString()}</td>
                  <td>
                    <span className="badge badge-success">✓ Sent</span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
