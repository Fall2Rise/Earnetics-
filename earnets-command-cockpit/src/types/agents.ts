export type AgentStatus = "idle" | "running" | "error" | "offline";

export type AgentDepartment =
  | "revenue"
  | "recon"
  | "automation"
  | "crm"
  | "library"
  | "executive";

export type AgentShape = "circle" | "hex" | "diamond" | "pill";

export interface AgentVisualPreset {
  icon: string;
  primaryColor: string;
  accentColor: string;
  shape: AgentShape;
}

export interface AgentDefinition {
  id: string;
  name: string;
  codename: string;
  role: string;
  department: AgentDepartment;
  defaultStatus: AgentStatus;
  visual: AgentVisualPreset;
  description: string;
}

export interface Agent {
  id: string;
  name: string;
  role: string;
  status: AgentStatus;
  department?: AgentDepartment;
  codename?: string;
  description?: string;
  visual?: AgentVisualPreset;
  currentTask?: string;
  skillLevel?: number;
  experience?: number;
}

export interface AgentActivity {
  id: number | string;
  agent?: string;
  action?: string;
  status?: string;
  timestamp?: string;
  message?: string;
}
