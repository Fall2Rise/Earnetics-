export type StreamStatus = "online" | "maintenance" | "paused" | "error";

export interface Stream {
  id: number;
  name: string;
  stage: string;
  progress: number;
  status?: StreamStatus;
  kpi?: string;
  metrics?: Record<string, unknown>;
  updated_at?: string;
}
