"""
Revenue Loop: Deployment Orchestrator
Generates deployment plans and executes revenue campaigns
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib

from earnetics.revenue_loop.opportunity import Opportunity
from earnetics.intelligence.decision_packets import DecisionPacketGenerator


class DeploymentOrchestrator:
    """Orchestrates deployment of revenue opportunities"""
    
    def __init__(self):
        self.packet_generator = DecisionPacketGenerator()
    
    def generate_deployment_plan(self, opportunity: Opportunity, 
                                 decision_packet: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate deployment plan from approved opportunity
        
        Returns deployment_plan.json with tasks:
        - landing page
        - copy
        - tracking
        - traffic
        - lead capture
        - follow-up sequence
        """
        campaign_id = f"campaign_{opportunity.opportunity_id}_{datetime.utcnow().strftime('%Y%m%d')}"
        
        plan = {
            "campaign_id": campaign_id,
            "opportunity_id": opportunity.opportunity_id,
            "generated_at": datetime.utcnow().isoformat(),
            "status": "planned",
            
            "tasks": [
                {
                    "task_id": f"{campaign_id}_landing_page",
                    "type": "landing_page",
                    "title": f"Create landing page for {opportunity.niche}",
                    "description": f"Landing page for {opportunity.offer_type} targeting {opportunity.target}",
                    "priority": "high",
                    "dependencies": [],
                    "estimated_hours": 4,
                    "assignee": "LaunchSpecialist"
                },
                {
                    "task_id": f"{campaign_id}_copy",
                    "type": "copy",
                    "title": f"Generate marketing copy for {opportunity.niche}",
                    "description": f"Sales copy, email sequences, ad copy for {opportunity.offer_type}",
                    "priority": "high",
                    "dependencies": [],
                    "estimated_hours": 6,
                    "assignee": "Nova"
                },
                {
                    "task_id": f"{campaign_id}_tracking",
                    "type": "tracking",
                    "title": f"Set up tracking for {campaign_id}",
                    "description": "Analytics, conversion tracking, KPI monitoring",
                    "priority": "high",
                    "dependencies": [f"{campaign_id}_landing_page"],
                    "estimated_hours": 2,
                    "assignee": "DataAnalyst"
                },
                {
                    "task_id": f"{campaign_id}_traffic",
                    "type": "traffic",
                    "title": f"Drive traffic to {campaign_id}",
                    "description": f"Traffic generation for {opportunity.niche} offer",
                    "priority": "medium",
                    "dependencies": [f"{campaign_id}_landing_page", f"{campaign_id}_copy"],
                    "estimated_hours": 8,
                    "assignee": "WebScraper"
                },
                {
                    "task_id": f"{campaign_id}_lead_capture",
                    "type": "lead_capture",
                    "title": f"Set up lead capture for {campaign_id}",
                    "description": "Email capture, form setup, CRM integration",
                    "priority": "high",
                    "dependencies": [f"{campaign_id}_landing_page"],
                    "estimated_hours": 3,
                    "assignee": "ListBuilder"
                },
                {
                    "task_id": f"{campaign_id}_followup",
                    "type": "followup_sequence",
                    "title": f"Create follow-up sequence for {campaign_id}",
                    "description": "Email nurture sequence, retargeting, conversion optimization",
                    "priority": "medium",
                    "dependencies": [f"{campaign_id}_lead_capture", f"{campaign_id}_copy"],
                    "estimated_hours": 4,
                    "assignee": "Nova"
                }
            ],
            
            "assets": {
                "required": opportunity.required_assets,
                "created": [],
                "missing": opportunity.required_assets.copy()
            },
            
            "kpis": {
                "primary": "revenue",
                "target": opportunity.expected_roi,
                "timeframe_days": opportunity.time_to_first_dollar,
                "metrics": {
                    "traffic": {"target": 1000, "current": 0},
                    "leads": {"target": 100, "current": 0},
                    "conversions": {"target": 10, "current": 0},
                    "revenue": {"target": opportunity.expected_roi, "current": 0}
                }
            },
            
            "timeline": {
                "start_date": datetime.utcnow().isoformat(),
                "target_launch": self._calculate_launch_date(opportunity.time_to_first_dollar),
                "estimated_completion": self._calculate_completion_date()
            }
        }
        
        return plan
    
    def execute_deployment(self, deployment_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute deployment plan
        
        Creates tasks in workflow queue and starts campaign
        """
        from backend.corporate_memory import CorporateMemory
        from autonomous.workflow_queue import WorkflowQueueRepository
        
        corp_mem = CorporateMemory()
        queue_repo = WorkflowQueueRepository()
        
        campaign_id = deployment_plan["campaign_id"]
        created_tasks = []
        
        for task in deployment_plan["tasks"]:
            workflow_task = corp_mem.create_task({
                "objective_id": None,
                "title": task["title"],
                "department": self._get_department_for_assignee(task["assignee"]),
                "assigned_agent": task["assignee"],
                "status": "pending",
                "priority": task["priority"],
                "due_date": None,
                "description": task["description"],
                "dependencies": task["dependencies"],
                "metadata": {
                    "campaign_id": campaign_id,
                    "task_id": task["task_id"],
                    "task_type": task["type"],
                    "estimated_hours": task["estimated_hours"]
                }
            })
            
            queue_repo.enqueue_from_task(workflow_task)
            created_tasks.append(task["task_id"])
        
        return {
            "campaign_id": campaign_id,
            "status": "deployed",
            "tasks_created": len(created_tasks),
            "task_ids": created_tasks,
            "deployed_at": datetime.utcnow().isoformat()
        }
    
    def _calculate_launch_date(self, days: int) -> str:
        """Calculate launch date from days"""
        from datetime import timedelta
        launch = datetime.utcnow() + timedelta(days=days)
        return launch.isoformat()
    
    def _calculate_completion_date(self) -> str:
        """Calculate estimated completion date"""
        from datetime import timedelta
        completion = datetime.utcnow() + timedelta(days=30)
        return completion.isoformat()
    
    def _get_department_for_assignee(self, assignee: str) -> str:
        """Map agent to department"""
        dept_map = {
            "LaunchSpecialist": "Revenue Execution",
            "Nova": "Email Marketing",
            "DataAnalyst": "Corporate Analytics",
            "WebScraper": "Lead Generation & Acquisition",
            "ListBuilder": "Lead Generation & Acquisition"
        }
        return dept_map.get(assignee, "Corporate Execution")
