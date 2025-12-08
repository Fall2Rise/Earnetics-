import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { runAutonomousCycle } from '../../api/autonomyApi';
import {
  ActivityEntry,
  OperationsMetricsResponse,
  RequestEntry,
  fetchOperationsMetrics,
} from '../../api/operationsApi';
import { toStatusLabel, toStatusTone } from '../../utils/status';

interface OperationsPulseProps {
  compact?: boolean;
  enableAutonomyControls?: boolean;
}

const formatTimestamp = (value?: string) => {
  if (!value) return 'N/A';
  const parsed = new Date(value);
  return Number.isNaN(parsed.valueOf()) ? value : parsed.toLocaleString();
};

const limitArray = <T,>(items: T[] | undefined, limit: number): T[] => {
  if (!items?.length) return [];
  return items.slice(0, limit);
};

export const OperationsPulse: React.FC<OperationsPulseProps> = ({
  compact = false,
  enableAutonomyControls = false,
}) => {
  const [metrics, setMetrics] = useState<OperationsMetricsResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [cycleStatus, setCycleStatus] = useState<string | null>(null);
  const [runningCycle, setRunningCycle] = useState<boolean>(false);
  const mountedRef = useRef(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchOperationsMetrics();
      if (!mountedRef.current) return;
      setMetrics(data);
      setError(null);
    } catch (err) {
      if (!mountedRef.current) return;
      setError(err instanceof Error ? err.message : 'Unable to load operations telemetry');
    } finally {
      if (mountedRef.current) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    void refresh();
    return () => {
      mountedRef.current = false;
    };
  }, [refresh]);

  const queue = metrics?.queue ?? { pending: 0, at_risk: 0, overdue: 0 };
  const workerStatus = metrics?.worker?.status as string | undefined;
  const workerTone = toStatusTone(workerStatus);
  const workerLabel = toStatusLabel(workerStatus);

  const activityList = useMemo<ActivityEntry[]>(
    () => limitArray(metrics?.activity, compact ? 5 : 10),
    [compact, metrics?.activity],
  );

  const requestList = useMemo<RequestEntry[]>(
    () => limitArray(metrics?.requests, compact ? 4 : 8),
    [compact, metrics?.requests],
  );

  const handleCycle = useCallback(async () => {
    if (runningCycle) return;
    setRunningCycle(true);
    setCycleStatus(null);
    try {
      const result = await runAutonomousCycle();
      if (!mountedRef.current) return;
      if (result.status === 'error') {
        setCycleStatus(result.message ?? 'Autonomous cycle failed');
      } else {
        setCycleStatus('Autonomous cycle completed successfully.');
        await refresh();
      }
    } catch (err) {
      if (!mountedRef.current) return;
      setCycleStatus(err instanceof Error ? err.message : 'Autonomous cycle failed');
    } finally {
      if (mountedRef.current) {
        setRunningCycle(false);
      }
    }
  }, [refresh, runningCycle]);

  return (
    <section className="operations-panel">
      <header className="panel-header">
        <div>
          <h3>Operations Pulse</h3>
          <span>Real-time activity from automation scheduler</span>
        </div>
        <div className="panel-header__actions">
          {workerStatus && <span className={`status-pill status-pill--${workerTone}`}>{workerLabel}</span>}
          <button type="button" className="refresh-button" onClick={() => void refresh()} disabled={loading}>
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </header>

      {error && <p className="panel-error">{error}</p>}

      <div className="operations-summary">
        <div className="operations-summary__item">
          <span>Pending workflows</span>
          <strong>{queue.pending}</strong>
        </div>
        <div className="operations-summary__item">
          <span>At risk</span>
          <strong>{queue.at_risk}</strong>
        </div>
        <div className="operations-summary__item">
          <span>Overdue</span>
          <strong>{queue.overdue}</strong>
        </div>
      </div>

      {enableAutonomyControls && (
        <div className="operations-controls">
          <button
            type="button"
            className="primary-button"
            onClick={() => void handleCycle()}
            disabled={runningCycle}
          >
            {runningCycle ? 'Running Autonomous Cycle...' : 'Run Autonomous Cycle'}
          </button>
          {cycleStatus && <span className="operations-controls__status">{cycleStatus}</span>}
        </div>
      )}

      <div className="operations-activity">
        <h4>Recent automation</h4>
        {activityList.length === 0 && !loading && <p className="panel-empty">No automation activity yet.</p>}
        {activityList.length === 0 && loading && <p className="panel-empty">Loading activity...</p>}
        {activityList.map((entry) => (
          <article key={`${entry.timestamp}-${entry.pipeline_id ?? entry.agent ?? Math.random()}`} className="activity-card">
            <header>
              <strong>{entry.agent ?? 'Automation'}</strong>
              <span>{formatTimestamp(entry.timestamp)}</span>
            </header>
            <p>{entry.summary ?? 'Automation update'}</p>
            <footer>
              <span>{entry.stage ?? entry.status ?? 'activity'}</span>
              {entry.priority && <span className="activity-priority">{entry.priority}</span>}
            </footer>
          </article>
        ))}
      </div>

      {!compact && (
        <div className="operations-requests">
          <h4>Delegated directives</h4>
          {requestList.length === 0 && !loading && <p className="panel-empty">No directives queued.</p>}
          {requestList.length === 0 && loading && <p className="panel-empty">Loading directives...</p>}
          {requestList.length > 0 && (
            <ul>
              {requestList.map((item) => (
                <li key={`${item.timestamp}-${item.title ?? Math.random()}`}>
                  <span>{item.title ?? 'Directive'}</span>
                  <span>{item.priority ?? 'normal'}</span>
                  <time>{formatTimestamp(item.timestamp)}</time>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </section>
  );
};
