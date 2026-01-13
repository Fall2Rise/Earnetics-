"""
Executive Tools: submit_decision_packet, decide, deploy
"""
from typing import Dict, Any, Optional
from datetime import datetime

from earnetics.intelligence.decision_packets import DecisionPacketGenerator
from earnetics.revenue_loop.deployment_orchestrator import DeploymentOrchestrator
from earnetics.revenue_loop.opportunity import Opportunity


class ExecTools:
    """Executive tools for decision packets and deployment"""
    
    def __init__(self):
        self.packet_generator = DecisionPacketGenerator()
        self.orchestrator = DeploymentOrchestrator()
    
    def submit_decision_packet(self, packet: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit decision packet to Executive Inbox
        
        Returns packet with status
        """
        # Store in executive inbox (would be in database)
        packet["status"] = "pending"
        packet["submitted_at"] = datetime.utcnow().isoformat()
        
        return {
            "success": True,
            "packet_id": packet.get("packet_id"),
            "status": "pending",
            "submitted_at": packet["submitted_at"]
        }
    
    def decide(self, packet_id: str, decision: str, 
              user_id: str = "executive",
              note: Optional[str] = None) -> Dict[str, Any]:
        """
        Executive decision on packet
        
        decision: deploy | experiment | reject | needs_evidence
        """
        # Get packet (would be from database)
        # For now, stub
        
        if decision == "deploy":
            return self._handle_deploy(packet_id, user_id, note)
        elif decision == "experiment":
            return self._handle_experiment(packet_id, user_id, note)
        elif decision == "reject":
            return self._handle_reject(packet_id, user_id, note)
        elif decision == "needs_evidence":
            return self._handle_needs_evidence(packet_id, user_id, note)
        else:
            return {"success": False, "message": f"Unknown decision: {decision}"}
    
    def _handle_deploy(self, packet_id: str, user_id: str, note: Optional[str]) -> Dict[str, Any]:
        """Handle deploy decision"""
        # Get opportunity from packet
        # Generate deployment plan
        # Execute deployment
        
        return {
            "success": True,
            "packet_id": packet_id,
            "decision": "deploy",
            "deployed_at": datetime.utcnow().isoformat(),
            "note": note
        }
    
    def _handle_experiment(self, packet_id: str, user_id: str, note: Optional[str]) -> Dict[str, Any]:
        """Handle experiment decision"""
        return {
            "success": True,
            "packet_id": packet_id,
            "decision": "experiment",
            "experiment_started_at": datetime.utcnow().isoformat(),
            "note": note
        }
    
    def _handle_reject(self, packet_id: str, user_id: str, note: Optional[str]) -> Dict[str, Any]:
        """Handle reject decision"""
        return {
            "success": True,
            "packet_id": packet_id,
            "decision": "reject",
            "rejected_at": datetime.utcnow().isoformat(),
            "note": note
        }
    
    def _handle_needs_evidence(self, packet_id: str, user_id: str, note: Optional[str]) -> Dict[str, Any]:
        """Handle needs_evidence decision"""
        return {
            "success": True,
            "packet_id": packet_id,
            "decision": "needs_evidence",
            "requested_at": datetime.utcnow().isoformat(),
            "note": note
        }
    
    def deploy(self, deployment_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute deployment plan"""
        result = self.orchestrator.execute_deployment(deployment_plan)
        return result
