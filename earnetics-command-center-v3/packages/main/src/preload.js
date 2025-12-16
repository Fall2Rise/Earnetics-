import { contextBridge, ipcRenderer } from 'electron';
contextBridge.exposeInMainWorld('api', {
    getEvents: (filter) => ipcRenderer.invoke('get-events', filter),
    publishEvent: (type, payload, meta) => ipcRenderer.invoke('publish-event', type, payload, meta),
    onNewEvent: (callback) => {
        const subscription = (_, event) => callback(event);
        ipcRenderer.on('new-event', subscription);
        return () => ipcRenderer.removeListener('new-event', subscription);
    }
});
