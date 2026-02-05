import { API_BASE_URL, getAuthHeaders } from './config';

export interface AutonomyCycleResponse {
  status: 'success' | 'ok' | 'error';
  message?: string;
  cycle_results?: Record<string, unknown>;
  [key: string]: unknown;
}

export const runAutonomousCycle = async (
  reason?: string,
  metadata?: Record<string, unknown>
): Promise<AutonomyCycleResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/autonomous/run_cycle`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ reason, ...metadata }),
  });

  if (!response.ok) {
    let errorMessage = `Autonomous cycle failed (${response.status})`;
    try {
        const errorData = await response.json();
        if (errorData.detail) {
            errorMessage = errorData.detail;
        } else if (errorData.message) {
            errorMessage = errorData.message;
        }
    } catch (e) {
        // use default error message if JSON parsing fails
    }
    throw new Error(errorMessage);
  }

  return response.json();
};
