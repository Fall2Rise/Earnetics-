import { API_BASE_URL } from './config';

export interface ContentAsset {
  id: number;
  title: string;
  type: string;
  content: string;
  status: string;
  metadata: any;
  created_at: string;
  updated_at: string;
}

export const contentEngineApi = {
  listContent: async (type?: string, limit: number = 50): Promise<{ assets: ContentAsset[] }> => {
    const queryParams = new URLSearchParams();
    if (type) queryParams.append('type', type);
    if (limit) queryParams.append('limit', limit.toString());

    const response = await fetch(`${API_BASE_URL}/api/content-engine/list?${queryParams}`, {
      headers: {
        'X-Fallat-Token': localStorage.getItem('api_token') || '',
      },
    });
    if (!response.ok) throw new Error('Failed to fetch content');
    return response.json();
  },

  generateMaster: async (topic: string, tone: string = 'viral'): Promise<ContentAsset> => {
    const response = await fetch(`${API_BASE_URL}/api/content-engine/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Fallat-Token': localStorage.getItem('api_token') || '',
      },
      body: JSON.stringify({ topic, tone }),
    });
    if (!response.ok) throw new Error('Failed to generate content');
    return response.json();
  }
};
