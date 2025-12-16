import { AppEvent } from './types';
import { v4 as uuidv4 } from 'uuid';

type EventHandler = (event: AppEvent) => void;

export class EventBus {
    private handlers: Map<string, EventHandler[]> = new Map();
    private events: AppEvent[] = []; // In-memory cache, should be backed by DB

    constructor(private persistEvent?: (event: AppEvent) => void) { }

    publish(type: string, payload: any, meta?: any): AppEvent {
        const event: AppEvent = {
            id: uuidv4(),
            type,
            payload,
            timestamp: Date.now(),
            meta,
        };

        this.events.push(event);
        if (this.persistEvent) {
            this.persistEvent(event);
        }

        this.dispatch(event);
        return event;
    }

    subscribe(type: string, handler: EventHandler): () => void {
        if (!this.handlers.has(type)) {
            this.handlers.set(type, []);
        }
        this.handlers.get(type)!.push(handler);

        return () => {
            const handlers = this.handlers.get(type);
            if (handlers) {
                this.handlers.set(
                    type,
                    handlers.filter((h) => h !== handler)
                );
            }
        };
    }

    private dispatch(event: AppEvent) {
        const specificHandlers = this.handlers.get(event.type) || [];
        const globalHandlers = this.handlers.get('*') || [];

        [...specificHandlers, ...globalHandlers].forEach((handler) => {
            try {
                handler(event);
            } catch (error) {
                console.error(`Error handling event ${event.type}:`, error);
            }
        });
    }

    getEvents(filter: { since?: number; until?: number; limit?: number; type?: string }): AppEvent[] {
        let filtered = this.events;

        if (filter.type) {
            filtered = filtered.filter((e) => e.type === filter.type);
        }
        if (filter.since) {
            filtered = filtered.filter((e) => e.timestamp >= filter.since!);
        }
        if (filter.until) {
            filtered = filtered.filter((e) => e.timestamp <= filter.until!);
        }
        if (filter.limit) {
            filtered = filtered.slice(-filter.limit);
        }

        return filtered;
    }

    replay(fromTs: number, toTs: number, speed: number = 1) {
        const eventsToReplay = this.getEvents({ since: fromTs, until: toTs });
        // This is a simplified replay. In a real app, this would likely emit events to a separate "simulation" state
        // or update the UI in real-time.
        console.log(`Replaying ${eventsToReplay.length} events...`);
        eventsToReplay.forEach(e => this.dispatch(e));
    }

    // Snapshot and restore would interact with the DB/State management

    connect(url: string) {
        console.log(`Connecting to backend at ${url}...`);
        const ws = new WebSocket(url);

        ws.onopen = () => {
            console.log('Connected to backend WebSocket');
            this.publish('SYSTEM_CONNECTED', { url, timestamp: Date.now() });
        };

        ws.onmessage = (message) => {
            try {
                const data = JSON.parse(message.data);
                if (data.type && data.payload) {
                    this.publish(data.type, data.payload, { source: 'backend' });
                }
            } catch (err) {
                console.error('Failed to parse backend message:', err);
            }
        };

        ws.onclose = () => {
            console.log('Backend WebSocket closed. Reconnecting in 5s...');
            setTimeout(() => this.connect(url), 5000);
        };

        ws.onerror = (err) => {
            console.error('Backend WebSocket error:', err);
        };

        this.ws = ws;
    }

    private ws: WebSocket | null = null;

    sendCommand(type: string, payload: any) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type, payload }));
        } else {
            console.warn('Cannot send command: Backend WebSocket not connected');
        }
    }
}
