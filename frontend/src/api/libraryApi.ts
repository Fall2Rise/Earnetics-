import { API_BASE_URL, getAuthHeaders } from './config';

export interface LibraryItem {
  id: number;
  title: string;
  category?: string | null;
  description?: string | null;
  detailed_playbook?: string | null;
  tags?: string[];
  created_by_agent?: string | null;
  last_updated?: string | null;
}

export interface LibraryListResponse {
  items: LibraryItem[];
}

export interface LibraryCreatePayload {
  title: string;
  category?: string;
  description?: string;
  detailed_playbook?: string;
  tags?: string[];
  created_by_agent?: string;
}

export const fetchLibraryItems = async (category?: string, signal?: AbortSignal): Promise<LibraryListResponse> => {
  const url = new URL(`${API_BASE_URL}/api/library/`);
  if (category) {
    url.searchParams.set('category', category);
  }
  const response = await fetch(url.toString(), {
    signal,
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(`Unable to load library (${response.status})`);
  }

  return response.json();
};

export const createLibraryItem = async (payload: LibraryCreatePayload): Promise<LibraryItem> => {
  const response = await fetch(`${API_BASE_URL}/api/library/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Unable to create item (${response.status})`);
  }

  const result = await response.json();
  return result.item ?? result;
};
