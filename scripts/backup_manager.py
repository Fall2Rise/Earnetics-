import os
import shutil
import sqlite3
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Paths
DATA_DIR = "data"
BACKUP_DIR = "backups"
DB_FILES = [
    "business_database.db",
    "vector_memory.db",
    "audit_log.db",
    "approval_queue.db",
    "workflow_scheduler.db",
    "credential_vault.db"
]

def create_backup():
    """Creates a timestamped backup of all corporate databases."""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        logger.info(f"Created backup directory: {BACKUP_DIR}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    current_backup_path = os.path.join(BACKUP_DIR, f"backup_{timestamp}")
    os.makedirs(current_backup_path)

    logger.info(f"Starting backup cycle: {timestamp}")

    for db_file in DB_FILES:
        src = os.path.join(DATA_DIR, db_file)
        if os.path.exists(src):
            # Use sqlite3 to perform a safe backup (handles open connections)
            dst = os.path.join(current_backup_path, db_file)
            try:
                with sqlite3.connect(src) as conn:
                    backup_conn = sqlite3.connect(dst)
                    conn.backup(backup_conn)
                    backup_conn.close()
                logger.info(f"Successfully backed up: {db_file}")
            except Exception as e:
                logger.error(f"Failed to back up {db_file}: {e}")
        else:
            logger.warning(f"Database file not found, skipping: {db_file}")

    logger.info(f"Backup cycle complete. Files stored in: {current_backup_path}")
    return current_backup_path

def cleanup_old_backups(keep=7):
    """Removes backups older than the specified number of days."""
    backups = sorted([d for d in os.listdir(BACKUP_DIR) if d.startswith("backup_")])
    if len(backups) > keep:
        for old_backup in backups[:-keep]:
            path = os.path.join(BACKUP_DIR, old_backup)
            shutil.rmtree(path)
            logger.info(f"Cleaned up old backup: {old_backup}")

if __name__ == "__main__":
    path = create_backup()
    cleanup_old_backups()
    print(f"Backup completed: {path}")
