import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { AgentStatusSummary, getAgentStatus } from '../../api/agentApi';

interface AgentEntry {
  name: string;
  role: string;
  division: string;
  memoryEntries: number;
  specialties: string[];
}

const toAgentsArray = (status: AgentStatusSummary | null): AgentEntry[] => {
  if (!status?.agents) return [];
  return Object.entries(status.agents).map(([name, details]) => ({
    name,
    role: details.role ?? 'Agent',
    division: details.division ?? 'Unassigned',
    memoryEntries: details.memory_entries ?? 0,
    specialties: details.specialties ?? [],
  }));
};

export const AgentsPanel: React.FC = () => {
  const [status, setStatus] = useState<AgentStatusSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeDivision, setActiveDivision] = useState<string>('All');
  const mountedRef = useRef(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const response = await getAgentStatus();
      if (!mountedRef.current) return;
      setStatus(response);
      setError(null);
    } catch (err) {
      if (!mountedRef.current) return;
      setError(err instanceof Error ? err.message : 'Unable to load agent roster');
    } finally {
      if (mountedRef.current) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    mountedRef.current = true;
    void refresh();
    // Set up polling to refresh agents every 10 seconds
    const intervalId = setInterval(() => {
      if (mountedRef.current) {
        void refresh();
      }
    }, 10000);
    return () => {
      mountedRef.current = false;
      clearInterval(intervalId);
    };
  }, [refresh]);

  const divisions = useMemo(() => {
    const base = status?.divisions ?? {};
    const items = Object.entries(base)
      .map(([label, count]) => ({ label, count }))
      .sort((a, b) => b.count - a.count);
    return [{ label: 'All', count: status?.total_agents ?? items.reduce((sum, item) => sum + item.count, 0) }, ...items];
  }, [status?.divisions, status?.total_agents]);

  const agents = useMemo(() => toAgentsArray(status), [status]);

  const filteredAgents = useMemo(() => {
    if (activeDivision === 'All') return agents;
    return agents.filter((agent) => agent.division === activeDivision);
  }, [activeDivision, agents]);

  return (
    <section className="agents-panel">
      <header className="panel-header">
        <div>
          <h3>Agent Roster</h3>
          <span>
            {status?.active_agents ?? 0} active / {status?.total_agents ?? 0} total agents
          </span>
        </div>
        <button type="button" className="refresh-button" onClick={() => void refresh()} disabled={loading}>
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </header>

      {error && <p className="panel-error">{error}</p>}

      <div className="agents-filters" role="tablist" aria-label="Agent divisions">
        {divisions.map((division) => {
          const isActive = activeDivision === division.label;
          return (
            <button
              key={division.label}
              type="button"
              role="tab"
              aria-selected={isActive}
              className={`agents-filter${isActive ? ' agents-filter--active' : ''}`}
              onClick={() => setActiveDivision(division.label)}
            >
              {division.label}
              <span>{division.count}</span>
            </button>
          );
        })}
      </div>

      <div className="agents-grid">
        {filteredAgents.length === 0 && !loading && <p className="panel-empty">No agents in this division yet.</p>}
        {filteredAgents.length === 0 && loading && <p className="panel-empty">Loading agents...</p>}
        {filteredAgents.map((agent) => (
          <article key={agent.name} className="agent-card">
            <header>
              <h4>{agent.name}</h4>
              <span>{agent.role}</span>
            </header>
            <dl>
              <div>
                <dt>Division</dt>
                <dd>{agent.division}</dd>
              </div>
              <div>
                <dt>Memory</dt>
                <dd>{agent.memoryEntries} entries</dd>
              </div>
              <div>
                <dt>Specialties</dt>
                <dd>{agent.specialties.length ? agent.specialties.join(', ') : 'None'}</dd>
              </div>
            </dl>
          </article>
        ))}
      </div>
    </section>
  );
};
