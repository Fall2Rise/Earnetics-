/// <reference types="vite/client" />

interface Window {
    api: {
        getAgents: () => Promise<any[]>;
        getDepartments: () => Promise<any[]>;
        publishEvent: (type: string, payload: any, meta?: any) => Promise<any>;
        onNewEvent: (callback: (event: any) => void) => () => void;
        sendCommand: (type: string, payload: any) => Promise<void>;
    };
}
