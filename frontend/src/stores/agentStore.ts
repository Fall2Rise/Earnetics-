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
  reconnectAttempts?: number;
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

const LAYOUT_CONFIG = {
  center: ['Executive Board'],
  inner: ['Finance & Revenue', 'Tech & Infrastructure', 'Creative & Product', 'Legal & Sovereignty'],
  outer: [
    'Corporate Analytics',
    'Corporate Execution',
    'Email Marketing',
    'Revenue Strategy Cell',
    'Revenue Execution',
    'Lead Generation & Acquisition',
    'Website Growth & Digital Presence',
    'Health & Human Factor',
  ],
};

const normalizeStatus = (value?: string, memoryEntries?: number): Agent['status'] => {
  const normalized = String(value || '').toLowerCase();
  if (normalized === 'active' || normalized === 'idle' || normalized === 'error' || normalized === 'offline') {
    return normalized;
  }
  return (memoryEntries || 0) > 0 ? 'active' : 'idle';
};

const buildAgentPositions = (agentsList: any[]): Agent[] => {
  const agentsByDept: Record<string, any[]> = {};
  agentsList.forEach((agent: any) => {
    const department = agent.department || 'Unknown';
    if (!agentsByDept[department]) agentsByDept[department] = [];
    agentsByDept[department].push(agent);
  });

  const outerAgents = agentsList.filter(
    (agent: any) =>
      !LAYOUT_CONFIG.center.includes(agent.department) &&
      !LAYOUT_CONFIG.inner.includes(agent.department),
  );

  return agentsList.map((agent: any) => {
    const department = agent.department || 'Unknown';
    let position: [number, number, number] = [0, 0, 0];

    if (LAYOUT_CONFIG.center.includes(department)) {
      const departmentAgents = agentsByDept[department] || [];
      const index = Math.max(0, departmentAgents.findIndex((a: any) => a.name === agent.name));
      const angle = departmentAgents.length > 0 ? (index / departmentAgents.length) * Math.PI * 2 : 0;
      const radius = 3;
      position = [Math.cos(angle) * radius, 0, Math.sin(angle) * radius];
    } else if (LAYOUT_CONFIG.inner.includes(department)) {
      const departmentAgents = agentsByDept[department] || [];
      const index = Math.max(0, departmentAgents.findIndex((a: any) => a.name === agent.name));
      const departmentIndex = LAYOUT_CONFIG.inner.indexOf(department);
      const sectorAngle = (Math.PI * 2) / LAYOUT_CONFIG.inner.length;
      const baseAngle = departmentIndex * sectorAngle;
      const localAngle = (index - (departmentAgents.length - 1) / 2) * 0.5;
      const radius = 12;
      position = [Math.cos(baseAngle + localAngle) * radius, 0, Math.sin(baseAngle + localAngle) * radius];
    } else {
      const globalIndex = Math.max(0, outerAgents.indexOf(agent));
      const totalOuterAgents = Math.max(1, outerAgents.length);
      const angle = (globalIndex / totalOuterAgents) * Math.PI * 2;
      const radius = 22;
      position = [Math.cos(angle) * radius, 0, Math.sin(angle) * radius];
    }

    const memoryEntries = Number(agent.memory_entries || agent.memoryEntries || 0);

    return {
      id: String(agent.id || agent.name || crypto.randomUUID()).toLowerCase(),
      name: agent.name || 'Unknown Agent',
      role: agent.role || 'Unassigned Role',
      division: agent.division || 'Unassigned Division',
      department,
      status: normalizeStatus(agent.status, memoryEntries),
      position,
      color: getAgentColor(department),
      performance: Number(agent.skill_score || agent.performance || 0),
      memoryEntries,
      specialties: Array.isArray(agent.specialties) ? agent.specialties : [],
      currentTask: agent.current_task || agent.currentTask || 'Awaiting live telemetry',
      lastActivity: agent.last_activity || agent.lastActivity || undefined,
    };
  });
};

