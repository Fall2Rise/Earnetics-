import { API_BASE_URL } from './config';

export interface PerformanceMetricsSnapshot {
  total_revenue?: number;
  monthly_target?: number;
  active_customers?: number;
  products_created?: number;
  directives_executed?: number;
  last_updated?: string;
  system_initialized?: string;
}

export interface SystemOverview {
  status?: string;
  total_agents?: number;
  active_departments?: number;
  performance_metrics?: PerformanceMetricsSnapshot;
}

export interface AgentPerformanceSummary {
  avg_response_time?: string;
  success_rate?: string;
  coordination_efficiency?: string;
}

export interface SystemHealth {
  system_overview?: SystemOverview;
  operations_assessment?: Record<string, unknown>;
  technical_infrastructure?: Record<string, unknown>;
  financial_health?: Record<string, unknown>;
  agent_performance?: AgentPerformanceSummary;
  timestamp?: string;
}

export interface SystemStatusResponse {
  status?: string;
  system_health?: SystemHealth;
  app_state?: Record<string, unknown>;
  timestamp?: string;
}

export const fetchSystemStatus = async (): Promise<SystemStatusResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/system_status`);

  if (!response.ok) {
    throw new Error(`Unable to load system status (${response.status})`);
  }

  return response.json();
};
