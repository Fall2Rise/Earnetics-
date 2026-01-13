#!/usr/bin/env python3
"""Comprehensive diagnostic of agent activity and task completion"""
import sys
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 80)
print("COMPREHENSIVE AGENT ACTIVITY DIAGNOSTIC")
print("=" * 80)
print(f"Time: {datetime.now()}\n")

# 1. Check Agent Status and Activity
print("1. AGENT STATUS & ACTIVITY")
print("-" * 80)
try:
    from backend.real_ai_agents import AIRevenueAgentCorporation
    corporation = AIRevenueAgentCorporation()
    agents = corporation.agents
    
    print(f"Total Agents: {len(agents)}")
    active_count = 0
    idle_count = 0
    
    for name, agent in agents.items():
        # Check if agent has recent activity
        status = "active" if hasattr(agent, 'last_activity') else "unknown"
        print(f"  {name}: {status}")
        if hasattr(agent, 'division'):
            print(f"    Division: {agent.division}")
        if hasattr(agent, 'role'):
            print(f"    Role: {agent.role}")
    
    print()
except Exception as e:
    print(f"  ERROR: {e}\n")

# 2. Check Workflow Queue Activity
print("2. WORKFLOW QUEUE ACTIVITY")
print("-" * 80)
try:
    from autonomous.workflow_queue import WorkflowQueueRepository
    repo = WorkflowQueueRepository()
    
    # Check pending
    pending_count = repo.count_pending()
    print(f"Pending Workflows: {pending_count}")
    
    # Check completed in last 24 hours
    with repo._connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM autonomy_task_queue 
            WHERE status = 'completed' 
            AND updated_at > datetime('now', '-24 hours')
        """)
        completed_24h = cursor.fetchone()[0]
        print(f"Completed in last 24h: {completed_24h}")
        
        # Get recent completed tasks
        cursor.execute("""
            SELECT task_id, department, priority, updated_at, metadata
            FROM autonomy_task_queue 
            WHERE status = 'completed' 
            ORDER BY updated_at DESC 
            LIMIT 10
        """)
        print("\nRecent Completed Tasks:")
        for row in cursor.fetchall():
            metadata = row['metadata'] or '{}'
            print(f"  - Task {row['task_id']}: {row['department']} ({row['priority']}) - {row['updated_at']}")
    
    print()
except Exception as e:
    print(f"  ERROR: {e}\n")

# 3. Check Corporate Memory - Tasks and Objectives
print("3. CORPORATE MEMORY - TASKS & OBJECTIVES")
print("-" * 80)
try:
    from backend.corporate_memory import CorporateMemory
    corp_mem = CorporateMemory()
    
    # Get all tasks
    all_tasks = corp_mem.list_tasks()
    print(f"Total Tasks: {len(all_tasks)}")
    
    # Group by status
    by_status = defaultdict(list)
    for task in all_tasks:
        status = task.get('status', 'unknown')
        by_status[status].append(task)
    
    for status, tasks in by_status.items():
        print(f"  {status}: {len(tasks)}")
        # Show recent tasks
        recent = sorted(tasks, key=lambda t: t.get('created_at', ''), reverse=True)[:3]
        for task in recent:
            title = task.get('title', 'Untitled')[:50]
            dept = task.get('department', 'Unknown')
            print(f"    - {title} ({dept})")
    
    # Get objectives
    objectives = corp_mem.list_objectives()
    print(f"\nTotal Objectives: {len(objectives)}")
    for obj in objectives[:5]:
        title = obj.get('title', 'Untitled')[:50]
        status = obj.get('status', 'unknown')
        print(f"  - {title} ({status})")
    
    print()
except Exception as e:
    print(f"  ERROR: {e}\n")

# 4. Check Audit Log for Agent Actions
print("4. RECENT AGENT ACTIONS (Audit Log)")
print("-" * 80)
try:
    from backend.audit_log import AuditLog
    audit = AuditLog()
    
    # Get recent events
    recent_events = audit.get_recent_events(limit=20)
    print(f"Recent Events: {len(recent_events)}")
    
    # Group by agent
    by_agent = defaultdict(list)
    for event in recent_events:
        agent = event.get('agent', 'system')
        by_agent[agent].append(event)
    
    for agent, events in list(by_agent.items())[:10]:
        print(f"\n  {agent}: {len(events)} events")
        for event in events[:3]:
            event_type = event.get('event_type', 'unknown')
            message = event.get('message', '')[:60]
            timestamp = event.get('timestamp', '')[:19]
            print(f"    - [{timestamp}] {event_type}: {message}")
    
    print()
except Exception as e:
    print(f"  ERROR: {e}\n")

# 5. Check Revenue Generation
print("5. REVENUE GENERATION")
print("-" * 80)
try:
    from backend.database import get_database_connection
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # Check products
    cursor.execute("SELECT COUNT(*) FROM products")
    product_count = cursor.fetchone()[0]
    print(f"Total Products: {product_count}")
    
    # Check revenue
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE status = 'completed'")
    total_revenue = cursor.fetchone()[0] or 0
    print(f"Total Revenue: ${total_revenue:.2f}")
    
    # Recent transactions
    cursor.execute("""
        SELECT amount, status, created_at 
        FROM transactions 
        ORDER BY created_at DESC 
        LIMIT 5
    """)
    print("\nRecent Transactions:")
    for row in cursor.fetchall():
        print(f"  - ${row[0]:.2f} ({row[1]}) - {row[2]}")
    
    conn.close()
    print()
except Exception as e:
    print(f"  ERROR: {e}\n")

# 6. Check Factory Engine Activity
print("6. FACTORY ENGINE - PRODUCT STREAMS")
print("-" * 80)
try:
    from backend.factory_engine import FACTORY_ENGINE
    streams = FACTORY_ENGINE.list_streams()
    print(f"Total Streams: {len(streams)}")
    
    by_stage = defaultdict(list)
    for stream in streams:
        stage = stream.get('stage', 'UNKNOWN')
        by_stage[stage].append(stream)
    
    for stage, stream_list in by_stage.items():
        print(f"  {stage}: {len(stream_list)}")
        for stream in stream_list[:3]:
            name = stream.get('name', 'Unknown')[:40]
            progress = stream.get('progress', 0)
            print(f"    - {name} ({progress}%)")
    
    print()
except Exception as e:
    print(f"  ERROR: {e}\n")

# 7. Check Scheduler Activity
print("7. SCHEDULER - JOB EXECUTION")
print("-" * 80)
try:
    from backend.workflow_scheduler import scheduler as workflow_scheduler
    
    jobs = workflow_scheduler.list_jobs()
    print(f"Scheduled Jobs: {len(jobs)}")
    
    for job in jobs:
        print(f"  - {job.id}: {job.handler}")
        print(f"    Schedule: {job.schedule_type} every {job.schedule_value}s")
        if job.last_run:
            print(f"    Last Run: {job.last_run}")
        print(f"    Next Run: {job.next_run}")
        print(f"    Status: {job.status}")
    
    # Check due jobs
    due = workflow_scheduler.due_jobs()
    print(f"\nDue Jobs Right Now: {len(due)}")
    
    print()
except Exception as e:
    print(f"  ERROR: {e}\n")

# 8. Check Autonomy Worker Activity
print("8. AUTONOMY WORKER - TASK PROCESSING")
print("-" * 80)
try:
    # Check if worker is running
    from backend.main_server import app
    worker = getattr(app.state, 'autonomy_worker', None)
    
    if worker:
        print(f"Worker Status: {'Running' if worker.is_running() else 'Stopped'}")
        if hasattr(worker, 'worker_id'):
            print(f"Worker ID: {worker.worker_id}")
        
        # Check processed count
        if hasattr(worker, 'processed_count'):
            print(f"Tasks Processed: {worker.processed_count}")
    else:
        print("Worker: Not initialized")
    
    print()
except Exception as e:
    print(f"  ERROR: {e}\n")

# 9. Check Agent Decision Making
print("9. AGENT DECISION MAKING ACTIVITY")
print("-" * 80)
try:
    # Check if agents are making decisions
    from backend.audit_log import AuditLog
    audit = AuditLog()
    
    # Look for decision/action events
    all_events = audit.get_recent_events(limit=100)
    decision_events = [e for e in all_events if 'decision' in e.get('event_type', '').lower() or 'action' in e.get('event_type', '').lower()]
    
    print(f"Decision/Action Events (last 100): {len(decision_events)}")
    
    if decision_events:
        for event in decision_events[:5]:
            agent = event.get('agent', 'unknown')
            event_type = event.get('event_type', 'unknown')
            message = event.get('message', '')[:70]
            print(f"  - {agent}: {event_type} - {message}")
    else:
        print("  ⚠️  No decision/action events found")
    
    print()
except Exception as e:
    print(f"  ERROR: {e}\n")

# 10. Summary & Recommendations
print("=" * 80)
print("SUMMARY & RECOMMENDATIONS")
print("=" * 80)

# Check if system is actually working
issues = []
if pending_count == 0 and completed_24h == 0:
    issues.append("⚠️  No workflow activity detected")
if total_revenue == 0:
    issues.append("⚠️  No revenue generated")
if len(decision_events) == 0:
    issues.append("⚠️  No agent decisions/actions detected")

if issues:
    print("\nISSUES DETECTED:")
    for issue in issues:
        print(f"  {issue}")
    print("\nRECOMMENDATIONS:")
    print("  1. Check if autonomy worker is actually running")
    print("  2. Verify agents are making decisions and taking actions")
    print("  3. Check if revenue generation systems are configured")
    print("  4. Review scheduler job execution logs")
    print("  5. Verify agents have proper prompts and can execute actions")
else:
    print("\n✅ System appears to be active")

print("\n" + "=" * 80)
