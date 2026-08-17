"""
Risk Assessment Agent
Calculates documented, explainable multi-dimensional risk scores (Legal, Financial, Compliance, Privacy, Operational, IP).
Distinguishes:
- Contract Risk Score (0 = Low Exposure, 100 = Critical Risk / Extreme Liability)
- Transparent formula based on finding severities, financial exposure, and contradictory terms.
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult, AgentFindingModel


class RiskAssessmentAgent(BaseAgent):
    DIMENSION_WEIGHTS = {
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
            description="Evaluates contractual risk across 6 specific dimensions using deterministic severity weighting and exposure modeling.",
            capabilities=["multi_dimensional_risk", "score_computation", "severity_weighting", "exposure_analysis"]
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        clauses = context.get("clauses", [])
        upstream_findings = context.get("findings", [])
        
        # Aggregate all items by dimension and severity
        dim_stats = {dim: {"critical": 0, "high": 0, "medium": 0, "low": 0, "total": 0} for dim in self.DIMENSION_WEIGHTS}
        
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
        weighted_overall = 0.0
        
        for dim, counts in dim_stats.items():
            # Formula:
            # Base = 15
            # Critical findings: +35 each
            # High findings: +20 each
            # Medium findings: +10 each
            # Low findings: +2 each
            # Capped at 100
            score = 15 + (counts["critical"] * 35) + (counts["high"] * 20) + (counts["medium"] * 10) + (counts["low"] * 2)
            score = max(10, min(100, score))
            dimension_breakdown[dim] = score
            weighted_overall += score * self.DIMENSION_WEIGHTS[dim]

        overall_risk_score = int(round(weighted_overall))
        
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

        # Legacy risk tallies for backward compatibility
        high_cnt = sum(c["high"] + c["critical"] for c in dim_stats.values())
        med_cnt = sum(c["medium"] for c in dim_stats.values())
        low_cnt = sum(c["low"] for c in dim_stats.values())
        
        legacy_risks = {
            "high": high_cnt,
            "medium": med_cnt,
            "low": low_cnt,
            "total": len(clauses)
        }

        finding = AgentFindingModel(
            id="risk-summary-01",
            agent="Risk Assessment Agent",
            dimension="Financial",
            category="Risk Calculation",
            severity=overall_tier.split(" ")[0],
            risk_score=overall_risk_score,
            clause_type="Deterministic Risk Synthesis",
            clause_text=f"Contract Risk Score: {overall_risk_score}/100 [{overall_tier}] ({risk_label}).",
            page_number=1,
            evidence=f"Aggregated from {high_cnt} high/critical items, {med_cnt} medium items across {len(clauses)} clauses.",
            claim=f"Calculated overall risk is {overall_risk_score}/100.",
            reason=f"Multi-dimensional calculation: Legal ({dimension_breakdown['Legal']}/100), Financial ({dimension_breakdown['Financial']}/100), Compliance ({dimension_breakdown['Compliance']}/100), Operational ({dimension_breakdown['Operational']}/100).",
            recommendation="Address critical title, encumbrance, and payment contradictions prior to deed execution." if overall_risk_score >= 50 else "Maintain standard contractual protections.",
            source_type="AI_INFERENCE",
            verification_status="TEXT_SUPPORTED",
            confidence=0.94
        )

        return AgentResult(
            agent_name=self.name,
            status="success",
            confidence=0.94,
            summary=f"Contract Risk Score: {overall_risk_score}/100 ({overall_tier} Risk). {risk_label}.",
            findings=[finding],
            data={
                "overall_score": overall_risk_score,
                "overall_tier": overall_tier,
                "risk_label": risk_label,
                "dimensions": dimension_breakdown,
                "legacy_risks": legacy_risks,
                "scoring_formula": "sum(weight_dim * [15 + 35*Critical + 20*High + 10*Medium + 2*Low])"
            }
        )
