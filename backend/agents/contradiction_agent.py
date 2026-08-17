"""
Contradiction Detection Agent
Identifies first-class internal contractual contradictions:
1. Consideration & Payment Contradictions (e.g. Advance + Balance on registration vs Full consideration already received)
2. Possession Contradictions (e.g. Possession on registration vs Prior physical possession delivered)
3. Dispute Resolution & Forum Contradictions (e.g. Bengaluru exclusive courts vs Mysuru arbitration)
4. Numerical, Temporal, and Notice Deadline Inconsistencies
"""
import re
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult, AgentFindingModel


class ContradictionDetectionAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Contradiction Agent",
            description="Identifies first-class internal contractual contradictions across payment terms, possession delivery, forum selection, and timelines.",
            capabilities=["conflict_detection", "payment_contradiction", "possession_contradiction", "forum_conflict", "date_mismatch"]
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        text = context.get("text", "")
        lower = text.lower()
        findings: List[AgentFindingModel] = []
        conflicts_count = 0

        # =========================================================================
        # 1. PAYMENT / CONSIDERATION CONTRADICTION
        # =========================================================================
        # Scenario: One part mentions advance + balance payable on registration/future date,
        # but another part states entire consideration has already been received in full.
        has_partial_balance_pending = bool(re.search(
            r"(?:advance\s+(?:token|sum|amount)|balance\s+(?:sale\s+)?consideration|payable\s+at\s+the\s+time\s+of\s+registration|remaining\s+(?:amount|sum)|shall\s+pay\s+(?:the\s+)?balance)",
            lower
        ))
        has_full_payment_acknowledged = bool(re.search(
            r"(?:entire\s+(?:sale\s+)?consideration\s+(?:of\s+[^\n]+)?has\s+been\s+received|received\s+the\s+full\s+and\s+final|hereby\s+acknowledges\s+receipt\s+of\s+the\s+entire|full\s+consideration\s+in\s+hand\s+paid|no\s+balance\s+amount\s+is\s+due|paid\s+in\s+full\s+and\s+final)",
            lower
        ))

        if has_partial_balance_pending and has_full_payment_acknowledged:
            conflicts_count += 1
            findings.append(AgentFindingModel(
                id="contra-pay-01",
                agent="Contradiction Agent",
                dimension="Financial",
                category="Consideration / Payment",
                severity="CRITICAL",
                risk_score=95,
                clause_type="Consideration / Payment Contradiction",
                clause_text="Document simultaneously asserts that balance consideration remains payable upon registration AND that entire sale consideration has already been received in full.",
                page_number=1,
                evidence="Found mutually conflicting payment terms: pending balance payable at registration vs. explicit acknowledgement of entire consideration received.",
                claim="Payment terms are irreconcilably contradictory.",
                reason="The document simultaneously states that a substantial balance consideration remains payable and that the entire consideration has already been received, creating severe financial and title transfer exposure.",
                recommendation="Rectify payment terms to clearly state whether consideration is paid in full prior to execution or whether a specified balance remains payable at the Sub-Registrar upon deed execution.",
                source_type="DOCUMENT_TEXT",
                verification_status="TEXT_SUPPORTED",
                confidence=0.96
            ))

        # =========================================================================
        # 2. POSSESSION DELIVERY CONTRADICTION
        # =========================================================================
        # Scenario: One part states possession shall be handed over upon registration,
        # while another states possession has already been delivered / vacant possession in hand.
        has_future_possession = bool(re.search(
            r"(?:possession[^\n.]{0,80}shall\s+be\s+(?:handed\s+over|delivered)|deliver[^\n.]{0,40}possession|on\s+or\s+after\s+registration|possession\s+to\s+be\s+given|handed\s+over[^\n.]{0,40}on\s+or\s+after\s+registration)",
            lower
        ))
        has_delivered_possession = bool(re.search(
            r"(?:(?:has\s+)?(?:already\s+)?handed\s+over[^\n.]{0,50}possession|already\s+in[^\n.]{0,30}possession|hereby\s+delivers[^\n.]{0,30}possession|put\s+the\s+purchaser\s+in\s+possession|prior\s+to\s+execution)",
            lower
        ))

        if has_future_possession and has_delivered_possession:
            conflicts_count += 1
            findings.append(AgentFindingModel(
                id="contra-pos-01",
                agent="Contradiction Agent",
                dimension="Operational",
                category="Possession",
                severity="HIGH",
                risk_score=85,
                clause_type="Possession Delivery Contradiction",
                clause_text="Document contains conflicting statements regarding handover of physical vacant possession (possession already handed over vs. possession to be delivered upon registration).",
                page_number=1,
                evidence="Clause states possession has already been handed over, while another clause states possession shall be delivered at registration.",
                claim="Possession status is contradictory.",
                reason="Conflicting possession recitals create evidential uncertainty regarding when risk, title, and actual physical custody of the property pass to the purchaser.",
                recommendation="Harmonize possession recitals: execute a formal possession letter confirming the exact date and mode of physical site handover.",
                source_type="DOCUMENT_TEXT",
                verification_status="TEXT_SUPPORTED",
                confidence=0.94
            ))

        # =========================================================================
        # 3. DISPUTE RESOLUTION / FORUM SELECTION CONTRADICTION
        # =========================================================================
        # Scenario: Explicit exclusive jurisdiction to City A courts, but also arbitration in City B / conflicting forum.
        has_exclusive_courts = bool(re.search(r"(?:exclusive\s+jurisdiction\s+of\s+(?:the\s+)?courts?\s+(?:at|in|of)\s+([A-Za-z\s]+?)(?:\.|\n|;|,|and))", text, re.IGNORECASE))
        has_arbitration_seat = bool(re.search(r"(?:arbitration\s+(?:shall\s+be\s+held|seated|conducted)\s+(?:at|in)\s+([A-Za-z\s]+?)(?:\.|\n|;|,))", text, re.IGNORECASE))

        # Check for multi-city forum conflict
        forum_cities = []
        for city in ["Bengaluru", "Bangalore", "Mysuru", "Mysore", "Mumbai", "Delhi", "Chennai", "Hyderabad", "Kolkata", "London", "Singapore"]:
            if re.search(rf"\b{city}\b", text, re.IGNORECASE):
                # Normalize city name
                norm = "Bengaluru" if city.lower() in ["bengaluru", "bangalore"] else ("Mysuru" if city.lower() in ["mysuru", "mysore"] else city)
                if norm not in forum_cities:
                    forum_cities.append(norm)

        has_arbitration_clause = bool(re.search(r"\b(arbitration|arbitrator|arbitral\s+tribunal)\b", lower))
        has_court_jurisdiction_clause = bool(re.search(r"\b(exclusive\s+jurisdiction\s+of\s+courts|subject\s+to\s+the\s+jurisdiction\s+of)\b", lower))

        if (len(forum_cities) >= 2 and (has_arbitration_clause or has_court_jurisdiction_clause)) or (has_exclusive_courts and has_arbitration_seat):
            conflicts_count += 1
            findings.append(AgentFindingModel(
                id="contra-forum-01",
                agent="Contradiction Agent",
                dimension="Legal",
                category="Dispute Resolution & Jurisdiction",
                severity="HIGH",
                risk_score=80,
                clause_type="Jurisdiction & Forum Contradiction",
                clause_text=f"Dispute resolution clauses designate conflicting venues / forums: {', '.join(forum_cities)} (e.g. exclusive civil court jurisdiction vs. separate arbitral venue).",
                page_number=1,
                evidence=f"Designated forum cities: {', '.join(forum_cities)} across arbitration and civil court jurisdiction clauses.",
                claim="Dispute resolution mechanism is inconsistent.",
                reason="Simultaneous designation of conflicting exclusive court jurisdictions and distinct arbitration venues can lead to protracted jurisdictional challenges under the Arbitration and Conciliation Act 1996.",
                recommendation="Align dispute resolution into a single tiered clause: mediation followed by arbitration at a specified seat, with courts of that seat having exclusive supervisory jurisdiction.",
                source_type="DOCUMENT_TEXT",
                verification_status="TEXT_SUPPORTED",
                confidence=0.92
            ))

        # =========================================================================
        # 4. NOTICE PERIOD & TIMELINE INCONSISTENCY
        # =========================================================================
        notice_periods = list(set(re.findall(r"\b(\d{1,3})\s+(?:days?|calendar\s+days?|business\s+days?)\s+(?:written\s+)?notice\b", text, re.IGNORECASE)))
        if len(notice_periods) > 1:
            conflicts_count += 1
            findings.append(AgentFindingModel(
                id="contra-notice-01",
                agent="Contradiction Agent",
                dimension="Operational",
                category="Notices & Formal Communications",
                severity="MEDIUM",
                risk_score=60,
                clause_type="Inconsistent Notice Timelines",
                clause_text=f"Multiple conflicting notice timelines detected in document: {', '.join(notice_periods)} days.",
                page_number=1,
                evidence=f"Notice periods: {', '.join(notice_periods)} days.",
                claim="Notice durations are contradictory.",
                reason=f"Document specifies different notice requirements ({', '.join(notice_periods)} days), creating ambiguity on valid cure or termination procedures.",
                recommendation="Harmonize notice periods across all termination and breach sections to a single uniform duration.",
                source_type="DOCUMENT_TEXT",
                verification_status="TEXT_SUPPORTED",
                confidence=0.89
            ))

        # If no contradictions found
        if not findings:
            findings.append(AgentFindingModel(
                id="contra-clean-01",
                agent="Contradiction Agent",
                dimension="Operational",
                category="Internal Consistency",
                severity="INFORMATIONAL",
                risk_score=10,
                clause_type="Internal Consistency Audit",
                clause_text="No glaring internal clause contradictions, payment discrepancies, or possession clashes detected.",
                page_number=1,
                evidence="Full document scan for mutually exclusive recitals.",
                claim="Document recitals appear internally consistent.",
                reason="Terms, schedules, and forum recitals do not exhibit glaring mutual exclusivity on preliminary scan.",
                recommendation="Maintain standardized definitions across all schedules and annexures.",
                source_type="DOCUMENT_TEXT",
                verification_status="TEXT_SUPPORTED",
                confidence=0.91
            ))

        critical_count = len([f for f in findings if f.severity in ["CRITICAL", "HIGH"]])
        return AgentResult(
            agent_name=self.name,
            status="warning" if critical_count > 0 else "success",
            confidence=0.94,
            summary=f"Contradiction scan identified {conflicts_count} first-class internal contradiction(s) ({critical_count} critical/high severity).",
            findings=findings,
            data={
                "conflicts_detected": conflicts_count,
                "critical_conflicts": critical_count,
                "has_payment_contradiction": has_partial_balance_pending and has_full_payment_acknowledged,
                "has_possession_contradiction": has_future_possession and has_delivered_possession,
                "has_forum_contradiction": len(forum_cities) >= 2
            }
        )
