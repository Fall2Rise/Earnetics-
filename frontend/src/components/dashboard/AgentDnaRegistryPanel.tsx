import React from 'react';
import { useAgentStore } from '../../stores/agentStore';
import { logAuditReason } from '../../api/auditApi';

export const AgentDnaRegistryPanel: React.FC = () => {
  const { agents, fetchAgents } = useAgentStore();
  const [reason, setReason] = React.useState('');
  const [status, setStatus] = React.useState<string | null>(null);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    void fetchAgents();
  }, [fetchAgents]);

  const handleSnapshot = async () => {
    setStatus(null);
    setError(null);
    try {
      const departments = Array.from(new Set(agents.map((agent) => agent.department))).sort();
      await logAuditReason({
        action: 'agent_dna_snapshot',
        reason,
        directive_ref: 'multi_agent_mesh',
        risk_level: 'YELLOW',
        owner_approved: true,
        context: {
          agent_count: agents.length,
          departments,
        },
      });
      setStatus('Snapshot logged to audit trail.');
      setReason('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to log snapshot');
    }
  };

  return (
    <div className="glass-panel p-6">
      <header className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-xl text-white">Agent DNA Registry</h3>
          <p className="text-sm text-slate-300">Lineage, roles, and operational signatures.</p>
        </div>
        <span className="text-xs text-cyan-300 uppercase tracking-[0.2em]">
          {agents.length} agents
        </span>
      </header>

      <div className="mt-6 flex flex-wrap items-center gap-3">
        <input
          className="flex-1 rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-sm text-white"
          placeholder="Reason for DNA snapshot"
          value={reason}
          onChange={(event) => setReason(event.target.value)}
        />
        <button
          className="rounded-full border border-cyan-400/50 px-4 py-2 text-xs uppercase text-cyan-200"
          onClick={handleSnapshot}
          disabled={!reason}
        >
          Log Snapshot
        </button>
      </div>

      {status && <p className="mt-2 text-xs text-emerald-300">{status}</p>}
      {error && <p className="mt-2 text-xs text-red-300">{error}</p>}

      <div className="mt-6 grid gap-3 md:grid-cols-2">
        {agents.map((agent) => (
          <div key={agent.id} className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <h4 className="text-base text-white">{agent.name}</h4>
            <p className="text-xs text-slate-400">{agent.department}</p>
            <div className="mt-2 text-xs text-slate-300">
              <p>Role: {agent.role}</p>
              <p>Division: {agent.division}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
