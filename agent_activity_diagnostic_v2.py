#!/usr/bin/env python3
"""Comprehensive diagnostic of agent activity - checks actual running system"""
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

# 1. Check Workflow Queue Activity
print("1. WORKFLOW QUEUE - CRITICAL STATUS")
print("-" * 80)
try:
    from autonomous.workflow_queue import WorkflowQueueRepository
    repo = WorkflowQueueRepository()
    
    pending_count = repo.count_pending()
    print(f"✅ Pending Workflows: {pending_count}")
    
    # Check completed in last 24 hours
    with repo._connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM autonomy_task_queue 
            WHERE status = 'completed' 
            AND updated_at > datetime('now', '-24 hours')
        """)
        completed_24h = cursor.fetchone()[0]
        print(f"⚠️  Completed in last 24h: {completed_24h}")
        
        # Check last completed
        cursor.execute("""
            SELECT MAX(updated_at) FROM autonomy_task_queue 
            WHERE status = 'completed'
        """)
        last_completed = cursor.fetchone()[0]
        if last_completed:
            print(f"⚠️  Last Completed: {last_completed}")
        else:
            print(f"❌ NO TASKS EVER COMPLETED!")
        
        # Get pending tasks details
        cursor.execute("""
            SELECT task_id, department, priority, created_at, metadata
            FROM autonomy_task_queue 
            WHERE status = 'pending' 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        print("\nTop 5 Pending Tasks:")
        for row in cursor.fetchall():
            print(f"  - Task {row['task_id']}: {row['department']} ({row['priority']}) - Created: {row['created_at']}")
    
    print()
except Exception as e:
    print(f"  ERROR: {e}\n")

# 2. Check Corporate Memory - Tasks
print("2. CORPORATE MEMORY - TASK BACKLOG")
print("-" * 80)
try:
    from backend.corporate_memory import CorporateMemory
    corp_mem = CorporateMemory()
    
    all_tasks = corp_mem.list_tasks()
    print(f"Total Tasks: {len(all_tasks)}")
    
    # Group by status
    by_status = defaultdict(list)
    for task in all_tasks:
        status = task.get('status', 'unknown')
        by_status[status].append(task)
    
    for status, tasks in sorted(by_status.items()):
        print(f"  {status}: {len(tasks)}")
        if status == 'pending' and len(tasks) > 0:
            # Show oldest pending
            oldest = sorted(tasks, key=lambda t: t.get('created_at', ''))[:3]
            print(f"    Oldest pending tasks:")
            for task in oldest:
                title = task.get('title', 'Untitled')[:60]
                dept = task.get('department', 'Unknown')
                created = task.get('created_at', 'Unknown')[:19]
                print(f"      - {title} ({dept}) - Created: {created}")
    
    # Check completion rate
    completed = len(by_status.get('completed', []))
    pending = len(by_status.get('pending', []))
    if completed + pending > 0:
        completion_rate = (completed / (completed + pending)) * 100
        print(f"\n⚠️  Completion Rate: {completion_rate:.1f}% ({completed} completed, {pending} pending)")
        if completion_rate < 5:
            print(f"❌ CRITICAL: Only {completion_rate:.1f}% of tasks are being completed!")
    
    print()
except Exception as e:
    print(f"  ERROR: {e}\n")

# 3. Check Audit Log for Recent Activity
print("3. RECENT SYSTEM ACTIVITY (Audit Log)")
print("-" * 80)
try:
    from backend.audit_log import AuditLogStore
    audit = AuditLogStore()
    
    # Get recent events
    with audit._connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT action, status, agent, message, timestamp 
            FROM audit_events 
            ORDER BY timestamp DESC 
            LIMIT 20
        """)
        events = cursor.fetchall()
        
        if events:
            print(f"Recent Events (last 20): {len(events)}")
            
            # Group by agent
            by_agent = defaultdict(list)
            for event in events:
                agent = event[2] or 'system'
                by_agent[agent].append(event)
            
            for agent, agent_events in list(by_agent.items())[:10]:
                print(f"\n  {agent}: {len(agent_events)} events")
                for event in agent_events[:2]:
                    action = event[0][:40]
                    status = event[1]
                    message = (event[3] or '')[:50]
                    timestamp = event[4][:19] if event[4] else 'unknown'
                    print(f"    - [{timestamp}] {action} ({status}): {message}")
        else:
            print("❌ NO AUDIT EVENTS FOUND!")
    
    print()
except Exception as e:
    print(f"  ERROR: {e}\n")

# 4. Check Revenue/Products
print("4. REVENUE & PRODUCTS")
print("-" * 80)
try:
    from backend.corporate_memory import BUSINESS_DB_PATH
    conn = sqlite3.connect(BUSINESS_DB_PATH)
    cursor = conn.cursor()
    
    # Check products table
    try:
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        print(f"Total Products: {product_count}")
        
        # Recent products
        cursor.execute("""
            SELECT name, price, created_at 
            FROM products 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        print("\nRecent Products:")
        for row in cursor.fetchall():
            print(f"  - {row[0]}: ${row[1]:.2f} - {row[2][:19]}")
    except sqlite3.OperationalError:
        print("⚠️  Products table not found")
    
    # Check transactions
    try:
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE status = 'completed'")
        tx_count = cursor.fetchone()[0]
        print(f"\nCompleted Transactions: {tx_count}")
        
        if tx_count > 0:
            cursor.execute("""
                SELECT SUM(amount) FROM transactions WHERE status = 'completed'
            """)
            total = cursor.fetchone()[0] or 0
            print(f"Total Revenue: ${total:.2f}")
        else:
            print("❌ NO REVENUE GENERATED!")
    except sqlite3.OperationalError:
        print("⚠️  Transactions table not found")
    
    conn.close()
    print()
