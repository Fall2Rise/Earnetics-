import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { ApprovalRequest, approveRequest, listApprovals, rejectRequest } from '../../api/approvalApi';

type FilterState = {
  status: string;
  handler: string;
};

const DEFAULT_FILTER: FilterState = {
  status: 'pending',
  handler: '',
};

export const ApprovalCenter: React.FC = () => {
  const [approvals, setApprovals] = useState<ApprovalRequest[]>([]);
  const [filter, setFilter] = useState<FilterState>(DEFAULT_FILTER);
  const [limit, setLimit] = useState(50);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [note, setNote] = useState('');

  const handlers = useMemo(() => {
    const unique = new Set<string>();
    approvals.forEach((item) => unique.add(item.handler));
    return Array.from(unique);
  }, [approvals]);

  const loadApprovals = useCallback(async (abortSignal?: AbortSignal) => {
    setLoading(true);
    try {
      const data = await listApprovals(filter.status || undefined, limit, abortSignal);
      if (abortSignal?.aborted) return; // Don't update state if request was cancelled
      const filtered = filter.handler ? data.filter((item) => item.handler === filter.handler) : data;
      setApprovals(filtered);
      setError(null);
    } catch (err) {
      if (abortSignal?.aborted) return; // Ignore errors from cancelled requests
      setError(err instanceof Error ? err.message : 'Failed to load approvals');
    } finally {
      if (!abortSignal?.aborted) {
        setLoading(false);
      }
    }
  }, [filter.status, filter.handler, limit]);

  // Debounce filter changes to avoid excessive API calls
  useEffect(() => {
    const abortController = new AbortController();
    const timeoutId = setTimeout(() => {
      void loadApprovals(abortController.signal);
    }, 300); // 300ms debounce for filter changes
    
    return () => {
      clearTimeout(timeoutId);
      abortController.abort(); // Cancel in-flight requests
    };
  }, [loadApprovals]);

  const handleStatusChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setFilter((prev) => ({ ...prev, status: event.target.value }));
  };

  const handleHandlerChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setFilter((prev) => ({ ...prev, handler: event.target.value }));
  };

  const handleLimitChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setLimit(Number.parseInt(event.target.value, 10));
  };

  const handleApprove = async (requestId: number) => {
    setActionLoading(true);
    try {
      await approveRequest(requestId, note || undefined);
      setNote('');
      await loadApprovals();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to approve request');
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async (requestId: number) => {
    setActionLoading(true);
    try {
      await rejectRequest(requestId, note || undefined);
      setNote('');
      await loadApprovals();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reject request');
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="approval-center">
      <header className="panel-header">
        <div>
          <h3>✅ Approval Queue</h3>
          <span className="approval-center__subtitle">Review and approve high-impact actions that require human oversight</span>
        </div>
        <div className="panel-header__actions">
          <button type="button" className="refresh-button" onClick={() => void loadApprovals()} disabled={loading}>
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </header>

      {error && <p className="panel-error">{error}</p>}

      <div className="approval-center__info">
        <p className="text-sm text-indigo-200/80 mb-4 p-3 rounded-lg bg-indigo-900/20 border border-indigo-500/20">
          <strong>💡 How it works:</strong> Agents request approval for high-impact actions (large payments, major changes, etc.). 
          Review the details, expected impact, and context before approving or rejecting. 
          Your decisions help agents learn and improve their decision-making.
        </p>
      </div>

      <div className="approval-filters">
        <label>
          Status
          <select value={filter.status} onChange={handleStatusChange}>
            <option value="pending">Pending</option>
            <option value="">All</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
        </label>
        <label>
          Handler
          <select value={filter.handler} onChange={handleHandlerChange}>
            <option value="">All</option>
            {handlers.map((handler) => (
              <option key={handler} value={handler}>
                {handler}
              </option>
            ))}
          </select>
        </label>
        <label>
          Limit
          <select value={limit} onChange={handleLimitChange}>
            {[25, 50, 100, 250].map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </label>
        <label className="approval-note">
          Decision Note
          <input value={note} onChange={(event) => setNote(event.target.value)} placeholder="optional note" />
        </label>
      </div>

      <div className="approval-list">
        {approvals.length === 0 ? (
          <p className="panel-empty">No approval requests found.</p>
        ) : (
          approvals.map((request) => (
            <article key={request.id} className={`approval-card approval-card--${request.status}`}>
              <header>
                <div>
                  <h4>{request.description || request.handler}</h4>
                  <div className="approval-card__meta-info">
                    <span>Handler: {request.handler}</span>
                    <span>ID: {request.id}</span>
                    <span>Job: {request.job_id}</span>
                  </div>
                </div>
                <div className="approval-card__meta">
                  <span>{new Date(request.created_at).toLocaleString()}</span>
                  <span className={`badge badge--${request.status === 'error' ? 'error' : 'ok'}`}>{request.status}</span>
                </div>
              </header>
              
              {/* Description Section */}
              <section className="approval-card__description">
                {request.description && (
                  <div className="approval-card__field">
                    <strong>📋 What needs approval:</strong>
                    <p>{request.description}</p>
                  </div>
                )}
                
                {request.context && (
                  <div className="approval-card__field">
                    <strong>ℹ️ Context:</strong>
                    <p>{request.context}</p>
                  </div>
                )}
                
                {request.impact && (
                  <div className="approval-card__field">
                    <strong>⚡ Expected Impact:</strong>
                    <p>{request.impact}</p>
                  </div>
                )}
              </section>
              
              {/* Payload Details (collapsible) */}
              <details className="approval-card__payload">
                <summary>📦 Technical Details (Click to expand)</summary>
                <pre>{JSON.stringify(request.payload, null, 2)}</pre>
              </details>
              
              {request.message && <p className="approval-card__message">{request.message}</p>}
              <footer>
                <div>
                  {request.decided_at && <span>Decided: {new Date(request.decided_at).toLocaleString()}</span>}
                  {request.decision && <span>Decision: {request.decision}</span>}
                </div>
                {request.status === 'pending' && (
                  <div className="approval-card__actions">
                    <button type="button" className="primary-button" onClick={() => void handleApprove(request.id)} disabled={actionLoading}>
                      ✅ Approve
                    </button>
                    <button type="button" className="refresh-button" onClick={() => void handleReject(request.id)} disabled={actionLoading}>
                      ❌ Reject
                    </button>
                  </div>
                )}
              </footer>
            </article>
          ))
        )}
      </div>
    </div>
  );
};
