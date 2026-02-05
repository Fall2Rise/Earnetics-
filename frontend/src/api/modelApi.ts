import { API_BASE_URL } from './config';

export type ModelFamily = 'embedding' | 'llm';

export interface ModelInfo {
  name: string;
  family: ModelFamily;
  version: string;
  local_path?: string | null;
  active: boolean;
}

export const listModels = async (family: ModelFamily): Promise<ModelInfo[]> => {
  const response = await fetch(`${API_BASE_URL}/api/models/${family}`);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  const data = (await response.json()) as { models: ModelInfo[] };
  return data.models;
};

export const registerModel = async (model: ModelInfo): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/api/models/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(model),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
};

export const activateModel = async (family: ModelFamily, name: string): Promise<ModelInfo | null> => {
  const response = await fetch(`${API_BASE_URL}/api/models/${family}/${name}/activate`, { method: 'POST' });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  const data = (await response.json()) as { active: ModelInfo | null };
  return data.active;
};
