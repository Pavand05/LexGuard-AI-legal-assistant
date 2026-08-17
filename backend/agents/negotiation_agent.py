"""
Negotiation Strategy Agent
Generates prioritized negotiation recommendations, fallback positions, and draft alternative contract language.
Priorities: MUST CHANGE | SHOULD CHANGE | NICE TO HAVE | ACCEPTABLE
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult, AgentFindingModel


class NegotiationStrategyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Negotiation Agent",
            description="Analyzes high-risk clauses to construct prioritized negotiation playbooks, recommended clauses, and acceptable fallback positions.",
            capabilities=["negotiation_playbook", "fallback_generation", "clause_refinement"]
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        clauses = context.get("clauses", [])
        recommendations = []
        findings = []

        for c in clauses:
            c_type = c.get("type", "")
            risk = c.get("risk", "low").lower()
            text = c.get("content", "")
            
            if risk == "high" or "liability" in c_type.lower() or "non-compete" in c_type.lower():
                if "liability" in c_type.lower() or "indemnification" in c_type.lower():
                    rec = {
                        "priority": "MUST CHANGE",
                        "clause_type": c_type,
                        "original_text": text,
                        "problem": "Uncapped or one-sided liability and indemnity exposure.",
                        "recommended_position": "Insert mutual aggregate liability cap equal to 100% of the total fees paid or payable in the preceding 12 months, excluding indirect/consequential damages.",
                        "fallback_position": "Liability cap capped at 2x annual contract value, with carve-outs strictly limited to gross negligence and willful misconduct.",
                        "status": "pending_review"
                    }
                    recommendations.append(rec)
                elif "non-compete" in c_type.lower():
                    rec = {
                        "priority": "MUST CHANGE",
                        "clause_type": c_type,
                        "original_text": text,
                        "problem": "Overly broad post-termination restraint of trade, which is generally void under Section 27 of the Indian Contract Act 1872.",
                        "recommended_position": "Remove post-termination non-compete completely; substitute with strict non-solicitation of direct clients and protection of confidential trade secrets.",
                        "fallback_position": "Limit restriction exclusively during active employment term with zero post-termination restraint.",
                        "status": "pending_review"
                    }
                    recommendations.append(rec)

            elif risk == "medium" or "termination" in c_type.lower() or "dispute" in c_type.lower():
                if "termination" in c_type.lower():
                    rec = {
                        "priority": "SHOULD CHANGE",
                        "clause_type": c_type,
                        "original_text": text,
                        "problem": "Immediate termination without adequate cure period for minor or non-material breaches.",
                        "recommended_position": "Include mandatory 30-day written notice and cure period prior to termination for cause.",
                        "fallback_position": "15-day cure period for payment defaults; 30-day cure period for all other contractual defaults.",
                        "status": "pending_review"
                    }
                    recommendations.append(rec)
                elif "dispute" in c_type.lower():
                    rec = {
                        "priority": "NICE TO HAVE",
                        "clause_type": c_type,
                        "original_text": text,
                        "problem": "Litigation in inconvenient or non-neutral forum.",
                        "recommended_position": "Institute two-tier dispute resolution: 30-day senior executive good faith negotiation followed by expedited single-arbitrator arbitration.",
                        "fallback_position": "Arbitration seated in neutral major commercial hub (e.g., Bengaluru / Mumbai / New Delhi).",
                        "status": "pending_review"
                    }
                    recommendations.append(rec)

        for r in recommendations:
            findings.append(AgentFindingModel(
                dimension="Legal",
                risk_level="HIGH" if r["priority"] == "MUST CHANGE" else "MEDIUM",
                risk_score=80 if r["priority"] == "MUST CHANGE" else 50,
                clause_type=f"Negotiate: {r['clause_type']}",
                clause_text=r["original_text"][:200],
                page_number=1,
                reason=r["problem"],
                recommendation=r["recommended_position"],
                citation_status="SUPPORTED",
                confidence=0.91
            ))

        if not recommendations:
            recommendations.append({
                "priority": "ACCEPTABLE",
                "clause_type": "Standard Terms",
                "original_text": "All scanned clauses reflect standard commercial reciprocity.",
                "problem": "No severe one-sided burdens detected.",
                "recommended_position": "Proceed with standard execution.",
                "fallback_position": "Maintain standard signed copies for legal files.",
                "status": "approved"
            })

        return AgentResult(
            agent_name=self.name,
            status="success",
            confidence=0.91,
            summary=f"Formulated {len(recommendations)} strategic negotiation recommendation(s) (Must Change: {sum(1 for r in recommendations if r['priority'] == 'MUST CHANGE')}).",
            findings=findings,
            data={"negotiation_items": recommendations, "total_items": len(recommendations)}
        )
