import axios from "axios";
import { Agent, AgentActivity } from "../types/agents";
import { mergeAgentWithCatalog } from "../agentScene/agentCatalog";

const api = axios.create({
  baseURL: "http://localhost:8000/api/agents",
  timeout: 8000,
});

export async function getAgents(): Promise<Agent[]> {
  const res = await api.get("/roster");
  const base: Agent[] = res.data.agents || [];
  return base.map(mergeAgentWithCatalog);
}

export async function getAgentActivity(): Promise<AgentActivity[]> {
  const res = await api.get("/activity?limit=50");
  return res.data.events || [];
}
