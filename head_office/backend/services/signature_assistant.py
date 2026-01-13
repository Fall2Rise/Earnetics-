"""
Signature Capacity Assistant
Determines proper signature block and detects guarantees
"""
import re
from typing import Dict, Optional, Tuple, List, Any
from head_office.backend.models.schemas import Contract


class SignatureAssistant:
    """Assistant for determining signature capacity and detecting guarantees"""
    
    def analyze_contract(self, contract_text: str, contract: Contract) -> Dict[str, Any]:
        """
        Analyze contract for signature capacity and guarantee detection
        
        Returns:
            {
                "party_name": str,
                "recommended_signature": str,
                "guarantee_detected": bool,
                "guarantee_language": List[str],
                "warnings": List[str]
            }
        """
        # Detect party name
        party_name = self._detect_party_name(contract_text, contract.party_name)
        
        # Detect guarantee language
        guarantee_detected, guarantee_language = self._detect_guarantee(contract_text)
        
        # Generate signature recommendation
        recommended_signature = self._recommend_signature(party_name, guarantee_detected)
        
        # Generate warnings
        warnings = []
        if guarantee_detected:
            warnings.append("🚨 PERSONAL GUARANTEE DETECTED: This contract includes personal guarantee language. Signature requires executive approval and should be escalated to Decision Queue as HIGH RISK.")
        
        warnings.append("⚠️ IMPORTANT: Adding 'without prejudice' notes to a signed contract does NOT replace negotiating terms. Terms should be negotiated BEFORE signing.")
        
        return {
            "party_name": party_name,
            "recommended_signature": recommended_signature,
            "guarantee_detected": guarantee_detected,
            "guarantee_language": guarantee_language,
            "warnings": warnings
        }
    
    def _detect_party_name(self, contract_text: str, default_party: str) -> str:
        """Detect the party name from contract text"""
        # Look for common patterns
        patterns = [
            r"party\s+['\"]?(?:a|1)['\"]?\s*[:\(]?\s*['\"]?([^'\"\)]+)['\"]?",
            r"this\s+agreement.*between.*['\"]?([^'\"\(]+)['\"]?\s*\(['\"]?[^'\"]+['\"]?\)",
            r"agreement.*between\s+['\"]?([^'\"\(]+)['\"]?",
        ]
        
        text_lower = contract_text.lower()
        for pattern in patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                party_name = match.group(1).strip()
                # Clean up common suffixes
                party_name = re.sub(r'\s*\(.*?\)', '', party_name)
                party_name = re.sub(r'\s*[,;].*$', '', party_name)
                if party_name and len(party_name) < 100:
                    return party_name
        
        # Fallback to contract.party_name or default
        return default_party or "Company Name"
    
    def _detect_guarantee(self, contract_text: str) -> Tuple[bool, List[str]]:
        """Detect personal guarantee language"""
        guarantee_patterns = [
            r"personal\s+guarantee",
            r"guarantee.*jointly\s+and\s+severally",
            r"guarantor\s+.*\b(?:i|we)\b",
            r"personally\s+liable",
            r"guarantee.*obligations.*\b(?:i|we|undersigned)\b",
            r"guarantee.*repayment",
            r"guarantee.*performance",
        ]
        
        text_lower = contract_text.lower()
        detected = []
        
        for pattern in guarantee_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                # Extract context (50 chars before and after)
                start = max(0, match.start() - 50)
                end = min(len(contract_text), match.end() + 50)
                context = contract_text[start:end].strip()
                if context not in detected:
                    detected.append(context)
        
        return len(detected) > 0, detected
    
    def _recommend_signature(self, party_name: str, guarantee_detected: bool) -> str:
        """Recommend signature block format"""
        if guarantee_detected:
            return f"""
⚠️ PERSONAL GUARANTEE DETECTED - SIGNATURE BLOCK REQUIRES EXECUTIVE APPROVAL

For COMPANY signature (if guarantee is removed):
{party_name}
By: _______________________
    [Name], [Title]
    Date: ___________________

For PERSONAL GUARANTEE (NOT RECOMMENDED):
{party_name}
By: _______________________
    [Name], [Title]
    Date: ___________________

Guarantor (Personal):
_______________________
[Name], Individual
Date: ___________________
"""
        else:
            return f"""
{party_name}
By: _______________________
    [Name], [Title]
    Date: ___________________
"""
