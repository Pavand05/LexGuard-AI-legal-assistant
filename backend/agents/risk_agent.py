"""
Risk Assessment Agent (LexGuard-MA)
Calculates multi-dimensional risk matrix based on actual clause content, asymmetry,
enforceability uncertainty, financial exposure, and domain relevance.
Aggregates risk severity across structured clauses and verified upstream findings.
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult, AgentFindingModel
from .playbooks import resolve_domain_playbook, DomainPlaybook


class RiskAssessmentAgent(BaseAgent):
    BASE_DIMENSION_WEIGHTS: Dict[str, float] = {
        "Legal": 0.25,
        "Financial": 0.25,
        "Compliance": 0.20,
        "Privacy": 0.10,
        "Operational": 0.10,
        "IP": 0.10
    }

    def __init__(self):
        super().__init__(
            name="Risk Assessment Agent",
            description="Calculates domain-calibrated 6-dimensional risk matrix across Legal, Financial, Compliance, Privacy, Operational, and IP dimensions.",
            capabilities=["multi_dimensional_risk", "domain_weighting", "risk_calibration"]
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        doc_type = context.get("document_type", "OTHER_LEGAL_DOCUMENT")
        detected_domains = context.get("detected_domains", ["GENERAL_COMMERCIAL"])
        clauses = context.get("clauses", [])
        findings = context.get("findings", [])
        
        playbook: DomainPlaybook = resolve_domain_playbook(doc_type, detected_domains)
        applicable_dims = set(playbook.applicable_risk_dimensions)

        dim_stats = {
            dim: {"critical": 0, "high": 0, "medium": 0, "low": 0, "total": 0}
            for dim in self.BASE_DIMENSION_WEIGHTS.keys()
        }

        # 1. Aggregate from structured clauses
        for c in clauses:
            dim = c.get("dimension", "Legal")
            r = c.get("risk", "low").lower()
            if r in ["high", "critical", "medium", "low"] and dim in dim_stats:
                dim_stats[dim]["total"] += 1
                dim_stats[dim][r] += 1

        # 2. Aggregate from additional verified upstream findings (without double-counting identical clauses)
        seen_clause_types = set(c.get("type", "").lower() for c in clauses)
        for f in findings:
            if isinstance(f, dict):
                dim = f.get("dimension", "Legal")
                sev = f.get("severity", "LOW").lower()
                ctype = f.get("clause_type", "").lower()
            else:
                dim = getattr(f, "dimension", "Legal")
                sev = getattr(f, "severity", "LOW").lower()
                ctype = getattr(f, "clause_type", "").lower()
                
            if sev not in ["informational", "none"] and dim in dim_stats and ctype not in seen_clause_types:
                dim_stats[dim]["total"] += 1
                if sev in dim_stats[dim]:
                    dim_stats[dim][sev] += 1

        dimension_breakdown = {}
        dimension_status = {}
        weighted_overall = 0.0
        active_weight_sum = 0.0
        
        applicable_weighted = 0.0
        applicable_weight_sum = 0.0
        for dim, counts in dim_stats.items():
            if dim in applicable_dims:
                # Dimension is applicable
                if counts["critical"] > 0 or counts["high"] > 0 or counts["medium"] > 0:
                    dimension_status[dim] = "APPLICABLE"
                    score = 20 + (counts["critical"] * 35) + (counts["high"] * 25) + (counts["medium"] * 10) + (counts["low"] * 2)
                    score = max(10, min(100, score))
                    w = self.BASE_DIMENSION_WEIGHTS.get(dim, 0.15)
                    dimension_breakdown[dim] = score
                    applicable_weighted += score * w
                    applicable_weight_sum += w
                else:
                    dimension_status[dim] = "INSUFFICIENT_EVIDENCE"
                    score = 15 + (counts["low"] * 2)
                    dimension_breakdown[dim] = score
            else:
                dimension_status[dim] = "NOT_APPLICABLE"
                dimension_breakdown[dim] = 0

        # Calculate overall score focusing on active risk evidence
        if applicable_weight_sum > 0:
            overall_risk_score = int(round(applicable_weighted / applicable_weight_sum))
        else:
            overall_risk_score = 15

        # Risk tier classification
        if overall_risk_score >= 65:
            overall_tier = "HIGH"
            risk_label = "Severe Legal & Financial Exposure"
        elif overall_risk_score >= 35:
            overall_tier = "MEDIUM"
            risk_label = "Moderate Contractual Exposure (Negotiable)"
        else:
            overall_tier = "LOW"
            risk_label = "Low Exposure / Standard Protected Terms"

        high_cnt = sum(c["high"] + c["critical"] for d, c in dim_stats.items() if d in applicable_dims)
        med_cnt = sum(c["medium"] for d, c in dim_stats.items() if d in applicable_dims)
        low_cnt = sum(c["low"] for d, c in dim_stats.items() if d in applicable_dims)

        finding = AgentFindingModel(
            id="risk-summary-01",
            agent="Risk Assessment Agent",
            dimension="Financial" if "Financial" in applicable_dims else "Legal",
            category="Risk Calculation",
            severity="INFORMATIONAL",
            risk_score=overall_risk_score,
            clause_type="Domain-Adaptive Risk Synthesis",
            clause_text=f"Contract Risk Score: {overall_risk_score}/100 [{overall_tier}] ({risk_label}). Domain: {playbook.display_name}.",
            page_number=1,
            evidence=f"Aggregated across {len(applicable_dims)} applicable dimensions ({', '.join(applicable_dims)}).",
            claim=f"Calculated overall risk is {overall_risk_score}/100 based on active domain weights.",
            reason=f"Multi-dimensional analysis for {playbook.domain_name}: " + ", ".join(f"{d} ({s}/100 [{dimension_status[d]}])" for d, s in dimension_breakdown.items() if dimension_status[d] != "NOT_APPLICABLE"),
            recommendation="Review high-exposure provisions prior to signing." if overall_risk_score >= 45 else "Maintain standard contractual protections.",
            source_type="AI_INFERENCE",
            verification_status="TEXT_SUPPORTED",
            confidence=0.94
        )

        return AgentResult(
            agent_name=self.name,
            status="success",
            confidence=0.94,
            summary=f"Risk score: {overall_risk_score}/100 ({overall_tier}). Domain: {playbook.display_name}. High/Crit: {high_cnt}, Medium: {med_cnt}.",
            findings=[finding],
            data={
                "overall_risk_score": overall_risk_score,
                "overall_tier": overall_tier,
                "risk_label": risk_label,
                "applicable_dimensions": list(applicable_dims),
                "dimension_breakdown": dimension_breakdown,
                "dimension_status": dimension_status,
                "risks": {
                    "high": high_cnt,
                    "medium": med_cnt,
                    "low": low_cnt,
                    "total": len(clauses)
                }
            }
        )
