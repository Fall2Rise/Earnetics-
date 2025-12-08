import sqlite3
from datetime import datetime

class AtomEvolutionEngine:
    def __init__(self, audit_log="audit_log.db", doctrine_memory="vector_memory.db"):
        self.audit_log = audit_log
        self.doctrine_memory = doctrine_memory

    def analyze_performance(self, timeframe_days=7):
        conn = sqlite3.connect(self.audit_log)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT agent, action, context, timestamp
            FROM audit_log
            WHERE timestamp >= datetime('now', ?)
        """, (f'-{timeframe_days} days',))
        results = cursor.fetchall()
        conn.close()

        summary = {
            "total_actions": len(results),
            "by_agent": {},
            "failures": [],
            "successes": []
        }

        for row in results:
            agent, action, context, timestamp = row
            summary["by_agent"].setdefault(agent, 0)
            summary["by_agent"][agent] += 1

            if "fail" in action.lower() or "error" in context.lower():
                summary["failures"].append(row)
            elif "success" in action.lower() or "completed" in context.lower():
                summary["successes"].append(row)

        return summary

    def propose_doctrine_adjustments(self, performance_summary):
        directives = []

        if performance_summary["failures"]:
            directives.append("Reduce execution frequency on failing agents.")
            directives.append("Implement retry limits and fallback workflows.")

        if performance_summary["successes"]:
            directives.append("Increase priority on high-ROI directives.")
            directives.append("Clone successful workflows across departments.")

        return directives

    def evolve_doctrine(self, proposed_directives):
        conn = sqlite3.connect(self.doctrine_memory)
        cursor = conn.cursor()
        for directive in proposed_directives:
            cursor.execute("""
                INSERT INTO vectors (title, content, tag)
                VALUES (?, ?, ?)
            """, ("New Doctrine Directive", directive, "doctrine_mutation"))
        conn.commit()
        conn.close()
        return {"mutations": len(proposed_directives), "status": "Doctrine updated"}

    def full_evolution_cycle(self):
        report = self.analyze_performance()
        proposed = self.propose_doctrine_adjustments(report)
        result = self.evolve_doctrine(proposed)
        return {
            "performance_report": report,
            "doctrine_updates": proposed,
            "update_result": result
        }
