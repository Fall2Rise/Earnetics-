import os
import sys
import json
import asyncio
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from backend.corporate_memory import CorporateMemory, Objective, Task, KnowledgeArticle
from backend.ewc.core_plays import CORE_PLAYS_SEED

def seed_data():
    print("🌱 SEEDING COMMAND CENTER DATABASE...")
    memory = CorporateMemory()
    
    # 1. Seed Core Plays as Objectives
    print(f"   > Processing {len(CORE_PLAYS_SEED)} Core Plays...")
    for play in CORE_PLAYS_SEED:
        # Check if objective already exists (simple check by title)
        # In a real app, we might check by source_directive_id or similar
        
        # Create Objective
        obj_data = {
            "title": play["name"],
            "owner": play["execution_plan"]["owner_roles"][0],
            "priority": play["risk_tier"],
            "status": "planned",
            "description": play["description"],
            "success_metrics": play["kpis"],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # We use the internal create_objective method which expects a dict
        # But let's use the class wrapper if possible, or just direct dict
        # The CorporateMemory.create_objective takes a dict.
        
        # We'll just insert it.
        try:
            created_obj = memory.create_objective(obj_data)
            print(f"     + Objective: {play['name']}")
            
            # Create Tasks for this Objective
            steps = play["execution_plan"]["steps"]
            for step in steps:
                task_data = {
                    "objective_id": created_obj["id"],
                    "title": step["title"],
                    "department": "strategy", # Default, or derive from owner
                    "assigned_agent": play["execution_plan"]["owner_roles"][0],
                    "status": "pending",
                    "priority": "medium",
                    "description": step["desc"],
                    "dependencies": [],
                    "metadata": {"automation_steps": step.get("automation", [])},
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
                memory.create_task(task_data)
                # print(f"       - Task: {step['title']}")
                
        except Exception as e:
            print(f"     ! Error creating {play['name']}: {e}")

    # 2. Seed Knowledge Articles
    print("   > Seeding Knowledge Base...")
    articles = [
        {
            "title": "Agentic Workflow Principles",
            "content": "Agents should be autonomous but aligned. Use the OODA loop: Observe, Orient, Decide, Act.",
            "tags": "agents, workflow, principles",
            "source": "Internal Doctrine"
        },
        {
            "title": "Revenue Command Center Guide",
            "content": "The Command Center is the central nervous system. It tracks revenue, assigns tasks, and monitors agent performance.",
            "tags": "guide, operations, revenue",
            "source": "Onboarding"
        },
        {
            "title": "Stripe Integration Docs",
            "content": "We use Stripe for all billing. Products are synced automatically. Webhooks handle status updates.",
            "tags": "stripe, billing, technical",
            "source": "Engineering"
        }
    ]
    
    for art in articles:
        art_data = {
            "title": art["title"],
            "content": art["content"],
            "tags": art["tags"],
            "source": art["source"],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        memory.create_article(art_data)
        print(f"     + Article: {art['title']}")

    print("\n✅ SEEDING COMPLETE!")
    print("   The Command Center is now populated with data.")

if __name__ == "__main__":
    seed_data()
