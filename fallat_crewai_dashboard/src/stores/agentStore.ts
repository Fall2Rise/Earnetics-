import { create } from 'zustand';
import { API_BASE_URL, getAuthHeaders } from '../api/config';

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
  selectedDepartment: string | null;
  loading: boolean;
  error: string | null;
  socket: WebSocket | null;
  setAgents: (agents: Agent[]) => void;
  selectAgent: (agent: Agent | null) => void;
  selectDepartment: (department: string | null) => void;
  updateAgentStatus: (id: string, status: Agent['status']) => void;
  updateAgentPosition: (id: string, position: [number, number, number]) => void;
  fetchAgents: () => Promise<void>;
  getAgentsByDepartment: (department: string) => Agent[];
  connectWebSocket: () => void;
  disconnectWebSocket: () => void;
}

export const useAgentStore = create<AgentStore>((set, get) => ({
  agents: [],
  selectedAgent: null,
  selectedDepartment: null,
  loading: false,
  error: null,
  socket: null,

  setAgents: (agents) => set({ agents }),

  selectAgent: (agent) => set({ selectedAgent: agent }),

  selectDepartment: (department) => set({ selectedDepartment: department }),

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

  connectWebSocket: () => {
    // Debug logging removed to reduce request spam
    const existingSocket = get().socket;
    if (existingSocket && existingSocket.readyState === WebSocket.OPEN) return;

    // Always connect directly to backend WebSocket (bypass Vite proxy for reliability)
    let wsUrl: string;
    if (import.meta.env?.VITE_API_BASE_URL) {
      // Use explicit API base URL from env
      wsUrl = import.meta.env.VITE_API_BASE_URL.replace('http://', 'ws://').replace('https://', 'wss://') + '/ws';
    } else if (API_BASE_URL) {
      // Use API_BASE_URL from config
      wsUrl = API_BASE_URL.replace('http://', 'ws://').replace('https://', 'wss://') + '/ws';
    } else {
      // Final fallback: use direct backend URL
      wsUrl = 'ws://127.0.0.1:8000/ws';
    }
    // Debug logging removed to reduce request spam
    const socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      // Debug logging removed to reduce request spam
      set({ socket, reconnectAttempts: 0 }); // Reset reconnect attempts on successful connection
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === 'agent_thinking' || data.type === 'agent_action') {
          const agentId = data.agent?.toLowerCase();
          if (agentId) {
            set((state) => ({
              agents: state.agents.map((agent) =>
                agent.id.toLowerCase() === agentId
                  ? {
                    ...agent,
                    status: 'active',
                    currentTask: data.message,
                    lastActivity: new Date().toISOString()
                  }
                  : agent
              ),
            }));

            // Auto-reset to idle after 5 seconds if no new activity
            setTimeout(() => {
              set((state) => ({
                agents: state.agents.map((agent) =>
                  agent.id.toLowerCase() === agentId && agent.status === 'active'
                    ? { ...agent, status: 'idle' }
                    : agent
                ),
              }));
            }, 5000);
          }
        }
      } catch (err) {
        console.error('Failed to parse WS message:', err);
      }
    };

    socket.onclose = (event) => {
      set({ socket: null });
      if (event.code !== 1000) { // 1000 is normal closure
        console.warn(`WebSocket closed unexpectedly (code: ${event.code}, reason: ${event.reason || 'No reason provided'})`);
        set({ error: `Connection lost (code: ${event.code}). Reconnecting...` });
      }
      // Reconnect with exponential backoff to reduce request spam
      const reconnectDelay = Math.min(30000, 3000 * Math.pow(2, get().reconnectAttempts || 0));
      setTimeout(() => {
        if (!get().socket || get().socket?.readyState !== WebSocket.OPEN) {
          set({ reconnectAttempts: (get().reconnectAttempts || 0) + 1 });
          get().connectWebSocket();
        }
      }, reconnectDelay);
    };

    socket.onerror = (err) => {
      // Debug logging removed to reduce request spam
      console.error('WebSocket error:', err);
      set({ error: 'WebSocket connection error - attempting to reconnect...' });
    };
  },

  disconnectWebSocket: () => {
    const socket = get().socket;
    if (socket) {
      socket.close();
      set({ socket: null });
    }
  },

  fetchAgents: async () => {
    set({ loading: true, error: null });
    try {
      const url = `${API_BASE_URL}/api/agents/status`;
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
      
      const response = await fetch(url, {
        signal: controller.signal,
        headers: getAuthHeaders(),
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('[AgentStore] Error response:', errorText);
        throw new Error(`Failed to fetch agents (${response.status}): ${errorText}`);
      }

      const data = await response.json();

      const agents: Agent[] = Object.entries(data.agent_status?.agents || {}).map(
        ([key, agent]: [string, any], index) => ({
          id: key,
          name: key.charAt(0).toUpperCase() + key.slice(1),
          role: agent.role || 'Agent',
          division: agent.division || 'Operations',
          department: agent.department || 'Corporate Execution',
          status: agent.memory_entries > 0 ? 'active' : 'idle', // Set status based on activity
          position: [
            Math.cos((index / 10) * Math.PI * 2) * 5,
            0,
            Math.sin((index / 10) * Math.PI * 2) * 5,
          ] as [number, number, number],
          color: getAgentColor(agent.department || 'Corporate Execution'),
          performance: Math.min(100, (agent.memory_entries || 0) * 10 + Math.random() * 20),
          memoryEntries: agent.memory_entries || 0,
          specialties: agent.specialties || [],
          currentTask: agent.current_task || 'Awaiting instructions',
          lastActivity: agent.last_activity || new Date().toISOString(),
        })
      );

      set({ agents, loading: false });
    } catch (error) {
      let errorMessage = 'Unknown error';
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          errorMessage = 'Request timeout - backend may be slow or offline. Please check if the server is running.';
        } else {
          errorMessage = error.message || 'Failed to fetch agents';
        }
      }
      console.error('[AgentStore] Error fetching agents:', error);
      set({
        error: errorMessage,
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
  'Revenue Strategy Cell': '#9333EA',
  'Revenue Execution': '#EF4444',
  'Lead Generation & Acquisition': '#06B6D4',
  'Website Growth & Digital Presence': '#8B5CF6',
};
  return colorMap[department] || '#6366f1';
}
