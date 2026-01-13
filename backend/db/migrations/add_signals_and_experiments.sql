-- Migration: Add signals and experiments tables

-- Experiment registry (if not exists)
CREATE TABLE IF NOT EXISTS experiment_registry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    experiment_id TEXT UNIQUE NOT NULL,
    play_id TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    attempts INTEGER NOT NULL DEFAULT 0,
    started_at TEXT,
    ended_at TEXT,
    result_json TEXT,
    decision TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_experiment_registry_play_id ON experiment_registry(play_id);
CREATE INDEX IF NOT EXISTS idx_experiment_registry_status ON experiment_registry(status);

-- Strategy artifacts (if not exists)
CREATE TABLE IF NOT EXISTS strategy_artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    play_id TEXT NOT NULL,
    artifact_type TEXT NOT NULL,
    filepath TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_strategy_artifacts_run_id ON strategy_artifacts(run_id);
CREATE INDEX IF NOT EXISTS idx_strategy_artifacts_play_id ON strategy_artifacts(play_id);

