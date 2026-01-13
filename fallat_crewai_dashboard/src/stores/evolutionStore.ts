import { create } from 'zustand';
import { API_BASE_URL } from '../api/config';

interface EvolutionMetrics {
    total_actions: number;
    by_agent: Record<string, number>;
    failures: any[];
    successes: any[];
}

interface EvolutionStore {
    metrics: EvolutionMetrics | null;
    loading: boolean;
    error: string | null;
    fetchMetrics: () => Promise<void>;
    triggerEvolution: () => Promise<void>;
}

export const useEvolutionStore = create<EvolutionStore>((set) => ({
    metrics: null,
    loading: false,
    error: null,

    fetchMetrics: async () => {
        set({ loading: true, error: null });
        try {
            const response = await fetch(`${API_BASE_URL || '/api'}/atom/evolution_metrics`);
            if (!response.ok) throw new Error('Failed to fetch evolution metrics');
            const data = await response.json();
            set({ metrics: data, loading: false });
        } catch (error) {
            set({
                error: error instanceof Error ? error.message : 'Unknown error',
                loading: false
            });
        }
    },

    triggerEvolution: async () => {
        set({ loading: true, error: null });
        try {
            const response = await fetch(`${API_BASE_URL || '/api'}/atom/evolve`, { method: 'POST' });
            if (!response.ok) throw new Error('Failed to trigger evolution');
            await useEvolutionStore.getState().fetchMetrics();
        } catch (error) {
            set({
                error: error instanceof Error ? error.message : 'Unknown error',
                loading: false
            });
        }
    },
}));
