import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { AgentStatusSummary, getAgentStatus, purgeAgentMemory, updateAgent } from '../../api/agentApi';
import { listNamespaceRecords, listNamespaces, MemoryRecord } from '../../api/memoryApi';

type SelectedAgent = {
  name: string;
  division?: string;
  role?: string;
  memoryNamespace?: string;
};

type AgentForm = {
  role: string;
  division: string;
  prompt: string;
  memoryNamespace: string;
};

const guessNamespace = (agentName: string): string => `agent:${agentName.toLowerCase().replace(/\s+/g, '_')}`;

export const AgentManager: React.FC = () => {
  const [status, setStatus] = useState<AgentStatusSummary | null>(null);
  const [agents, setAgents] = useState<SelectedAgent[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<SelectedAgent | null>(null);
  const [form, setForm] = useState<AgentForm | null>(null);
  const [namespaces, setNamespaces] = useState<string[]>([]);
  const [memoryRecords, setMemoryRecords] = useState<MemoryRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [memoryLoading, setMemoryLoading] = useState(false);
  const [updateLoading, setUpdateLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [memoryError, setMemoryError] = useState<string | null>(null);
  const [updateError, setUpdateError] = useState<string | null>(null);
  const [updateSuccess, setUpdateSuccess] = useState<string | null>(null);
  const [purgeSuccess, setPurgeSuccess] = useState<string | null>(null);
  const [namespaceFilter, setNamespaceFilter] = useState('');

  const loadAgents = useCallback(async () => {
    setLoading(true);
    try {
      const summary = await getAgentStatus();
      setStatus(summary);
      const mapped = summary.agents
        ? Object.entries(summary.agents).map(([name, details]) => ({
            name,
            division: details.division,
            role: details.role,
            memoryNamespace: guessNamespace(name),
          }))
        : [];
      setAgents(mapped);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load agents');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadAgents();
  }, [loadAgents]);

  const loadNamespaces = useCallback(
    async (prefix?: string) => {
      try {
        const data = await listNamespaces(prefix);
        setNamespaces(data);
        return data;
      } catch (err) {
        setMemoryError(err instanceof Error ? err.message : 'Failed to load namespaces');
        return [];
      }
    },
    [],
  );

  useEffect(() => {
    void loadNamespaces();
  }, [loadNamespaces]);

  const loadMemory = async (namespace: string) => {
    setMemoryLoading(true);
    try {
      const records = await listNamespaceRecords(namespace);
      setMemoryRecords(records);
      setMemoryError(null);
    } catch (err) {
      setMemoryError(err instanceof Error ? err.message : 'Failed to load memory records');
      setMemoryRecords([]);
    } finally {
      setMemoryLoading(false);
    }
  };

  const handleSelectAgent = async (agent: SelectedAgent) => {
    setSelectedAgent(agent);
    const memoryNamespace = agent.memoryNamespace ?? guessNamespace(agent.name);
    setForm({
      role: agent.role ?? '',
      division: agent.division ?? '',
      prompt: '',
      memoryNamespace,
    });
    setUpdateError(null);
    setUpdateSuccess(null);
    setPurgeSuccess(null);
    if (memoryNamespace) {
      await loadMemory(memoryNamespace);
    } else {
      setMemoryRecords([]);
    }
  };

  const handleFormChange =
    (key: keyof AgentForm) => (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      const value = event.target.value;
      setForm((prev) => (prev ? { ...prev, [key]: value } : prev));
    };

  const handleUpdateAgent = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!selectedAgent || !form) return;
    setUpdateLoading(true);
    setUpdateError(null);
    setUpdateSuccess(null);
    try {
      await updateAgent({
        agent_name: selectedAgent.name,
        role: form.role || null,
        division: form.division || null,
        prompt: form.prompt || null,
        memory_namespace: form.memoryNamespace || null,
      });
      setUpdateSuccess('Agent settings saved.');
      await loadAgents();
    } catch (err) {
      setUpdateError(err instanceof Error ? err.message : 'Failed to update agent');
    } finally {
      setUpdateLoading(false);
    }
  };

  const handleLoadMemory = async () => {
    if (form?.memoryNamespace) {
      await loadMemory(form.memoryNamespace);
    }
  };

  const handlePurgeMemory = async () => {
    if (!form?.memoryNamespace) return;
    setUpdateLoading(true);
    setPurgeSuccess(null);
    setUpdateError(null);
    try {
      const removed = await purgeAgentMemory(form.memoryNamespace);
      setPurgeSuccess(`Removed ${removed} memory record(s).`);
      await loadMemory(form.memoryNamespace);
    } catch (err) {
      setUpdateError(err instanceof Error ? err.message : 'Failed to purge memory');
    } finally {
      setUpdateLoading(false);
    }
  };

  const stats = useMemo(() => {
    if (!status) return null;
    return {
      total: status.total_agents ?? agents.length,
      active: status.active_agents ?? 0,
      divisions: status.divisions ?? {},
    };
  }, [status, agents.length]);

  return (
    <div className="agent-manager glass-panel">
      <header className="panel-header">
        <div>
          <h3>Agent Manager</h3>
          <span>Inspect and edit agent configuration</span>
        </div>
        <div className="panel-header__actions">
          <button type="button" className="refresh-button" onClick={() => void loadAgents()} disabled={loading}>
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </header>

      {error && <p className="panel-error">{error}</p>}

      {stats && (
        <div className="agent-stats">
          <div>
            <span>Total Agents</span>
            <strong>{stats.total}</strong>
          </div>
          <div>
            <span>Active Agents</span>
            <strong>{stats.active}</strong>
          </div>
          <div>
            <span>Divisions</span>
            <strong>{Object.keys(stats.divisions).length}</strong>
          </div>
        </div>
      )}

      <div className="agent-grid">
        <aside className="agent-list">
          <h4>Agents</h4>
          <ul>
            {agents.map((agent) => (
              <li key={agent.name}>
                <button
                  type="button"
                  onClick={() => void handleSelectAgent(agent)}
                  className={selectedAgent?.name === agent.name ? 'active' : ''}
                >
                  <strong>{agent.name}</strong>
                  <span>{agent.role ?? 'Agent'}</span>
                  <span>{agent.division ?? 'Unassigned'}</span>
                </button>
              </li>
            ))}
          </ul>
        </aside>

        <section className="agent-detail">
          {!selectedAgent || !form ? (
            <p className="panel-empty">Select an agent to inspect and edit configuration.</p>
          ) : (
            <>
              <header className="agent-detail__header">
                <h4>{selectedAgent.name}</h4>
                <span>{form.role || 'Agent'}</span>
                <span>{form.division || 'Unassigned'}</span>
              </header>

              {updateError && <p className="panel-error">{updateError}</p>}
              {updateSuccess && <p className="panel-success">{updateSuccess}</p>}
              {purgeSuccess && <p className="panel-success">{purgeSuccess}</p>}

              <form className="agent-form" onSubmit={handleUpdateAgent}>
                <label>
                  Role
                  <input value={form.role} onChange={handleFormChange('role')} placeholder="Agent role" />
                </label>
                <label>
                  Division
                  <input value={form.division} onChange={handleFormChange('division')} placeholder="Division" />
                </label>
                <label className="agent-form__prompt">
                  Prompt Override
                  <textarea value={form.prompt} onChange={handleFormChange('prompt')} rows={4} placeholder="Custom prompt (optional)" />
                </label>
                <label>
                  Memory Namespace
                  <input
                    value={form.memoryNamespace}
                    onChange={handleFormChange('memoryNamespace')}
                    list="memory-namespaces"
                    placeholder="agent:agent_name"
                  />
                  <datalist id="memory-namespaces">
                    {namespaces.map((ns) => (
                      <option key={ns} value={ns} />
                    ))}
                  </datalist>
                </label>
                <button type="submit" className="primary-button" disabled={updateLoading}>
                  {updateLoading ? 'Saving...' : 'Save Changes'}
                </button>
              </form>

              <div className="agent-memory-controls">
                <button type="button" className="refresh-button" disabled={memoryLoading} onClick={() => void handleLoadMemory()}>
                  {memoryLoading ? 'Loading...' : 'Load Memory'}
                </button>
                <button type="button" className="refresh-button" disabled={updateLoading} onClick={() => void handlePurgeMemory()}>
                  Purge Memory
                </button>
                <label>
                  Namespace Filter
                  <input
                    value={namespaceFilter}
                    onChange={(event) => setNamespaceFilter(event.target.value)}
                    onBlur={() => void loadNamespaces(namespaceFilter)}
                    placeholder="filter namespaces"
                  />
                </label>
              </div>

              {memoryError && <p className="panel-error">{memoryError}</p>}

              <div className="agent-memory-list">
                {memoryRecords.length === 0 ? (
                  <p className="panel-empty">No memory records found for this namespace.</p>
                ) : (
                  <ul>
                    {memoryRecords.map((record) => (
                      <li key={record.id}>
                        <header>
                          <strong>{record.id}</strong>
                          <span>{record.updated_at ? new Date(record.updated_at).toLocaleString() : 'unknown'}</span>
                        </header>
                        {record.content && <p>{record.content}</p>}
                        {record.metadata && Object.keys(record.metadata).length > 0 && (
                          <pre>{JSON.stringify(record.metadata, null, 2)}</pre>
                        )}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </>
          )}
        </section>
      </div>
    </div>
  );
};