except Exception as e:
    print(f"  ERROR: {e}\n")

# 5. Check Factory Engine
print("5. FACTORY ENGINE - PRODUCT STREAMS")
print("-" * 80)
try:
    from backend.factory_engine import FACTORY_ENGINE
    streams = FACTORY_ENGINE.list_streams()
    print(f"Total Streams: {len(streams)}")
    
    by_stage = defaultdict(list)
    for stream in streams:
        stage = stream.get('stage', 'UNKNOWN')
        by_stage[stage].append(stream)
    
    for stage, stream_list in sorted(by_stage.items()):
        print(f"  {stage}: {len(stream_list)}")
        if stage != 'MAINTENANCE':
            for stream in stream_list[:3]:
                name = stream.get('name', 'Unknown')[:40]
                progress = stream.get('progress', 0)
                print(f"    - {name} ({progress}%)")
    
    if len(streams) <= 1:
        print("⚠️  Very few streams - factory may not be generating products")
    
    print()
except Exception as e:
    print(f"  ERROR: {e}\n")

# 6. Check Scheduler Jobs
print("6. SCHEDULER - JOB STATUS")
print("-" * 80)
try:
    from backend.workflow_scheduler import OrchestrationScheduler
    from backend.workflow_scheduler import SCHEDULER_DB
    
    scheduler = OrchestrationScheduler(db_path=SCHEDULER_DB)
    jobs = scheduler.list_jobs()
    
    print(f"Scheduled Jobs: {len(jobs)}")
    
    now = datetime.utcnow()
    due_count = 0
    for job in jobs:
        is_due = job.next_run <= now if job.next_run else False
        if is_due:
            due_count += 1
        
        status_icon = "⏰" if is_due else "✅"
        print(f"  {status_icon} {job.id}: {job.handler}")
        print(f"    Schedule: {job.schedule_type} every {job.schedule_value}s")
        if job.last_run:
            print(f"    Last Run: {job.last_run}")
        print(f"    Next Run: {job.next_run}")
        print(f"    Status: {job.status}")
    
    if due_count > 0:
        print(f"\n⚠️  {due_count} jobs are due but may not be executing")
    
    print()
except Exception as e:
    print(f"  ERROR: {e}\n")

# 7. Check Agent Status
print("7. AGENT STATUS")
print("-" * 80)
try:
    from backend.real_ai_agents import get_real_agent_status
    status = get_real_agent_status()
    
    agents = status.get('agents', {})
    print(f"Total Agents: {len(agents)}")
    
    # Count active vs idle
    active = sum(1 for a in agents.values() if a.get('memory_entries', 0) > 0)
    idle = len(agents) - active
    
    print(f"  Active (has memory): {active}")
    print(f"  Idle (no memory): {idle}")
    
    if idle > active:
        print(f"⚠️  Most agents are idle - they may not be working")
    
    # Show agents with most activity
    sorted_agents = sorted(agents.items(), key=lambda x: x[1].get('memory_entries', 0), reverse=True)
    print(f"\nTop 5 Most Active Agents:")
    for name, agent in sorted_agents[:5]:
        entries = agent.get('memory_entries', 0)
        dept = agent.get('department', 'Unknown')
        print(f"  - {name}: {entries} memory entries ({dept})")
    
    print()
except Exception as e:
    print(f"  ERROR: {e}\n")

# 8. SUMMARY & CRITICAL ISSUES
print("=" * 80)
print("CRITICAL DIAGNOSIS")
print("=" * 80)

issues = []
warnings = []

# Check if tasks are being processed
if completed_24h == 0:
    issues.append("❌ NO TASKS COMPLETED IN LAST 24 HOURS - Autonomy worker may not be running!")

if pending > 2000 and completion_rate < 5:
    issues.append(f"❌ MASSIVE BACKLOG: {pending} pending tasks, only {completion_rate:.1f}% completion rate")

if due_count > 0:
    warnings.append(f"⚠️  {due_count} scheduled jobs are due but may not be executing")

if idle > active:
    warnings.append(f"⚠️  Most agents ({idle}) are idle - they may not be making decisions")

if issues:
    print("\n🚨 CRITICAL ISSUES DETECTED:")
    for issue in issues:
        print(f"  {issue}")

if warnings:
    print("\n⚠️  WARNINGS:")
    for warning in warnings:
        print(f"  {warning}")

if not issues and not warnings:
    print("\n✅ System appears to be operating normally")

print("\n" + "=" * 80)
print("RECOMMENDATIONS:")
print("=" * 80)
print("1. Check if autonomy worker is actually running (check server logs)")
print("2. Verify agents are making decisions (check audit log for 'decision' events)")
print("3. Check if scheduler is executing due jobs (check server logs)")
print("4. Verify agents have proper LLM access and can execute actions")
print("5. Check if there are errors preventing task execution")
print("\n" + "=" * 80)
