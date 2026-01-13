"""Shared corporate memory layer for autonomous workflow coordination.

This module centralizes objectives, department tasks, and knowledge artifacts
so executive directives can flow into concrete operational work. It stores data
inside the primary business SQLite database, exposing helper methods for
creating, listing, and updating records with structured metadata.
"""

from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

def _normalize_env_path(env_value: Optional[str], default: str) -> Path:
    """Normalize path from environment variable, converting backslashes to forward slashes."""
    if not env_value:
        return Path(default)
    return Path(env_value.replace("\\", "/"))

BUSINESS_DB_PATH = _normalize_env_path(os.getenv("BUSINESS_DB_PATH"), "business_database.db")
ISO_FORMAT = "%Y-%m-%dT%H:%M:%S"


def _utcnow() -> str:
    return datetime.utcnow().strftime(ISO_FORMAT)


class CorporateMemoryError(RuntimeError):
    """Raised when corporate memory persistence fails."""


class CorporateMemory:
    """Facade around shared objective/task/knowledge tables."""

    def __init__(self, db_path: Path = BUSINESS_DB_PATH):
        self.db_path = db_path



    def _connection(self) -> sqlite3.Connection:

        conn = sqlite3.connect(self.db_path)

        conn.row_factory = sqlite3.Row

        return conn



    def create_tables(self) -> None:

        with self._connection() as conn:

            cur = conn.cursor()

            cur.execute(

                """

                CREATE TABLE IF NOT EXISTS corporate_objectives (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    title TEXT NOT NULL,

                    owner TEXT NOT NULL,

                    priority TEXT NOT NULL,

                    status TEXT NOT NULL,

                    description TEXT,

                    success_metrics JSON,

                    start_date TEXT,

                    due_date TEXT,

                    source_directive_id INTEGER,

                    created_at TEXT NOT NULL,

                    updated_at TEXT NOT NULL

                )

                """

            )

            cur.execute(

                """

                CREATE TABLE IF NOT EXISTS department_tasks (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    objective_id INTEGER,

                    title TEXT NOT NULL,

                    department TEXT NOT NULL,

                    assigned_agent TEXT,

                    status TEXT NOT NULL,

                    priority TEXT NOT NULL,

                    due_date TEXT,

                    description TEXT,

                    dependencies JSON,

                    metadata JSON,

                    created_at TEXT NOT NULL,

                    updated_at TEXT NOT NULL,

                    completed_at TEXT,

                    claimed_by TEXT,

                    claimed_at TEXT,

                    sla_minutes INTEGER DEFAULT 0,

                    FOREIGN KEY (objective_id) REFERENCES corporate_objectives (id)

                )

                """

            )

            cur.execute(

                """

                CREATE TABLE IF NOT EXISTS knowledge_articles (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    title TEXT NOT NULL,

                    content TEXT NOT NULL,

                    tags TEXT,

                    source TEXT,

                    related_objective_id INTEGER,

                    created_at TEXT NOT NULL,

                    updated_at TEXT NOT NULL,

                    FOREIGN KEY (related_objective_id) REFERENCES corporate_objectives (id)

                )

                """

            )

            cur.execute(

                """

                CREATE TABLE IF NOT EXISTS executive_directives (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    title TEXT NOT NULL,

                    directive_type TEXT NOT NULL,

                    owner TEXT NOT NULL,

                    priority TEXT NOT NULL,

                    status TEXT NOT NULL DEFAULT 'pending',

                    description TEXT,

                    payload JSON NOT NULL,

                    confidence REAL,

                    due_date TEXT,

                    created_at TEXT NOT NULL,

                    updated_at TEXT NOT NULL,

                    source_snapshot_id INTEGER,

                    FOREIGN KEY (source_snapshot_id) REFERENCES strategic_snapshots (id)

                )

                """

            )

            conn.commit()



    # Objectives -----------------------------------------------------------



    def create_objective(self, record: Dict[str, Any]) -> Dict[str, Any]:

        with self._connection() as conn:

            cur = conn.cursor()

            cur.execute(

                """

                INSERT INTO corporate_objectives (

                    title, owner, priority, status, description,

                    success_metrics, start_date, due_date,

                    source_directive_id, created_at, updated_at

                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

                """,

                (

                    record["title"],

                    record["owner"],

                    record["priority"],

                    record["status"],

                    record.get("description"),

                    json.dumps(record.get("success_metrics", {}), ensure_ascii=False),

                    record.get("start_date"),

                    record.get("due_date"),

                    record.get("source_directive_id"),

                    record["created_at"],

                    record["updated_at"],

                ),

            )

            record_id = cur.lastrowid

            conn.commit()

        record["id"] = record_id

        return record

    

    

    def list_objectives(self, status: Optional[str] = None) -> List[Dict[str, Any]]:

        query = "SELECT * FROM corporate_objectives"

        params: List[Any] = []

        if status:

            query += " WHERE status = ?"

            params.append(status)

        query += " ORDER BY created_at DESC"

        with self._connection() as conn:

            cur = conn.cursor()

            cur.execute(query, params)

            rows = cur.fetchall()

        results: List[Dict[str, Any]] = []

        for row in rows:

            payload = dict(row)

            payload["success_metrics"] = json.loads(payload.get("success_metrics") or "{}")

            results.append(payload)

        return results

        

        

    def get_objective_by_source(self, directive_id: int) -> Optional[Dict[str, Any]]:

        with self._connection() as conn:

            cur = conn.cursor()

            cur.execute(

                """

                SELECT * FROM corporate_objectives

                WHERE source_directive_id = ?

                ORDER BY created_at DESC

                LIMIT 1

                """,

                (directive_id,),

            )

            row = cur.fetchone()

        if not row:

            return None

        payload = dict(row)

        payload["success_metrics"] = json.loads(payload.get("success_metrics") or "{}")

        return payload

        

        

    def update_objective_status(self, objective_id: int, status: str) -> None:

        with self._connection() as conn:

            cur = conn.cursor()

            cur.execute(

                """

                UPDATE corporate_objectives

                SET status = ?, updated_at = ?

                WHERE id = ?

                """,

                (status, _utcnow(), objective_id),

            )

            conn.commit()



    # Tasks ----------------------------------------------------------------

    

    def create_task(self, record: Dict[str, Any]) -> Dict[str, Any]:

        with self._connection() as conn:

            cur = conn.cursor()

            cur.execute(

                """

                INSERT INTO department_tasks (

                    objective_id, title, department, assigned_agent, status,

                    priority, due_date, description, dependencies, metadata,

                    created_at, updated_at, completed_at, claimed_by, claimed_at,

                    sla_minutes

                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

                """,

                (

                    record.get("objective_id"),

                    record["title"],

                    record["department"],

                    record.get("assigned_agent"),

                    record["status"],

                    record["priority"],

                    record.get("due_date"),

                    record.get("description"),

                    json.dumps(record.get("dependencies", []), ensure_ascii=False),

                    json.dumps(record.get("metadata", {}), ensure_ascii=False),

                    record["created_at"],

                    record["updated_at"],

                    record.get("completed_at"),

                    record.get("claimed_by"),

                    record.get("claimed_at"),

                    record.get("sla_minutes", 0),

                ),

            )

            task_id = cur.lastrowid

            conn.commit()

        record["id"] = task_id

        return record



    def list_tasks(

        self,

        department: Optional[str] = None,

        status: Optional[str] = None,

        objective_id: Optional[int] = None,

    ) -> List[Dict[str, Any]]:

        query = "SELECT * FROM department_tasks"

        clauses: List[str] = []

        params: List[Any] = []

        if department:

            clauses.append("department = ?")

            params.append(department)

        if status:

            clauses.append("status = ?")

            params.append(status)

        if objective_id is not None:

            clauses.append("objective_id = ?")

            params.append(objective_id)

        if clauses:

            query += " WHERE " + " AND ".join(clauses)

        query += " ORDER BY created_at DESC"

        with self._connection() as conn:

            cur = conn.cursor()

            cur.execute(query, params)

            rows = cur.fetchall()

        tasks: List[Dict[str, Any]] = []

        for row in rows:

            payload = dict(row)

            payload["dependencies"] = json.loads(payload.get("dependencies") or "[]")

            payload["metadata"] = json.loads(payload.get("metadata") or "{}")

            tasks.append(payload)

        return tasks

        

    @staticmethod

    def _priority_rank(priority: Optional[str]) -> int:

        if not priority:

            return 4

        order = {"critical": 0, "high": 1, "medium": 2, "low": 3}

        return order.get(priority.lower(), 4)

        

    def _priority_sort_key(self, task: Dict[str, Any]):

        return (

            self._priority_rank(task.get("priority")),

            task.get("due_date") or "9999-12-31",

            task.get("created_at") or "9999-12-31T00:00:00",

        )

        

    def _dependencies_satisfied(

        self, cursor: sqlite3.Cursor, dependencies: Iterable[Any]

    ) -> bool:

        for dep in dependencies or []:

            try:

                dep_id = int(dep)

            except (TypeError, ValueError):

                return False

            cursor.execute(

                "SELECT status FROM department_tasks WHERE id = ?", (dep_id,)

            )

            row = cursor.fetchone()

            if not row or row[0] != "completed":

                return False

        return True

        

    def list_overdue_tasks(self) -> List[Dict[str, Any]]:

        now = datetime.utcnow()

        with self._connection() as conn:

            cur = conn.cursor()

            cur.execute("SELECT * FROM department_tasks")

            rows = cur.fetchall()



        overdue: List[Dict[str, Any]] = []

        for row in rows:

            record = dict(row)

            record["dependencies"] = json.loads(record.get("dependencies") or "[]")

            record["metadata"] = json.loads(record.get("metadata") or "{}")



            status = record.get("status", "").lower()

            sla_minutes = int(record.get("sla_minutes") or 0)

            claimed_at = record.get("claimed_at")

            due_date = record.get("due_date")

            overdue_flag = False



            if status == "in_progress" and sla_minutes > 0 and claimed_at:

                try:

                    claimed_dt = datetime.fromisoformat(claimed_at)

                    if (now - claimed_dt).total_seconds() > sla_minutes * 60:

                        overdue_flag = True

                        record["overdue_reason"] = "sla_breach"

                except ValueError:

                    overdue_flag = True

                    record["overdue_reason"] = "invalid_claim_timestamp"



            if not overdue_flag and due_date:

                try:

                    due_dt = datetime.fromisoformat(due_date)

                except ValueError:

                    try:

                        due_dt = datetime.strptime(due_date, "%Y-%m-%d")

                    except ValueError:

                        due_dt = None

                if due_dt and due_dt < now and status in {"pending", "in_progress"}:

                    overdue_flag = True

                    record.setdefault("overdue_reason", "past_due")



            if overdue_flag:

                overdue.append(record)



        overdue.sort(key=lambda task: (

            self._priority_rank(task.get("priority")),

            task.get("due_date") or "9999-12-31",

            task.get("claimed_at") or task.get("created_at") or "9999-12-31T00:00:00",

        ))

        return overdue

        

    def list_ready_tasks(

        self, department: Optional[str] = None, limit: int = 10

    ) -> List[Dict[str, Any]]:

        with self._connection() as conn:

            cur = conn.cursor()

            query = "SELECT * FROM department_tasks WHERE status = 'pending'"

            params: List[Any] = []

            if department:

                query += " AND department = ?"

                params.append(department)

            cur.execute(query, params)

            rows = cur.fetchall()



            ready: List[Dict[str, Any]] = []

            for row in rows:

                record = dict(row)

                record["dependencies"] = json.loads(record.get("dependencies") or "[]")

                record["metadata"] = json.loads(record.get("metadata") or "{}")

                if self._dependencies_satisfied(cur, record["dependencies"]):

                    ready.append(record)



            ready.sort(key=self._priority_sort_key)

            return ready[:limit]

            

    def claim_next_task(

        self, department: str, agent: Optional[str] = None

    ) -> Optional[Dict[str, Any]]:

        ready = self.list_ready_tasks(department=department, limit=1)

        if not ready:

            return None

        task = ready[0]

        claimed_by = agent or task.get("assigned_agent") or department

        timestamp = _utcnow()

        with self._connection() as conn:

            cur = conn.cursor()

            cur.execute(

                """

                UPDATE department_tasks

                SET status = 'in_progress',

                    assigned_agent = COALESCE(?, assigned_agent),

                    claimed_by = ?,

                    claimed_at = ?,

                    updated_at = ?

                WHERE id = ?

                """,

                (agent, claimed_by, timestamp, timestamp, task["id"]),

            )

            conn.commit()

        task["status"] = "in_progress"

        if agent:

            task["assigned_agent"] = agent

        task["claimed_by"] = claimed_by

        task["claimed_at"] = timestamp

        return task

        

    def mark_task_in_progress(

        self,

        task_id: int,

        *,

        claimed_by: Optional[str] = None,

        assigned_agent: Optional[str] = None,

    ) -> Dict[str, Any]:

        """Mark a task as in progress without re-running dependency checks."""

        task = self.get_task(task_id)

        if not task:

            raise CorporateMemoryError(f"Task {task_id} not found")

        timestamp = _utcnow()

        target_assigned = task.get("assigned_agent") if assigned_agent is None else assigned_agent

        target_claimed = (

            claimed_by

            or task.get("claimed_by")

            or target_assigned

            or task.get("department")

            or "autonomy_worker"

        )

        with self._connection() as conn:

            cur = conn.cursor()

            cur.execute(

                """

                UPDATE department_tasks

                SET status = 'in_progress',

                    assigned_agent = ?,

                    claimed_by = ?,

                    claimed_at = ?,

                    updated_at = ?

                WHERE id = ?

                """,

                (target_assigned, target_claimed, timestamp, timestamp, task_id),

            )

            conn.commit()

        task["status"] = "in_progress"

        task["assigned_agent"] = target_assigned

        task["claimed_by"] = target_claimed

        task["claimed_at"] = timestamp

        task["updated_at"] = timestamp

        return task

        

    def release_claimed_tasks(self, *, claimed_by: Optional[str] = None) -> int:

        """Return in-progress tasks to pending so automation can resume after restart."""



        timestamp = _utcnow()

        query = """

                UPDATE department_tasks

                SET status = 'pending',

                    claimed_by = NULL,

                    claimed_at = NULL,

                    updated_at = ?

                WHERE status = 'in_progress'

            """

        params: list[Any] = [timestamp]

        if claimed_by is not None:

            query += " AND (claimed_by = ? OR claimed_by IS NULL)"

            params.append(claimed_by)

        with self._connection() as conn:

            cur = conn.cursor()

            cur.execute(query, params)

            conn.commit()

            return cur.rowcount

            

    def release_task(self, task_id: int) -> Optional[Dict[str, Any]]:

        with self._connection() as conn:

            cur = conn.cursor()

            cur.execute(

                """

                UPDATE department_tasks

                SET status = 'pending',

                    claimed_by = NULL,

                    claimed_at = NULL,

                    updated_at = ?

                WHERE id = ?

                """,

                (_utcnow(), task_id),

            )

            conn.commit()

        return self.get_task(task_id)

        

    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:

        with self._connection() as conn:

            cur = conn.cursor()

            cur.execute("SELECT * FROM department_tasks WHERE id = ?", (task_id,))

            row = cur.fetchone()

        if not row:

            return None

        payload = dict(row)

        payload["dependencies"] = json.loads(payload.get("dependencies") or "[]")

        payload["metadata"] = json.loads(payload.get("metadata") or "{}")

        return payload

        

    def mark_task_complete(self, task_id: int) -> None:

        timestamp = _utcnow()

        with self._connection() as conn:

            cur = conn.cursor()

            cur.execute(

                """

                UPDATE department_tasks

                SET status = 'completed', updated_at = ?, completed_at = ?

                WHERE id = ?

                """,

                (timestamp, timestamp, task_id),

            )

            conn.commit()

            

    def append_task_log(self, task_id: int, entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:

        payload = dict(entry)

        payload.setdefault("timestamp", _utcnow())

        with self._connection() as conn:

            cur = conn.cursor()

            cur.execute("SELECT metadata FROM department_tasks WHERE id = ?", (task_id,))

            row = cur.fetchone()

            if not row:

                return None

            metadata = json.loads(row[0] or "{}")

            logs = metadata.setdefault("automation_logs", [])

            logs.append(payload)

            metadata["last_execution"] = payload

            cur.execute(

                """

                UPDATE department_tasks

                SET metadata = ?, updated_at = ?

                WHERE id = ?

                """,

                (json.dumps(metadata, ensure_ascii=False), payload["timestamp"], task_id),

            )

            conn.commit()

        return metadata

        

    def list_recent_automation_logs(self, limit: int = 20) -> List[Dict[str, Any]]:

        """Return most recent automation worker executions across tasks."""



        limit = max(1, int(limit))

        with self._connection() as conn:

            cur = conn.cursor()

            cur.execute(

                """

                SELECT id, title, department, priority, objective_id, metadata

                FROM department_tasks

                WHERE metadata IS NOT NULL AND metadata != ''

                ORDER BY updated_at DESC

                LIMIT ?

                """,

                (limit * 5,),

            )

            rows = cur.fetchall()



        events: List[Dict[str, Any]] = []

        for row in rows:

            metadata = json.loads(row["metadata"] or "{}")

            logs = metadata.get("automation_logs") or []

            if not logs:

                continue

            fallback_timestamp = None

            last_execution = metadata.get("last_execution")

            if isinstance(last_execution, dict):

                fallback_timestamp = last_execution.get("timestamp")

            for entry in logs[-5:]:

                record = dict(entry)

                record.setdefault("timestamp", fallback_timestamp)

                record.setdefault("department", row["department"])

                record.setdefault("priority", row["priority"])

                record.setdefault("title", row["title"])

                record["task_id"] = row["id"]

                record["objective_id"] = row["objective_id"]

                events.append(record)



        def _sort_key(item: Dict[str, Any]) -> str:

            timestamp = item.get("timestamp")

            if isinstance(timestamp, str):

                return timestamp

            if isinstance(timestamp, (int, float)):

                return datetime.utcfromtimestamp(float(timestamp)).strftime(ISO_FORMAT)

            return ""



        events.sort(key=_sort_key, reverse=True)

        return events[:limit]

        

    def mark_task_blocked(

        self,

        task_id: int,

        *,

        reason: str,

        details: Optional[Dict[str, Any]] = None,

    ) -> None:

        timestamp = _utcnow()

        with self._connection() as conn:

            cur = conn.cursor()

            cur.execute(

                """

                UPDATE department_tasks

                SET status = 'blocked', updated_at = ?, completed_at = NULL

                WHERE id = ?

                """,

                (timestamp, task_id),

            )

            if cur.rowcount == 0:

                raise CorporateMemoryError(f"Task {task_id} not found")

            conn.commit()

        log_entry = {"event": "blocked", "reason": reason}

        if details:

            log_entry.update(details)

        self.append_task_log(task_id, log_entry)



    # Knowledge ------------------------------------------------------------

    

    def create_article(self, record: Dict[str, Any]) -> Dict[str, Any]:

        with self._connection() as conn:

            cur = conn.cursor()

            cur.execute(

                """

                INSERT INTO knowledge_articles (

                    title, content, tags, source, related_objective_id,

                    created_at, updated_at

                ) VALUES (?, ?, ?, ?, ?, ?, ?)

                """,

                (

                    record["title"],

                    record["content"],

                    record.get("tags"),

                    record.get("source"),

                    record.get("related_objective_id"),

                    record["created_at"],

                    record["updated_at"],

                ),

            )

            article_id = cur.lastrowid

            conn.commit()

        record["id"] = article_id

        return record



    def list_articles(self, tag: Optional[str] = None) -> List[Dict[str, Any]]:

        query = "SELECT * FROM knowledge_articles"

        params: List[Any] = []

        if tag:

            query += " WHERE tags LIKE ?"

            params.append(f"%{tag}%")

        query += " ORDER BY created_at DESC"

        with self._connection() as conn:

            cur = conn.cursor()

            cur.execute(query, params)

            rows = cur.fetchall()

        return [dict(row) for row in rows]

        

@dataclass
class Objective:
    title: str
    owner: str
    priority: str
    status: str = "planned"
    description: Optional[str] = None
    success_metrics: Optional[Dict[str, Any]] = None
    start_date: Optional[str] = None
    due_date: Optional[str] = None
    source_directive_id: Optional[int] = None

    def to_record(self) -> Dict[str, Any]:
        now = _utcnow()
        data = asdict(self)
        data.update({"created_at": now, "updated_at": now})
        return data


@dataclass
class Task:
    title: str
    department: str
    status: str = "pending"
    priority: str = "medium"
    objective_id: Optional[int] = None
    assigned_agent: Optional[str] = None
    due_date: Optional[str] = None
    description: Optional[str] = None
    dependencies: Optional[Iterable[Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    completed_at: Optional[str] = None
    claimed_by: Optional[str] = None
    claimed_at: Optional[str] = None
    sla_minutes: int = 0

    def to_record(self) -> Dict[str, Any]:
        now = _utcnow()
        data = asdict(self)
        data.update({"created_at": now, "updated_at": now})
        if data["dependencies"] is None:
            data["dependencies"] = []
        if data["metadata"] is None:
            data["metadata"] = {}
        return data


@dataclass
class KnowledgeArticle:
    title: str
    content: str
    tags: Optional[str] = None
    source: Optional[str] = None
    related_objective_id: Optional[int] = None

    def to_record(self) -> Dict[str, Any]:
        now = _utcnow()
        data = asdict(self)
        data.update({"created_at": now, "updated_at": now})
        return data

def get_latest_earnetics_vision(
    conn: Optional[sqlite3.Connection] = None,
) -> Optional[Dict[str, Any]]:
    """
    Return the latest *active* Earnetics vision directive as a dict, with payload parsed.
    Filters out archived directives and only uses directive_type='earnetics_vision'.
    """
    close_conn = False
    if conn is None:
        conn = sqlite3.connect(BUSINESS_DB_PATH)
        conn.row_factory = sqlite3.Row
        close_conn = True

    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, title, directive_type, owner, status,
               payload, due_date, created_at, updated_at
        FROM executive_directives
        WHERE directive_type = 'earnetics_vision'
          AND (status IS NULL OR status != 'archived')
        ORDER BY created_at DESC
        LIMIT 1
        """
    )
    row = cur.fetchone()

    if close_conn:
        conn.close()

    if not row:
        return None

    d = dict(row)
    try:
        d["payload"] = json.loads(d["payload"])
    except Exception:
        d["payload"] = None
    return d




__all__ = [
    "CorporateMemory",
    "CorporateMemoryError",
    "Objective",
    "Task",
    "KnowledgeArticle",
    "get_latest_earnetics_vision",
]

