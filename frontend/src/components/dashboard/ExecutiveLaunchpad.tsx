import React, { useCallback, useEffect, useState } from 'react';
import { fetchOwnerBrief, fetchTodayBoard } from '../../api/headOfficeApi';

interface OwnerBrief {
  daily_summary?: string;
  weekly_summary?: string;
  key_metrics?: Record<string, unknown>;
  pending_decisions?: number;
  deadlines?: Array<{ title: string; date: string }>;
}

interface TodayBoard {
  deadlines?: Array<{ title: string; date: string; status: string }>;
  approvals?: Array<{ id: string; title: string; category: string }>;
  money_events?: Array<{ type: string; amount: number; date: string }>;
  risks?: Array<{ severity: string; message: string }>;
  blocked_items?: Array<{ reason: string; item: string }>;
}

export const ExecutiveLaunchpad: React.FC = () => {
  const [brief, setBrief] = useState<OwnerBrief | null>(null);
  const [todayBoard, setTodayBoard] = useState<TodayBoard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [briefData, boardData] = await Promise.all([
        fetchOwnerBrief(),
        fetchTodayBoard(),
      ]);
      setBrief(briefData);
      setTodayBoard(boardData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load executive data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
    const interval = setInterval(refresh, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [refresh]);

  if (loading && !brief) {
    return (
      <div className="command-panel">
        <div className="panel-header">
          <h2>Executive Launchpad</h2>
        </div>
        <div className="panel-content">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="command-panel">
        <div className="panel-header">
          <h2>Executive Launchpad</h2>
          <button onClick={refresh} className="btn-secondary">Retry</button>
        </div>
        <div className="panel-content error">{error}</div>
      </div>
    );
  }

  return (
    <div className="command-panel">
      <div className="panel-header">
        <h2>Executive Launchpad</h2>
        <button onClick={refresh} className="btn-secondary" disabled={loading}>
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>
      <div className="panel-content">
        {/* Owner Brief */}
        {brief && (
          <div className="brief-section">
            <h3>Owner Brief</h3>
            {brief.daily_summary && (
              <div className="brief-item">
                <strong>Today:</strong>
                <p>{brief.daily_summary}</p>
              </div>
            )}
            {brief.weekly_summary && (
              <div className="brief-item">
                <strong>This Week:</strong>
                <p>{brief.weekly_summary}</p>
              </div>
            )}
            {brief.pending_decisions !== undefined && (
              <div className="brief-item">
                <strong>Pending Decisions:</strong> {brief.pending_decisions}
              </div>
            )}
          </div>
        )}

        {/* Today Board */}
        {todayBoard && (
          <div className="today-board">
            <h3>Today's Board</h3>
            
            {todayBoard.deadlines && todayBoard.deadlines.length > 0 && (
              <div className="board-section">
                <h4>Deadlines</h4>
                <ul>
                  {todayBoard.deadlines.map((deadline, idx) => (
                    <li key={idx} className={deadline.status === 'overdue' ? 'overdue' : ''}>
                      <strong>{deadline.title}</strong> - {deadline.date}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {todayBoard.approvals && todayBoard.approvals.length > 0 && (
              <div className="board-section">
                <h4>Pending Approvals</h4>
                <ul>
                  {todayBoard.approvals.map((approval) => (
                    <li key={approval.id}>
                      <strong>{approval.title}</strong> ({approval.category})
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {todayBoard.risks && todayBoard.risks.length > 0 && (
              <div className="board-section">
                <h4>Risks</h4>
                <ul>
                  {todayBoard.risks.map((risk, idx) => (
                    <li key={idx} className={`risk-${risk.severity}`}>
                      {risk.message}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {todayBoard.blocked_items && todayBoard.blocked_items.length > 0 && (
              <div className="board-section">
                <h4>Blocked Items</h4>
                <ul>
                  {todayBoard.blocked_items.map((item, idx) => (
                    <li key={idx}>
                      <strong>{item.item}</strong>: {item.reason}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Global Search Hint */}
        <div className="search-hint">
          <p>💡 Press <kbd>Ctrl+K</kbd> for global search and command palette</p>
        </div>
      </div>
    </div>
  );
};
