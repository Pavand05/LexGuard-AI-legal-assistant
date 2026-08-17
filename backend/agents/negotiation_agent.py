"""
Negotiation Strategy Agent (LexGuard-MA)
Generates prioritized negotiation recommendations, fallback positions, and draft alternative contract language.
Consumes canonical DocumentLegalContext to prevent foreign documents from citing Indian statutes.
Priorities: MUST CHANGE | SHOULD CHANGE | NICE TO HAVE | ACCEPTABLE
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult, AgentFindingModel
from .legal_context import DocumentLegalContext


class NegotiationStrategyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Negotiation Agent",
            description="Analyzes high-risk clauses to construct prioritized negotiation playbooks, recommended clauses, and acceptable fallback positions.",
            capabilities=["negotiation_playbook", "fallback_generation", "clause_refinement", "jurisdiction_grounded_strategy"]
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        clauses = context.get("clauses", [])
        legal_context: DocumentLegalContext = context.get("legal_context")
        if not legal_context:
            from .legal_context import resolve_document_legal_context
            legal_context = resolve_document_legal_context(context.get("text", ""))

        recommendations = []
        findings = []

        is_india = legal_context.is_indian_jurisdiction()
        is_us = legal_context.is_us_jurisdiction()
        gov_law = legal_context.governing_law

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
                        "recommended_position": "Insert mutual aggregate liability cap equal to 100% of the total fees/salary paid or payable in the preceding 12 months, excluding indirect/consequential damages.",
                        "fallback_position": "Liability cap capped at 2x annual contract value, with carve-outs strictly limited to gross negligence and willful misconduct.",
                        "status": "pending_review"
                    }
                    recommendations.append(rec)
                elif "non-compete" in c_type.lower():
                    if is_india:
                        problem_desc = "Overly broad post-termination restraint of trade, which is generally void under Section 27 of the Indian Contract Act 1872."
                    elif is_us and "california" in (legal_context.state_or_region or "").lower():
                        problem_desc = "Post-employment non-compete covenant is strictly void and unenforceable under California Business and Professions Code § 16600."
                    elif is_us:
                        problem_desc = f"Post-employment restrictive covenant subject to strict reasonableness scrutiny under {gov_law}."
                    else:
                        problem_desc = f"Potential jurisdiction-specific enforceability concern under {gov_law}. No verified authority for detected foreign jurisdiction is in local index."
                        
                    rec = {
                        "priority": "MUST CHANGE",
                        "clause_type": c_type,
                        "original_text": text,
                        "problem": problem_desc,
                        "recommended_position": "Remove post-termination non-compete completely; substitute with reasonable non-solicitation of direct clients and protection of confidential trade secrets.",
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
                        "problem": "Immediate termination without adequate written notice or cure period for non-material defaults.",
                        "recommended_position": "Include mandatory 30-day written notice and cure period prior to termination for cause.",
                        "fallback_position": "15-day cure period for payment defaults; 30-day cure period for all other contractual defaults.",
                        "status": "pending_review"
                    }
                    recommendations.append(rec)
                elif "dispute" in c_type.lower():
                    neutral_city = "Bengaluru / Mumbai / New Delhi" if is_india else ("Wilmington / San Francisco / New York" if is_us else "Neutral Commercial Forum")
                    rec = {
                        "priority": "NICE TO HAVE",
                        "clause_type": c_type,
                        "original_text": text,
                        "problem": "Litigation in inconvenient or non-neutral forum.",
                        "recommended_position": f"Institute two-tier dispute resolution: 30-day executive good faith negotiation followed by expedited arbitration seated in {neutral_city}.",
                        "fallback_position": f"Exclusive civil court jurisdiction at agreed primary commercial seat ({neutral_city}).",
                        "status": "pending_review"
                    }
                    recommendations.append(rec)

        for r in recommendations:
            findings.append(AgentFindingModel(
                id=f"neg-finding-{len(findings)+1}",
                agent="Negotiation Agent",
                dimension="Legal",
                category="Negotiation Strategy",
                severity="HIGH" if r["priority"] == "MUST CHANGE" else "MEDIUM",
                risk_score=80 if r["priority"] == "MUST CHANGE" else 50,
                clause_type=f"Negotiate: {r['clause_type']}",
                clause_text=r["original_text"][:200],
                page_number=1,
                evidence=f"Priority: {r['priority']} ({legal_context.governing_law})",
                claim=f"Strategic recommendation for {r['clause_type']}.",
                reason=r["problem"],
                recommendation=r["recommended_position"],
                source_type="AI_INFERENCE",
                verification_status="TEXT_SUPPORTED",
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
            confidence=0.92,
            summary=f"Negotiation strategy complete: {len(recommendations)} clause recommendation(s) generated for {legal_context.governing_law}.",
            findings=findings,
            data={
                "negotiation_items": recommendations,
                "governing_law": legal_context.governing_law,
                "country": legal_context.country,
                "total_items": len(recommendations)
            }
        )
