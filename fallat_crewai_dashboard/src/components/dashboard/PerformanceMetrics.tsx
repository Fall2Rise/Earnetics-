import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { getMetrics, Metric, MetricsResult } from '../../api/metricsApi';
import { toStatusLabel, toStatusTone } from '../../utils/status';
import { MetricDetailModal } from './MetricDetailModal';

type MetricsState = MetricsResult | null;

export const PerformanceMetrics: React.FC = () => {
  const [metricsState, setMetricsState] = useState<MetricsState>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const mountedRef = useRef(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalType, setModalType] = useState<'products' | 'workflows' | 'customers' | 'revenue' | 'directives'>('products');
  const [modalTitle, setModalTitle] = useState('');

  const applyMetrics = useCallback((result: MetricsResult) => {
    setMetricsState(result);
    setError(result.errorMessage ?? null);
  }, []);

  const loadMetrics = useCallback(async () => {
    // Debug logging removed to reduce request spam
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
    mountedRef.current = true;
    void loadMetrics();
    // Set up polling to refresh metrics every 10 seconds
    const intervalId = setInterval(() => {
      if (mountedRef.current) {
        void loadMetrics();
      }
    }, 10000);
    return () => {
      mountedRef.current = false;
      clearInterval(intervalId);
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

  // Always show metrics, even if empty (fallback data will be shown)
  const displayMetrics = metrics.length > 0 ? metrics : [
    { id: 'total_revenue', label: 'Total Revenue', value: '$0.00', trend: 'Awaiting launch' },
    { id: 'monthly_target', label: 'Monthly Target', value: '$150,000.00', trend: 'Configured by CFO' },
    { id: 'active_customers', label: 'Active Customers', value: '0', trend: 'Pipeline forming' },
    { id: 'products_created', label: 'Products Live', value: '0', trend: 'Ready to launch' },
  ];

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
        {displayMetrics.map((metric) => {
          const handleClick = () => {
            if (metric.id === 'products_created') {
              setModalType('products');
              setModalTitle('Live Products');
              setModalOpen(true);
            } else if (metric.id === 'active_customers') {
              setModalType('customers');
              setModalTitle('Active Customers');
              setModalOpen(true);
            } else if (metric.id === 'total_revenue') {
              setModalType('revenue');
              setModalTitle('Revenue Details');
              setModalOpen(true);
            }
          };

          const isClickable = ['products_created', 'active_customers', 'total_revenue'].includes(metric.id);

          return (
            <div
              key={metric.id}
              className={`metrics-card ${isClickable ? 'cursor-pointer hover:bg-slate-800/70 transition-colors' : ''}`}
              onClick={isClickable ? handleClick : undefined}
              role={isClickable ? 'button' : undefined}
              tabIndex={isClickable ? 0 : undefined}
              onKeyDown={(e) => {
                if (isClickable && (e.key === 'Enter' || e.key === ' ')) {
                  e.preventDefault();
                  handleClick();
                }
              }}
            >
              <p className="metrics-label">{metric.label}</p>
              <p className="metrics-value">{metric.value}</p>
              {metric.trend ? (
                <span className="metrics-trend">{metric.trend}</span>
              ) : (
                <span className="metrics-trend muted">--</span>
              )}
              {isClickable && (
                <span className="text-[10px] text-cyan-400/50 mt-1">Click to view details</span>
              )}
            </div>
          );
        })}
      </div>

      <MetricDetailModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        metricType={modalType}
        title={modalTitle}
      />

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
