import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class AtomEvolutionEngine:
    def __init__(self, audit_log="audit_log.db", doctrine_memory="vector_memory.db", evolution_db="agent_evolution.db"):
        self.audit_log = audit_log
        self.doctrine_memory = doctrine_memory
        self.evolution_db = evolution_db
        self._ensure_evolution_schema()

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

    def _ensure_evolution_schema(self):
        """Create evolution database schema for storing learning insights."""
        conn = sqlite3.connect(self.evolution_db)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evolution_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent TEXT NOT NULL,
                action_type TEXT NOT NULL,
                insight_type TEXT NOT NULL,
                insight_text TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                learned_at TEXT NOT NULL,
                applied INTEGER DEFAULT 0
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_knowledge (
                agent TEXT PRIMARY KEY,
                knowledge_base TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                total_insights INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.0
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evolution_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                agent TEXT,
                action TEXT,
                feedback_type TEXT,
                feedback_text TEXT,
                impact_score REAL
            )
        """)
        conn.commit()
        conn.close()
    
    def learn_from_action(self, agent: str, action: str, context: str, status: str, details: Optional[Dict] = None):
        """Learn from a single action immediately and provide feedback."""
        try:
            feedback = self._extract_insights(agent, action, context, status, details)
            if feedback:
                self._store_feedback(feedback)
                self._update_agent_knowledge(agent, feedback)
                return feedback
        except Exception as e:
            logger.error(f"Error learning from action: {e}")
        return None
    
    def _extract_insights(self, agent: str, action: str, context: str, status: str, details: Optional[Dict] = None) -> Optional[Dict]:
        """Extract learning insights from an action."""
        feedback_type = "positive" if status == "success" else "negative" if status == "error" else "neutral"
        
        # Analyze action patterns
        insights = []
        impact_score = 0.0
        
        if status == "success":
            if "product.created" in action or "product" in action.lower():
                insights.append(f"{agent} successfully created products. Pattern: Focus on validated opportunities with clear pricing.")
                impact_score = 0.8
            elif "revenue" in action.lower() or "sales" in action.lower():
                insights.append(f"{agent} generated revenue activity. Pattern: Market context analysis followed by execution works well.")
                impact_score = 0.7
            elif "workflow" in action.lower() or "cycle" in action.lower():
                insights.append(f"{agent} completed workflow successfully. Pattern: Structured workflows with clear steps improve success rates.")
                impact_score = 0.6
            elif "strategy" in action.lower():
                insights.append(f"{agent} executed strategic action. Pattern: Data-driven strategies lead to better outcomes.")
                impact_score = 0.7
        elif status == "error":
            insights.append(f"{agent} encountered error in {action}. Learning: Investigate context for failure patterns.")
            impact_score = -0.3
        else:
            insights.append(f"{agent} executed {action}. Monitoring for outcomes.")
            impact_score = 0.1
        
        # Extract specific patterns from context/details
        if details:
            if "product_id" in details:
                insights.append(f"Product creation successful. ID: {details.get('product_id')}. Replicate successful product generation patterns.")
            if "price" in details:
                price = details.get("price", 0)
                if price > 0:
                    insights.append(f"Successfully priced product at ${price}. This price point appears viable.")
        
        if not insights:
            return None
        
        feedback_text = " | ".join(insights)
        
        return {
            "agent": agent,
            "action": action,
            "feedback_type": feedback_type,
            "feedback_text": feedback_text,
            "impact_score": impact_score,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _store_feedback(self, feedback: Dict):
        """Store feedback in evolution database."""
        conn = sqlite3.connect(self.evolution_db)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO evolution_feedback (timestamp, agent, action, feedback_type, feedback_text, impact_score)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            feedback["timestamp"],
            feedback["agent"],
            feedback["action"],
            feedback["feedback_type"],
            feedback["feedback_text"],
            feedback["impact_score"]
        ))
        conn.commit()
        conn.close()
    
    def _update_agent_knowledge(self, agent: str, feedback: Dict):
        """Update agent's knowledge base with new insights."""
        conn = sqlite3.connect(self.evolution_db)
        cursor = conn.cursor()
        
        # Get existing knowledge
        cursor.execute("SELECT knowledge_base, total_insights, success_rate FROM agent_knowledge WHERE agent = ?", (agent,))
        row = cursor.fetchone()
        
        if row:
            existing_knowledge = json.loads(row[0] or "{}")
            total_insights = row[1] + 1
            # Simple success rate calculation
            current_rate = row[2] or 0.0
            if feedback["feedback_type"] == "positive":
                new_rate = (current_rate * (total_insights - 1) + 1.0) / total_insights
            else:
                new_rate = (current_rate * (total_insights - 1)) / total_insights
        else:
            existing_knowledge = {}
            total_insights = 1
            new_rate = 1.0 if feedback["feedback_type"] == "positive" else 0.0
        
        # Update knowledge base with new insight
        if "insights" not in existing_knowledge:
            existing_knowledge["insights"] = []
        existing_knowledge["insights"].append({
            "text": feedback["feedback_text"],
            "type": feedback["feedback_type"],
            "learned_at": feedback["timestamp"],
            "impact": feedback["impact_score"]
        })
        # Keep only last 50 insights
        existing_knowledge["insights"] = existing_knowledge["insights"][-50:]
        
        # Update or insert
        cursor.execute("""
            INSERT OR REPLACE INTO agent_knowledge (agent, knowledge_base, last_updated, total_insights, success_rate)
            VALUES (?, ?, ?, ?, ?)
        """, (
            agent,
            json.dumps(existing_knowledge),
            datetime.utcnow().isoformat(),
            total_insights,
            new_rate
        ))
        conn.commit()
        conn.close()
    
    def get_agent_knowledge(self, agent: str) -> Dict:
        """Get current knowledge base for an agent."""
        conn = sqlite3.connect(self.evolution_db)
        cursor = conn.cursor()
        cursor.execute("SELECT knowledge_base, total_insights, success_rate, last_updated FROM agent_knowledge WHERE agent = ?", (agent,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "agent": agent,
                "knowledge_base": json.loads(row[0] or "{}"),
                "total_insights": row[1] or 0,
                "success_rate": row[2] or 0.0,
                "last_updated": row[3]
            }
        return {
            "agent": agent,
            "knowledge_base": {},
            "total_insights": 0,
            "success_rate": 0.0,
            "last_updated": None
        }
    
    def get_recent_feedback(self, limit: int = 50, agent: Optional[str] = None) -> List[Dict]:
        """Get recent evolution feedback."""
        conn = sqlite3.connect(self.evolution_db)
        cursor = conn.cursor()
        
        if agent:
            cursor.execute("""
                SELECT timestamp, agent, action, feedback_type, feedback_text, impact_score
                FROM evolution_feedback
                WHERE agent = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (agent, limit))
        else:
            cursor.execute("""
                SELECT timestamp, agent, action, feedback_type, feedback_text, impact_score
                FROM evolution_feedback
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "timestamp": row[0],
                "agent": row[1],
                "action": row[2],
                "feedback_type": row[3],
                "feedback_text": row[4],
                "impact_score": row[5]
            }
            for row in rows
        ]
    
    def get_evolution_summary(self) -> Dict:
        """Get overall evolution summary."""
        conn = sqlite3.connect(self.evolution_db)
        cursor = conn.cursor()
        
        # Total feedback count
        cursor.execute("SELECT COUNT(*) FROM evolution_feedback")
        total_feedback = cursor.fetchone()[0]
        
        # By feedback type
        cursor.execute("SELECT feedback_type, COUNT(*) FROM evolution_feedback GROUP BY feedback_type")
        by_type = {row[0]: row[1] for row in cursor.fetchall()}
        
        # By agent
        cursor.execute("SELECT agent, COUNT(*) FROM evolution_feedback GROUP BY agent")
        by_agent = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Average impact score
        cursor.execute("SELECT AVG(impact_score) FROM evolution_feedback")
        avg_impact = cursor.fetchone()[0] or 0.0
        
        # Agent knowledge stats
        cursor.execute("SELECT COUNT(*), AVG(success_rate) FROM agent_knowledge")
        knowledge_stats = cursor.fetchone()
        agent_count = knowledge_stats[0] or 0
        avg_success_rate = knowledge_stats[1] or 0.0
        
        conn.close()
        
        return {
            "total_feedback": total_feedback,
            "by_type": by_type,
            "by_agent": by_agent,
            "average_impact_score": round(avg_impact, 2),
            "agents_tracked": agent_count,
            "average_success_rate": round(avg_success_rate, 2),
            "status": "active" if total_feedback > 0 else "learning"
        }
    
    def full_evolution_cycle(self):
        """Full evolution cycle - analyze performance and propose updates."""
        report = self.analyze_performance()
        proposed = self.propose_doctrine_adjustments(report)
        result = self.evolve_doctrine(proposed)
        summary = self.get_evolution_summary()
        return {
            "performance_report": report,
            "doctrine_updates": proposed,
            "update_result": result,
            "evolution_summary": summary
        }
