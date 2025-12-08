import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { getMetrics, Metric, MetricsResult } from '../../api/metricsApi';
import { toStatusLabel, toStatusTone } from '../../utils/status';

type MetricsState = MetricsResult | null;

export const PerformanceMetrics: React.FC = () => {
  const [metricsState, setMetricsState] = useState<MetricsState>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const mountedRef = useRef(true);

  const applyMetrics = useCallback((result: MetricsResult) => {
    setMetricsState(result);
    setError(result.errorMessage ?? null);
  }, []);

  const loadMetrics = useCallback(async () => {
    setLoading(true);
    try {
      const result = await getMetrics();
      if (!mountedRef.current) return;
      applyMetrics(result);
    } catch (err) {
      if (!mountedRef.current) return;
      const message = err instanceof Error ? err.message : 'Failed to load metrics';
      setError(message);
    } finally {
      if (mountedRef.current) {
        setLoading(false);
      }
    }
  }, [applyMetrics]);

  useEffect(() => {
    void loadMetrics();
    return () => {
      mountedRef.current = false;
    };
  }, [loadMetrics]);

  const updatedLabel = useMemo(() => {
    if (loading) return 'Syncing latest data...';
    if (metricsState?.updatedAt) {
      const updated = new Date(metricsState.updatedAt);
      if (!Number.isNaN(updated.valueOf())) {
        return `Updated ${updated.toLocaleTimeString()}`;
      }
    }
    if (error) return 'Fallback data in use';
    return 'Awaiting live transactions';
  }, [metricsState?.updatedAt, error, loading]);

  const statusLabel = toStatusLabel(metricsState?.overviewStatus);
  const statusClass = `status-pill status-pill--${toStatusTone(metricsState?.overviewStatus)}`;
  const metrics: Metric[] = metricsState?.metrics ?? [];

  const displayMetrics =
    loading && metrics.length === 0
      ? Array.from({ length: 4 }, (_, index) => ({
          id: `placeholder-${index}`,
          label: 'Loading...',
          value: '--',
          trend: '',
        }))
      : metrics;

  return (
    <div className="metrics-panel">
      <header className="metrics-header">
        <div className="metrics-header__title">
          <h3>Core Performance</h3>
          <span>{updatedLabel}</span>
        </div>
        <div className="metrics-header__actions">
          <span className={statusClass}>{statusLabel}</span>
          <button type="button" onClick={() => void loadMetrics()} disabled={loading} className="refresh-button">
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </header>

      {error && <p className="metrics-error">{error}</p>}

      <div className="metrics-grid">
        {displayMetrics.map((metric) => (
          <div key={metric.id} className="metrics-card">
            <p className="metrics-label">{metric.label}</p>
            <p className="metrics-value">{metric.value}</p>
            {metric.trend ? (
              <span className="metrics-trend">{metric.trend}</span>
            ) : (
              <span className="metrics-trend muted">--</span>
            )}
          </div>
        ))}
      </div>

      {typeof metricsState?.progressPercentage === 'number' && (
        <div className="metrics-progress">
          <div className="metrics-progress__label">
            <span>Target Progress</span>
            <span>{metricsState.progressPercentage.toFixed(1)}%</span>
          </div>
          <div className="metrics-progress__bar">
            <span style={{ width: `${Math.min(100, Math.max(0, metricsState.progressPercentage))}%` }} />
          </div>
        </div>
      )}

      {typeof metricsState?.totalRequests === 'number' && (
        <footer className="metrics-footer">
          <span>Total requests served</span>
          <strong>{metricsState.totalRequests.toLocaleString()}</strong>
        </footer>
      )}
    </div>
  );
};
