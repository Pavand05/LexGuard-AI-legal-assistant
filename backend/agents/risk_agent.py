"""
Risk Assessment Agent
Calculates domain-adaptive, explainable multi-dimensional risk scores.
Dynamically enables/disables risk dimensions (Legal, Financial, Compliance, Privacy, Operational, IP)
based on domain applicability:
- APPLICABLE: Actively contributes to aggregate risk score
- NOT_APPLICABLE: Domain is outside scope for this document type (e.g. IP in Land Deeds, Financial in basic NDAs)
- INSUFFICIENT_EVIDENCE: Applicable domain but no high/medium risk signals identified
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult, AgentFindingModel
from .playbooks import resolve_domain_playbook, DomainPlaybook


class RiskAssessmentAgent(BaseAgent):
    BASE_DIMENSION_WEIGHTS = {
        "Legal": 0.25,
        "Financial": 0.25,
        "Compliance": 0.20,
        "Operational": 0.15,
        "Privacy": 0.10,
        "IP": 0.05
    }

    def __init__(self):
        super().__init__(
            name="Risk Assessment Agent",
            description="Evaluates contractual risk across dynamic applicable dimensions with domain-adaptive mathematical scoring.",
            capabilities=["domain_adaptive_risk", "score_computation", "dimension_filtering", "exposure_analysis"]
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        doc_type = context.get("document_type", "OTHER_LEGAL_DOCUMENT")
        detected_domains = context.get("detected_domains", [])
        clauses = context.get("clauses", [])
        upstream_findings = context.get("findings", [])
        
        # 1. Resolve applicable dimensions from domain playbook
        playbook: DomainPlaybook = resolve_domain_playbook(doc_type, detected_domains)
        applicable_dims = set(playbook.applicable_risk_dimensions)
        
        # Auto-activate Privacy / IP if clauses exist in those areas regardless of playbook
        clause_dims = set(c.get("dimension", "Legal") for c in clauses)
        applicable_dims.update(clause_dims)

        # 2. Aggregate findings and clauses across dimensions
        dim_stats = {dim: {"critical": 0, "high": 0, "medium": 0, "low": 0, "total": 0} for dim in self.BASE_DIMENSION_WEIGHTS}
        
        for c in clauses:
            dim = c.get("dimension", "Legal")
            risk = c.get("risk", "low").lower()
            if dim in dim_stats:
                dim_stats[dim]["total"] += 1
                if risk in dim_stats[dim]:
                    dim_stats[dim][risk] += 1

        for f in upstream_findings:
            if isinstance(f, dict):
                dim = f.get("dimension", "Legal")
                sev = f.get("severity", "LOW").lower()
            else:
                dim = getattr(f, "dimension", "Legal")
                sev = getattr(f, "severity", "LOW").lower()
                
            if dim in dim_stats:
                dim_stats[dim]["total"] += 1
                if sev in dim_stats[dim]:
                    dim_stats[dim][sev] += 1

        dimension_breakdown = {}
        dimension_status = {}
        weighted_overall = 0.0
        active_weight_sum = 0.0
        
        for dim, counts in dim_stats.items():
            if dim in applicable_dims:
                # Dimension is applicable
                if counts["critical"] > 0 or counts["high"] > 0 or counts["medium"] > 0:
                    dimension_status[dim] = "APPLICABLE"
                    score = 15 + (counts["critical"] * 35) + (counts["high"] * 20) + (counts["medium"] * 10) + (counts["low"] * 2)
                else:
                    dimension_status[dim] = "INSUFFICIENT_EVIDENCE"
                    score = 15 + (counts["low"] * 2)
                    
                score = max(10, min(100, score))
                w = self.BASE_DIMENSION_WEIGHTS.get(dim, 0.15)
                dimension_breakdown[dim] = score
                weighted_overall += score * w
                active_weight_sum += w
            else:
                # Dimension is outside document domain
                dimension_status[dim] = "NOT_APPLICABLE"
                dimension_breakdown[dim] = 0

        # Normalize score over applicable dimensions only
        if active_weight_sum > 0:
            overall_risk_score = int(round(weighted_overall / active_weight_sum))
        else:
            overall_risk_score = 20

        # Risk tier classification
        if overall_risk_score >= 70:
            overall_tier = "CRITICAL / HIGH"
            risk_label = "Severe Legal & Financial Exposure"
        elif overall_risk_score >= 45:
            overall_tier = "MEDIUM"
            risk_label = "Moderate Contractual Exposure (Negotiable)"
        else:
            overall_tier = "LOW"
            risk_label = "Low Exposure / Standard Terms"

        high_cnt = sum(c["high"] + c["critical"] for d, c in dim_stats.items() if d in applicable_dims)
        med_cnt = sum(c["medium"] for d, c in dim_stats.items() if d in applicable_dims)
        low_cnt = sum(c["low"] for d, c in dim_stats.items() if d in applicable_dims)
        
        legacy_risks = {
            "high": high_cnt,
            "medium": med_cnt,
            "low": low_cnt,
            "total": len(clauses)
        }

        finding = AgentFindingModel(
            id="risk-summary-01",
            agent="Risk Assessment Agent",
            dimension="Financial" if "Financial" in applicable_dims else "Legal",
            category="Risk Calculation",
            severity=overall_tier.split(" ")[0],
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
            summary=f"Contract Risk Score: {overall_risk_score}/100 ({overall_tier} Risk). Active Domain: {playbook.display_name}.",
            findings=[finding],
            data={
                "overall_score": overall_risk_score,
                "overall_tier": overall_tier,
                "risk_label": risk_label,
                "dimensions": dimension_breakdown,
                "dimension_status": dimension_status,
                "applicable_dimensions": list(applicable_dims),
                "legacy_risks": legacy_risks,
                "scoring_formula": "Normalized sum over APPLICABLE dimensions: sum(w_i * Dim_Score_i) / sum(w_applicable)"
            }
        )
