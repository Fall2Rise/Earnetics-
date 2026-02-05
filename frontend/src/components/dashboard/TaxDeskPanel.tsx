import React, { useCallback, useEffect, useState } from 'react';
import { fetchTaxTasks, fetchTaxCalendar, TaxTask } from '../../api/headOfficeApi';

export const TaxDeskPanel: React.FC = () => {
  const [tasks, setTasks] = useState<TaxTask[]>([]);
  const [calendar, setCalendar] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [tasksData, calendarData] = await Promise.all([
        fetchTaxTasks(),
        fetchTaxCalendar(),
      ]);
      setTasks(tasksData);
      setCalendar(calendarData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load tax data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
    const interval = setInterval(loadData, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, [loadData]);

  if (loading && tasks.length === 0) {
    return (
      <div className="command-panel">
        <div className="panel-header">
          <h2>Tax Desk</h2>
        </div>
        <div className="panel-content">Loading...</div>
      </div>
    );
  }

  return (
    <div className="command-panel command-panel--full">
      <div className="panel-header">
        <h2>Tax Desk</h2>
        <button onClick={loadData} className="btn-secondary" disabled={loading}>
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>
      {error && <div className="panel-error">{error}</div>}
      <div className="panel-content">
        <div className="tax-tasks">
          <h3>Tax Tasks ({tasks.length})</h3>
          {tasks.length === 0 ? (
            <p className="empty-state">No tax tasks found</p>
          ) : (
            <div className="task-list">
              {tasks.map((task) => (
                <div key={task.id} className={`task-item status-${task.status}`}>
                  <div className="task-header">
                    <strong>{task.title}</strong>
                    <span className={`status-badge status-${task.status}`}>
                      {task.status}
                    </span>
                  </div>
                  {task.description && <p>{task.description}</p>}
                  <div className="task-meta">
                    <span>Jurisdiction: {task.jurisdiction}</span>
                    <span>Type: {task.filing_type}</span>
                    <span>Deadline: {task.deadline}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {calendar && (
          <div className="tax-calendar">
            <h3>Tax Calendar</h3>
            <pre>{JSON.stringify(calendar, null, 2)}</pre>
          </div>
        )}
      </div>
    </div>
  );
};
