import { useState } from "react";
import { TopHudBar } from "./components/TopHudBar";
import { NavRail } from "./components/NavRail";
import { StatusDock } from "./components/StatusDock";
import { RevenueStreamsPanel } from "./components/RevenueStreamsPanel";
import { CrmPanel } from "./components/CrmPanel";
import { AgentOpsDeck } from "./components/AgentOpsDeck";
import { InternalLibraryPanel } from "./components/InternalLibraryPanel";
import { KpiTilesRow } from "./components/KpiTilesRow";
import { useCommandCenterState } from "./hooks/useCommandCenterState";

function Dashboard({ activeStreams, agents }: { activeStreams: number; agents: number }) {
  return (
    <div className="space-y-4 text-white">
      <KpiTilesRow
        kpis={[
          { label: "Active Streams", value: activeStreams },
          { label: "Active Agents", value: agents },
          { label: "Projected Monthly", value: "$0" },
          { label: "Open Deals", value: "--" },
        ]}
      />
      <div className="rounded-hud border border-white/10 bg-white/5 p-4">
        <div className="text-sm uppercase text-white/60">Today’s Mission</div>
        <div className="text-white/80 mt-2">High-level priorities will be surfaced here.</div>
      </div>
    </div>
  );
}

export default function App() {
  const [active, setActive] = useState("dashboard");
  const { streams, agents, activity } = useCommandCenterState();

  return (
    <div className="min-h-screen flex flex-col bg-[radial-gradient(circle_at_20%_0%,rgba(34,211,238,0.12),transparent_55%),radial-gradient(circle_at_80%_100%,rgba(168,85,247,0.14),transparent_55%),#050814]">
      <TopHudBar
        stats={[
          { label: "Streams", value: streams.length },
          { label: "Agents", value: agents.length },
          { label: "API", value: "localhost:8000" },
        ]}
      />
      <div className="flex flex-1">
        <NavRail active={active} onSelect={setActive} />
        <main className="flex-1 p-4 overflow-y-auto">
          {active === "dashboard" && <Dashboard activeStreams={streams.length} agents={agents.length} />}
          {active === "streams" && <RevenueStreamsPanel />}
          {active === "crm" && <CrmPanel />}
          {active === "agents" && <AgentOpsDeck agents={agents} activity={activity} />}
          {active === "library" && <InternalLibraryPanel />}
          {active === "settings" && <div className="text-white/70">Settings placeholder.</div>}
        </main>
        <StatusDock notifications={activity.slice(0, 5).map((ev, idx) => ({ id: idx, message: ev.action || ev.status || ev.message || "event", timestamp: ev.timestamp }))} />
      </div>
    </div>
  );
}
