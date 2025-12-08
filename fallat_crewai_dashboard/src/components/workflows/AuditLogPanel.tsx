import React, { useCallback, useEffect, useState } from 'react';
import { AuditEvent, fetchAuditEvents } from '../../api/auditApi';

const DEFAULT_LIMIT = 50;

export const AuditLogPanel: React.FC = () => {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [limit, setLimit] = useState(DEFAULT_LIMIT);
  const [status, setStatus] = useState<string>('');
  const [actionFilter, setActionFilter] = useState<string>('');

  const loadEvents = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchAuditEvents({
        limit,
        status: status || undefined,
        action: actionFilter || undefined,
      });
      setEvents(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load audit events');
    } finally {
      setLoading(false);
    }
  }, [limit, status, actionFilter]);

  useEffect(() => {
    void loadEvents();
  }, [loadEvents]);

  return (
    <div className="audit-panel glass-panel">
      <header className="panel-header">
        <div>
          <h3>Audit Trail</h3>
          <span>Monitor high-impact actions and credentials usage</span>
        </div>
        <div className="panel-header__actions">
          <button type="button" className="refresh-button" onClick={() => void loadEvents()} disabled={loading}>
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </header>

      {error && <p className="panel-error">{error}</p>}

      <div className="audit-filters">
        <label>
          Limit
          <select value={limit} onChange={(event) => setLimit(Number(event.target.value))}>
            {[25, 50, 100, 250].map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </label>
        <label>
          Status
          <select value={status} onChange={(event) => setStatus(event.target.value)}>
            <option value="">All</option>
            <option value="success">Success</option>
            <option value="error">Error</option>
          </select>
        </label>
        <label>
          Action Contains
          <input value={actionFilter} onChange={(event) => setActionFilter(event.target.value)} placeholder="e.g. credentials" />
        </label>
      </div>

      <div className="audit-table">
        {events.length === 0 ? (
          <p className="panel-empty">No audit events found for the current filters.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Action</th>
                <th>Status</th>
                <th>Agent / User</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {events.map((event) => (
                <tr key={`${event.timestamp}-${event.action}-${event.status}`}>
                  <td>{new Date(event.timestamp).toLocaleString()}</td>
                  <td>{event.action}</td>
                  <td>
                    <span className={`badge badge--${event.status === 'error' ? 'error' : 'ok'}`}>{event.status}</span>
                  </td>
                  <td>
                    {event.agent || event.user ? (
                      <>
                        {event.agent && <span>Agent: {event.agent}</span>}
                        {event.user && <span>User: {event.user}</span>}
                      </>
                    ) : (
                      <span className="muted">—</span>
                    )}
                  </td>
                  <td className="audit-details">
                    {event.message && <p>{event.message}</p>}
                    {event.details && Object.keys(event.details).length > 0 && (
                      <pre>{JSON.stringify(event.details, null, 2)}</pre>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
