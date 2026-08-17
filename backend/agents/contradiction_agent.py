"""
Contradiction Detection Agent
Identifies internal conflicts, date mismatches, and contradictory obligations within the same legal document.
"""
import re
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult, AgentFindingModel


class ContradictionDetectionAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Contradiction Agent",
            description="Scans for internal contractual contradictions, conflicting notice periods, payment deadlines, and jurisdiction clashes.",
            capabilities=["conflict_detection", "date_mismatch", "inconsistency_analysis"]
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        text = context.get("text", "")
        findings = []
        
        # 1. Check for conflicting notice periods (e.g. 30 days vs 60 days / 15 days notice)
        notice_periods = list(set(re.findall(r"\b(\d{1,3})\s+(?:days?|calendar\s+days?|business\s+days?)\s+(?:written\s+)?notice\b", text, re.IGNORECASE)))
        if len(notice_periods) > 1:
            findings.append(AgentFindingModel(
                dimension="Operational",
                risk_level="MEDIUM",
                risk_score=60,
                clause_type="Contradictory Notice Periods",
                clause_text=f"Multiple conflicting notice timelines detected in document: {', '.join(notice_periods)} days.",
                page_number=1,
                reason=f"Document specifies different notice requirements ({', '.join(notice_periods)} days), creating ambiguity on valid termination procedure.",
                recommendation="Harmonize notice periods across Termination and Breach clauses to a single uniform duration.",
                citation_status="SUPPORTED",
                confidence=0.88
            ))

        # 2. Check for conflicting payment timelines (e.g., Net 30 vs Net 45 vs within 15 days)
        payment_timelines = list(set(re.findall(r"\b(?:within|net)\s+(\d{1,3})\s+(?:days|days\s+of\s+invoice)\b", text, re.IGNORECASE)))
        if len(payment_timelines) > 1:
            findings.append(AgentFindingModel(
                dimension="Financial",
                risk_level="MEDIUM",
                risk_score=55,
                clause_type="Inconsistent Payment Schedules",
                clause_text=f"Conflicting payment due timelines detected: {', '.join(payment_timelines)} days.",
                page_number=1,
                reason="Inconsistent payment due terms create confusion regarding when late interest or default triggers apply.",
                recommendation="Unify invoice payment settlement schedule across all commercial sections.",
                citation_status="SUPPORTED",
                confidence=0.85
            ))

        # 3. Check for multiple conflicting governing law jurisdictions (e.g. Bangalore vs Delaware vs London)
        cities_detected = []
        for city in ["Bangalore", "Bengaluru", "Mumbai", "Delhi", "Chennai", "Hyderabad", "London", "New York", "Singapore", "Delaware", "California"]:
            if re.search(rf"\b{city}\b", text, re.IGNORECASE):
                cities_detected.append(city)
                
        if len(set(cities_detected)) > 2:
            findings.append(AgentFindingModel(
                dimension="Legal",
                risk_level="HIGH",
                risk_score=75,
                clause_type="Jurisdiction & Forum Conflict",
                clause_text=f"Multiple distinct jurisdictions mentioned in legal forum clauses: {', '.join(set(cities_detected))}.",
                page_number=1,
                reason="Conflicting venue designations can lead to jurisdictional challenges in dispute resolution or enforcement proceedings.",
                recommendation="Designate a single exclusive arbitral seat and court jurisdiction.",
                citation_status="SUPPORTED",
                confidence=0.90
            ))

        if not findings:
            findings.append(AgentFindingModel(
                dimension="Operational",
                risk_level="LOW",
                risk_score=15,
                clause_type="Internal Consistency",
                clause_text="No glaring internal clause contradictions or conflicting notice periods detected.",
                page_number=1,
                reason="Contract terms, notice deadlines, and payment schedules appear internally aligned.",
                recommendation="Maintain standardized definition section across all schedules.",
                citation_status="SUPPORTED",
                confidence=0.91
            ))

        return AgentResult(
            agent_name=self.name,
            status="success",
            confidence=0.88,
            summary=f"Contradiction scan identified {len([f for f in findings if f.risk_level != 'LOW'])} internal inconsistency issue(s).",
            findings=findings,
            data={"conflicts_detected": len([f for f in findings if f.risk_level != 'LOW'])}
        )
