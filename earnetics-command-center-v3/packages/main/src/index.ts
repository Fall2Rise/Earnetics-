import { app, BrowserWindow, ipcMain, IpcMainInvokeEvent } from 'electron';
import path from 'path';
import { EventStore, EventBus } from '@earnetics/core';
import { Simulator } from './simulator';
import { v4 as uuidv4 } from 'uuid';

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (require('electron-squirrel-startup')) {
    app.quit();
}

let mainWindow: BrowserWindow | null = null;
const dbPath = path.join(app.getPath('userData'), 'earnetics-v3.db');
const eventStore = new EventStore(dbPath);
const eventBus = new EventBus((event) => eventStore.saveEvent(event));

// Connect to Backend
const BACKEND_WS = process.env.EARNETICS_BACKEND_WS || 'ws://localhost:8000/ws';
eventBus.connect(BACKEND_WS);

// const simulator = new Simulator(eventBus); // Disabled in favor of real backend

const createWindow = () => {
    mainWindow = new BrowserWindow({
        width: 1280,
        height: 800,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: false,
            contextIsolation: true,
        },
    });

    if (process.env.NODE_ENV === 'development') {
        mainWindow.loadURL('http://localhost:5173');
        mainWindow.webContents.openDevTools();
    } else {
        mainWindow.loadFile(path.join(__dirname, '../../renderer/dist/index.html'));
    }
};

app.on('ready', () => {
    createWindow();
    // simulator.start(); // Removed

    // IPC Handlers
    ipcMain.handle('get-events', async (event: IpcMainInvokeEvent, filter: any) => {
        return eventStore.getEvents(filter?.since, filter?.until, filter?.limit);
    });

    ipcMain.handle('get-agents', async () => {
        return eventStore.readModels.getAgents();
    });

    ipcMain.handle('get-departments', async () => {
        return eventStore.readModels.getDepartments();
    });

    ipcMain.handle('publish-event', async (event: IpcMainInvokeEvent, type: string, payload: any, meta: any) => {
        const newEvent = eventBus.publish(type, payload, meta);
        // Broadcast to all windows
        BrowserWindow.getAllWindows().forEach((win: BrowserWindow) => {
            win.webContents.send('new-event', newEvent);
        });
        return newEvent;
    });

    ipcMain.handle('send-command', async (event: IpcMainInvokeEvent, type: string, payload: any) => {
        eventBus.sendCommand(type, payload);
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});
