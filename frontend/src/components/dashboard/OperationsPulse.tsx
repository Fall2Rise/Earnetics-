import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { runAutonomousCycle } from '../../api/autonomyApi';
import {
  ActivityEntry,
  OperationsMetricsResponse,
  RequestEntry,
  fetchOperationsMetrics,
  updateDirectiveStatus,
} from '../../api/operationsApi';
import { toStatusLabel, toStatusTone } from '../../utils/status';
import { MetricDetailModal } from './MetricDetailModal';
import { DetailModal } from './DetailModal';

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
  const [modalOpen, setModalOpen] = useState(false);
  const [activityDetail, setActivityDetail] = useState<ActivityEntry | null>(null);
  const [directiveDetail, setDirectiveDetail] = useState<RequestEntry | null>(null);
  const [expandedDirectiveId, setExpandedDirectiveId] = useState<number | null>(null);
  const [directiveActionStatus, setDirectiveActionStatus] = useState<string | null>(null);
  const [directiveActionError, setDirectiveActionError] = useState<string | null>(null);
  const [updatingDirectiveId, setUpdatingDirectiveId] = useState<number | null>(null);

  const refresh = useCallback(async (signal?: AbortSignal) => {
    // Debug logging removed to reduce request spam
    setLoading(true);
    try {
      const data = await fetchOperationsMetrics(signal);
      if (!mountedRef.current) return;
      setMetrics(data);
      setError(null);
    } catch (err) {
      if (!mountedRef.current) return;
      // Ignore abort errors
      if (err instanceof Error && err.name === 'AbortError') return;
      setError(err instanceof Error ? err.message : 'Unable to load operations telemetry');
    } finally {
      if (mountedRef.current) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    const handleRefresh = () => {
        void refresh();
    };
    window.addEventListener('refresh-operations', handleRefresh);
    return () => window.removeEventListener('refresh-operations', handleRefresh);
  }, [refresh]);

  useEffect(() => {
    mountedRef.current = true;
    const abortController = new AbortController();
    void refresh(abortController.signal);
    
    // Optimized: Poll every 15 seconds instead of 5 to reduce server load
    // Real-time updates should come via WebSocket when available
    const intervalId = setInterval(() => {
      if (mountedRef.current) {
        const intervalAbortController = new AbortController();
        void refresh(intervalAbortController.signal);
      }
    }, 15000); // Increased from 5000ms to 15000ms for better efficiency
    
    return () => {
      mountedRef.current = false;
      clearInterval(intervalId);
      abortController.abort(); // Cancel in-flight requests on unmount
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

  const handleDirectiveAction = useCallback(
    async (directive: RequestEntry, status: 'approved' | 'rejected' | 'completed') => {
      if (!directive.id) {
        setDirectiveActionError('Directive ID missing. Refresh metrics and try again.');
        return;
      }
      if (updatingDirectiveId === directive.id) return;
      setUpdatingDirectiveId(directive.id);
      setDirectiveActionStatus(null);
      setDirectiveActionError(null);
      try {
        await updateDirectiveStatus(directive.id, status);
        setDirectiveActionStatus(`Directive "${directive.title ?? 'Untitled'}" marked ${status}.`);
        await refresh();
      } catch (err) {
        setDirectiveActionError(err instanceof Error ? err.message : 'Failed to update directive');
      } finally {
        setUpdatingDirectiveId((current) => (current === directive.id ? null : current));
      }
    },
    [refresh, updatingDirectiveId],
  );

  return (
    <section className="operations-panel">
      <header className="panel-header">
        <div>
          <h3>💓 Operations Pulse</h3>
          <span className="operations-panel__subtitle">Real-time activity monitoring from automation scheduler and agent operations</span>
        </div>
        <div className="panel-header__actions">
          {workerStatus && <span className={`status-pill status-pill--${workerTone}`}>{workerLabel}</span>}
          <button type="button" className="refresh-button" onClick={() => void refresh()} disabled={loading}>
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </header>

      {error && <p className="panel-error">{error}</p>}

      <div className="operations-panel__info">
        <p className="text-sm text-indigo-200/80 mb-4 p-3 rounded-lg bg-indigo-900/20 border border-indigo-500/20">
          <strong>💡 How it works:</strong> Monitor real-time operations, pending workflows, and agent activity. 
          Click on "Pending workflows" to see detailed task information. 
          Use "Run Autonomous Cycle" to trigger a full agent execution cycle manually.
        </p>
      </div>

      <div className="operations-summary">
        <div
          className="operations-summary__item cursor-pointer hover:bg-slate-800/70 transition-colors"
          onClick={() => setModalOpen(true)}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              setModalOpen(true);
            }
          }}
        >
          <span>Pending workflows</span>
          <strong>{queue.pending}</strong>
          <span className="text-[10px] text-cyan-400/50 mt-1">Click to view details</span>
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

      <MetricDetailModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        metricType="workflows"
        title="Pending Workflows"
      />
      <DetailModal
        isOpen={Boolean(activityDetail)}
        onClose={() => setActivityDetail(null)}
        title="Automation Detail"
        subtitle={activityDetail?.summary ?? 'Recent automation entry'}
      >
        <div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-xs text-slate-200">
            <div>
              <span className="text-slate-400">Agent</span>
              <div className="text-white">{activityDetail?.agent ?? 'Automation'}</div>
            </div>
            <div>
              <span className="text-slate-400">Stage</span>
              <div className="text-white">{activityDetail?.stage ?? activityDetail?.status ?? 'N/A'}</div>
            </div>
            <div>
              <span className="text-slate-400">Timestamp</span>
              <div className="text-white">{formatTimestamp(activityDetail?.timestamp)}</div>
            </div>
            {activityDetail?.pipeline_id && (
              <div>
                <span className="text-slate-400">Pipeline</span>
                <div className="text-white">{activityDetail.pipeline_id}</div>
              </div>
            )}
            {activityDetail?.task_id && (
              <div>
                <span className="text-slate-400">Task</span>
                <div className="text-white">{activityDetail.task_id}</div>
              </div>
            )}
            {activityDetail?.priority && (
              <div>
                <span className="text-slate-400">Priority</span>
                <div className="text-white">{activityDetail.priority}</div>
              </div>
            )}
          </div>
          <div>
            <h4 className="text-sm text-cyan-300 font-semibold mb-2">Raw telemetry</h4>
            {renderObjectDetails(activityDetail)}
          </div>
        </div>
      </DetailModal>
      <DetailModal
        isOpen={Boolean(directiveDetail)}
        onClose={() => setDirectiveDetail(null)}
        title="Directive Detail"
        subtitle={directiveDetail?.title ?? 'Delegated directive'}
      >
        <div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-xs text-slate-200">
            <div>
              <span className="text-slate-400">Status</span>
              <div className="text-white">{directiveDetail?.status ?? 'pending'}</div>
            </div>
            <div>
              <span className="text-slate-400">Owner</span>
              <div className="text-white">{directiveDetail?.agent ?? 'N/A'}</div>
            </div>
            <div>
              <span className="text-slate-400">Priority</span>
              <div className="text-white">{directiveDetail?.priority ?? 'normal'}</div>
            </div>
            {directiveDetail?.directive_type && (
              <div>
                <span className="text-slate-400">Type</span>
                <div className="text-white">{directiveDetail.directive_type}</div>
              </div>
            )}
            {directiveDetail?.pipeline_id && (
              <div>
                <span className="text-slate-400">Pipeline</span>
                <div className="text-white">{directiveDetail.pipeline_id}</div>
              </div>
            )}
            {directiveDetail?.due_date && (
              <div>
                <span className="text-slate-400">Due</span>
                <div className="text-white">{formatTimestamp(directiveDetail.due_date)}</div>
              </div>
            )}
            {directiveDetail?.confidence !== undefined && directiveDetail?.confidence !== null && (
              <div>
                <span className="text-slate-400">Confidence</span>
                <div className="text-white">{directiveDetail.confidence}</div>
              </div>
            )}
          </div>
          {directiveDetail?.description && (
            <div className="text-sm text-slate-200">
              <span className="text-slate-400">Notes</span>
              <div className="mt-1">{directiveDetail.description}</div>
            </div>
          )}
          <div>
            <h4 className="text-sm text-cyan-300 font-semibold mb-2">Full directive payload</h4>
            {renderObjectDetails(directiveDetail)}
          </div>
        </div>
      </DetailModal>

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
        {activityList.map((entry, index) => (
          <article
            key={`activity-${entry.timestamp}-${entry.pipeline_id ?? entry.agent ?? index}-${entry.agent ?? 'unknown'}`}
            className="activity-card cursor-pointer hover:border-cyan-500/40 transition-colors"
            onClick={() => setActivityDetail(entry)}
            role="button"
            tabIndex={0}
            onKeyDown={(event) => {
              if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                setActivityDetail(entry);
              }
            }}
          >
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
          {directiveActionError && <p className="panel-error">{directiveActionError}</p>}
          {directiveActionStatus && <p className="panel-success">{directiveActionStatus}</p>}
          {requestList.length === 0 && !loading && <p className="panel-empty">No directives queued.</p>}
          {requestList.length === 0 && loading && <p className="panel-empty">Loading directives...</p>}
          {requestList.length > 0 && (
            <ul>
              {requestList.map((item, index) => {
                const statusLabel = item.status ?? 'pending';
                const isPending = statusLabel === 'pending';
                const showDetails = isPending || expandedDirectiveId === item.id;
                return (
                <li key={`request-${item.timestamp}-${item.title ?? 'directive'}-${index}`}>
                  <div className="directive-summary">
                    <button
                      type="button"
                      className="directive-toggle"
                      onClick={() =>
                        setExpandedDirectiveId((current) => (current === item.id ? null : item.id ?? null))
                      }
                      disabled={!item.id}
                    >
                      <span>{item.title ?? 'Directive'}</span>
                      <span className="directive-status">{statusLabel}</span>
                    </button>
                    <div className="directive-meta">
                      <span>{item.priority ?? 'normal'}</span>
                      <time>{formatTimestamp(item.timestamp)}</time>
                    </div>
                  </div>
                  <div className="directive-actions">
                    <button
                      type="button"
                      className="refresh-button"
                      onClick={() => void handleDirectiveAction(item, 'approved')}
                      disabled={updatingDirectiveId === item.id || item.status === 'approved'}
                    >
                      Approve
                    </button>
                    <button
                      type="button"
                      className="refresh-button"
                      onClick={() => void handleDirectiveAction(item, 'rejected')}
                      disabled={updatingDirectiveId === item.id || item.status === 'rejected'}
                    >
                      Reject
                    </button>
                    <button
                      type="button"
                      className="primary-button"
                      onClick={() => void handleDirectiveAction(item, 'completed')}
                      disabled={updatingDirectiveId === item.id || item.status === 'completed'}
                    >
                      Mark Done
                    </button>
                    <button
                      type="button"
                      className="refresh-button"
                      onClick={() => setDirectiveDetail(item)}
                    >
                      View full details
                    </button>
                  </div>
                  {showDetails && (
                    <div className="directive-details">
                      <div className="directive-detail-grid">
                        <div>
                          <strong>Status:</strong> {statusLabel}
                        </div>
                        {item.directive_type && (
                          <div>
                            <strong>Type:</strong> {item.directive_type}
                          </div>
                        )}
                        {item.agent && (
                          <div>
                            <strong>Owner:</strong> {item.agent}
                          </div>
                        )}
                        {item.pipeline_id && (
                          <div>
                            <strong>Pipeline:</strong> {item.pipeline_id}
                          </div>
                        )}
                        {item.due_date && (
                          <div>
                            <strong>Due:</strong> {formatTimestamp(item.due_date)}
                          </div>
                        )}
                        {item.confidence !== undefined && item.confidence !== null && (
                          <div>
                            <strong>Confidence:</strong> {item.confidence}
                          </div>
                        )}
                      </div>
                      {item.directive_type && (
                        <div>
                          <strong>Type:</strong> {item.directive_type}
                        </div>
                      )}
                      {item.description && (
                        <div>
                          <strong>Notes:</strong> {item.description}
                        </div>
                      )}
                      {!item.description && !item.payload && (
                        <div>
                          <strong>Notes:</strong> No additional details provided yet.
                        </div>
                      )}
                      {item.payload && (
                        <div className="directive-payload">
                          <strong>Payload:</strong>
                          <pre>{JSON.stringify(item.payload, null, 2)}</pre>
                        </div>
                      )}
                    </div>
                  )}
                </li>
              );
              })}
            </ul>
          )}
        </div>
      )}
    </section>
  );
};

