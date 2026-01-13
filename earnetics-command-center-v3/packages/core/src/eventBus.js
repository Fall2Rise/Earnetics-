import { v4 as uuidv4 } from 'uuid';
export class EventBus {
    persistEvent;
    handlers = new Map();
    events = []; // In-memory cache, should be backed by DB
    constructor(persistEvent) {
        this.persistEvent = persistEvent;
    }
    publish(type, payload, meta) {
        const event = {
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
    subscribe(type, handler) {
        if (!this.handlers.has(type)) {
            this.handlers.set(type, []);
        }
        this.handlers.get(type).push(handler);
        return () => {
            const handlers = this.handlers.get(type);
            if (handlers) {
                this.handlers.set(type, handlers.filter((h) => h !== handler));
            }
        };
    }
    dispatch(event) {
        const specificHandlers = this.handlers.get(event.type) || [];
        const globalHandlers = this.handlers.get('*') || [];
        [...specificHandlers, ...globalHandlers].forEach((handler) => {
            try {
                handler(event);
            }
            catch (error) {
                console.error(`Error handling event ${event.type}:`, error);
            }
        });
    }
    getEvents(filter) {
        let filtered = this.events;
        if (filter.type) {
            filtered = filtered.filter((e) => e.type === filter.type);
        }
        if (filter.since) {
            filtered = filtered.filter((e) => e.timestamp >= filter.since);
        }
        if (filter.until) {
            filtered = filtered.filter((e) => e.timestamp <= filter.until);
        }
        if (filter.limit) {
            filtered = filtered.slice(-filter.limit);
        }
        return filtered;
    }
    replay(fromTs, toTs, speed = 1) {
        const eventsToReplay = this.getEvents({ since: fromTs, until: toTs });
        // This is a simplified replay. In a real app, this would likely emit events to a separate "simulation" state
        // or update the UI in real-time.
        console.log(`Replaying ${eventsToReplay.length} events...`);
        eventsToReplay.forEach(e => this.dispatch(e));
    }
    // Snapshot and restore would interact with the DB/State management
    connect(url) {
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
            }
            catch (err) {
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
    ws = null;
    sendCommand(type, payload) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type, payload }));
        }
        else {
            console.warn('Cannot send command: Backend WebSocket not connected');
        }
    }
}
