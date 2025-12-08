import { motion } from "framer-motion";
import { Agent } from "../types/agents";
import { getStatusVisual } from "./agentStyles";

type Props = {
  agents: Agent[];
  onSelect?: (agent: Agent) => void;
};

export function AgentScene2D({ agents, onSelect }: Props) {
  return (
    <div className="grid grid-cols-3 gap-3 p-3 bg-gradient-to-br from-[#020617] to-[#050814] rounded-[16px] border border-slate-700 shadow-[0_0_24px_rgba(34,211,238,0.25)]">
      {agents.map((a) => {
        const statusViz = getStatusVisual(a.status);
        return (
          <motion.div
            key={a.id}
            className="p-3 rounded-xl border border-slate-700 bg-[rgba(2,6,23,0.8)] text-white cursor-pointer panel-hover"
            onClick={() => onSelect && onSelect(a)}
            animate={statusViz.animate}
            transition={statusViz.transition}
          >
            <div className="flex items-center gap-2">
              <div className={`h-3 w-3 rounded-full ${a.status === "running" ? "bg-neon-cyan" : "bg-white/50"}`} />
              <div className="font-semibold">{a.codename || a.name}</div>
            </div>
            <div className="text-xs text-white/60">{a.role}</div>
            {a.currentTask && <div className="text-xs text-white/70 mt-1">Task: {a.currentTask}</div>}
          </motion.div>
        );
      })}
    </div>
  );
}