export const useAgentStore = create<AgentStore>((set, get) => ({
  agents: [],
  selectedAgent: null,
  selectedDepartment: null,
  loading: false,
  error: null,
  socket: null,
  reconnectAttempts: 0,

  setAgents: (agents) => set({ agents }),

  selectAgent: (agent) => set({ selectedAgent: agent }),

  selectDepartment: (department) => set({ selectedDepartment: department }),

  updateAgentStatus: (id, status) =>
    set((state) => ({
      agents: state.agents.map((agent) =>
        agent.id === id ? { ...agent, status } : agent,
      ),
    })),

  updateAgentPosition: (id, position) =>
    set((state) => ({
      agents: state.agents.map((agent) =>
        agent.id === id ? { ...agent, position } : agent,
      ),
    })),

  getAgentsByDepartment: (department: string) => {
    return get().agents.filter((agent) => agent.department === department);
  },

  connectWebSocket: () => {
    const existingSocket = get().socket;
    if (existingSocket && existingSocket.readyState === WebSocket.OPEN) return;

    let wsUrl: string;
    if (import.meta.env?.VITE_API_BASE_URL) {
      wsUrl = `${import.meta.env.VITE_API_BASE_URL.replace('http://', 'ws://').replace('https://', 'wss://')}/ws`;
    } else if (API_BASE_URL) {
      wsUrl = `${API_BASE_URL.replace('http://', 'ws://').replace('https://', 'wss://')}/ws`;
    } else {
      wsUrl = 'ws://127.0.0.1:8000/ws';
    }

    const socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      set({ socket, reconnectAttempts: 0, error: null });
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === 'agent_roster' && Array.isArray(data.agents)) {
          set({ agents: buildAgentPositions(data.agents), error: null });
          return;
        }

        if (data.type === 'agent_thinking' || data.type === 'agent_action') {
          const agentId = data.agent?.toLowerCase();
          if (agentId) {
            set((state) => ({
              agents: state.agents.map((agent) =>
                agent.id.toLowerCase() === agentId
                  ? {
                    ...agent,
                    status: 'active',
                    currentTask: data.message || agent.currentTask,
                    lastActivity: new Date().toISOString(),
                  }
                  : agent,
              ),
            }));

            setTimeout(() => {
              set((state) => ({
                agents: state.agents.map((agent) =>
                  agent.id.toLowerCase() === agentId && agent.status === 'active'
                    ? { ...agent, status: 'idle' }
                    : agent,
                ),
              }));
            }, 5000);
          }
        }
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
      }
    };

    socket.onclose = (event) => {
      set({ socket: null });
      if (event.code !== 1000) {
        set({ error: `Live telemetry connection lost (code: ${event.code}). Reconnecting...` });
      }
      const reconnectDelay = Math.min(30000, 3000 * Math.pow(2, get().reconnectAttempts || 0));
      setTimeout(() => {
        if (!get().socket || get().socket?.readyState !== WebSocket.OPEN) {
          set({ reconnectAttempts: (get().reconnectAttempts || 0) + 1 });
          get().connectWebSocket();
        }
      }, reconnectDelay);
    };

    socket.onerror = (err) => {
      console.error('WebSocket error:', err);
      set({ error: 'Live telemetry connection error. Attempting reconnect...' });
    };
  },

  disconnectWebSocket: () => {
    const socket = get().socket;
    if (socket) {
      socket.close(1000);
      set({ socket: null });
    }
  },

  fetchAgents: async () => {
    set({ loading: true, error: null });
    try {
      const url = `${API_BASE_URL}/api/agents/roster`;
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      const response = await fetch(url, {
        signal: controller.signal,
        headers: getAuthHeaders(),
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`Failed to fetch live agent roster (${response.status})`);
      }

      const data = await response.json();
      const agentsList = Array.isArray(data.agents) ? data.agents : [];

      set({ agents: buildAgentPositions(agentsList), loading: false, error: null });
    } catch (error) {
      console.error('[AgentStore] Live agent telemetry unavailable:', error);
      set({
        agents: [],
        loading: false,
        error: 'Awaiting live telemetry from /api/agents/roster',
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
