// Use explicit backend URL for reliability
// Vite proxy should handle /api routes, but explicit URL ensures connectivity
const DEFAULT_BASE_URL = 'http://127.0.0.1:8000';

export const API_BASE_URL =
  typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_BASE_URL
    ? String(import.meta.env.VITE_API_BASE_URL)
    : DEFAULT_BASE_URL; // Default to direct backend URL for reliability

// Get API token from environment if available
export const getApiToken = (): string | null => {
  if (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_TOKEN) {
    return String(import.meta.env.VITE_API_TOKEN);
  }
  return null;
};

// Helper to create headers with authentication if token is available
export const getAuthHeaders = (): Record<string, string> => {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  
  const token = getApiToken();
  if (token) {
    headers['X-Fallat-Token'] = token;
  }
  
  return headers;
};
