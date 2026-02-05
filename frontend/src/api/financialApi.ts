import { API_BASE_URL, getAuthHeaders } from './config';

export interface FinancialMetrics {
  total_revenue: number;
  total_paid_out: number;
  total_reinvested: number;
  pending_payouts_count: number;
  pending_payout_amount: number;
  failed_payouts_count: number;
}

export const fetchFinancialMetrics = async (signal?: AbortSignal): Promise<FinancialMetrics> => {
  const response = await fetch(`${API_BASE_URL}/api/financial/metrics`, {
    signal,
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(`Unable to load financial metrics (${response.status})`);
  }

  return response.json();
};
