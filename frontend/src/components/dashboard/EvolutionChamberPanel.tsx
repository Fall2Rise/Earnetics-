import React from 'react';
import { useEvolutionStore } from '../../stores/evolutionStore';
import { logAuditReason } from '../../api/auditApi';

export const EvolutionChamberPanel: React.FC = () => {
  const { metrics, loading, error, fetchMetrics, triggerEvolution } = useEvolutionStore();
  const [reason, setReason] = React.useState('');
  const [logging, setLogging] = React.useState(false);

  React.useEffect(() => {
    void fetchMetrics();
  }, [fetchMetrics]);

  const handleTrigger = async () => {
    if (!reason) return;
    setLogging(true);
    try {
      await logAuditReason({
        action: 'evolution_cycle',
        reason,
        directive_ref: 'self_improvement',
        risk_level: 'YELLOW',
        owner_approved: true,
      });
      await triggerEvolution();
      setReason('');
    } finally {
      setLogging(false);
    }
  };

  return (
    <div className="glass-panel p-6">
      <header className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-xl text-white">Evolution Chamber</h3>
          <p className="text-sm text-slate-300">Self‑improvement cycles with directive‑linked rationale.</p>
        </div>
      </header>

      {error && <p className="mt-4 text-sm text-red-300">{error}</p>}

      <div className="mt-6 grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p className="text-xs uppercase text-slate-400">Total Actions</p>
          <p className="text-lg text-white">{metrics?.total_actions ?? 0}</p>
          <p className="mt-2 text-xs uppercase text-slate-400">Successes</p>
          <p className="text-sm text-slate-200">{metrics?.successes?.length ?? 0}</p>
          <p className="mt-2 text-xs uppercase text-slate-400">Failures</p>
          <p className="text-sm text-slate-200">{metrics?.failures?.length ?? 0}</p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p className="text-xs uppercase text-slate-400">Trigger Evolution Cycle</p>
          <input
            className="mt-3 w-full rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-sm text-white"
            placeholder="Reason / directive linkage"
            value={reason}
            onChange={(event) => setReason(event.target.value)}
          />
          <button
            className="mt-3 rounded-full border border-cyan-400/50 px-4 py-2 text-xs uppercase text-cyan-200"
            onClick={handleTrigger}
            disabled={logging || loading || !reason}
          >
            {logging || loading ? 'Running…' : 'Run Evolution'}
          </button>
        </div>
      </div>
    </div>
  );
};
