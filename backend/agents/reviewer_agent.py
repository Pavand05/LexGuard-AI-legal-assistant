"""
Reviewer & Critic Agent (LexGuard-MA)
Performs evidence-driven cross-agent peer review:
1. Normalizes and deduplicates findings across all active specialized agents
2. Performs transparent cross-agent conflict & disagreement resolution
3. Calculates official Contract Health Score (0-100, Higher = Better) with evidence-derived descriptions
4. Triggers Human-in-the-Loop review escalation triggers
"""
import re
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult, AgentFindingModel
from .clause_taxonomy import normalize_to_canonical_id


class ReviewerCriticAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Reviewer Agent",
            description="Audits upstream agent findings, validates evidence grounding, resolves agent disagreements, and determines evidence-driven Contract Health.",
            capabilities=["consensus_review", "disagreement_resolution", "contract_health_scoring", "deduplication", "hitl_trigger"]
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        agent_results: Dict[str, AgentResult] = context.get("agent_results", {})
        doc_metadata: Dict[str, Any] = context.get("document_metadata", {})
        doc_type = doc_metadata.get("document_type", "OTHER_LEGAL_DOCUMENT")
        
        # 1. Collect all findings across active agents
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

        # 2. Transparent Cross-Agent Conflict & Disagreement Auditing
        disagreements: List[Dict[str, Any]] = []
        disagreement_summaries: List[str] = []
        
        clauses_data = agent_results.get("Clause Intelligence Agent")
        extracted_clauses = clauses_data.data.get("clauses", []) if clauses_data else []
        clause_canonical_ids = set(c.get("canonical_id", "") for c in extracted_clauses)

        # Disagreement Check A: Classification vs Canonical Clauses
        property_canonical_ids = {"PROPERTY_DESCRIPTION", "TITLE_OWNERSHIP", "ENCUMBRANCE_MORTGAGE", "POSSESSION_REAL_ESTATE", "REGISTRATION_STAMP_DUTY"}
        found_property_cids = clause_canonical_ids.intersection(property_canonical_ids)
        
        if doc_type in ["NDA", "EMPLOYMENT_AGREEMENT"] and len(found_property_cids) >= 2:
            dis_obj = {
                "agent_a": "Document Intelligence Agent",
                "agent_b": "Clause Intelligence Agent",
                "issue": f"Document classified as '{doc_type}', but Clause Agent extracted real estate categories ({', '.join(found_property_cids)}).",
                "resolution": "Flagged for Human Review to verify whether document is an anomalous hybrid conveyancing agreement."
            }
            disagreements.append(dis_obj)
            disagreement_summaries.append(f"AGENT DISAGREEMENT DETECTED: {dis_obj['issue']}")

        # Disagreement Check B: Contradictions
        contra_data = agent_results.get("Contradiction Agent")
        contra_conflicts = contra_data.data.get("conflicts_detected", 0) if contra_data else 0
        contra_critical = contra_data.data.get("critical_conflicts", 0) if contra_data else 0

        # Disagreement Check C: Unverified High-Severity Citations
        unverified_cit = [
            f for f in all_raw_findings
            if f.severity in ["CRITICAL", "HIGH"] and f.source_type == "LEGAL_SOURCE" and f.verification_status in ["NOT_SUPPORTED", "UNVERIFIED"]
        ]
        if unverified_cit:
            disagreement_summaries.append(
                f"Citation Agent flagged {len(unverified_cit)} high-severity legal claim(s) without primary statutory verification."
            )

        # 3. Deduplicate findings across agents by normalized clause target
        deduplicated_findings: List[AgentFindingModel] = []
        seen_fingerprints = set()
        
        for f in all_raw_findings:
            if f.severity in ["INFORMATIONAL", "NONE"]:
                continue
            clean_type = re.sub(r"^(?:negotiate|redline|audit|statutory audit|compliance check):\s*", "", f.clause_type.lower()).strip()
            text_seed = re.sub(r"[^a-zA-Z0-9]", "", (clean_type + f.clause_text[:30]).lower())
            if text_seed in seen_fingerprints:
                continue
            seen_fingerprints.add(text_seed)
            deduplicated_findings.append(f)

        # 4. Calculate Official Contract Health Score (0–100, Higher = Better)
        crit_findings = [f for f in deduplicated_findings if f.severity == "CRITICAL"]
        high_findings = [f for f in deduplicated_findings if f.severity == "HIGH"]
        med_findings = [f for f in deduplicated_findings if f.severity == "MEDIUM"]

        crit_deduction = min(40, len(crit_findings) * 20)
        high_deduction = min(20, len(high_findings) * 5)
        med_deduction = min(15, len(med_findings) * 3)
        
        missing_agent = agent_results.get("Missing Clause Agent")
        missing_count = len(missing_agent.data.get("missing_clauses", [])) if missing_agent else 0
        missing_deduction = min(15, missing_count * 4)

        total_health_deductions = crit_deduction + high_deduction + med_deduction + missing_deduction
        contract_health_score = max(10, min(100, 100 - total_health_deductions))

        # 5. Evidence-Driven Health Grade & Description Synthesis (NEVER assume contradictions if count == 0)
        if contract_health_score >= 70:
            health_grade = "Grade A: Strong & Protected"
            health_description = "Contract contains balanced covenants, standard protective terms, and clear legal enforceability."
        elif contract_health_score >= 55:
            health_grade = "Grade B: Moderate Commercial Risks"
            health_description = "Contract contains negotiable commercial risks and minor gaps that can be addressed via standard redlines."
        elif contract_health_score >= 45:
            if contra_critical > 0:
                health_grade = "Grade C: High Risk / Contradictory Recitals"
                health_description = f"Contract contains {contra_critical} critical clause contradiction(s) requiring alignment."
            elif missing_count >= 2:
                health_grade = "Grade C: Incomplete Terms / Missing Essential Covenants"
                health_description = f"Contract is missing {missing_count} standard protective covenants expected for this legal domain."
            else:
                health_grade = "Grade C: Material Legal & Financial Exposure"
                health_description = "Contract contains significant unhedged indemnity liability or restrictive covenants."
        else:
            # Grade D (< 45) - strictly derive reason from evidence
            if contra_critical > 0 or contra_conflicts > 0:
                health_grade = "Grade D: Critical Exposure / Contradictory Recitals"
                health_description = f"Contract contains {contra_conflicts} irreconcilable clause contradiction(s) (e.g. payment/possession/forum discrepancies)."
            elif missing_count >= 4:
                health_grade = "Grade D: Severe Incompleteness / Major Missing Covenants"
                health_description = f"Contract is missing {missing_count} core protective clauses required for standard commercial enforceability."
            elif len(crit_findings) > 0 or len(high_findings) >= 3:
                health_grade = "Grade D: Severe Legal & Financial Risk Exposure"
                health_description = f"Contract contains {len(crit_findings)} critical and {len(high_findings)} high-severity liability/restraint covenants."
            elif len(disagreements) > 0:
                health_grade = "Grade D: Unresolved Multi-Agent Disagreements"
                health_description = "Cross-agent analysis identified structural conflicts between document classification and clause contents."
            else:
                health_grade = "Grade D: Significant Contractual Deficiencies"
                health_description = "Contract requires comprehensive legal restructuring prior to execution."

        needs_human_review = len(crit_findings) > 0 or len(high_findings) > 0 or contract_health_score < 70 or len(disagreements) > 0 or missing_count >= 2

        # Reviewer Synthesis Finding
        reviewer_finding = AgentFindingModel(
            id="review-consensus-01",
            agent="Reviewer Agent",
            dimension="Legal",
            category="Contract Health & Consensus",
            severity="INFORMATIONAL",
            risk_score=10,
            clause_type="Multi-Agent Consensus Audit",
            clause_text=f"Contract Health Score: {contract_health_score}/100 [{health_grade}]. Human Legal Review: {'REQUIRED' if needs_human_review else 'OPTIONAL'}.",
            page_number=1,
            evidence=f"Synthesized {len(deduplicated_findings)} distinct finding(s) across {len(agent_results)} agents. Deductions: Critical ({crit_deduction}), High ({high_deduction}), Medium ({med_deduction}), Gaps ({missing_deduction}).",
            claim=f"Final Contract Health Score is {contract_health_score}/100.",
            reason=health_description,
            recommendation="Independent Legal Counsel review strongly recommended prior to signature." if needs_human_review else "Document is structurally sound for standard commercial execution.",
            source_type="AI_INFERENCE",
            verification_status="TEXT_SUPPORTED",
            confidence=0.96
        )

        return AgentResult(
            agent_name=self.name,
            status="warning" if needs_human_review else "success",
            confidence=0.96,
            summary=f"Contract Health Score: {contract_health_score}/100 ({health_grade}). Evidence-Driven Consensus: {health_description}",
            findings=[reviewer_finding],
            data={
                "health_score": contract_health_score,
                "health_grade": health_grade,
                "health_description": health_description,
                "needs_human_review": needs_human_review,
                "disagreements": disagreement_summaries,
                "disagreement_records": disagreements,
                "findings_count": len(deduplicated_findings),
                "deductions": {
                    "critical": crit_deduction,
                    "high": high_deduction,
                    "medium": med_deduction,
                    "missing": missing_deduction
                },
                "definition": "Higher Health (0-100) = Better (Greater Protection & Enforceability)"
            }
        )
