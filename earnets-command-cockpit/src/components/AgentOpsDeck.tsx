import { useState } from "react";
import { Agent } from "../types/agents";
import { AgentScene2D } from "../agentScene/AgentScene2D";
import { AgentScene3D } from "../agentScene/AgentScene3D";
import { AgentAvatarCard } from "./AgentAvatarCard";
import { defaultMockAgents } from "../agentScene/agentCatalog";

type Props = {
  agents: Agent[];
  activity?: any[];
};

export function AgentOpsDeck({ agents, activity = [] }: Props) {
  const [view, setView] = useState<"2d" | "3d">("2d");
  const [selected, setSelected] = useState<Agent | null>(null);
  const [filter, setFilter] = useState<string>("all");

  const data = agents && agents.length ? agents : defaultMockAgents();
  const filtered =
    filter === "all"
      ? data
      : data.filter((a) => {
          if (filter === "revenue") return a.department === "revenue" || a.department === "automation";
          if (filter === "recon") return a.department === "recon";
          if (filter === "crm") return a.department === "crm";
          if (filter === "library") return a.department === "library";
          if (filter === "executive") return a.department === "executive";
          return true;
        });

  return (
    <div className="grid grid-cols-3 gap-4 text-white">
      <div className="col-span-2 flex flex-col gap-3">
        <div className="flex items-center gap-3">
          <select
            value={view}
            onChange={(e) => setView(e.target.value as "2d" | "3d")}
            className="bg-[rgba(2,6,23,0.8)] border border-slate-700 rounded-full px-3 py-2 text-slate-200 shadow-[0_0_14px_rgba(34,211,238,0.25)]"
          >
            <option value="2d">Ops Floor (2D)</option>
            <option value="3d">Ops Deck 3D</option>
          </select>
          <div className="text-cyan-300 text-sm">Agents: {filtered.length}</div>
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="bg-[rgba(2,6,23,0.8)] border border-slate-700 rounded-full px-3 py-2 text-sm text-slate-200 shadow-[0_0_14px_rgba(168,85,247,0.25)]"
          >
            <option value="all">All</option>
            <option value="revenue">Revenue Ops</option>
            <option value="recon">Recon / Research</option>
            <option value="crm">Relationship Ops</option>
            <option value="library">Knowledge / Library</option>
            <option value="executive">Executive</option>
          </select>
        </div>
        {view === "2d" ? <AgentScene2D agents={filtered} onSelect={(a) => setSelected(a)} /> : <AgentScene3D />}
      </div>
      <div className="col-span-1 rounded-[16px] border border-slate-700 bg-[rgba(2,6,23,0.85)] p-3 flex flex-col gap-3 shadow-[0_0_24px_rgba(15,23,42,0.9)] panel-hover">
        <div className="hud-label">Agent Detail</div>
        {selected ? (
          <>
            <div className="text-sm text-cyan-300">{selected.codename || selected.name}</div>
            <div className="text-lg font-semibold text-slate-50">{selected.role}</div>
            {selected.department && <div className="text-xs uppercase text-violet-300">{selected.department}</div>}
            {selected.description && <div className="text-sm text-slate-300">{selected.description}</div>}
            <AgentAvatarCard agent={selected} />
            <div className="flex gap-2">
              <button className="flex-1 btn-primary">Focus in Scene</button>
              <button className="flex-1 btn-secondary">View Logs</button>
              <button className="flex-1 btn-secondary">Assign Task</button>
            </div>
          </>
        ) : (
          <div className="text-white/50 text-sm">Select an agent to view details.</div>
        )}
        <div className="hud-label">Activity</div>
        <div className="flex-1 overflow-y-auto">
          {activity.slice(0, 10).map((ev: any, idx: number) => (
            <div key={idx} className="text-xs text-white/70 py-1 border-b border-white/5">
              {ev.timestamp || ""} — {ev.action || ev.status || ev.message || ""}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
