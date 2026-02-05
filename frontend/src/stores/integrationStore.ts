import { create } from 'zustand';
import { API_BASE_URL } from '../api/config';

interface IntegrationStatus {
    status: 'connected' | 'disconnected';
    missing_vars: string[];
    production_mode: boolean;
}

interface IntegrationStore {
    integrations: Record<string, IntegrationStatus>;
    loading: boolean;
    error: string | null;
    fetchIntegrations: () => Promise<void>;
}

export const useIntegrationStore = create<IntegrationStore>((set) => ({
    integrations: {},
    loading: false,
    error: null,

    fetchIntegrations: async () => {
        set({ loading: true, error: null });
        try {
            // Try new endpoint first, fallback to old endpoint for backward compatibility
            const response = await fetch(`${API_BASE_URL || '/api'}/integrations/status`).catch(() => 
                fetch(`${API_BASE_URL || '/api'}/system/integrations`)
            );
            if (!response.ok) throw new Error('Failed to fetch integrations');
            const data = await response.json();
            set({ integrations: data, loading: false });
        } catch (error) {
            set({
                error: error instanceof Error ? error.message : 'Unknown error',
                loading: false
            });
        }
    },
}));
