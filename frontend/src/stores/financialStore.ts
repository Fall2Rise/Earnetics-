import { create } from 'zustand';
import { API_BASE_URL } from '../api/config';

interface FinancialMetrics {
    total_revenue: number;
    total_paid_out: number;
    total_reinvested: number;
    pending_payouts_count: number;
    pending_payout_amount: number;
    failed_payouts_count: number;
}

interface FinancialStore {
    metrics: FinancialMetrics | null;
    loading: boolean;
    error: string | null;
    fetchMetrics: () => Promise<void>;
}

export const useFinancialStore = create<FinancialStore>((set) => ({
    metrics: null,
    loading: false,
    error: null,

    fetchMetrics: async () => {
        set({ loading: true, error: null });
        try {
            const url = `${API_BASE_URL}/api/financial/metrics`;
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
            
            const response = await fetch(url, {
                signal: controller.signal,
                headers: {
                    'Content-Type': 'application/json',
                },
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) throw new Error(`Failed to fetch financial metrics (${response.status})`);
            const data = await response.json();
            set({ metrics: data, loading: false });
        } catch (error) {
            const errorMessage = error instanceof Error 
                ? (error.name === 'AbortError' ? 'Request timeout - backend may be slow' : error.message)
                : 'Unknown error';
            set({
                error: errorMessage,
                loading: false
            });
        }
    },
}));
