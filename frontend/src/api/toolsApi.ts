import { API_BASE_URL, getAuthHeaders } from './config';

export interface ToolSpec {
  name: string;
  category: string;
  description: string;
}

export interface ToolsResponse {
  count: number;
  tools: ToolSpec[];
}

export const fetchTools = async (signal?: AbortSignal): Promise<ToolsResponse> => {
  const response = await fetch(`${API_BASE_URL}/ops/tools`, {
    signal,
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(`Unable to load tools (${response.status})`);
  }

  return response.json();
};
