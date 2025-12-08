import sqlite3
from datetime import datetime
from backend.atom_doctrine import ATOM_DOCTRINE

class AtomStrategicPlanner:
    def __init__(self, db_path="business_database.db", vector_db="vector_memory.db", audit_log="audit_log.db"):
        self.db_path = db_path
        self.vector_db = vector_db
        self.audit_log = audit_log
        self.directives = ATOM_DOCTRINE["directives"]

    def run_planning_cycle(self):
        opportunities = self._scan_for_opportunities()
        planned_actions = []

        for opp in opportunities:
            strategy = self._convert_opportunity_to_plan(opp)
            self._inject_strategy(strategy["title"], strategy["content"])
            planned_actions.append(strategy)

        self._log(f"Planned {len(planned_actions)} new strategic actions.")
        return planned_actions

    def _scan_for_opportunities(self):
        conn = sqlite3.connect(self.vector_db)
        cursor = conn.cursor()
        cursor.execute("SELECT title, content FROM vectors WHERE tag='missed_opportunity'")
        data = cursor.fetchall()
        conn.close()
        return [{"title": row[0], "content": row[1]} for row in data]

    def _convert_opportunity_to_plan(self, opp):
        return {
            "title": f"Capitalize: {opp['title']}",
            "content": f"Opportunity detected: {opp['content']}. Injecting into workflow for monetization."
        }

    def _inject_strategy(self, title, content):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO workflows (title, description, status, created_by, created_at)
            VALUES (?, ?, 'pending', 'ATOM_PLANNER', ?)
        """, (title, content, datetime.utcnow()))
        conn.commit()
        conn.close()

    def _log(self, message):
        conn = sqlite3.connect(self.audit_log)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audit_log (timestamp, agent, action, context)
            VALUES (?, ?, ?, ?)
        """, (datetime.utcnow(), "ATOM_PLANNER", "planning_cycle", message))
        conn.commit()
        conn.close()
