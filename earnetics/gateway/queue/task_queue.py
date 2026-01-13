"""
Task Queue: Stores pending actions for retry with exponential backoff
"""
import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import time

from backend.corporate_memory import BUSINESS_DB_PATH


class TaskQueue:
    """Task queue with retry and dead-letter queue"""
    
    def __init__(self, config: Dict[str, Any], db_path: Optional[str] = None):
        self.config = config
        queue_config = config.get("queue", {})
        self.enabled = queue_config.get("enabled", True)
        self.max_retries = queue_config.get("max_retries", 5)
        self.backoff_type = queue_config.get("backoff", "exponential")
        self.initial_delay = queue_config.get("initial_delay_seconds", 1)
        self.max_delay = queue_config.get("max_delay_seconds", 60)
        self.dead_letter_enabled = queue_config.get("dead_letter_enabled", True)
        
        self.db_path = db_path or str(Path(BUSINESS_DB_PATH).parent / "gateway_queue.db")
        self._ensure_schema()
    
    def _ensure_schema(self):
        """Create task queue database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Pending tasks
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pending_tasks (
                    task_id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    action TEXT NOT NULL,
                    params TEXT NOT NULL,
                    retry_count INTEGER DEFAULT 0,
                    next_retry_at TEXT,
                    created_at TEXT NOT NULL,
                    last_error TEXT,
                    status TEXT DEFAULT 'pending'
                )
            """)
            
            # Dead letter queue
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dead_letter_queue (
                    task_id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    action TEXT NOT NULL,
                    params TEXT NOT NULL,
                    retry_count INTEGER,
                    final_error TEXT,
                    created_at TEXT NOT NULL,
                    failed_at TEXT NOT NULL
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_next_retry 
                ON pending_tasks(next_retry_at)
            """)
            
            conn.commit()
    
    def enqueue(self, agent_id: str, role: str, action: str, params: Dict[str, Any],
               error: Optional[str] = None) -> str:
        """Enqueue a task for retry"""
        import uuid
        task_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        # Calculate next retry time
        next_retry = self._calculate_next_retry(0)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO pending_tasks
                    (task_id, agent_id, role, action, params, retry_count,
                     next_retry_at, created_at, last_error, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    task_id,
                    agent_id,
                    role,
                    action,
                    json.dumps(params),
                    0,
                    next_retry,
                    now,
                    error,
                    "pending"
                ))
                conn.commit()
        except Exception as e:
            print(f"Error enqueueing task: {e}")
        
        return task_id
    
    def get_due_tasks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get tasks that are due for retry"""
        if not self.enabled:
            return []
        
        tasks = []
        now = datetime.utcnow().isoformat()
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM pending_tasks
                    WHERE status = 'pending'
                    AND next_retry_at <= ?
                    AND retry_count < ?
                    ORDER BY next_retry_at ASC
                    LIMIT ?
                """, (now, self.max_retries, limit))
                
                for row in cursor.fetchall():
                    task = dict(row)
                    task["params"] = json.loads(task["params"])
                    tasks.append(task)
        except Exception as e:
            print(f"Error getting due tasks: {e}")
        
        return tasks
    
    def mark_success(self, task_id: str):
        """Mark task as successfully completed"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM pending_tasks WHERE task_id = ?
                """, (task_id,))
                conn.commit()
        except Exception as e:
            print(f"Error marking task success: {e}")
    
    def mark_retry(self, task_id: str, error: Optional[str] = None):
        """Mark task for retry with updated retry count"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get current retry count
                cursor.execute("SELECT retry_count FROM pending_tasks WHERE task_id = ?", (task_id,))
                row = cursor.fetchone()
                if not row:
                    return
                
                retry_count = row[0] + 1
                
                if retry_count >= self.max_retries:
                    # Move to dead letter queue
                    self._move_to_dead_letter(task_id, error)
                else:
                    # Update retry info
                    next_retry = self._calculate_next_retry(retry_count)
                    cursor.execute("""
                        UPDATE pending_tasks
                        SET retry_count = ?, next_retry_at = ?, last_error = ?
                        WHERE task_id = ?
                    """, (retry_count, next_retry, error, task_id))
                
                conn.commit()
        except Exception as e:
            print(f"Error marking task retry: {e}")
    
    def _move_to_dead_letter(self, task_id: str, final_error: Optional[str]):
        """Move task to dead letter queue"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get task
                cursor.execute("SELECT * FROM pending_tasks WHERE task_id = ?", (task_id,))
                row = cursor.fetchone()
                if not row:
                    return
                
                # Insert into dead letter queue
                cursor.execute("""
                    INSERT INTO dead_letter_queue
                    (task_id, agent_id, role, action, params, retry_count,
                     final_error, created_at, failed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row[1],  # task_id
                    row[2],  # agent_id
                    row[3],  # role
                    row[4],  # action
                    row[5],  # params
                    row[6],  # retry_count
                    final_error,
                    row[8],  # created_at
                    datetime.utcnow().isoformat()
                ))
                
                # Remove from pending
                cursor.execute("DELETE FROM pending_tasks WHERE task_id = ?", (task_id,))
                conn.commit()
        except Exception as e:
            print(f"Error moving to dead letter: {e}")
    
    def _calculate_next_retry(self, retry_count: int) -> str:
        """Calculate next retry time using exponential backoff"""
        if self.backoff_type == "exponential":
            delay = min(self.initial_delay * (2 ** retry_count), self.max_delay)
        else:
            delay = self.initial_delay
        
        next_retry = datetime.utcnow() + timedelta(seconds=delay)
        return next_retry.isoformat()
