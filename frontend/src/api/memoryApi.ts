
import { API_BASE_URL } from './config';

export interface MemoryRecord {
  id: string;
  namespace: string;
  content?: string;
  metadata?: Record<string, unknown>;
  embedding?: number[];
  created_at?: string;
  updated_at?: string;
}

export const listNamespaces = async (prefix?: string, limit = 100): Promise<string[]> => {
  const url = new URL(`${API_BASE_URL}/api/memory/namespaces`);
  if (prefix) url.searchParams.set('prefix', prefix);
  if (limit) url.searchParams.set('limit', String(limit));
  const response = await fetch(url.toString());
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  const data = (await response.json()) as { namespaces: string[] };
  return data.namespaces;
};

export const listNamespaceRecords = async (namespace: string, limit = 50): Promise<MemoryRecord[]> => {
  const url = new URL(`${API_BASE_URL}/api/memory/namespace/${encodeURIComponent(namespace)}`);
  if (limit) url.searchParams.set('limit', String(limit));
  const response = await fetch(url.toString());
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  const data = (await response.json()) as { records: MemoryRecord[] };
  return data.records;
};
