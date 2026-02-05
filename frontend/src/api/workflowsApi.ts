import { API_BASE_URL, getAuthHeaders } from './config';

export interface WorkflowTask {
  id: string;
  title: string;
  department: string;
  priority: string;
  status: string;
  description?: string | null;
  assigned_agent?: string | null;
  created_at: string;
  metadata?: Record<string, unknown>;
}

export interface WorkflowListResponse {
  workflows: WorkflowTask[];
  total: number;
}

export const fetchPendingWorkflows = async (signal?: AbortSignal): Promise<WorkflowListResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/workflows/pending`, {
    signal,
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(`Unable to load workflows (${response.status})`);
  }

  return response.json();
};
