import { API_BASE_URL, getAuthHeaders } from './config';

export interface Website {
  id: number;
  domain: string;
  url: string;
  purpose: string;
  status: string;
  last_checked: string;
}

export interface AnalyticsData {
  visitors: number;
  pageviews: number;
  bounce_rate: number;
  avg_duration: number;
  sources: Record<string, number>;
}

export const websiteGrowthApi = {
  listWebsites: async (): Promise<{ websites: Website[] }> => {
    const response = await fetch(`${API_BASE_URL}/api/website-growth/websites`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to list websites');
    return response.json();
  },

  getAnalytics: async (websiteId: number, days: number = 30): Promise<{ analytics: any[] }> => {
    const response = await fetch(`${API_BASE_URL}/api/website-growth/websites/${websiteId}/analytics?days=${days}`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to get analytics');
    return response.json();
  },
  
  getSocialConnections: async (websiteId: number): Promise<{ connections: any[] }> => {
    const response = await fetch(`${API_BASE_URL}/api/website-growth/websites/${websiteId}/social-connections`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to get social connections');
    return response.json();
  }
};
