import { motion } from "framer-motion";
import { Agent } from "../types/agents";
import { getStatusVisual } from "../agentScene/agentStyles";

type Props = {
  agent: Agent;
  onFocus?: (agent: Agent) => void;
};

function AvatarShape({ agent }: { agent: Agent }) {
  const visual = agent.visual;
  const shape = visual?.shape || "circle";
  const baseColor = visual?.primaryColor || "#38bdf8";
  const border = visual?.accentColor || "#0ea5e9";

  const shapeClass =
    shape === "hex"
      ? "clip-hex"
      : shape === "diamond"
      ? "clip-diamond"
      : shape === "pill"
      ? "rounded-full"
      : "rounded-full";

  return (
    <div
      className={`h-12 w-12 flex items-center justify-center font-semibold text-xs text-slate-900 ${shapeClass}`}
      style={{
        background: `radial-gradient(circle at 20% 20%, ${border}, ${baseColor})`,
        border: `2px solid ${border}`,
        boxShadow: `0 0 14px ${border}`,
      }}
    >
      {agent.codename ? agent.codename.slice(0, 3) : agent.name.slice(0, 3)}
    </div>
  );
}

export function AgentAvatarCard({ agent, onFocus }: Props) {
  const statusViz = getStatusVisual(agent.status);

  return (
    <motion.div
      className="p-3 rounded-[16px] border border-slate-700 bg-[rgba(2,6,23,0.85)] text-white shadow-[0_0_24px_rgba(15,23,42,0.9)] panel-hover"
      whileHover={{ y: -2, scale: 1.01 }}
      animate={statusViz.animate}
      transition={statusViz.transition}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <AvatarShape agent={agent} />
          <div>
            <div className="font-semibold">{agent.codename || agent.name}</div>
            <div className="text-xs text-white/60">{agent.role}</div>
            {agent.department && (
              <div className="text-[11px] text-white/50 uppercase">{agent.department}</div>
            )}
          </div>
        </div>
        <div
          className={`text-xs px-2 py-1 rounded-full border ${
            agent.status === "running" ? "border-neon-cyan text-neon-cyan" : "border-white/20 text-white/70"
          }`}
        >
          {agent.status}
        </div>
      </div>
      {agent.description && <div className="mt-2 text-xs text-white/70">{agent.description}</div>}
      {agent.currentTask && <div className="mt-2 text-sm text-white/80">Task: {agent.currentTask}</div>}
      <div className="mt-2 flex items-center gap-2 text-xs text-white/60">
        <div>Skill {agent.skillLevel ?? 0}</div>
        <div>XP {agent.experience ?? 0}</div>
      </div>
      {onFocus && (
        <button
          onClick={() => onFocus(agent)}
          className="mt-2 px-3 py-1 rounded border border-white/20 text-white/80 hover:border-neon-cyan"
        >
          Focus
        </button>
      )}
    </motion.div>
  );
}
