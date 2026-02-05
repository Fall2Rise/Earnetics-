import { API_BASE_URL, getAuthHeaders } from './config';

export interface AuditEvent {
  id: number;
  timestamp: string;
  action: string;
  status: string;
  agent?: string;
  user?: string;
  message?: string;
  details?: Record<string, unknown>;
}

export interface AuditEventsResponse {
  events: AuditEvent[];
}

export interface ReasonLogPayload {
  action: string;
  reason: string;
  directive_ref: string;
  risk_level: 'GREEN' | 'YELLOW' | 'RED';
  context?: Record<string, unknown>;
  owner_approved?: boolean;
  cryptographic_approval?: boolean;
}

export interface AuditQuery {
  limit?: number;
  status?: string;
  action?: string;
  agent?: string;
  user?: string;
}

const buildQueryString = (params: AuditQuery) => {
  const searchParams = new URLSearchParams();
  if (params.limit) searchParams.set('limit', String(params.limit));
  if (params.status) searchParams.set('status', params.status);
  if (params.action) searchParams.set('action', params.action);
  if (params.agent) searchParams.set('agent', params.agent);
  if (params.user) searchParams.set('user', params.user);
  const query = searchParams.toString();
  return query ? `?${query}` : '';
};

export const fetchAuditEvents = async (
  signal?: AbortSignal,
  query: AuditQuery = {}
): Promise<AuditEventsResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/audit/events${buildQueryString(query)}`, {
    signal,
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(`Unable to load audit events (${response.status})`);
  }

  return response.json();
};

export const logAuditReason = async (payload: ReasonLogPayload): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/api/audit/reason`, {
    method: 'POST',
    headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Failed to log reason (${response.status})`);
  }
};
