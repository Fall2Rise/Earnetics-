import Database from 'better-sqlite3';
export class EventStore {
    db;
    constructor(dbPath) {
        this.db = new Database(dbPath);
        this.init();
    }
    init() {
        this.db.exec(`
      CREATE TABLE IF NOT EXISTS events (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL,
        payload TEXT NOT NULL,
        timestamp INTEGER NOT NULL,
        meta TEXT
      );
      
      CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
      CREATE INDEX IF NOT EXISTS idx_events_type ON events(type);
    `);
    }
    saveEvent(event) {
        const stmt = this.db.prepare(`
      INSERT INTO events (id, type, payload, timestamp, meta)
      VALUES (?, ?, ?, ?, ?)
    `);
        stmt.run(event.id, event.type, JSON.stringify(event.payload), event.timestamp, event.meta ? JSON.stringify(event.meta) : null);
    }
    getEvents(since = 0, until = Date.now(), limit = 1000) {
        const stmt = this.db.prepare(`
      SELECT * FROM events
      WHERE timestamp >= ? AND timestamp <= ?
      ORDER BY timestamp ASC
      LIMIT ?
    `);
        const rows = stmt.all(since, until, limit);
        return rows.map(row => ({
            id: row.id,
            type: row.type,
            payload: JSON.parse(row.payload),
            timestamp: row.timestamp,
            meta: row.meta ? JSON.parse(row.meta) : undefined
        }));
    }
}
