import React, { useCallback, useEffect, useState } from 'react';
import {
  fetchMasterAIStatus,
  submitMasterAIRequest,
  MasterAIAction,
} from '../../api/headOfficeApi';

export const MasterAIPanel: React.FC = () => {
  const [status, setStatus] = useState<Record<string, unknown> | null>(null);
  const [request, setRequest] = useState('');
  const [mode, setMode] = useState('advisor');
  const [submitting, setSubmitting] = useState(false);
  const [lastAction, setLastAction] = useState<MasterAIAction | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadStatus = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchMasterAIStatus();
      setStatus(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load Master AI status');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadStatus();
    const interval = setInterval(loadStatus, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [loadStatus]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!request.trim()) return;

    try {
      setSubmitting(true);
      setError(null);
      const action = await submitMasterAIRequest(request, mode);
      setLastAction(action);
      setRequest('');
      await loadStatus();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit request');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading && !status) {
    return (
      <div className="command-panel">
        <div className="panel-header">
          <h2>Master AI</h2>
        </div>
        <div className="panel-content">Loading...</div>
      </div>
    );
  }

  return (
    <div className="command-panel command-panel--full">
      <div className="panel-header">
        <h2>Master AI (Owner Assistant)</h2>
        <button onClick={loadStatus} className="btn-secondary" disabled={loading}>
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>
      {error && <div className="panel-error">{error}</div>}
      <div className="panel-content">
        {status && (
          <div className="master-ai-status">
            <h3>Status</h3>
            <pre>{JSON.stringify(status, null, 2)}</pre>
          </div>
        )}

        <div className="master-ai-request">
          <h3>Submit Request</h3>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="mode">Mode</label>
              <select
                id="mode"
                value={mode}
                onChange={(e) => setMode(e.target.value)}
                className="select-input"
              >
                <option value="advisor">Advisor (Recommend only)</option>
                <option value="operator">Operator (Low-risk execute)</option>
                <option value="executive">Executive (Requires approval)</option>
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="request">Request</label>
              <textarea
                id="request"
                value={request}
                onChange={(e) => setRequest(e.target.value)}
                className="textarea-input"
                rows={4}
                placeholder="Enter your request..."
              />
            </div>
            <button
              type="submit"
              className="btn-primary"
              disabled={submitting || !request.trim()}
            >
              {submitting ? 'Submitting...' : 'Submit Request'}
            </button>
          </form>
        </div>

        {lastAction && (
          <div className="last-action">
            <h3>Last Action Result</h3>
            <div className={`action-result status-${lastAction.result_status}`}>
              <p><strong>Status:</strong> {lastAction.result_status}</p>
              <p><strong>Message:</strong> {lastAction.result_message}</p>
              <p><strong>Mode:</strong> {lastAction.mode}</p>
              <p><strong>Approval Required:</strong> {lastAction.approval_required ? 'Yes' : 'No'}</p>
              <p><strong>Timestamp:</strong> {new Date(lastAction.timestamp).toLocaleString()}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
