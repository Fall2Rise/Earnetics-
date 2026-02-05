import { API_BASE_URL, getAuthHeaders } from './config';

export interface ServiceInfo {
  key: string;
  name: string;
  category: string;
  status: string;
  description: string;
  endpoint?: string | null;
  documentation?: string | null;
  dependencies?: string[] | null;
}

export interface ServicesResponse {
  services: ServiceInfo[];
}

export const fetchServices = async (signal?: AbortSignal): Promise<ServicesResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/services/`, {
    signal,
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(`Unable to load services (${response.status})`);
  }

  return response.json();
};
