
import { API_BASE_URL } from './config';

export interface VaultCredential {
  service: string;
  name: string;
  metadata?: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
}

export interface StoreCredentialRequest {
  service: string;
  name: string;
  secret: string;
  metadata?: Record<string, unknown>;
}

const credentialsUrl = `${API_BASE_URL}/api/credentials`;

const handleResponse = async <T>(response: Response): Promise<T> => {
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  return response.json() as Promise<T>;
};

export const listCredentials = async (service?: string, signal?: AbortSignal): Promise<VaultCredential[]> => {
  const url = service ? `${credentialsUrl}/list?service=${encodeURIComponent(service)}` : `${credentialsUrl}/list`;
  const response = await fetch(url, { signal });
  const data = await handleResponse<{ credentials: VaultCredential[] }>(response);
  return data.credentials;
};

export const storeCredential = async (payload: StoreCredentialRequest): Promise<void> => {
  const response = await fetch(`${credentialsUrl}/store`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  await handleResponse(response);
};

export const deleteCredential = async (service: string, name: string): Promise<void> => {
  const response = await fetch(`${credentialsUrl}/delete`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ service, name }),
  });
  await handleResponse(response);
};

export interface CredentialSuggestion {
  id: number;
  service: string;
  name: string;
  description: string;
  revenue_impact: string;
  revenue_stream: string;
  priority: number;
  discovered_by: string;
  status: string;
  is_added: boolean;
  discovered_at?: string;
  metadata?: Record<string, unknown>;
}

export interface SuggestionsResponse {
  suggestions: CredentialSuggestion[];
  total: number;
  added_count: number;
  pending_count: number;
}

export const getCredentialSuggestions = async (
  revenue_stream?: string,
  min_priority?: number
): Promise<SuggestionsResponse> => {
  const url = new URL(`${credentialsUrl}/suggestions`);
  if (revenue_stream) url.searchParams.set('revenue_stream', revenue_stream);
  if (min_priority) url.searchParams.set('min_priority', String(min_priority));
  const response = await fetch(url.toString());
  return handleResponse<SuggestionsResponse>(response);
};

export const markSuggestionAdded = async (service: string, name: string): Promise<void> => {
  const response = await fetch(`${credentialsUrl}/suggestions/mark-added`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ service, name }),
  });
  await handleResponse(response);
};

export const dismissSuggestion = async (service: string, name: string): Promise<void> => {
  const response = await fetch(`${credentialsUrl}/suggestions/dismiss`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ service, name }),
  });
  await handleResponse(response);
};
