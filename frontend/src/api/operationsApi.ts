import { API_BASE_URL, getAuthHeaders } from './config';

export interface QueueMetrics {
  pending: number;
  at_risk: number;
  overdue: number;
}

export interface ActivityEntry {
  timestamp: string;
  agent?: string;
  stage?: string;
  summary?: string;
  status?: string;
  task_id?: string;
  worker?: string;
  pipeline_id?: string;
  priority?: string;
}

export interface RequestEntry {
  id?: number;
  timestamp: string;
  pipeline_id?: string;
  title?: string;
  directive_type?: string;
  priority?: string;
  agent?: string;
  stage?: string;
  status?: string;
  description?: string;
  payload?: Record<string, unknown> | null;
  confidence?: number | null;
  due_date?: string | null;
}

export interface AutonomyPipelineState {
  last_pipeline_id?: string;
  last_cycle_timestamp?: string | null;
  alert_count?: number;
}

export interface WorkerSnapshot {
  status?: string;
  last_heartbeat?: string;
  error?: string;
  uptime?: string;
  [key: string]: unknown;
}

export interface SchedulerSnapshot {
  enabled?: boolean;
  workflow_interval_seconds?: number | null;
  telemetry_interval_seconds?: number | null;
  monitor_interval_seconds?: number | null;
  [key: string]: unknown;
}

export interface EmailCampaignSnapshot {
  campaigns: Record<string, unknown>;
  active_campaign_count: number;
}

export interface OperationsMetricsResponse {
  worker?: WorkerSnapshot;
  scheduler?: SchedulerSnapshot;
  queue?: QueueMetrics;
  alerts?: Array<Record<string, unknown>>;
  activity?: ActivityEntry[];
  requests?: RequestEntry[];
  pipeline?: AutonomyPipelineState;
  email_marketing?: EmailCampaignSnapshot;
}

export const fetchOperationsMetrics = async (signal?: AbortSignal): Promise<OperationsMetricsResponse> => {
  // Debug logging removed to reduce request spam
  const response = await fetch(`${API_BASE_URL}/metrics`, { signal });

  if (!response.ok) {
    throw new Error(`Unable to load operational metrics (${response.status})`);
  }

  const data = await response.json();
  return data;
};

export const updateDirectiveStatus = async (
  directiveId: number,
  status: string,
  notes?: string,
): Promise<{ id: number; status: string }> => {
  const response = await fetch(`${API_BASE_URL}/api/directives/${directiveId}/status`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ status, notes }),
  });

  if (!response.ok) {
    throw new Error(`Failed to update directive (${response.status})`);
  }

  return response.json();
};
