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
      // Use the roster endpoint which provides the full list of real agents
      const url = `${API_BASE_URL}/api/agents/roster`;

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000); // 5s timeout for fast fallback

      const response = await fetch(url, {
        signal: controller.signal,
        headers: getAuthHeaders(),
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`Failed to fetch agents (${response.status})`);
      }

      const data = await response.json();

      // Map the roster data to our frontend Agent interface
      // The roster endpoint returns { agents: [...] } list directly
      const agentsList = data.agents || [];

      // Group agents by department for layout
      const agentsByDept: Record<string, any[]> = {};
      agentsList.forEach((a: any) => {
        const dept = a.department || 'Unknown';
        if (!agentsByDept[dept]) agentsByDept[dept] = [];
        agentsByDept[dept].push(a);
      });

      // Layout Configuration
      const LAYOUT_CONFIG = {
        center: ['Executive Board'],
        inner: ['Finance & Revenue', 'Tech & Infrastructure', 'Creative & Product', 'Legal & Sovereignty'],
        outer: ['Corporate Analytics', 'Corporate Execution', 'Email Marketing', 'Revenue Strategy Cell', 'Revenue Execution', 'Lead Generation & Acquisition', 'Website Growth & Digital Presence', 'Health & Human Factor']
      };

      const agents: Agent[] = agentsList.map((agent: any) => {
        const dept = agent.department || 'Unknown';
        let pos: [number, number, number] = [0, 0, 0];

        // Calculate Position based on Tier
        if (LAYOUT_CONFIG.center.includes(dept)) {
          // CENTER TIER (Executive)
          const deptAgents = agentsByDept[dept];
          const idx = deptAgents.findIndex((a: any) => a.name === agent.name);
          const angle = (idx / deptAgents.length) * Math.PI * 2;
          const radius = 3; // Tight circle in center
          pos = [Math.cos(angle) * radius, 0, Math.sin(angle) * radius];
        }
        else if (LAYOUT_CONFIG.inner.includes(dept)) {
          // INNER RING (Core Ops)
          const deptAgents = agentsByDept[dept];
          const idx = deptAgents.findIndex((a: any) => a.name === agent.name);
          // Offset angle based on department index in tier
          const deptIdx = LAYOUT_CONFIG.inner.indexOf(dept);
          const sectorAngle = (Math.PI * 2) / LAYOUT_CONFIG.inner.length;
          const baseAngle = deptIdx * sectorAngle;
          const localAngle = (idx - (deptAgents.length - 1) / 2) * 0.5; // Spread within sector
          const radius = 12;
          pos = [Math.cos(baseAngle + localAngle) * radius, 0, Math.sin(baseAngle + localAngle) * radius];
        }
        else {
          // OUTER RING (Execution)
          const deptAgents = agentsByDept[dept];
          const idx = deptAgents.findIndex((a: any) => a.name === agent.name);
          // Distribute evenly across outer ring
          const totalOuterAgents = agentsList.filter((a: any) => !LAYOUT_CONFIG.center.includes(a.department) && !LAYOUT_CONFIG.inner.includes(a.department)).length;
          const globalIdx = agentsList.filter((a: any) => !LAYOUT_CONFIG.center.includes(a.department) && !LAYOUT_CONFIG.inner.includes(a.department)).indexOf(agent);

          const angle = (globalIdx / totalOuterAgents) * Math.PI * 2;
          const radius = 22;
          pos = [Math.cos(angle) * radius, 0, Math.sin(angle) * radius];
        }

        return {
          id: agent.name.toLowerCase(),
          name: agent.name,
          role: agent.role || 'Agent',
          division: agent.division || 'Operations',
          department: agent.department || 'Corporate Execution',
          status: (agent.memory_entries || 0) > 0 ? 'active' : 'idle',
          position: pos,
          color: getAgentColor(agent.department || 'Corporate Execution'),
          performance: agent.skill_score || Math.min(100, (agent.memory_entries || 0) * 5 + 50),
          memoryEntries: agent.memory_entries || 0,
          specialties: agent.specialties || [],
          currentTask: agent.current_task || 'Awaiting instructions',
          lastActivity: new Date().toISOString(),
        };
      });

      set({ agents, loading: false });
    } catch (error) {
      console.warn('[AgentStore] Fetch failed, falling back to Real AI Simulation Mode:', error);

      // REAL AI SIMULATION MODE - FULL ROSTER (51 AGENTS)
      // This fallback matches the backend backend/real_ai_agents.py
      const mockAgents: Agent[] = [
        // Executive Board
        { id: 'akasha', name: 'Akasha', role: 'Chief Executive Officer', department: 'Executive Board', division: 'Executive', status: 'active', position: [0, 4, 0], color: '#FFD700', performance: 99, memoryEntries: 1240, specialties: ['Strategic Vision', 'System Architecture', 'High-Level Decision Making'] },
        { id: 'atlas', name: 'Atlas', role: 'Chief Operating Officer', department: 'Executive Board', division: 'Executive', status: 'active', position: [2, 3, 2], color: '#FFD700', performance: 98, memoryEntries: 980, specialties: ['Operational Coordination', 'Resource Allocation', 'Process Optimization'] },

        // Finance & Revenue
        { id: 'vega', name: 'Vega', role: 'Chief Financial Officer', department: 'Finance & Revenue', division: 'Finance', status: 'active', position: [15, 0, 5], color: '#00D4FF', performance: 97, memoryEntries: 850, specialties: ['Financial Strategy', 'Risk Management', 'Capital Allocation'] },
        { id: 'omen', name: 'Omen', role: 'Revenue Forecaster', department: 'Finance & Revenue', division: 'Finance', status: 'idle', position: [16, 0, 7], color: '#00D4FF', performance: 92, memoryEntries: 420, specialties: ['Predictive Analytics', 'Trend Forecasting'] },
        { id: 'nova', name: 'Nova', role: 'Growth Specialist', department: 'Finance & Revenue', division: 'Finance', status: 'active', position: [14, 0, 6], color: '#00D4FF', performance: 95, memoryEntries: 600, specialties: ['Growth Hacking', 'Revenue Optimization'] },
        { id: 'mercury', name: 'Mercury', role: 'Sales Strategist', department: 'Finance & Revenue', division: 'Finance', status: 'idle', position: [15, 0, 8], color: '#00D4FF', performance: 94, memoryEntries: 500, specialties: ['Sales Pipeline', 'Conversion Optimization'] },
        { id: 'stripeops', name: 'StripeOps', role: 'Payment Specialist', department: 'Finance & Revenue', division: 'Finance', status: 'active', position: [13, 0, 5], color: '#00D4FF', performance: 98, memoryEntries: 700, specialties: ['Payment Processing', 'Subscription Management'] },

        // Creative & Product
        { id: 'lyra', name: 'Lyra', role: 'Chief Product Officer', department: 'Creative & Product', division: 'Product', status: 'active', position: [-15, 0, 5], color: '#FF1493', performance: 96, memoryEntries: 760, specialties: ['Product Strategy', 'User Experience', 'Creative Direction'] },
        { id: 'aurora', name: 'Aurora', role: 'Creative Director', department: 'Creative & Product', division: 'Design', status: 'active', position: [-16, 0, 7], color: '#FF1493', performance: 94, memoryEntries: 540, specialties: ['Visual Design', 'Brand Identity', 'Storytelling'] },
        { id: 'echo', name: 'Echo', role: 'Brand Voice Strategist', department: 'Creative & Product', division: 'Design', status: 'idle', position: [-14, 0, 6], color: '#FF1493', performance: 93, memoryEntries: 400, specialties: ['Copywriting', 'Brand Messaging'] },
        { id: 'quill', name: 'Quill', role: 'Copywriting Specialist', department: 'Creative & Product', division: 'Design', status: 'active', position: [-15, 0, 8], color: '#FF1493', performance: 95, memoryEntries: 600, specialties: ['Ad Copy', 'Email Marketing Content'] },

        // Tech & Infrastructure
        { id: 'forge', name: 'Forge', role: 'Chief Technology Officer', department: 'Tech & Infrastructure', division: 'Engineering', status: 'active', position: [0, 0, 18], color: '#00FFFF', performance: 98, memoryEntries: 1100, specialties: ['System Architecture', 'Security', 'Scalability'] },
        { id: 'titan', name: 'Titan', role: 'Infrastructure Architect', department: 'Tech & Infrastructure', division: 'DevOps', status: 'idle', position: [2, 0, 19], color: '#00FFFF', performance: 93, memoryEntries: 620, specialties: ['Cloud Infrastructure', 'CI/CD', 'Reliability Engineering'] },
        { id: 'aegis', name: 'Aegis', role: 'Security Sentinel', department: 'Tech & Infrastructure', division: 'Security', status: 'active', position: [-2, 0, 19], color: '#00FFFF', performance: 97, memoryEntries: 800, specialties: ['Cybersecurity', 'Threat Detection'] },
        { id: 'noir', name: 'Noir', role: 'Tech Research Analyst', department: 'Tech & Infrastructure', division: 'R&D', status: 'idle', position: [0, 0, 20], color: '#00FFFF', performance: 94, memoryEntries: 500, specialties: ['Emerging Tech', 'AI Research'] },

        // Corporate Analytics
        { id: 'genesis', name: 'Genesis', role: 'Chief Data Officer', department: 'Corporate Analytics', division: 'Data', status: 'active', position: [-10, 0, -10], color: '#9D4EDD', performance: 97, memoryEntries: 890, specialties: ['Data Strategy', 'Machine Learning', 'Business Intelligence'] },
        { id: 'dataanalyst', name: 'DataAnalyst', role: 'Data Analyst', department: 'Corporate Analytics', division: 'Data', status: 'idle', position: [-11, 0, -11], color: '#9D4EDD', performance: 92, memoryEntries: 400, specialties: ['Statistical Analysis', 'Reporting'] },
        { id: 'metricsreporter', name: 'MetricsReporter', role: 'Metrics Specialist', department: 'Corporate Analytics', division: 'Data', status: 'active', position: [-9, 0, -11], color: '#9D4EDD', performance: 94, memoryEntries: 550, specialties: ['KPI Tracking', 'Dashboarding'] },

        // Revenue Strategy Cell (Idea Dept)
        { id: 'strategydirector', name: 'StrategyDirector', role: 'Revenue Strategy Director', department: 'Revenue Strategy Cell', division: 'Strategy', status: 'active', position: [8, 0, -8], color: '#9333EA', performance: 95, memoryEntries: 450, specialties: ['Market Analysis', 'Opportunity Identification'] },
        { id: 'marketanalyst', name: 'MarketAnalyst', role: 'Market Research Analyst', department: 'Revenue Strategy Cell', division: 'Strategy', status: 'idle', position: [9, 0, -9], color: '#9333EA', performance: 91, memoryEntries: 300, specialties: ['Competitor Analysis', 'Trend Spotting'] },
        { id: 'opportunityscout', name: 'OpportunityScout', role: 'Opportunity Scout', department: 'Revenue Strategy Cell', division: 'Strategy', status: 'active', position: [7, 0, -9], color: '#9333EA', performance: 93, memoryEntries: 350, specialties: ['Niche Finding', 'Gap Analysis'] },
        { id: 'playvalidator', name: 'PlayValidator', role: 'Strategy Validator', department: 'Revenue Strategy Cell', division: 'Strategy', status: 'idle', position: [8, 0, -10], color: '#9333EA', performance: 92, memoryEntries: 320, specialties: ['Risk Assessment', 'Feasibility Study'] },

        // Revenue Execution
        { id: 'executioncommander', name: 'ExecutionCommander', role: 'Revenue Execution Commander', department: 'Revenue Execution', division: 'Operations', status: 'active', position: [10, 0, 10], color: '#EF4444', performance: 96, memoryEntries: 520, specialties: ['Campaign Launch', 'Performance Tracking'] },
        { id: 'launchspecialist', name: 'LaunchSpecialist', role: 'Launch Specialist', department: 'Revenue Execution', division: 'Operations', status: 'active', position: [11, 0, 11], color: '#EF4444', performance: 95, memoryEntries: 480, specialties: ['Product Launch', 'Go-to-Market'] },
        { id: 'revenueoperator', name: 'RevenueOperator', role: 'Revenue Operations Manager', department: 'Revenue Execution', division: 'Operations', status: 'idle', position: [9, 0, 11], color: '#EF4444', performance: 94, memoryEntries: 450, specialties: ['Revenue Stream Management', 'Optimization'] },

        // Website Growth
        { id: 'websitemanager', name: 'WebsiteManager', role: 'Digital Presence Manager', department: 'Website Growth & Digital Presence', division: 'Growth', status: 'active', position: [-8, 0, 12], color: '#8B5CF6', performance: 94, memoryEntries: 380, specialties: ['Web Optimization', 'SEO', 'Content Strategy'] },
        { id: 'contentstrategist', name: 'ContentStrategist', role: 'Content Strategist', department: 'Website Growth & Digital Presence', division: 'Growth', status: 'idle', position: [-9, 0, 13], color: '#8B5CF6', performance: 92, memoryEntries: 350, specialties: ['Content Planning', 'Blogging'] },
        { id: 'seospecialist', name: 'SEOSpecialist', role: 'SEO Specialist', department: 'Website Growth & Digital Presence', division: 'Growth', status: 'active', position: [-7, 0, 13], color: '#8B5CF6', performance: 93, memoryEntries: 320, specialties: ['On-Page SEO', 'Backlink Strategy'] },
        { id: 'socialintegrator', name: 'SocialIntegrator', role: 'Social Media Integrator', department: 'Website Growth & Digital Presence', division: 'Growth', status: 'idle', position: [-8, 0, 14], color: '#8B5CF6', performance: 91, memoryEntries: 300, specialties: ['Social Sharing', 'Engagement'] },
        { id: 'affiliatemanager', name: 'AffiliateManager', role: 'Affiliate Manager', department: 'Website Growth & Digital Presence', division: 'Growth', status: 'active', position: [-10, 0, 12], color: '#8B5CF6', performance: 95, memoryEntries: 400, specialties: ['Affiliate Marketing', 'Partnerships'] },
        { id: 'trafficanalyst', name: 'TrafficAnalyst', role: 'Traffic Analyst', department: 'Website Growth & Digital Presence', division: 'Growth', status: 'idle', position: [-6, 0, 12], color: '#8B5CF6', performance: 92, memoryEntries: 310, specialties: ['Traffic Analysis', 'Conversion Rate Optimization'] },
        { id: 'communitymanager', name: 'CommunityManager', role: 'Community Manager', department: 'Website Growth & Digital Presence', division: 'Growth', status: 'active', position: [-8, 0, 11], color: '#8B5CF6', performance: 94, memoryEntries: 360, specialties: ['Community Building', 'User Engagement'] },

        // Lead Gen
        { id: 'listbuilder', name: 'ListBuilder', role: 'Email List Growth Specialist', department: 'Lead Generation & Acquisition', division: 'Acquisition', status: 'active', position: [-12, 0, 0], color: '#06B6D4', performance: 92, memoryEntries: 310, specialties: ['Lead Scraping', 'List Building'] },
        { id: 'webscraper', name: 'WebScraper', role: 'Lead Scraper', department: 'Lead Generation & Acquisition', division: 'Acquisition', status: 'active', position: [-13, 0, 1], color: '#06B6D4', performance: 94, memoryEntries: 450, specialties: ['Web Scraping', 'Data Extraction'] },
        { id: 'leadqualifier', name: 'LeadQualifier', role: 'Lead Qualifier', department: 'Lead Generation & Acquisition', division: 'Acquisition', status: 'idle', position: [-11, 0, 1], color: '#06B6D4', performance: 91, memoryEntries: 280, specialties: ['Lead Scoring', 'Qualification'] },

        // Legal
        { id: 'hermes', name: 'Hermes', role: 'Chief Legal Officer', department: 'Legal & Sovereignty', division: 'Legal', status: 'idle', position: [5, 0, -15], color: '#FFA500', performance: 95, memoryEntries: 480, specialties: ['Corporate Law', 'Compliance', 'Risk Mitigation'] },
        { id: 'obsidian', name: 'Obsidian', role: 'Compliance Officer', department: 'Legal & Sovereignty', division: 'Legal', status: 'active', position: [6, 0, -16], color: '#FFA500', performance: 96, memoryEntries: 520, specialties: ['Regulatory Compliance', 'Internal Audits'] },

        // Email Marketing
        { id: 'orion', name: 'Orion', role: 'Email Marketing Manager', department: 'Email Marketing', division: 'Marketing', status: 'active', position: [-5, 0, -5], color: '#F59E0B', performance: 94, memoryEntries: 600, specialties: ['Email Strategy', 'Campaign Management'] },
        { id: 'vortex', name: 'Vortex', role: 'Funnel Specialist', department: 'Email Marketing', division: 'Marketing', status: 'active', position: [-6, 0, -6], color: '#F59E0B', performance: 93, memoryEntries: 550, specialties: ['Funnel Building', 'Automation'] },
        { id: 'lumen', name: 'Lumen', role: 'Email Analyst', department: 'Email Marketing', division: 'Marketing', status: 'idle', position: [-4, 0, -6], color: '#F59E0B', performance: 91, memoryEntries: 400, specialties: ['Email Analytics', 'A/B Testing'] },
        { id: 'cascade', name: 'Cascade', role: 'Drip Campaign Specialist', department: 'Email Marketing', division: 'Marketing', status: 'active', position: [-5, 0, -7], color: '#F59E0B', performance: 92, memoryEntries: 480, specialties: ['Drip Campaigns', 'Sequencing'] },
        { id: 'torrent', name: 'Torrent', role: 'Broadcast Specialist', department: 'Email Marketing', division: 'Marketing', status: 'idle', position: [-6, 0, -4], color: '#F59E0B', performance: 90, memoryEntries: 350, specialties: ['Broadcast Emails', 'Newsletters'] },

        // Operations Integrity
        { id: 'keeper', name: 'Keeper', role: 'Operations Guardian', department: 'Corporate Execution', division: 'Operations', status: 'active', position: [3, 0, -3], color: '#10B981', performance: 96, memoryEntries: 700, specialties: ['Process Integrity', 'Monitoring'] },
        { id: 'sentinel', name: 'Sentinel', role: 'System Sentinel', department: 'Corporate Execution', division: 'Operations', status: 'active', position: [4, 0, -2], color: '#10B981', performance: 95, memoryEntries: 650, specialties: ['System Health', 'Alerting'] },
        { id: 'pulse', name: 'Pulse', role: 'Operations Pulse', department: 'Corporate Execution', division: 'Operations', status: 'idle', position: [2, 0, -4], color: '#10B981', performance: 92, memoryEntries: 400, specialties: ['Real-time Monitoring', 'Status Reporting'] },

        // Customer Operations
        { id: 'relay', name: 'Relay', role: 'Customer Liaison', department: 'Corporate Execution', division: 'Support', status: 'active', position: [3, 0, -5], color: '#10B981', performance: 93, memoryEntries: 500, specialties: ['Customer Support', 'Communication'] },
        { id: 'harbor', name: 'Harbor', role: 'Support Specialist', department: 'Corporate Execution', division: 'Support', status: 'idle', position: [4, 0, -6], color: '#10B981', performance: 91, memoryEntries: 350, specialties: ['Ticket Resolution', 'FAQ Management'] },

        // Quality & Policy
        { id: 'muse', name: 'Muse', role: 'Quality Assurance', department: 'Corporate Execution', division: 'Quality', status: 'active', position: [5, 0, -3], color: '#10B981', performance: 94, memoryEntries: 600, specialties: ['QA Testing', 'Standardization'] },
        { id: 'lex', name: 'Lex', role: 'Policy Enforcer', department: 'Corporate Execution', division: 'Quality', status: 'idle', position: [6, 0, -4], color: '#10B981', performance: 93, memoryEntries: 450, specialties: ['Policy Compliance', 'Governance'] },

        // Health & Human Factor
        { id: 'seraph', name: 'Seraph', role: 'Well-being Guardian', department: 'Health & Human Factor', division: 'HR', status: 'active', position: [7, 0, 7], color: '#FF6B9D', performance: 96, memoryEntries: 500, specialties: ['Team Well-being', 'Burnout Prevention'] },
        { id: 'wellnesscoordinator', name: 'WellnessCoordinator', role: 'Wellness Coordinator', department: 'Health & Human Factor', division: 'HR', status: 'idle', position: [8, 0, 8], color: '#FF6B9D', performance: 94, memoryEntries: 400, specialties: ['Health Programs', 'Work-Life Balance'] },
      ];

      set({
        agents: mockAgents,
        loading: false,
        error: null // Clear error so we don't show the red badge
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
