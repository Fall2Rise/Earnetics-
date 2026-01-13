import { API_BASE_URL } from './config';

export interface AuditEvent {
  id?: number;
  timestamp: string;
  action: string;
  status: string;
  agent?: string | null;
  user?: string | null;
  message?: string | null;
  details?: Record<string, unknown>;
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

export const fetchAuditEvents = async (query: AuditQuery = {}, signal?: AbortSignal): Promise<AuditEvent[]> => {
  const response = await fetch(`${API_BASE_URL}/api/audit/events${buildQueryString(query)}`, { signal });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  const data = (await response.json()) as { events: AuditEvent[] };
  return data.events;
};
