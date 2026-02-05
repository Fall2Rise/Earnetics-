import { API_BASE_URL, getAuthHeaders } from './config';

export interface PlaybookTemplate {
  id: string;
  name?: string;
  category?: string;
  description?: string;
}

export interface PlaybooksResponse {
  templates: PlaybookTemplate[];
  version?: string;
}

export const fetchPlaybooks = async (
  signal?: AbortSignal,
): Promise<PlaybooksResponse | PlaybookTemplate[]> => {
  const response = await fetch(`${API_BASE_URL}/playbooks/list`, {
    signal,
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(`Unable to load playbooks (${response.status})`);
  }

  return response.json();
};
