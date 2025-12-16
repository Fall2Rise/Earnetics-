import Database from 'better-sqlite3';
import { AppEvent } from './types';
import { ReadModelStore, rebuild_read_models } from './readModels';
import path from 'path';

export class EventStore {
  private db: Database.Database;
  public readModels: ReadModelStore;

  constructor(dbPath: string) {
    this.db = new Database(dbPath);
    this.init();
    // Rebuild read models on startup
    const allEvents = this.getEvents();
    this.readModels = rebuild_read_models(allEvents);
  }

  private init() {
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

  saveEvent(event: AppEvent) {
    const stmt = this.db.prepare(`
      INSERT INTO events (id, type, payload, timestamp, meta)
      VALUES (?, ?, ?, ?, ?)
    `);
    stmt.run(
      event.id,
      event.type,
      JSON.stringify(event.payload),
      event.timestamp,
      event.meta ? JSON.stringify(event.meta) : null
    );

    // Update read models in memory
    this.readModels.handleEvent(event);
  }

  getEvents(since: number = 0, until: number = Date.now(), limit: number = 1000): AppEvent[] {
    const stmt = this.db.prepare(`
      SELECT * FROM events
      WHERE timestamp >= ? AND timestamp <= ?
      ORDER BY timestamp ASC
      LIMIT ?
    `);

    const rows = stmt.all(since, until, limit) as any[];
    return rows.map(row => ({
      id: row.id,
      type: row.type,
      payload: JSON.parse(row.payload),
      timestamp: row.timestamp,
      meta: row.meta ? JSON.parse(row.meta) : undefined
    }));
  }
}
