import { AgentDefinition } from "../types/agents";

export const AGENT_CATALOG: AgentDefinition[] = [
  {
    id: "agent_stream_architect",
    name: "Stream Architect",
    codename: "ARCHITECT",
    role: "Designs and optimizes revenue streams end-to-end.",
    department: "revenue",
    defaultStatus: "idle",
    visual: { icon: "Cpu", shape: "hex", primaryColor: "#38bdf8", accentColor: "#0ea5e9" },
    description: "Builds and refines automated money flows, monitors KPIs, and recommends upgrades.",
  },
  {
    id: "agent_funnel_engineer",
    name: "Funnel Engineer",
    codename: "FUNNEL",
    role: "Landing pages, funnels, and conversion paths.",
    department: "revenue",
    defaultStatus: "idle",
    visual: { icon: "Filter", shape: "diamond", primaryColor: "#22c55e", accentColor: "#4ade80" },
    description: "Owns landing pages and conversion paths for every stream.",
  },
  {
    id: "agent_lead_hunter",
    name: "Lead Hunter",
    codename: "HUNTER",
    role: "Prospecting, scraping leads, contact discovery.",
    department: "recon",
    defaultStatus: "idle",
    visual: { icon: "Target", shape: "circle", primaryColor: "#f97316", accentColor: "#fdba74" },
    description: "Discovers and captures new leads across channels.",
  },
  {
    id: "agent_recon_analyst",
    name: "Recon Analyst",
    codename: "ORACLE",
    role: "Researches markets, competitors, and data patterns.",
    department: "recon",
    defaultStatus: "idle",
    visual: { icon: "Radar", shape: "hex", primaryColor: "#a855f7", accentColor: "#c4b5fd" },
    description: "Scans markets, competitors, and data signals for opportunities.",
  },
  {
    id: "agent_crm_sentinel",
    name: "CRM Sentinel",
    codename: "SENTINEL",
    role: "Guards and manages the Earnetics CRM, follow-ups, and deal flow.",
    department: "crm",
    defaultStatus: "idle",
    visual: { icon: "Users", shape: "pill", primaryColor: "#22d3ee", accentColor: "#67e8f9" },
    description: "Keeps the CRM clean, follow-ups timely, and deals moving.",
  },
  {
    id: "agent_deal_closer",
    name: "Deal Closer",
    codename: "CLOSER",
    role: "Negotiation helper, offer drafting, closing support.",
    department: "crm",
    defaultStatus: "idle",
    visual: { icon: "Handshake", shape: "diamond", primaryColor: "#facc15", accentColor: "#fde047" },
    description: "Negotiates, drafts offers, and pushes deals over the finish line.",
  },
  {
    id: "agent_library_curator",
    name: "Library Curator",
    codename: "CURATOR",
    role: "Manages Internal Library, playbooks, and knowledge graph.",
    department: "library",
    defaultStatus: "idle",
    visual: { icon: "BookOpen", shape: "circle", primaryColor: "#0ea5e9", accentColor: "#38bdf8" },
    description: "Organizes playbooks and keeps the knowledge base up to date.",
  },
  {
    id: "agent_systems_orchestrator",
    name: "Systems Orchestrator",
    codename: "ORCHESTRATOR",
    role: "High-level controller that oversees all agents and streams.",
    department: "executive",
    defaultStatus: "idle",
    visual: { icon: "Orbit", shape: "hex", primaryColor: "#f97316", accentColor: "#fbbf24" },
    description: "Oversees the entire Earnetics stack and aligns agents to mission goals.",
  },
];

export function mergeAgentWithCatalog(agent: any) {
  const byId = AGENT_CATALOG.find((a) => a.id === agent.id);
  const byRole = AGENT_CATALOG.find((a) => agent.role && a.role.toLowerCase().includes(agent.role.toLowerCase()));
  const def = byId || byRole;
  if (!def) return agent;
  return {
    ...agent,
    codename: def.codename,
    department: def.department,
    visual: def.visual,
    description: def.description,
  };
}

export function defaultMockAgents() {
  return [
    mergeAgentWithCatalog({
      id: "agent_stream_architect",
      name: "Stream Architect",
      role: "Architect",
      status: "running",
      currentTask: "TikTok Affiliate Loop – Stream v1.2",
    }),
    mergeAgentWithCatalog({
      id: "agent_lead_hunter",
      name: "Lead Hunter",
      role: "Lead Hunter",
      status: "running",
      currentTask: "Scraping new leads from FB groups.",
    }),
    mergeAgentWithCatalog({
      id: "agent_crm_sentinel",
      name: "CRM Sentinel",
      role: "CRM",
      status: "idle",
      currentTask: "Awaiting new follow-up tasks.",
    }),
    mergeAgentWithCatalog({
      id: "agent_library_curator",
      name: "Library Curator",
      role: "Library",
      status: "running",
      currentTask: "Indexing new playbook: Wholesale RE Basics.",
    }),
    mergeAgentWithCatalog({
      id: "agent_systems_orchestrator",
      name: "Systems Orchestrator",
      role: "Executive",
      status: "running",
      currentTask: "Monitoring 4 active streams, 12 open tasks.",
    }),
  ];
}
