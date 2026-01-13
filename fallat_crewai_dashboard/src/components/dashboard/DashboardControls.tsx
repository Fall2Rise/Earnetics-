import React, { useCallback, useEffect, useState } from 'react';
import { fetchSystemStatus, SystemStatusResponse } from '../../api/systemStatusApi';
import { runAutonomousCycle } from '../../api/autonomyApi';
import { API_BASE_URL } from '../../api/config';

export const DashboardControls: React.FC = () => {
  const [status, setStatus] = useState<SystemStatusResponse | null>(null);
  const [runningCycle, setRunningCycle] = useState(false);
  const [loading, setLoading] = useState(false);

  const loadStatus = useCallback(async () => {
    try {
      const data = await fetchSystemStatus();
      setStatus(data);
    } catch (err) {
      console.error('Failed to load system status:', err);
    }
  }, []);

  useEffect(() => {
    void loadStatus();
    const interval = setInterval(loadStatus, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [loadStatus]);

  const handleToggleSafeMode = useCallback(async () => {
    try {
      setLoading(true);
      const currentSafeMode = status?.safe_mode ?? false;
      const response = await fetch(`${API_BASE_URL}/api/system/controls`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ safe_mode: !currentSafeMode }),
      });
      if (response.ok) {
        await loadStatus();
      }
    } catch (err) {
      console.error('Failed to toggle safe mode:', err);
    } finally {
      setLoading(false);
    }
  }, [status, loadStatus]);

  const handleToggleAgentExecution = useCallback(async () => {
    try {
      setLoading(true);
      const currentPaused = status?.agent_paused ?? false;
      const response = await fetch(`${API_BASE_URL}/api/system/controls`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agent_execution_paused: !currentPaused }),
      });
      if (response.ok) {
        await loadStatus();
      }
    } catch (err) {
      console.error('Failed to toggle agent execution:', err);
    } finally {
      setLoading(false);
    }
  }, [status, loadStatus]);

  const handleToggleMailSending = useCallback(async () => {
    try {
      setLoading(true);
      const currentPaused = status?.mail_paused ?? false;
      const response = await fetch(`${API_BASE_URL}/api/system/controls`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mail_sending_paused: !currentPaused }),
      });
      if (response.ok) {
        await loadStatus();
      }
    } catch (err) {
      console.error('Failed to toggle mail sending:', err);
    } finally {
      setLoading(false);
    }
  }, [status, loadStatus]);

  const handleRunCycle = useCallback(async () => {
    try {
      setRunningCycle(true);
      await runAutonomousCycle('Manual dashboard trigger', { source: 'dashboard_controls' });
      // Refresh status after cycle
      setTimeout(() => {
        void loadStatus();
      }, 2000);
    } catch (err) {
      console.error('Failed to run cycle:', err);
    } finally {
      setRunningCycle(false);
    }
  }, [loadStatus]);

  return (
    <div className="dashboard-controls">
      <div className="controls-header">
        <h3>System Controls</h3>
        <button
          onClick={loadStatus}
          className="btn-secondary btn-sm"
          disabled={loading}
        >
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>
      <div className="controls-grid">
        {/* Safe Mode Toggle */}
        <div className="control-item">
          <div className="control-label">
            <span>Safe Mode</span>
            <span className={`status-indicator ${status?.safe_mode ? 'active' : 'inactive'}`}>
              {status?.safe_mode ? 'ON' : 'OFF'}
            </span>
          </div>
          <button
            onClick={handleToggleSafeMode}
            className={`btn-toggle ${status?.safe_mode ? 'active' : ''}`}
            disabled={loading}
          >
            {status?.safe_mode ? 'Disable' : 'Enable'}
          </button>
        </div>

        {/* Agent Execution Toggle */}
        <div className="control-item">
          <div className="control-label">
            <span>Agent Execution</span>
            <span className={`status-indicator ${status?.agent_paused ? 'paused' : 'active'}`}>
              {status?.agent_paused ? 'PAUSED' : 'RUNNING'}
            </span>
          </div>
          <button
            onClick={handleToggleAgentExecution}
            className={`btn-toggle ${status?.agent_paused ? 'paused' : ''}`}
            disabled={loading}
          >
            {status?.agent_paused ? 'Resume' : 'Pause'}
          </button>
        </div>

        {/* Mail Sending Toggle */}
        <div className="control-item">
          <div className="control-label">
            <span>Mail Sending</span>
            <span className={`status-indicator ${status?.mail_paused ? 'paused' : 'active'}`}>
              {status?.mail_paused ? 'PAUSED' : 'ENABLED'}
            </span>
          </div>
          <button
            onClick={handleToggleMailSending}
            className={`btn-toggle ${status?.mail_paused ? 'paused' : ''}`}
            disabled={loading}
          >
            {status?.mail_paused ? 'Resume' : 'Pause'}
          </button>
        </div>

        {/* Manual Cycle Trigger */}
        <div className="control-item control-item--action">
          <div className="control-label">
            <span>Run Cycle</span>
            <span className="control-description">Trigger autonomous cycle manually</span>
          </div>
          <button
            onClick={handleRunCycle}
            className="btn-primary"
            disabled={runningCycle || loading}
          >
            {runningCycle ? 'Running...' : 'Run Cycle'}
          </button>
        </div>
      </div>
    </div>
  );
};
