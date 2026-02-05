import React from 'react';
import { useAgentStore } from '../../stores/agentStore';

const statusTone: Record<string, string> = {
  active: 'text-emerald-300',
  idle: 'text-slate-300',
  error: 'text-rose-300',
  offline: 'text-slate-500',
};

export const AgentNexusPanel: React.FC = () => {
  const { agents, loading, error, fetchAgents, connectWebSocket } = useAgentStore();

  React.useEffect(() => {
    void fetchAgents();
    connectWebSocket();
  }, [fetchAgents, connectWebSocket]);

  return (
    <div className="glass-panel p-6">
      <header className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-xl text-white">Agent Nexus</h3>
          <p className="text-sm text-slate-300">Status, DNA, and active assignments.</p>
        </div>
        <span className="text-xs text-cyan-300 uppercase tracking-[0.2em]">
          {agents.length} agents
        </span>
      </header>

      {loading && <p className="mt-4 text-sm text-slate-300">Syncing agents…</p>}
      {error && <p className="mt-4 text-sm text-red-300">{error}</p>}

      <div className="mt-6 grid gap-3 md:grid-cols-2">
        {agents.map((agent) => (
          <div key={agent.id} className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h4 className="text-base text-white">{agent.name}</h4>
                <p className="text-xs text-slate-400">{agent.department}</p>
              </div>
              <span className={`text-xs uppercase ${statusTone[agent.status] ?? 'text-slate-300'}`}>
                {agent.status}
              </span>
            </div>
            <div className="mt-2 text-xs text-slate-400">
              <p>Role: {agent.role}</p>
              <p>Division: {agent.division}</p>
            </div>
            <div className="mt-3 flex flex-wrap gap-3 text-xs text-slate-400">
              <span>Performance: {agent.performance ?? 0}%</span>
              {agent.memoryEntries !== undefined && <span>Memory: {agent.memoryEntries}</span>}
            </div>
            {agent.currentTask && (
              <p className="mt-2 text-sm text-slate-200">{agent.currentTask}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
