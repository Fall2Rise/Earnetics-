
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

export const listCredentials = async (service?: string): Promise<VaultCredential[]> => {
  const url = service ? `${credentialsUrl}/list?service=${encodeURIComponent(service)}` : `${credentialsUrl}/list`;
  const response = await fetch(url);
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
