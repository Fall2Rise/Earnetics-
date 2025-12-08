import { AgentStatus, AgentDepartment } from "../types/agents";

export const departmentColors: Record<
  AgentDepartment,
  { primary: string; accent: string }
> = {
  revenue: { primary: "#22c55e", accent: "#4ade80" },
  recon: { primary: "#f97316", accent: "#fdba74" },
  automation: { primary: "#38bdf8", accent: "#0ea5e9" },
  crm: { primary: "#22d3ee", accent: "#67e8f9" },
  library: { primary: "#a855f7", accent: "#c4b5fd" },
  executive: { primary: "#facc15", accent: "#fde047" },
};

export function getStatusVisual(status: AgentStatus) {
  switch (status) {
    case "running":
      return {
        className: "shadow-glow",
        animate: { scale: 1.05, opacity: 1 },
        transition: { repeat: Infinity, repeatType: "mirror", duration: 1.5 },
      };
    case "idle":
      return {
        className: "opacity-90",
        animate: { scale: 1, opacity: 0.9 },
        transition: { duration: 0.5 },
      };
    case "error":
      return {
        className: "ring-2 ring-red-400",
        animate: { scale: [1, 1.05, 1], opacity: [0.8, 1, 0.8] },
        transition: { repeat: Infinity, duration: 1.2 },
      };
    case "offline":
    default:
      return {
        className: "opacity-50",
        animate: { scale: 0.98, opacity: 0.5 },
        transition: { duration: 0.5 },
      };
  }
}
