import { create } from 'zustand';

interface SystemState {
    isConnected: boolean;
    safeMode: boolean;
    mailPaused: boolean;
    agentPaused: boolean;
    logs: any[];
    agents: any[];

    connect: () => void;
    toggleSafeMode: () => void;
    toggleMailPaused: () => void;
    toggleAgentPaused: () => void;
}

export const useSystemStore = create<SystemState>((set, get) => ({
    isConnected: false,
    safeMode: false,
    mailPaused: false,
    agentPaused: false,
    logs: [],
    agents: [],

    connect: () => {
        const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
        const WS_URL = import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:8000/ws';
        const ws = new WebSocket(WS_URL);

        ws.onopen = () => {
            set({ isConnected: true });
            console.log('Connected to backend');
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log('WS Message:', data);

                if (data.type === 'CONTROL_UPDATE') {
                    set((state) => ({
                        safeMode: data.payload.safe_mode ?? state.safeMode,
                        mailPaused: data.payload.mail_sending_paused ?? state.mailPaused,
                        agentPaused: data.payload.agent_execution_paused ?? state.agentPaused,
                    }));
                } else if (data.type === 'AUDIT_LOG') {
                    set((state) => ({ logs: [data.payload, ...state.logs].slice(0, 100) }));
                }
            } catch (e) {
                console.error('Failed to parse WS message', e);
            }
        };

        ws.onclose = (event) => {
            set({ isConnected: false });
            if (event.code !== 1000) { // 1000 is normal closure
                console.warn(`WebSocket closed unexpectedly (code: ${event.code}, reason: ${event.reason || 'No reason provided'})`);
            } else {
                console.log('Disconnected from backend');
            }
            // Reconnect after 5 seconds if not a normal closure
            if (event.code !== 1000) {
                setTimeout(() => {
                    if (!get().isConnected) {
                        get().connect();
                    }
                }, 5000);
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            set({ isConnected: false });
        };
    },

    toggleSafeMode: async () => {
        const newState = !get().safeMode;
        await fetch(`${API_BASE}/api/system/controls`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ safe_mode: newState })
        });
    },

    toggleMailPaused: async () => {
        const newState = !get().mailPaused;
        await fetch(`${API_BASE}/api/system/controls`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mail_sending_paused: newState })
        });
    },

    toggleAgentPaused: async () => {
        const newState = !get().agentPaused;
        await fetch(`${API_BASE}/api/system/controls`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ agent_execution_paused: newState })
        });
    },
}));
