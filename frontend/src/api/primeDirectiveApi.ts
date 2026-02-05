import { API_BASE_URL, getAuthHeaders } from './config';

export interface PrimeDirectiveResponse {
  prime_directive: Record<string, unknown>;
}

export const fetchPrimeDirective = async (signal?: AbortSignal): Promise<PrimeDirectiveResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/prime_directive`, {
    signal,
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(`Unable to load Prime Directive (${response.status})`);
  }

  return response.json();
};