const formatPayload = (payload: unknown): React.ReactNode => {
  if (!payload) return <span className="text-slate-500 italic">No details available</span>;

  let data = payload;
  
  // Handle double-encoded JSON strings (common issue)
  if (typeof payload === 'string') {
    try {
      data = JSON.parse(payload);
    } catch {
      // Keep as string if parse fails
    }
  }

  // If it's an object, try to clean up nested stringified fields
  if (typeof data === 'object' && data !== null) {
    const cleanData: Record<string, unknown> = {};
    Object.entries(data as Record<string, unknown>).forEach(([key, value]) => {
      if (typeof value === 'string' && (value.startsWith('{') || value.startsWith('['))) {
        try {
          cleanData[key] = JSON.parse(value);
        } catch {
          cleanData[key] = value;
        }
      } else {
        cleanData[key] = value;
      }
    });
    data = cleanData;
  }

  // Render human-readable view
  if (typeof data === 'object' && data !== null) {
    return (
      <div className="space-y-2">
        {Object.entries(data as Record<string, unknown>).map(([key, value]) => {
          // Skip internal/technical keys if needed, or format them nicely
          const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
          
          let displayValue: React.ReactNode = String(value);
          
          if (typeof value === 'object' && value !== null) {
             displayValue = (
               <pre className="text-[10px] text-cyan-200/70 mt-1 bg-black/20 p-1 rounded overflow-x-auto">
                 {JSON.stringify(value, null, 2)}
               </pre>
             );
          } else if (typeof value === 'string' && value.length > 100) {
             displayValue = <div className="text-slate-300 text-xs whitespace-pre-wrap">{value}</div>;
          } else {
             displayValue = <span className="text-slate-200 font-medium">{String(value)}</span>;
          }

          return (
            <div key={key} className="bg-white/5 p-2 rounded border border-white/5">
              <div className="text-[10px] text-slate-400 uppercase tracking-wider mb-1">{label}</div>
              {displayValue}
            </div>
          );
        })}
      </div>
    );
  }

  return <div className="text-slate-300">{String(data)}</div>;
};

const renderObjectDetails = (value: unknown) => (
  <div className="text-xs bg-black/40 border border-cyan-500/20 rounded-lg p-4 overflow-x-auto text-cyan-100 max-h-60 custom-scrollbar">
    {formatPayload(value)}
  </div>
);
