import { API_BASE_URL } from './config';

export interface AutonomyCycleResponse {
  status: 'success' | 'ok' | 'error';
  message?: string;
  cycle_results?: Record<string, unknown>;
  [key: string]: unknown;
}

export const runAutonomousCycle = async (): Promise<AutonomyCycleResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/autonomous/run_cycle`);

  if (!response.ok) {
    throw new Error(`Autonomous cycle failed (${response.status})`);
  }

  return response.json();
};
