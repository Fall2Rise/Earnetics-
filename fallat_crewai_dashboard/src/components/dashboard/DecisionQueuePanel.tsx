import React, { useCallback, useEffect, useState, useRef, useMemo } from 'react';
import {
  fetchDecisions,
  approveDecision,
  denyDecision,
  getDecision,
  DecisionQueueItem,
} from '../../api/headOfficeApi';
import { dedupeRequest } from '../../utils/apiHelpers';

export const DecisionQueuePanel: React.FC = React.memo(() => {
  const [decisions, setDecisions] = useState<DecisionQueueItem[]>([]);
  const [selectedDecision, setSelectedDecision] = useState<DecisionQueueItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('pending');
  const [processingIds, setProcessingIds] = useState<Set<string>>(new Set());
  const mountedRef = useRef(true);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const loadDecisions = useCallback(async () => {
    if (!mountedRef.current) return;
    
    try {
      setLoading(true);
      setError(null);
      
      // Use deduplication to prevent duplicate requests
      const cacheKey = `decisions-${statusFilter}`;
      const data = await dedupeRequest(cacheKey, () =>
        fetchDecisions(statusFilter === 'all' ? undefined : statusFilter)
      );
      
      if (mountedRef.current) {
        setDecisions(data);
      }
    } catch (err) {
      if (mountedRef.current) {
        setError(err instanceof Error ? err.message : 'Failed to load decisions');
      }
    } finally {
      if (mountedRef.current) {
        setLoading(false);
      }
    }
  }, [statusFilter]);

  useEffect(() => {
    mountedRef.current = true;
    void loadDecisions();
    
    // Optimized polling - pause when tab is hidden
    const startInterval = () => {
      if (intervalRef.current) return;
      intervalRef.current = setInterval(() => {
        if (!document.hidden && mountedRef.current) {
          void loadDecisions();
        }
      }, 15000); // Refresh every 15 seconds
    };

    const stopInterval = () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };

    const handleVisibilityChange = () => {
      if (document.hidden) {
        stopInterval();
      } else {
        startInterval();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    startInterval();

    return () => {
      mountedRef.current = false;
      stopInterval();
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [loadDecisions]);

  // Optimistic update helper
  const updateDecisionOptimistically = useCallback((id: string, updates: Partial<DecisionQueueItem>) => {
    setDecisions(prev => prev.map(d => d.id === id ? { ...d, ...updates } : d));
    if (selectedDecision?.id === id) {
      setSelectedDecision(prev => prev ? { ...prev, ...updates } : null);
    }
  }, [selectedDecision]);

  const handleApprove = useCallback(async (id: string) => {
    // Optimistic update
    const originalDecision = decisions.find(d => d.id === id);
    if (originalDecision) {
      updateDecisionOptimistically(id, { status: 'approved' });
      setProcessingIds(prev => new Set(prev).add(id));
    }

    try {
      const updated = await approveDecision(id);
      // Update with server response
      setDecisions(prev => prev.map(d => d.id === id ? updated : d));
      if (selectedDecision?.id === id) {
        setSelectedDecision(updated);
      }
      // Reload to get latest list
      void loadDecisions();
    } catch (err) {
      // Revert on error
      if (originalDecision) {
        updateDecisionOptimistically(id, { status: originalDecision.status });
      }
      setError(err instanceof Error ? err.message : 'Failed to approve decision');
    } finally {
      setProcessingIds(prev => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    }
  }, [decisions, selectedDecision, loadDecisions, updateDecisionOptimistically]);

  const handleDeny = useCallback(async (id: string, reason?: string) => {
    // Optimistic update
    const originalDecision = decisions.find(d => d.id === id);
    if (originalDecision) {
      updateDecisionOptimistically(id, { status: 'denied' });
      setProcessingIds(prev => new Set(prev).add(id));
    }

    try {
      const updated = await denyDecision(id, reason);
      // Update with server response
      setDecisions(prev => prev.map(d => d.id === id ? updated : d));
      if (selectedDecision?.id === id) {
        setSelectedDecision(updated);
      }
      // Reload to get latest list
      void loadDecisions();
    } catch (err) {
      // Revert on error
      if (originalDecision) {
        updateDecisionOptimistically(id, { status: originalDecision.status });
      }
      setError(err instanceof Error ? err.message : 'Failed to deny decision');
    } finally {
      setProcessingIds(prev => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    }
  }, [decisions, selectedDecision, loadDecisions, updateDecisionOptimistically]);

  const handleSelectDecision = async (id: string) => {
    try {
      const decision = await getDecision(id);
      setSelectedDecision(decision);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load decision details');
    }
  };

  if (loading && decisions.length === 0) {
    return (
      <div className="command-panel">
        <div className="panel-header">
          <h2>Decision Queue</h2>
        </div>
        <div className="panel-content">Loading...</div>
      </div>
    );
  }

  return (
    <div className="command-panel command-panel--full">
      <div className="panel-header">
        <h2>Decision Queue</h2>
        <div className="panel-controls">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="select-input"
          >
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="denied">Denied</option>
            <option value="all">All</option>
          </select>
          <button onClick={loadDecisions} className="btn-secondary" disabled={loading}>
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>
      {error && <div className="panel-error">{error}</div>}
      <div className="panel-content panel-content--split">
        <div className="decision-list">
          <h3>Decisions ({decisions.length})</h3>
          {decisions.length === 0 ? (
            <p className="empty-state">No decisions found</p>
          ) : (
            <ul className="decision-items">
              {decisions.map((decision) => (
                <li
                  key={decision.id}
                  className={`decision-item ${selectedDecision?.id === decision.id ? 'selected' : ''} status-${decision.status}`}
                  onClick={() => handleSelectDecision(decision.id)}
                >
                  <div className="decision-item-header">
                    <strong>{decision.title}</strong>
                    <span className={`status-badge status-${decision.status}`}>
                      {decision.status}
                    </span>
                  </div>
                  <div className="decision-item-meta">
                    <span className="category">{decision.category}</span>
                    <span className="required-by">Required by: {decision.required_by}</span>
                  </div>
                  {decision.cost !== undefined && (
                    <div className="decision-item-cost">Cost: ${decision.cost.toFixed(2)}</div>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>

        {selectedDecision && (
          <div className="decision-details">
            <h3>{selectedDecision.title}</h3>
            <div className="detail-section">
              <h4>Recommendation</h4>
              <p>{selectedDecision.recommendation}</p>
            </div>
            <div className="detail-section">
              <h4>Upside</h4>
              <p>{selectedDecision.upside}</p>
            </div>
            <div className="detail-section">
              <h4>Risk</h4>
              <p>{selectedDecision.risk}</p>
            </div>
            <div className="detail-section">
              <h4>Reversibility</h4>
              <p>{selectedDecision.reversibility}</p>
            </div>
            {selectedDecision.alternatives.length > 0 && (
              <div className="detail-section">
                <h4>Alternatives</h4>
                <ul>
                  {selectedDecision.alternatives.map((alt, idx) => (
                    <li key={idx}>{alt}</li>
                  ))}
                </ul>
              </div>
            )}
            {selectedDecision.status === 'pending' && (
              <div className="decision-actions">
                <button
                  onClick={() => handleApprove(selectedDecision.id)}
                  className="btn-primary"
                  disabled={processingIds.has(selectedDecision.id)}
                >
                  {processingIds.has(selectedDecision.id) ? 'Processing...' : 'Approve'}
                </button>
                <button
                  onClick={() => handleDeny(selectedDecision.id)}
                  className="btn-danger"
                  disabled={processingIds.has(selectedDecision.id)}
                >
                  {processingIds.has(selectedDecision.id) ? 'Processing...' : 'Deny'}
                </button>
              </div>
            )}
            <div className="detail-meta">
              <p>Status: <strong>{selectedDecision.status}</strong></p>
              <p>Created: {new Date(selectedDecision.created_at).toLocaleString()}</p>
              <p>Updated: {new Date(selectedDecision.updated_at).toLocaleString()}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
});

DecisionQueuePanel.displayName = 'DecisionQueuePanel';
