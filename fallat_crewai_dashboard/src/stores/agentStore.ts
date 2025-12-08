import { create } from 'zustand';

export interface Agent {
  id: string;
  name: string;
  role: string;
  division: string;
  department: string;
  status: 'active' | 'idle' | 'error' | 'offline';
  position: [number, number, number];
  color: string;
  performance: number;
  currentTask?: string;
  lastActivity?: string;
  memoryEntries?: number;
  specialties?: string[];
}


interface AgentStore {
  agents: Agent[];
  selectedAgent: Agent | null;
  loading: boolean;
  error: string | null;
  setAgents: (agents: Agent[]) => void;
  selectAgent: (agent: Agent | null) => void;
  updateAgentStatus: (id: string, status: Agent['status']) => void;
  updateAgentPosition: (id: string, position: [number, number, number]) => void;
  fetchAgents: () => Promise<void>;
  getAgentsByDepartment: (department: string) => Agent[];
}

  fetchAgents: () => Promise<void>;
export const useAgentStore = create<AgentStore>((set, get) => ({
  agents: [],
  selectedAgent: null,
  loading: false,
  error: null,

  setAgents: (agents) => set({ agents }),

  selectAgent: (agent) => set({ selectedAgent: agent }),

  updateAgentStatus: (id, status) =>
    set((state) => ({
      agents: state.agents.map((agent) =>
        agent.id === id ? { ...agent, status } : agent
      ),
    })),

  updateAgentPosition: (id, position) =>
    set((state) => ({
      agents: state.agents.map((agent) =>
        agent.id === id ? { ...agent, position } : agent
      ),
    })),

  getAgentsByDepartment: (department: string) => {
    return get().agents.filter(agent => agent.department === department);
  },

  fetchAgents: async () => {
    set({ loading: true, error: null });
    try {
      const response = await fetch('http://localhost:8080/api/agents/status');
      if (!response.ok) throw new Error('Failed to fetch agents');
      
      const data = await response.json();
      
      const agents: Agent[] = Object.entries(data.agent_status?.agents || {}).map(
        ([key, agent]: [string, any], index) => ({
          id: key,
          name: key.charAt(0).toUpperCase() + key.slice(1),
          role: agent.role || 'Agent',
          division: agent.division || 'Operations',
          department: agent.department || 'Corporate Execution',
          status: agent.memory_entries > 0 ? 'active' : 'idle',
          position: [
            Math.cos((index / 30) * Math.PI * 2) * 5,
            Math.sin(index * 0.5) * 2,
            Math.sin((index / 30) * Math.PI * 2) * 5,
          ] as [number, number, number],
          color: getAgentColor(agent.department || 'Corporate Execution'),
          performance: Math.min(100, (agent.memory_entries || 0) * 10 + Math.random() * 20),
          memoryEntries: agent.memory_entries || 0,
          specialties: agent.specialties || [],
          currentTask: agent.memory_entries > 0 ? 'Processing tasks' : 'Idle',
          lastActivity: new Date().toISOString(),
        })
      );

      set({ agents, loading: false });
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : 'Unknown error',
        loading: false 
      });
    }
  },
}));
function getAgentColor(department: string): string {
  const colorMap: Record<string, string> = {
    'Executive Board': '#FFD700',
    'Finance & Revenue': '#00D4FF',
    'Creative & Product': '#FF1493',
    'Tech & Infrastructure': '#00FFFF',
    'Legal & Sovereignty': '#FFA500',
    'Health & Human Factor': '#FF6B9D',
    'Corporate Analytics': '#9D4EDD',
    'Corporate Execution': '#10B981',
    'Email Marketing': '#F59E0B',
  };
  return colorMap[department] || '#6366f1';
}
