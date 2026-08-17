"""
Reviewer & Critic Agent
Performs cross-agent consensus verification, quality audit, disagreement resolution,
and calculates the overall Contract Health Score (0-100).
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult, AgentFindingModel


class ReviewerCriticAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Reviewer Agent",
            description="Audits all upstream agent findings, checks evidence grounding, resolves agent disagreements, and determines the Contract Health Score.",
            capabilities=["consensus_review", "critic_evaluation", "contract_health_scoring", "hitl_trigger"]
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        agent_results = context.get("agent_results", {})
        all_findings = []
        for a_name, a_res in agent_results.items():
            all_findings.extend(a_res.findings)

        # 1. Check for cross-agent disagreements (e.g. Risk Agent vs Compliance Agent)
        high_risk_findings = [f for f in all_findings if f.risk_level == "HIGH"]
        compliance_findings = [f for f in all_findings if f.dimension == "Compliance" and f.risk_level in ["HIGH", "MEDIUM"]]
        unverified_citations = [f for f in all_findings if f.citation_status in ["UNVERIFIED", "NOT_SUPPORTED"] and f.risk_level == "HIGH"]

        disagreements = []
        if unverified_citations:
            disagreements.append(
                f"Citation Agent flagged {len(unverified_citations)} high-risk finding(s) as unverified against official statutes."
            )

        # 2. Compute Contract Health Score (0-100)
        # Base = 100
        # Deduct for high risks (-12 each, max 40)
        # Deduct for compliance gaps (-8 each, max 25)
        # Deduct for unverified citations (-5 each, max 15)
        # Deduct for missing clauses (-6 each, max 20)
        risk_deduction = min(40, len(high_risk_findings) * 12)
        comp_deduction = min(25, len(compliance_findings) * 8)
        cit_deduction = min(15, len(unverified_citations) * 5)
        
        missing_data = agent_results.get("Missing Clause Agent", None)
        missing_count = len(missing_data.data.get("missing_clauses", [])) if missing_data else 0
        missing_deduction = min(20, missing_count * 6)

        total_deductions = risk_deduction + comp_deduction + cit_deduction + missing_deduction
        health_score = max(10, min(100, 100 - total_deductions))

        # Health tier classification
        if health_score >= 80:
            health_grade = "A (Strong & Protected)"
        elif health_score >= 65:
            health_grade = "B (Moderate Risks / Negotiable)"
        elif health_score >= 45:
            health_grade = "C (Significant Exposure / High Gaps)"
        else:
            health_grade = "D (Critical Liabilities & Non-compliant)"

        needs_human_review = len(high_risk_findings) > 0 or health_score < 70 or len(disagreements) > 0

        findings = [
            AgentFindingModel(
                dimension="Legal",
                risk_level="INFORMATIONAL",
                risk_score=10,
                clause_type="Reviewer Consensus Audit",
                clause_text=f"Contract Health Score: {health_score}/100 [Grade: {health_grade}].",
                page_number=1,
                reason=f"Synthesized {len(all_findings)} finding(s) across {len(agent_results)} specialized agents. Deductions: Risks (-{risk_deduction}), Compliance (-{comp_deduction}), Missing Clauses (-{missing_deduction}).",
                recommendation="Human Legal Counsel review recommended prior to signature." if needs_human_review else "Document is well-balanced for execution.",
                citation_status="SUPPORTED",
                confidence=0.96
            )
        ]

        return AgentResult(
            agent_name=self.name,
            status="success",
            confidence=0.96,
            summary=f"Final Multi-Agent Consensus: Contract Health Score is {health_score}/100 ({health_grade}). Human review required: {'YES' if needs_human_review else 'NO'}.",
            findings=findings,
            data={
                "health_score": health_score,
                "health_grade": health_grade,
                "needs_human_review": needs_human_review,
                "disagreements": disagreements,
                "total_findings": len(all_findings),
                "scoring_formula": "100 - (Risk_Ded + Comp_Ded + Missing_Ded + Citation_Ded)"
            }
        )
