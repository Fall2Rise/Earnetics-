"""
Contract Loophole Scanner Engine
Rule-based contract analysis (no paid APIs)
"""
import re
from typing import Dict, List, Any
from head_office.backend.models.schemas import ContractScanResult


class ContractScanner:
    """Contract loophole scanner using rule-based pattern detection"""
    
    # Risk patterns to detect
    HIGH_RISK_PATTERNS = {
        "uncapped_liability": [
            r"unlimited\s+liability",
            r"liability\s+without\s+limit",
            r"no\s+cap\s+on\s+liability",
            r"maximum\s+liability.*unlimited"
        ],
        "one_way_indemnity": [
            r"indemnify.*\b(?:you|your|customer|client|counterparty)\b",
            r"hold\s+harmless.*\b(?:you|your|customer|client)\b",
            r"defend.*\b(?:you|your|customer|client)\b"
        ],
        "ip_assignment": [
            r"assign.*all\s+right.*intellectual\s+property",
            r"all\s+inventions.*assigned",
            r"work\s+for\s+hire.*all\s+rights",
            r"any\s+and\s+all\s+intellectual\s+property.*assigned"
        ],
        "termination_without_compensation": [
            r"terminate\s+.*\b(?:for\s+convenience|at\s+will)\b.*without\s+.*compensation",
            r"terminate.*without\s+.*payment",
            r"cancel.*without\s+.*refund"
        ],
        "sole_discretion": [
            r"sole\s+discretion.*payment",
            r"sole\s+discretion.*accept",
            r"sole\s+discretion.*withhold",
            r"in\s+our\s+sole\s+discretion"
        ],
        "guarantee_language": [
            r"personal\s+guarantee",
            r"guarantee.*jointly\s+and\s+severally",
            r"guarantor",
            r"personally\s+liable",
            r"guarantee.*obligations"
        ]
    }
    
    MEDIUM_RISK_PATTERNS = {
        "auto_renew": [
            r"automatically\s+renew",
            r"auto[\s-]?renew",
            r"renewal.*automatic"
        ],
        "long_net_terms": [
            r"net\s+\d+\s+days",  # net 90, net 120, etc.
            r"payment\s+terms.*\d{3,}\s+days"
        ],
        "changeable_terms": [
            r"terms\s+may\s+change",
            r"website\s+terms.*incorporated",
            r"as\s+posted\s+on.*website"
        ],
        "venue_traps": [
            r"venue.*exclusive.*\b(?:seller|licensor|provider)\b",
            r"jurisdiction.*exclusive.*\b(?:seller|licensor|provider)\b",
            r"waiver.*jury\s+trial"
        ],
        "attorney_fees": [
            r"prevailing\s+party.*attorney.*fees",
            r"loser\s+pays.*attorney",
            r"attorney.*fees.*prevailing"
        ]
    }
    
    LOW_RISK_PATTERNS = {
        "non_compete": [
            r"non[\s-]?compete",
            r"not\s+compete.*\d+\s+(?:year|month)"
        ],
        "confidentiality_scope": [
            r"confidential.*definition.*broad",
            r"all\s+information.*confidential"
        ]
    }
    
    def scan(self, contract_text: str, contract_id: str) -> ContractScanResult:
        """
        Scan contract text for loopholes and risks
        
        Returns ContractScanResult with risk analysis
        """
        text_lower = contract_text.lower()
        
        # Detect risks
        high_risks = []
        medium_risks = []
        low_risks = []
        
        # Check high-risk patterns
        for category, patterns in self.HIGH_RISK_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    high_risks.append(self._format_risk(category, pattern))
                    break
        
        # Check medium-risk patterns
        for category, patterns in self.MEDIUM_RISK_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    medium_risks.append(self._format_risk(category, pattern))
                    break
        
        # Check low-risk patterns
        for category, patterns in self.LOW_RISK_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    low_risks.append(self._format_risk(category, pattern))
                    break
        
        # Determine overall risk level
        if high_risks:
            risk_level = "high"
        elif medium_risks:
            risk_level = "medium"
        elif low_risks:
            risk_level = "low"
        else:
            risk_level = "low"
        
        # Check for guarantee language
        guarantee_detected = any("guarantee" in risk.lower() for risk in high_risks)
        
        # Build risk map
        risk_map = {
            "high": high_risks,
            "medium": medium_risks,
            "low": low_risks
        }
        
        # Generate executive summary
        executive_summary = self._generate_summary(risk_level, high_risks, medium_risks, guarantee_detected)
        
        # Missing items checklist
        missing_items = self._check_missing_items(contract_text)
        
        # Redline suggestions
        redline_suggestions = self._generate_redlines(high_risks, medium_risks)
        
        # Negotiation playbook
        negotiation_playbook = self._generate_playbook(high_risks, medium_risks)
        
        # Signature recommendation (basic - will be enhanced by signature assistant)
        signature_recommendation = None
        
        return ContractScanResult(
            contract_id=contract_id,
            risk_level=risk_level,
            executive_summary=executive_summary,
            risk_map=risk_map,
            missing_items=missing_items,
            redline_suggestions=redline_suggestions,
            negotiation_playbook=negotiation_playbook,
            guarantee_detected=guarantee_detected,
            signature_recommendation=signature_recommendation
        )
    
    def _format_risk(self, category: str, pattern: str) -> str:
        """Format risk category name"""
        return category.replace("_", " ").title()
    
    def _generate_summary(self, risk_level: str, high_risks: List[str], 
                         medium_risks: List[str], guarantee_detected: bool) -> str:
        """Generate executive summary"""
        summary_parts = []
        
        if risk_level == "high":
            summary_parts.append(f"⚠️ HIGH RISK: {len(high_risks)} critical issues detected.")
        elif risk_level == "medium":
            summary_parts.append(f"⚡ MEDIUM RISK: {len(medium_risks)} issues require attention.")
        else:
            summary_parts.append("✅ LOW RISK: No critical issues detected.")
        
        if guarantee_detected:
            summary_parts.append("🚨 PERSONAL GUARANTEE DETECTED - Requires immediate review.")
        
        if high_risks:
            summary_parts.append(f"Critical issues: {', '.join(high_risks[:3])}")
        
        return " ".join(summary_parts)
    
    def _check_missing_items(self, contract_text: str) -> List[str]:
        """Check for missing standard contract items"""
        text_lower = contract_text.lower()
        missing = []
        
        standard_items = {
            "termination clause": r"terminat",
            "dispute resolution": r"dispute|arbitration|mediation",
            "governing law": r"governing\s+law|jurisdiction",
            "limitation of liability": r"limit.*liability|liability.*cap",
            "confidentiality": r"confidential|nda|non[\s-]?disclosure"
        }
        
        for item, pattern in standard_items.items():
            if not re.search(pattern, text_lower, re.IGNORECASE):
                missing.append(item)
        
        return missing
    
    def _generate_redlines(self, high_risks: List[str], medium_risks: List[str]) -> List[Dict[str, Any]]:
        """Generate redline suggestions"""
        suggestions = []
        
        risk_mapping = {
            "Uncapped Liability": {
                "suggestion": "Add limitation of liability cap (e.g., 'Liability shall not exceed the total fees paid in the 12 months preceding the claim')",
                "strength": "strong"
            },
            "One Way Indemnity": {
                "suggestion": "Mutual indemnification clause (both parties indemnify for their own breaches)",
                "strength": "strong"
            },
            "Ip Assignment": {
                "suggestion": "Clarify IP ownership: assign only work product, retain pre-existing IP and background IP",
                "strength": "strong"
            },
            "Termination Without Compensation": {
                "suggestion": "Add termination payment clause (prorated fees or work completed)",
                "strength": "medium"
            },
            "Sole Discretion": {
                "suggestion": "Add objective criteria or remove 'sole discretion' language",
                "strength": "medium"
            },
            "Auto Renew": {
                "suggestion": "Require written notice to renew, or add automatic renewal notification period",
                "strength": "light"
            }
        }
        
        for risk in high_risks + medium_risks:
            if risk in risk_mapping:
                suggestions.append({
                    "risk": risk,
                    "suggestion": risk_mapping[risk]["suggestion"],
                    "strength": risk_mapping[risk]["strength"]
                })
        
        return suggestions
    
    def _generate_playbook(self, high_risks: List[str], medium_risks: List[str]) -> List[str]:
        """Generate negotiation playbook"""
        playbook = []
        
        if "Uncapped Liability" in high_risks:
            playbook.append("1. Request liability cap: 'Our standard cap is [12 months fees] or $X, whichever is lower.'")
        
        if "One Way Indemnity" in high_risks:
            playbook.append("2. Propose mutual indemnification: 'Each party indemnifies for their own breaches and violations of law.'")
        
        if "Ip Assignment" in high_risks:
            playbook.append("3. Clarify IP scope: 'We retain pre-existing IP and background IP. Only work product is assigned.'")
        
        if "Personal Guarantee" in str(high_risks):
            playbook.append("4. ESCALATE: Personal guarantee requires executive approval. Consider entity-only structure.")
        
        if not playbook:
            playbook.append("No high-risk items requiring negotiation.")
        
        return playbook
