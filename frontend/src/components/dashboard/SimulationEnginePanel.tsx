import React from 'react';
import { fetchPendingWorkflows, WorkflowTask } from '../../api/workflowsApi';
import { logAuditReason } from '../../api/auditApi';

export const SimulationEnginePanel: React.FC = () => {
  const [workflows, setWorkflows] = React.useState<WorkflowTask[]>([]);
  const [error, setError] = React.useState<string | null>(null);
  const [reason, setReason] = React.useState('');
  const [selected, setSelected] = React.useState<string>('');
  const [saving, setSaving] = React.useState(false);

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
        setError(err instanceof Error ? err.message : 'Failed to load workflows');
      }
    };

    void load();
    return () => {
      mounted = false;
      controller.abort();
    };
  }, []);

  const logSimulationIntent = async () => {
    if (!selected || !reason) return;
    setSaving(true);
    try {
      await logAuditReason({
        action: 'simulation_request',
        reason,
        directive_ref: 'decision_framework',
        risk_level: 'YELLOW',
        context: { workflow_id: selected },
        owner_approved: true,
      });
      setReason('');
      setSelected('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to log simulation intent');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="glass-panel p-6">
      <header className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-xl text-white">Simulation Engine</h3>
          <p className="text-sm text-slate-300">Queue items staged for pre‑execution review.</p>
        </div>
      </header>

      {error && <p className="mt-4 text-sm text-red-300">{error}</p>}

      <div className="mt-6 space-y-3">
        {workflows.length === 0 ? (
          <p className="text-sm text-slate-300">No pending workflows to simulate.</p>
        ) : (
          workflows.map((task) => (
            <label key={task.id} className="flex items-start gap-3 rounded-2xl border border-white/10 bg-white/5 p-4">
              <input
                type="radio"
                name="simulation-workflow"
                value={task.id}
                checked={selected === task.id}
                onChange={() => setSelected(task.id)}
              />
              <div>
                <p className="text-sm text-white">{task.title}</p>
                <p className="text-xs text-slate-400">{task.department} · {task.priority}</p>
              </div>
            </label>
          ))
        )}
      </div>

      <div className="mt-6 flex flex-wrap items-center gap-3">
        <input
          className="flex-1 rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-sm text-white"
          placeholder="Reason for simulation (directive linked)"
          value={reason}
          onChange={(event) => setReason(event.target.value)}
        />
        <button
          className="rounded-full border border-cyan-400/50 px-4 py-2 text-xs uppercase text-cyan-200"
          onClick={logSimulationIntent}
          disabled={saving || !selected || !reason}
        >
          {saving ? 'Logging…' : 'Log Simulation'}
        </button>
      </div>
    </div>
  );
};
