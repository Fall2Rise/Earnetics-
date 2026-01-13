import { API_BASE_URL, getAuthHeaders } from './config';

export interface SystemMetrics {
  uptime_hours: number;
  total_requests: number;
  connected_modules: number;
  total_revenue: number;
}

export interface SystemServices {
  vector_memory: string;
  credential_vault: string;
}

export interface SystemStatusResponse {
  status: string;
  timestamp: string;
  kill_switch_active: boolean;
  safe_mode: boolean;
  agent_paused: boolean;
  mail_paused: boolean;
  metrics: SystemMetrics;
  services: SystemServices;
}

export const fetchSystemStatus = async (): Promise<SystemStatusResponse> => {
  // Use explicit API_BASE_URL for reliability
  const url = `${API_BASE_URL}/api/system/status`;
  
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
    
    const response = await fetch(url, {
      signal: controller.signal,
      headers: getAuthHeaders(),
    });
    
    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('[SystemStatus] Error response:', errorText);
      throw new Error(`Unable to load system status (${response.status}): ${errorText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      console.error('[SystemStatus] Request timeout');
      throw new Error('Request timeout - backend may be slow or unresponsive');
    }
    console.error('[SystemStatus] Fetch error:', error);
    throw error;
  }
};
