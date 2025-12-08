import { API_BASE_URL } from './config';

export type ScheduleType = 'interval' | 'cron' | 'once';

export interface SchedulerJob {
  id: string;
  handler: string;
  payload: Record<string, unknown>;
  schedule_type: ScheduleType;
  schedule_value: string;
  next_run: string;
  last_run?: string | null;
  status: string;
  created_at: string;
}

export interface SchedulerJobResult {
  job_id: string;
  status: 'success' | 'error';
  message?: string;
  result?: unknown;
}

const schedulerUrl = `${API_BASE_URL}/api/workflows/scheduler`;

const jsonHeaders = {
  'Content-Type': 'application/json',
};

const handleResponse = async <T>(response: Response): Promise<T> => {
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  return response.json() as Promise<T>;
};

export const listJobs = async (): Promise<SchedulerJob[]> => {
  const response = await fetch(`${schedulerUrl}/jobs`);
  const data = await handleResponse<{ jobs: SchedulerJob[] }>(response);
  return data.jobs;
};

export const createJob = async (job: {
  job_id: string;
  handler: string;
  payload: Record<string, unknown>;
  schedule_type: ScheduleType;
  schedule_value: string;
  start_at?: string | null;
}): Promise<SchedulerJob> => {
  const response = await fetch(`${schedulerUrl}/jobs`, {
    method: 'POST',
    headers: jsonHeaders,
    body: JSON.stringify(job),
  });
  const data = await handleResponse<{ job: SchedulerJob }>(response);
  return data.job;
};

export const deleteJob = async (jobId: string): Promise<void> => {
  const response = await fetch(`${schedulerUrl}/jobs/${jobId}`, {
    method: 'DELETE',
  });
  await handleResponse<{ status: string }>(response);
};

export const runJob = async (jobId: string): Promise<SchedulerJobResult> => {
  const response = await fetch(`${schedulerUrl}/jobs/${jobId}/run`, {
    method: 'POST',
  });
  return handleResponse<SchedulerJobResult>(response);
};

export const runDueJobs = async (): Promise<SchedulerJobResult[]> => {
  const response = await fetch(`${schedulerUrl}/run-due`, {
    method: 'POST',
  });
  const data = await handleResponse<{ results: SchedulerJobResult[] }>(response);
  return data.results;
};
