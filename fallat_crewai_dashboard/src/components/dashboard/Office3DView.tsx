import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { fetchSystemStatus, SystemStatusResponse } from '../../api/systemStatusApi';
import { toStatusLabel, toStatusTone } from '../../utils/status';

const formatCurrency = (value?: number) =>
  new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
  }).format(value ?? 0);

const getLastUpdated = (data: SystemStatusResponse | null): string | undefined => {
  if (!data) return undefined;
  return (
    data.system_health?.system_overview?.performance_metrics?.last_updated ??
    data.system_health?.timestamp ??
    data.timestamp
  );
};

export const Office3DView: React.FC = () => {
  const [status, setStatus] = useState<SystemStatusResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const mountedRef = useRef(true);

  const loadStatus = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetchSystemStatus();
      if (!mountedRef.current) return;
      setStatus(response);
      setError(null);
    } catch (err) {
      if (!mountedRef.current) return;
      const message = err instanceof Error ? err.message : 'Unable to sync system status';
      setError(message);
    } finally {
      if (mountedRef.current) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    void loadStatus();
    return () => {
      mountedRef.current = false;
    };
  }, [loadStatus]);

  const overview = status?.system_health?.system_overview;
  const metrics = overview?.performance_metrics;
  const agentPerformance = status?.system_health?.agent_performance;

  const lastUpdated = useMemo(() => {
    const timestamp = getLastUpdated(status);
    if (!timestamp) return 'Awaiting telemetry sync';
    const parsed = new Date(timestamp);
    if (Number.isNaN(parsed.valueOf())) return 'Awaiting telemetry sync';
    return `Last sync ${parsed.toLocaleString()}`;
  }, [status]);

  const quickStats = useMemo(
    () => [
      {
        label: 'Agents Online',
        value: overview?.total_agents ?? '--',
      },
      {
        label: 'Departments Active',
        value: overview?.active_departments ?? '--',
      },
      {
        label: 'Avg Response',
        value: agentPerformance?.avg_response_time ?? 'N/A',
      },
      {
        label: 'Success Rate',
        value: agentPerformance?.success_rate ?? 'N/A',
      },
    ],
    [agentPerformance?.avg_response_time, agentPerformance?.success_rate, overview?.active_departments, overview?.total_agents],
  );

  const totalRevenue = metrics?.total_revenue ?? 0;
  const monthlyTarget = metrics?.monthly_target ?? 0;
  const progress = monthlyTarget > 0 ? Math.min(100, (totalRevenue / monthlyTarget) * 100) : 0;

  const statusPillClass = `status-pill status-pill--${toStatusTone(overview?.status)}`;
  const statusLabel = toStatusLabel(overview?.status);

  return (
    <div className="holo-stage">
      <div className="holo-grid" />
      <div className="holo-core">
        <div className="holo-core__inner">
          <div className="holo-header">
            <div>
              <h2 className="holo-title">Fallat Command Nexus</h2>
              <p className="holo-subtitle">{lastUpdated}</p>
            </div>
            <span className={statusPillClass}>{statusLabel}</span>
          </div>

          <div className="holo-highlight">
            <span>Total Revenue</span>
            <strong>{formatCurrency(totalRevenue)}</strong>
            <small>
              {monthlyTarget > 0
                ? `${progress.toFixed(1)}% of ${formatCurrency(monthlyTarget)} target`
                : 'Set monthly target in finance controls'}
            </small>
          </div>

          <div className="holo-stats">
            {quickStats.map((stat) => (
              <div key={stat.label} className="holo-stat">
                <span>{stat.label}</span>
                <strong>{stat.value}</strong>
              </div>
            ))}
          </div>

          {error && <p className="holo-error">{error}</p>}

          <button
            type="button"
            className="refresh-button refresh-button--compact"
            onClick={() => void loadStatus()}
            disabled={loading}
          >
            {loading ? 'Refreshing...' : 'Resync Telemetry'}
          </button>
        </div>
      </div>
      <div className="holo-pulse" />
    </div>
  );
};
