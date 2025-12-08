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

  const loadApprovals = useCallback(async () => {
    setLoading(true);
    try {
      const data = await listApprovals(filter.status || undefined, limit);
      const filtered = filter.handler ? data.filter((item) => item.handler === filter.handler) : data;
      setApprovals(filtered);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load approvals');
    } finally {
      setLoading(false);
    }
  }, [filter.status, filter.handler, limit]);

  useEffect(() => {
    void loadApprovals();
  }, [loadApprovals]);

  const handleStatusChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setFilter((prev) => ({ ...prev, status: event.target.value }));
  };

  const handleHandlerChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setFilter((prev) => ({ ...prev, handler: event.target.value }));
  };

  const handleLimitChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setLimit(Number(event.target.value));
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
    <div className="approval-center glass-panel">
      <header className="panel-header">
        <div>
          <h3>Approval Queue</h3>
          <span>Review and approve high-impact actions</span>
        </div>
        <div className="panel-header__actions">
          <button type="button" className="refresh-button" onClick={() => void loadApprovals()} disabled={loading}>
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </header>

      {error && <p className="panel-error">{error}</p>}

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
                  <h4>{request.handler}</h4>
                  <span>ID: {request.id}</span>
                  <span>Job: {request.job_id}</span>
                </div>
                <div className="approval-card__meta">
                  <span>{new Date(request.created_at).toLocaleString()}</span>
                  <span className={`badge badge--${request.status === 'error' ? 'error' : 'ok'}`}>{request.status}</span>
                </div>
              </header>
              <pre>{JSON.stringify(request.payload, null, 2)}</pre>
              {request.message && <p className="approval-card__message">{request.message}</p>}
              <footer>
                <div>
                  {request.decided_at && <span>Decided: {new Date(request.decided_at).toLocaleString()}</span>}
                  {request.decision && <span>Decision: {request.decision}</span>}
                </div>
                {request.status === 'pending' && (
                  <div className="approval-card__actions">
                    <button type="button" className="primary-button" onClick={() => void handleApprove(request.id)} disabled={actionLoading}>
                      Approve
                    </button>
                    <button type="button" className="refresh-button" onClick={() => void handleReject(request.id)} disabled={actionLoading}>
                      Reject
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
