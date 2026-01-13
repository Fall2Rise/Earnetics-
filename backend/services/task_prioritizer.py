"""
Intelligent Task Prioritization Service
Prioritizes tasks based on revenue impact, dependencies, and success rates
"""
import sqlite3
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from backend.services.performance_monitor import get_performance_monitor

logger = logging.getLogger(__name__)

class TaskPrioritizer:
    """Intelligent task prioritization based on multiple factors"""
    
    def __init__(self, db_path: str = "business_database.db"):
        self.db_path = db_path
        self.performance_monitor = get_performance_monitor()
    
    def calculate_priority_score(
        self,
        task: Dict[str, Any],
        agent_name: Optional[str] = None
    ) -> float:
        """Calculate priority score (0-100) for a task"""
        score = 0.0
        
        # Base priority (0-40 points)
        priority_map = {"critical": 40, "high": 30, "medium": 20, "low": 10}
        base_priority = task.get("priority", "medium").lower()
        score += priority_map.get(base_priority, 20)
        
        # Revenue impact (0-30 points)
        revenue_impact = task.get("metadata", {}).get("revenue_impact", 0.0)
        if revenue_impact > 0:
            # Scale: $1000 = 10 points, $5000 = 20 points, $10000+ = 30 points
            score += min(30, (revenue_impact / 1000) * 10)
        
        # Agent success rate (0-20 points)
        if agent_name:
            success_rate_data = self.performance_monitor.get_success_rate(
                agent_name,
                task.get("title", "unknown")
            )
            success_rate = success_rate_data.get("success_rate", 0.5)
            # Higher success rate = higher priority (agent is reliable)
            score += success_rate * 20
        
        # Dependency status (0-10 points)
        dependencies = task.get("dependencies", [])
        if not dependencies:
            score += 10  # No dependencies = can start immediately
        else:
            # Check if dependencies are complete
            completed_deps = self._check_dependencies_complete(dependencies)
            if completed_deps == len(dependencies):
                score += 10
            elif completed_deps > 0:
                score += 5  # Partial completion
        
        # Urgency (due date proximity) (0-10 points)
        due_date = task.get("due_date")
        if due_date:
            try:
                due = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                now = datetime.now(timezone.utc)
                hours_until_due = (due - now).total_seconds() / 3600
                
                if hours_until_due < 0:
                    score += 10  # Overdue - highest urgency
                elif hours_until_due < 24:
                    score += 8  # Due today
                elif hours_until_due < 72:
                    score += 5  # Due in 3 days
                elif hours_until_due < 168:
                    score += 2  # Due in a week
            except:
                pass
        
        return min(100.0, score)
    
    def _check_dependencies_complete(self, dependency_ids: List[int]) -> int:
        """Check how many dependencies are complete"""
        if not dependency_ids:
            return 0
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                placeholders = ','.join('?' * len(dependency_ids))
                rows = conn.execute(f"""
                    SELECT COUNT(*) as completed
                    FROM department_tasks
                    WHERE id IN ({placeholders}) AND status = 'completed'
                """, dependency_ids).fetchone()
                
                return rows['completed'] if rows else 0
        except Exception as e:
            logger.error(f"Error checking dependencies: {e}")
            return 0
    
    def prioritize_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize a list of tasks"""
        prioritized = []
        
        for task in tasks:
            agent_name = task.get("assigned_agent")
            priority_score = self.calculate_priority_score(task, agent_name)
            
            prioritized.append({
                **task,
                "priority_score": priority_score,
                "calculated_at": datetime.now(timezone.utc).isoformat()
            })
        
        # Sort by priority score (descending)
        prioritized.sort(key=lambda x: x.get("priority_score", 0), reverse=True)
        
        return prioritized
    
    def get_recommended_next_task(
        self,
        department: Optional[str] = None,
        agent_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get the highest priority task for a department/agent"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                query = "SELECT * FROM department_tasks WHERE status = 'pending'"
                params = []
                
                if department:
                    query += " AND department = ?"
                    params.append(department)
                
                if agent_name:
                    query += " AND (assigned_agent = ? OR assigned_agent IS NULL)"
                    params.append(agent_name)
                
                query += " ORDER BY created_at ASC"
                
                rows = conn.execute(query, params).fetchall()
                tasks = [dict(row) for row in rows]
                
                # Parse JSON fields
                for task in tasks:
                    task["dependencies"] = json.loads(task.get("dependencies") or "[]")
                    task["metadata"] = json.loads(task.get("metadata") or "{}")
                
                if not tasks:
                    return None
                
                # Prioritize and return top task
                prioritized = self.prioritize_tasks(tasks)
                return prioritized[0] if prioritized else None
                
        except Exception as e:
            logger.error(f"Error getting recommended task: {e}")
            return None


# Global instance
_prioritizer: Optional[TaskPrioritizer] = None

def get_task_prioritizer() -> TaskPrioritizer:
    """Get global task prioritizer instance"""
    global _prioritizer
    if _prioritizer is None:
        _prioritizer = TaskPrioritizer()
    return _prioritizer
