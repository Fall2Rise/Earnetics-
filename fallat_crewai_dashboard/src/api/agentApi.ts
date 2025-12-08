import { API_BASE_URL } from './config';

export interface Agent {
  id: string;
  name: string;
  division: string;
  role: string;
  status: 'active' | 'idle' | 'busy';
  memoryEntries: number;
  specialties: string[];
}

export interface AgentStatusSummary {
  total_agents?: number;
  active_agents?: number;
  divisions?: Record<string, number>;
  agents?: Record<
    string,
    {
      role?: string;
      division?: string;
      memory_entries?: number;
      specialties?: string[];
    }
  >;
}

export const getAgentStatus = async (): Promise<AgentStatusSummary> => {
  const response = await fetch(`${API_BASE_URL}/api/agents/real_status`);

  if (!response.ok) {
    throw new Error(`Unable to load agent status (${response.status})`);
  }

  const data = await response.json();
  return data?.agent_status ?? {};
};

export const getAgents = async (): Promise<Agent[]> => {
  try {
    const status = await getAgentStatus();
    const agents = status.agents ?? {};

    return Object.entries(agents).map(([name, details]) => {
      const memoryEntries = details.memory_entries ?? 0;
      return {
        id: name.replace(/\s+/g, '-').toLowerCase(),
        name,
        division: details.division ?? 'Unassigned',
        role: details.role ?? 'Agent',
        status: memoryEntries > 0 ? 'active' : 'idle',
        memoryEntries,
        specialties: details.specialties ?? [],
      };
    });
  } catch (error) {
    console.error('Failed to fetch agents:', error);
    return [];
  }
};

export interface AgentUpdateRequest {
  agent_name: string;
  role?: string | null;
  division?: string | null;
  prompt?: string | null;
  memory_namespace?: string | null;
}

export const updateAgent = async (payload: AgentUpdateRequest): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/api/agents/update`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
};

export const purgeAgentMemory = async (namespace: string): Promise<number> => {
  const response = await fetch(`${API_BASE_URL}/api/agents/memory`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ namespace }),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  const data = (await response.json()) as { removed: number };
  return data.removed;
};
