"""
Performance Monitoring Service
Tracks system health, bottlenecks, and success rates for optimization
"""
import sqlite3
import time
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from pathlib import Path
import json

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Single performance measurement"""
    timestamp: datetime
    metric_type: str  # 'api_call', 'database_query', 'agent_action', 'task_execution'
    name: str
    duration_ms: float
    success: bool
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class Bottleneck:
    """Identified performance bottleneck"""
    metric_type: str
    name: str
    avg_duration_ms: float
    p95_duration_ms: float
    failure_rate: float
    call_count: int
    recommendation: str

class PerformanceMonitor:
    """Monitors system performance and identifies bottlenecks"""
    
    def __init__(self, db_path: str = "performance_metrics.db"):
        self.db_path = db_path
        self._ensure_schema()
        self._recent_metrics: deque = deque(maxlen=1000)  # In-memory buffer
        self._success_rates: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
    def _ensure_schema(self):
        """Create database schema for performance metrics"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    duration_ms REAL NOT NULL,
                    success INTEGER NOT NULL,
                    error TEXT,
                    metadata TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_timestamp 
                ON performance_metrics(timestamp)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_type_name 
                ON performance_metrics(metric_type, name)
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS success_rates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_name TEXT,
                    action_type TEXT,
                    success_count INTEGER DEFAULT 0,
                    failure_count INTEGER DEFAULT 0,
                    total_revenue_impact REAL DEFAULT 0.0,
                    last_updated TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_success_rates_unique 
                ON success_rates(agent_name, action_type)
            """)
            
            conn.commit()
    
    def record_metric(
        self,
        metric_type: str,
        name: str,
        duration_ms: float,
        success: bool = True,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record a performance metric"""
        metric = PerformanceMetric(
            timestamp=datetime.now(timezone.utc),
            metric_type=metric_type,
            name=name,
            duration_ms=duration_ms,
            success=success,
            error=error,
            metadata=metadata or {}
        )
        
        # Add to in-memory buffer
        self._recent_metrics.append(metric)
        
        # Persist to database (async write in production)
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO performance_metrics 
                    (timestamp, metric_type, name, duration_ms, success, error, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    metric.timestamp.isoformat(),
                    metric_type,
                    name,
                    duration_ms,
                    1 if success else 0,
                    error,
                    json.dumps(metadata) if metadata else None
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to record metric: {e}")
    
    def update_success_rate(
        self,
        agent_name: str,
        action_type: str,
        success: bool,
        revenue_impact: float = 0.0
    ):
        """Update success rate tracking for an agent/action"""
        key = f"{agent_name}:{action_type}"
        self._success_rates[key].append(success)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                if success:
                    conn.execute("""
                        INSERT INTO success_rates (agent_name, action_type, success_count, total_revenue_impact)
                        VALUES (?, ?, 1, ?)
                        ON CONFLICT(agent_name, action_type) DO UPDATE SET
                            success_count = success_count + 1,
                            total_revenue_impact = total_revenue_impact + ?,
                            last_updated = CURRENT_TIMESTAMP
                    """, (agent_name, action_type, revenue_impact, revenue_impact))
                else:
                    conn.execute("""
                        INSERT INTO success_rates (agent_name, action_type, failure_count)
                        VALUES (?, ?, 1)
                        ON CONFLICT(agent_name, action_type) DO UPDATE SET
                            failure_count = failure_count + 1,
                            last_updated = CURRENT_TIMESTAMP
                    """, (agent_name, action_type))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to update success rate: {e}")
    
    def get_success_rate(self, agent_name: str, action_type: str) -> Dict[str, Any]:
        """Get success rate for an agent/action"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("""
                SELECT success_count, failure_count, total_revenue_impact
                FROM success_rates
                WHERE agent_name = ? AND action_type = ?
            """, (agent_name, action_type)).fetchone()
            
            if row:
                total = row['success_count'] + row['failure_count']
                return {
                    "success_rate": row['success_count'] / total if total > 0 else 0.0,
                    "total_actions": total,
                    "success_count": row['success_count'],
                    "failure_count": row['failure_count'],
                    "total_revenue_impact": row['total_revenue_impact'] or 0.0,
                    "avg_revenue_per_success": (
                        row['total_revenue_impact'] / row['success_count'] 
                        if row['success_count'] > 0 else 0.0
                    )
                }
            return {
                "success_rate": 0.0,
                "total_actions": 0,
                "success_count": 0,
                "failure_count": 0,
                "total_revenue_impact": 0.0,
                "avg_revenue_per_success": 0.0
            }
    
    def detect_bottlenecks(self, timeframe_hours: int = 24) -> List[Bottleneck]:
        """Detect performance bottlenecks"""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=timeframe_hours)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT 
                    metric_type,
                    name,
                    AVG(duration_ms) as avg_duration,
                    COUNT(*) as call_count,
                    SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failure_count
                FROM performance_metrics
                WHERE timestamp >= ?
                GROUP BY metric_type, name
                HAVING call_count >= 5
                ORDER BY avg_duration DESC
                LIMIT 20
            """, (cutoff.isoformat(),)).fetchall()
            
            bottlenecks = []
            for row in rows:
                # Get P95 duration
                p95_row = conn.execute("""
                    SELECT duration_ms
                    FROM performance_metrics
                    WHERE metric_type = ? AND name = ? AND timestamp >= ?
                    ORDER BY duration_ms DESC
                    LIMIT 1 OFFSET CAST(COUNT(*) * 0.05 AS INTEGER)
                """, (row['metric_type'], row['name'], cutoff.isoformat())).fetchone()
                
                p95_duration = p95_row['duration_ms'] if p95_row else row['avg_duration']
                failure_rate = row['failure_count'] / row['call_count'] if row['call_count'] > 0 else 0.0
                
                # Generate recommendation
                recommendation = self._generate_recommendation(
                    row['metric_type'],
                    row['avg_duration'],
                    failure_rate
                )
                
                bottlenecks.append(Bottleneck(
                    metric_type=row['metric_type'],
                    name=row['name'],
                    avg_duration_ms=row['avg_duration'],
                    p95_duration_ms=p95_duration,
                    failure_rate=failure_rate,
                    call_count=row['call_count'],
                    recommendation=recommendation
                ))
        
        return bottlenecks
    
    def _generate_recommendation(
        self,
        metric_type: str,
        avg_duration_ms: float,
        failure_rate: float
    ) -> str:
        """Generate optimization recommendation"""
        if failure_rate > 0.3:
            return f"High failure rate ({failure_rate:.1%}). Review error logs and add retry logic."
        
        if metric_type == "database_query" and avg_duration_ms > 100:
            return "Slow database query. Add index or optimize query structure."
        
        if metric_type == "api_call" and avg_duration_ms > 1000:
            return "Slow API call. Consider caching or rate limiting."
        
        if metric_type == "agent_action" and avg_duration_ms > 5000:
            return "Agent action taking too long. Break into smaller steps or optimize LLM calls."
        
        if avg_duration_ms > 2000:
            return "Consider caching or parallel processing."
        
        return "Performance is acceptable."
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall system health status"""
        bottlenecks = self.detect_bottlenecks(timeframe_hours=1)
        recent_metrics = [m for m in self._recent_metrics 
                         if (datetime.now(timezone.utc) - m.timestamp).total_seconds() < 3600]
        
        if not recent_metrics:
            return {
                "status": "unknown",
                "message": "No recent metrics available",
                "bottlenecks": []
            }
        
        avg_duration = sum(m.duration_ms for m in recent_metrics) / len(recent_metrics)
        success_rate = sum(1 for m in recent_metrics if m.success) / len(recent_metrics)
        
        # Determine health status
        if success_rate < 0.7 or len(bottlenecks) > 5:
            status = "critical"
        elif success_rate < 0.85 or len(bottlenecks) > 2:
            status = "warning"
        else:
            status = "healthy"
        
        return {
            "status": status,
            "avg_duration_ms": avg_duration,
            "success_rate": success_rate,
            "total_metrics_last_hour": len(recent_metrics),
            "bottlenecks": [asdict(b) for b in bottlenecks[:5]],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def get_top_performers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top performing agents/actions by success rate and revenue"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT 
                    agent_name,
                    action_type,
                    success_count,
                    failure_count,
                    total_revenue_impact,
                    (CAST(success_count AS FLOAT) / (success_count + failure_count)) as success_rate
                FROM success_rates
                WHERE (success_count + failure_count) >= 5
                ORDER BY 
                    success_rate DESC,
                    total_revenue_impact DESC
                LIMIT ?
            """, (limit,)).fetchall()
            
            return [
                {
                    "agent": row['agent_name'],
                    "action": row['action_type'],
                    "success_rate": row['success_rate'],
                    "total_actions": row['success_count'] + row['failure_count'],
                    "revenue_impact": row['total_revenue_impact'] or 0.0
                }
                for row in rows
            ]


# Global instance
_performance_monitor: Optional[PerformanceMonitor] = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor
