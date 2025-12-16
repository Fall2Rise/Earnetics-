import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('api', {
    getEvents: (filter: any) => ipcRenderer.invoke('get-events', filter),
    getAgents: () => ipcRenderer.invoke('get-agents'),
    getDepartments: () => ipcRenderer.invoke('get-departments'),
    publishEvent: (type: string, payload: any, meta?: any) => ipcRenderer.invoke('publish-event', type, payload, meta),
    onNewEvent: (callback: (event: any) => void) => {
        const subscription = (_: any, event: any) => callback(event);
        ipcRenderer.on('new-event', subscription);
        return () => ipcRenderer.removeListener('new-event', subscription);
    },
    sendCommand: (type: string, payload: any) => ipcRenderer.invoke('send-command', type, payload),
});
