import { API_BASE_URL, getAuthHeaders } from './config';

export interface RevenueCycle {
  id: string;
  created_at: string;
  market_context: any;
  product_roadmap: any;
  validated_opportunity: any;
  automation_module_spec: any;
  approved_module: any;
  revenue_play_report: any;
}

export interface RevenueHistoryResponse {
  cycles: RevenueCycle[];
}

export interface RunRevenueLoopResponse {
  status: string;
  cycle: RevenueCycle;
}

export const revenueLoopsApi = {
  getHistory: async (limit: number = 50): Promise<RevenueHistoryResponse> => {
    const response = await fetch(`${API_BASE_URL}/api/revenue-loop/history?limit=${limit}`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch revenue loop history');
    return response.json();
  },

  runLoop: async (marketContext: any): Promise<RunRevenueLoopResponse> => {
    const response = await fetch(`${API_BASE_URL}/api/revenue-loop/run`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ market_context: marketContext }),
    });
    if (!response.ok) throw new Error('Failed to run revenue loop');
    return response.json();
  },

  injectTools: async (tools: string[]): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/api/revenue-loop/inject-tools`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ tools }),
    });
    if (!response.ok) throw new Error('Failed to inject tools');
    return response.json();
  }
};
