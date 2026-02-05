import { create } from 'zustand';
import { API_BASE_URL } from '../api/config';

interface SystemStatus {
    kill_switch_active: boolean;
    safe_mode: boolean;
    agent_paused: boolean;
    mail_paused: boolean;
}

interface SecurityStore {
    status: SystemStatus | null;
    loading: boolean;
    error: string | null;
    fetchStatus: () => Promise<void>;
    toggleKillSwitch: (active: boolean) => Promise<void>;
}

export const useSecurityStore = create<SecurityStore>((set) => ({
    status: null,
    loading: false,
    error: null,

    fetchStatus: async () => {
        set({ loading: true, error: null });
        try {
            const response = await fetch(`${API_BASE_URL || '/api'}/system/status`);
            if (!response.ok) throw new Error('Failed to fetch system status');
            const data = await response.json();
            set({ status: data, loading: false });
        } catch (error) {
            set({
                error: error instanceof Error ? error.message : 'Unknown error',
                loading: false
            });
        }
    },

    toggleKillSwitch: async (active: boolean) => {
        set({ loading: true, error: null });
        try {
            const response = await fetch(`${API_BASE_URL || '/api'}/system/kill-switch?active=${active}`, {
                method: 'POST',
            });
            if (!response.ok) throw new Error('Failed to toggle kill switch');
            const data = await response.json();
            set((state) => ({
                status: state.status ? { ...state.status, kill_switch_active: data.kill_switch_active } : null,
                loading: false
            }));
        } catch (error) {
            set({
                error: error instanceof Error ? error.message : 'Unknown error',
                loading: false
            });
        }
    },
}));
