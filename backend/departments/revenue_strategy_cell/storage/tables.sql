-- Revenue Strategy Cell Database Schema

-- Strategy runs table
CREATE TABLE IF NOT EXISTS strategy_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT UNIQUE NOT NULL,
    created_at TEXT NOT NULL,
    goal_cash_target REAL NOT NULL DEFAULT 150000,
    goal_deadline TEXT NOT NULL DEFAULT '2026-01-31',
    cash_collected_to_date REAL NOT NULL DEFAULT 0,
    output_json TEXT NOT NULL,
    duration_ms INTEGER,
    number_of_plays_generated INTEGER DEFAULT 0,
    number_of_experiments_launched INTEGER DEFAULT 0,
    number_of_dispatch_packets INTEGER DEFAULT 0,
    number_of_jobs_created INTEGER DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'completed',
    error_message TEXT
);

-- Strategy play cards table
CREATE TABLE IF NOT EXISTS strategy_play_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    play_id TEXT NOT NULL,
    title TEXT NOT NULL,
    target_buyer TEXT,
    price_points_json TEXT,
    ev_json TEXT,
    play_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (run_id) REFERENCES strategy_runs(run_id)
);

CREATE INDEX IF NOT EXISTS idx_play_cards_run_id ON strategy_play_cards(run_id);
CREATE INDEX IF NOT EXISTS idx_play_cards_play_id ON strategy_play_cards(play_id);

-- Strategy experiments table
CREATE TABLE IF NOT EXISTS strategy_experiments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    experiment_id TEXT NOT NULL,
    linked_play_id TEXT,
    hypothesis TEXT NOT NULL,
    steps_json TEXT NOT NULL,
    pass_metrics_json TEXT NOT NULL,
    fail_metrics_json TEXT NOT NULL,
    duration_hours INTEGER NOT NULL DEFAULT 48,
    owner_department TEXT NOT NULL,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    FOREIGN KEY (run_id) REFERENCES strategy_runs(run_id)
);

CREATE INDEX IF NOT EXISTS idx_experiments_run_id ON strategy_experiments(run_id);
CREATE INDEX IF NOT EXISTS idx_experiments_play_id ON strategy_experiments(linked_play_id);

-- Dispatch packets table
CREATE TABLE IF NOT EXISTS dispatch_packets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    department_name TEXT NOT NULL,
    packet_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    dispatched_job_id TEXT,
    dispatched_at TEXT,
    FOREIGN KEY (run_id) REFERENCES strategy_runs(run_id)
);

CREATE INDEX IF NOT EXISTS idx_dispatch_run_id ON dispatch_packets(run_id);
CREATE INDEX IF NOT EXISTS idx_dispatch_department ON dispatch_packets(department_name);
CREATE INDEX IF NOT EXISTS idx_dispatch_job_id ON dispatch_packets(dispatched_job_id);

