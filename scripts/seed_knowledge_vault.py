import os
import sqlite3
import json
from pathlib import Path
from datetime import datetime

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "backend" / "corporate_memory.db"
DOCS_DIR = PROJECT_ROOT / "docs"
MODULES_DIR = PROJECT_ROOT / "command_center" / "modules"
ROOT_MD_FILES = ["START_HERE.md", "README.md", "LEAD_MANAGEMENT_SYSTEM.md", "MANUAL.md", "RUNBOOK.md"]

def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_table(conn):
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS library_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT,
            description TEXT,
            detailed_playbook TEXT,
            tags TEXT,
            created_by_agent TEXT,
            last_updated TEXT
        )
        """
    )
    conn.commit()

def seed_file(conn, file_path, category="Knowledge", tags=[]):
    path = Path(file_path)
    if not path.exists():
        print(f"Skipping missing file: {path}")
        return

    try:
        content = path.read_text(encoding="utf-8")
        title = path.stem.replace("_", " ").title()
        
        # Check for existing
        cur = conn.cursor()
        cur.execute("SELECT id FROM library_items WHERE title = ?", (title,))
        if cur.fetchone():
            print(f"Skipping existing item: {title}")
            return

        # Simple description extraction (first non-header line)
        lines = content.splitlines()
        description = "System documentation."
        for line in lines:
            if line.strip() and not line.startswith("#"):
                description = line.strip()[:200]
                break
        
        now = datetime.utcnow().isoformat()
        
        cur.execute(
            """
            INSERT INTO library_items (title, category, description, detailed_playbook, tags, created_by_agent, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                category,
                description,
                content,
                json.dumps(tags),
                "System Seeder",
                now
            )
        )
        conn.commit()
        print(f"Seeded: {title}")
        
    except Exception as e:
        print(f"Error seeding {path}: {e}")

def main():
    print(f"Seeding Knowledge Vault at {DB_PATH}...")
    conn = connect_db()
    ensure_table(conn)

    # Seed root files
    for filename in ROOT_MD_FILES:
        seed_file(conn, PROJECT_ROOT / filename, category="Knowledge", tags=["system", "root"])

    # Seed docs
    if DOCS_DIR.exists():
        for md_file in DOCS_DIR.glob("*.md"):
            seed_file(conn, md_file, category="Knowledge", tags=["documentation"])

    # Seed modules
    if MODULES_DIR.exists():
        for md_file in MODULES_DIR.glob("**/*.md"):
            seed_file(conn, md_file, category="Knowledge", tags=["module", "playbook"])

    print("Seeding complete.")
    conn.close()

if __name__ == "__main__":
    main()
