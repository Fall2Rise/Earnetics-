import { API_BASE_URL } from './config';

export interface ApprovalRequest {
  id: number;
  job_id: string;
  handler: string;
  payload: Record<string, unknown>;
  status: string;
  created_at: string;
  decided_at?: string | null;
  decision?: string | null;
  message?: string | null;
}

export interface ApprovalActionBody {
  note?: string;
}

const approvalsUrl = `${API_BASE_URL}/api/approvals`;

const handleResponse = async <T>(response: Response): Promise<T> => {
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  return response.json() as Promise<T>;
};

export const listApprovals = async (status?: string, limit = 100): Promise<ApprovalRequest[]> => {
  const url = new URL(approvalsUrl);
  if (status) url.searchParams.set('status', status);
  url.searchParams.set('limit', String(limit));
  const response = await fetch(url.toString());
  const data = await handleResponse<{ approvals: ApprovalRequest[] }>(response);
  return data.approvals;
};

export const approveRequest = async (requestId: number, note?: string): Promise<ApprovalRequest> => {
  const response = await fetch(`${approvalsUrl}/${requestId}/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ note } satisfies ApprovalActionBody),
  });
  const data = await handleResponse<{ status: string; request: ApprovalRequest }>(response);
  return data.request;
};

export const rejectRequest = async (requestId: number, note?: string): Promise<ApprovalRequest> => {
  const response = await fetch(`${approvalsUrl}/${requestId}/reject`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ note } satisfies ApprovalActionBody),
  });
  const data = await handleResponse<{ status: string; request: ApprovalRequest }>(response);
  return data.request;
};
