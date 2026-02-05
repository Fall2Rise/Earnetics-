import React from 'react';
import { fetchPendingWorkflows, WorkflowTask } from '../../api/workflowsApi';

export const WorkflowMonitorPanel: React.FC = () => {
  const [workflows, setWorkflows] = React.useState<WorkflowTask[]>([]);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    let mounted = true;
    const controller = new AbortController();

    const load = async () => {
      try {
        const response = await fetchPendingWorkflows(controller.signal);
        if (!mounted) return;
        setWorkflows(response.workflows || []);
        setError(null);
      } catch (err) {
        if (!mounted) return;
        setWorkflows([]);
        setError(err instanceof Error ? err.message : 'Failed to load workflows');
      }
    };

    void load();
    const interval = setInterval(load, 15000);

    return () => {
      mounted = false;
      controller.abort();
      clearInterval(interval);
    };
  }, []);

  return (
    <div className="glass-panel p-6">
      <header className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-xl text-white">Workflow Monitor</h3>
          <p className="text-sm text-slate-300">Pending queue, priority, and owner context.</p>
        </div>
        <span className="text-xs text-cyan-300 uppercase tracking-[0.2em]">
          {workflows.length} pending
        </span>
      </header>

      {error ? (
        <p className="mt-4 text-sm text-red-300">{error}</p>
      ) : workflows.length === 0 ? (
        <p className="mt-4 text-sm text-slate-300">No pending workflows.</p>
      ) : (
        <div className="mt-6 space-y-3">
          {workflows.map((task) => (
            <div
              key={task.id}
              className="rounded-2xl border border-white/10 bg-white/5 p-4"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h4 className="text-base text-white">{task.title}</h4>
                  <p className="text-xs text-slate-400">{task.department}</p>
                </div>
                <span className="text-xs uppercase text-amber-300">{task.priority}</span>
              </div>
              {task.description && (
                <p className="mt-2 text-sm text-slate-200">{task.description}</p>
              )}
              <div className="mt-3 flex flex-wrap gap-3 text-xs text-slate-400">
                <span>Status: {task.status}</span>
                {task.assigned_agent && <span>Agent: {task.assigned_agent}</span>}
                <span>Created: {new Date(task.created_at).toLocaleString()}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
