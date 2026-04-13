import { API_BASE_URL } from './config';

export interface Campaign {
  id: number;
  name: string;
  type: string;
  status: string;
  content_asset_id?: number;
  target_audience_filter?: any;
  schedule_at?: string;
  created_at: string;
}

export const campaignApi = {
  listCampaigns: async (status?: string, limit: number = 50): Promise<{ campaigns: Campaign[] }> => {
    const queryParams = new URLSearchParams();
    if (status) queryParams.append('status', status);
    if (limit) queryParams.append('limit', limit.toString());

    const response = await fetch(`${API_BASE_URL}/api/campaigns/?${queryParams}`, {
      headers: {
        'X-Fallat-Token': localStorage.getItem('api_token') || '',
      },
    });
    if (!response.ok) throw new Error('Failed to fetch campaigns');
    return response.json();
  },

  createCampaign: async (data: Partial<Campaign>): Promise<Campaign> => {
    const response = await fetch(`${API_BASE_URL}/api/campaigns/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Fallat-Token': localStorage.getItem('api_token') || '',
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to create campaign');
    return response.json();
  },

  startCampaign: async (id: number): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/api/campaigns/${id}/start`, {
      method: 'POST',
      headers: {
        'X-Fallat-Token': localStorage.getItem('api_token') || '',
      },
    });
    if (!response.ok) throw new Error('Failed to start campaign');
  },

  pauseCampaign: async (id: number): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/api/campaigns/${id}/pause`, {
      method: 'POST',
      headers: {
        'X-Fallat-Token': localStorage.getItem('api_token') || '',
      },
    });
    if (!response.ok) throw new Error('Failed to pause campaign');
  }
};
