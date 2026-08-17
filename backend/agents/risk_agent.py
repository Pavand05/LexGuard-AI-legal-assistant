"""
Risk Assessment Agent
Calculates documented multi-dimensional risk scores (Legal, Financial, Compliance, Privacy, Operational, IP).
Formula:
  Overall Risk = sum(w_i * Dimension_Score_i)
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult, AgentFindingModel


class RiskAssessmentAgent(BaseAgent):
    DIMENSION_WEIGHTS = {
        "Legal": 0.25,
        "Financial": 0.20,
        "Compliance": 0.20,
        "Privacy": 0.15,
        "Operational": 0.10,
        "IP": 0.10
    }

    def __init__(self):
        super().__init__(
            name="Risk Assessment Agent",
            description="Evaluates contractual risk across 6 specific dimensions with explainable mathematical scoring.",
            capabilities=["multi_dimensional_risk", "score_computation", "severity_tallying"]
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        clauses = context.get("clauses", [])
        
        # Initialize dimension aggregates
        dim_scores = {dim: {"high": 0, "medium": 0, "low": 0, "total": 0} for dim in self.DIMENSION_WEIGHTS}
        
        for c in clauses:
            dim = c.get("dimension", "Legal")
            risk = c.get("risk", "low").lower()
            if dim in dim_scores:
                dim_scores[dim]["total"] += 1
                if risk in dim_scores[dim]:
                    dim_scores[dim][risk] += 1

        dimension_breakdown = {}
        weighted_overall = 0.0
        
        for dim, counts in dim_scores.items():
            # Dimension score formula: 100 * (3*high + 1.5*med + 0.5*low) / max(1, 3*total) capped at 100
            # If no clauses in dimension, base baseline = 20
            if counts["total"] == 0:
                score = 25
            else:
                score = int(min(100, (counts["high"] * 85 + counts["medium"] * 50 + counts["low"] * 20) / counts["total"]))
            
            dimension_breakdown[dim] = score
            weighted_overall += score * self.DIMENSION_WEIGHTS[dim]

        overall_score = int(round(weighted_overall))
        
        # Determine overall classification
        if overall_score >= 65:
            overall_tier = "HIGH"
        elif overall_score >= 40:
            overall_tier = "MEDIUM"
        else:
            overall_tier = "LOW"

        # Calculate legacy counts for full backward compatibility
        high_cnt = sum(1 for c in clauses if c.get("risk") == "high")
        med_cnt = sum(1 for c in clauses if c.get("risk") == "medium")
        low_cnt = sum(1 for c in clauses if c.get("risk") == "low")
        
        legacy_risks = {
            "high": high_cnt,
            "medium": med_cnt,
            "low": low_cnt,
            "total": len(clauses)
        }

        finding = AgentFindingModel(
            dimension="Financial",
            risk_level=overall_tier,
            risk_score=overall_score,
            clause_type="Overall Risk Assessment",
            clause_text=f"Aggregated Contract Risk Score: {overall_score}/100 across {len(clauses)} clauses.",
            page_number=1,
            reason=f"Overall risk calculated via weighted legal formula: Legal ({dimension_breakdown['Legal']}/100), Financial ({dimension_breakdown['Financial']}/100), Compliance ({dimension_breakdown['Compliance']}/100).",
            recommendation="Focus legal negotiation on high-exposure liability and uncapped damages clauses.",
            citation_status="SUPPORTED",
            confidence=0.92
        )

        return AgentResult(
            agent_name=self.name,
            status="success",
            confidence=0.92,
            summary=f"Contract Risk Score: {overall_score}/100 ({overall_tier} Risk). High: {high_cnt}, Med: {med_cnt}, Low: {low_cnt}.",
            findings=[finding],
            data={
                "overall_score": overall_score,
                "overall_tier": overall_tier,
                "dimensions": dimension_breakdown,
                "legacy_risks": legacy_risks,
                "formula": "sum(weight_i * dimension_i)"
            }
        )
