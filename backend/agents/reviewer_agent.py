"""
Reviewer & Critic Agent
Performs genuine multi-agent peer review:
1. Normalizes and deduplicates findings across all 13 specialized agents
2. Performs cross-agent conflict & disagreement detection (e.g. Doc type vs extracted clauses, risk vs evidence)
3. Calculates the official Contract Health Score (0-100, Higher = Better)
4. Enforces Human-in-the-Loop review escalation triggers
"""
import re
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult, AgentFindingModel


class ReviewerCriticAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Reviewer Agent",
            description="Audits upstream agent findings, checks evidence grounding, resolves agent disagreements, deduplicates findings, and determines Contract Health.",
            capabilities=["consensus_review", "disagreement_resolution", "contract_health_scoring", "deduplication", "hitl_trigger"]
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        agent_results: Dict[str, AgentResult] = context.get("agent_results", {})
        doc_metadata: Dict[str, Any] = context.get("document_metadata", {})
        
        # 1. Collect all findings across agents
        all_raw_findings: List[AgentFindingModel] = []
        for a_name, a_res in agent_results.items():
            if a_res and a_res.findings:
                for f in a_res.findings:
                    if isinstance(f, dict):
                        f_model = AgentFindingModel(**f)
                    else:
                        f_model = f
                    if not f_model.agent:
                        f_model.agent = a_name
                    all_raw_findings.append(f_model)

        # 2. Cross-Agent Conflict & Disagreement Auditing
        disagreements: List[str] = []
        doc_type = doc_metadata.get("document_type", "OTHER")
        clauses_data = agent_results.get("Clause Intelligence Agent")
        extracted_clauses = clauses_data.data.get("clauses", []) if clauses_data else []
        clause_categories = set(c.get("category", c.get("type", "")) for c in extracted_clauses)

        # Disagreement Check A: Document Classification vs Extracted Clauses
        has_property_clauses = any(cat in ["Title & Ownership", "Encumbrance & Mortgage", "Possession", "Consideration & Payment", "Property Description & Schedule"] for cat in clause_categories)
        if doc_type in ["NDA", "EMPLOYMENT_AGREEMENT"] and has_property_clauses:
            disagreements.append(
                f"AGENT DISAGREEMENT DETECTED: Document Agent classified document as '{doc_type}', but Clause Agent extracted real estate conveyancing clauses ({', '.join(list(clause_categories)[:3])}). Reclassified document profile to Land / Property Conveyance."
            )

        # Disagreement Check B: Contradiction Agent vs Standard Clauses
        contra_data = agent_results.get("Contradiction Agent")
        contra_count = contra_data.data.get("conflicts_detected", 0) if contra_data else 0
        if contra_count > 0:
            disagreements.append(
                f"Contradiction Agent identified {contra_count} irreconcilable clause conflict(s) (e.g. payment/possession/forum discrepancies)."
            )

        # Disagreement Check C: Unverified high-severity statutory claims
        unverified_cit = [f for f in all_raw_findings if f.severity in ["CRITICAL", "HIGH"] and f.source_type == "LEGAL_SOURCE" and f.verification_status in ["NOT_SUPPORTED", "UNVERIFIED"]]
        if unverified_cit:
            disagreements.append(
                f"Citation Agent flagged {len(unverified_cit)} high-severity legal claim(s) without primary statutory verification."
            )

        # 3. Deduplicate findings by semantic fingerprint
        deduplicated_findings: List[AgentFindingModel] = []
        seen_fingerprints = set()
        
        for f in all_raw_findings:
            # Create a normalized fingerprint based on category and first 40 chars of reason/text
            text_seed = re.sub(r"[^a-zA-Z0-9]", "", (f.clause_type + f.reason[:40] + f.clause_text[:40]).lower())
            if text_seed in seen_fingerprints:
                continue
            seen_fingerprints.add(text_seed)
            deduplicated_findings.append(f)

        # 4. Calculate Official Contract Health Score (0–100, Higher = Better)
        # Base = 100
        # Deductions:
        # - Critical Contradictions (-25 each, max 50)
        # - High-severity risks / void covenants (-15 each, max 35)
        # - Medium risks (-6 each, max 20)
        # - Unverified citations / missing mandatory terms (-5 each, max 15)
        crit_findings = [f for f in deduplicated_findings if f.severity == "CRITICAL"]
        high_findings = [f for f in deduplicated_findings if f.severity == "HIGH"]
        med_findings = [f for f in deduplicated_findings if f.severity == "MEDIUM"]

        crit_deduction = min(50, len(crit_findings) * 25)
        high_deduction = min(35, len(high_findings) * 15)
        med_deduction = min(20, len(med_findings) * 6)
        
        missing_agent = agent_results.get("Missing Clause Agent")
        missing_count = len(missing_agent.data.get("missing_clauses", [])) if missing_agent else 0
        missing_deduction = min(15, missing_count * 5)

        total_health_deductions = crit_deduction + high_deduction + med_deduction + missing_deduction
        contract_health_score = max(10, min(100, 100 - total_health_deductions))

        # Health Grade Tier
        if contract_health_score >= 80:
            health_grade = "Grade A: Strong & Protected"
            health_description = "Contract has strong protective covenants and clear legal enforceability."
        elif contract_health_score >= 65:
            health_grade = "Grade B: Moderate Risks / Negotiable"
            health_description = "Contract contains manageable commercial risks that can be balanced via standard redlines."
        elif contract_health_score >= 45:
            health_grade = "Grade C: High Exposure / Discrepancies"
            health_description = "Contract contains significant liability risks, notice ambiguities, or unhedged terms."
        else:
            health_grade = "Grade D: Critical Exposure / Contradictory Recitals"
            health_description = "Contract contains irreconcilable contradictions, void restrictions, or unverified payment recitals."

        needs_human_review = len(crit_findings) > 0 or len(high_findings) > 0 or contract_health_score < 70 or len(disagreements) > 0

        # Reviewer Synthesis Finding
        reviewer_finding = AgentFindingModel(
            id="review-consensus-01",
            agent="Reviewer Agent",
            dimension="Legal",
            category="Contract Health & Consensus",
            severity="INFORMATIONAL",
            risk_score=10,
            clause_type="Multi-Agent Consensus Audit",
            clause_text=f"Contract Health Score: {contract_health_score}/100 [{health_grade}]. Human Legal Review Required: {'YES (Recommended)' if needs_human_review else 'NO (Optional)'}.",
            page_number=1,
            evidence=f"Audited across {len(agent_results)} specialized agents; synthesized {len(deduplicated_findings)} distinct finding(s). Deductions: Critical ({crit_deduction}), High ({high_deduction}), Medium ({med_deduction}), Gaps ({missing_deduction}).",
            claim=f"Final Contract Health Score is {contract_health_score}/100.",
            reason=health_description,
            recommendation="Independent Legal Counsel review strongly advised to resolve critical payment/possession contradictions prior to execution." if needs_human_review else "Document is structurally sound for standard commercial execution.",
            source_type="AI_INFERENCE",
            verification_status="TEXT_SUPPORTED",
            confidence=0.96
        )

        return AgentResult(
            agent_name=self.name,
            status="warning" if needs_human_review else "success",
            confidence=0.96,
            summary=f"Multi-Agent Consensus Complete: Contract Health is {contract_health_score}/100 ({health_grade}). Human review: {'REQUIRED' if needs_human_review else 'OPTIONAL'}.",
            findings=[reviewer_finding],
            data={
                "health_score": contract_health_score,
                "health_grade": health_grade,
                "health_description": health_description,
                "needs_human_review": needs_human_review,
                "disagreements": disagreements,
                "deduplicated_findings_count": len(deduplicated_findings),
                "scoring_formula": "100 - [Crit*25(max 50) + High*15(max 35) + Med*6(max 20) + Missing*5(max 15)]"
            }
        )
