import { useEffect, useState } from "react";
import { Stream } from "../types/streams";
import { Agent, AgentActivity } from "../types/agents";
import { getStreams } from "../api/streamsClient";
import { getAgents, getAgentActivity } from "../api/agentsClient";

export function useCommandCenterState() {
  const [streams, setStreams] = useState<Stream[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [activity, setActivity] = useState<AgentActivity[]>([]);

  useEffect(() => {
    const load = async () => {
      try {
        setStreams(await getStreams());
        const fetched = await getAgents(); setAgents(fetched.length ? fetched : []);
        setActivity(await getAgentActivity());
      } catch (err) {
        console.warn("CommandCenterState load error", err);
      }
    };
    load();
    const timer = setInterval(load, 15000);
    return () => clearInterval(timer);
  }, []);

  return { streams, agents, activity };
}
