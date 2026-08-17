"""
Redlining Intelligence Agent
Generates safe tracked-changes and word-level visual diffs between original clauses and proposed redlines.
Never overwrites original files; provides interactive Accept / Reject / Edit states.
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult, AgentFindingModel
from agent_tools.diff_tools import compute_clause_diff


class RedliningIntelligenceAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Redlining Agent",
            description="Generates suggested clause modifications, redline tracked changes, and side-by-side visual diffs.",
            capabilities=["visual_diff", "redlining", "revision_tracking"]
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        negotiations = context.get("negotiation_items", [])
        redlines = []
        findings = []

        for idx, neg in enumerate(negotiations):
            orig = neg.get("original_text", "")
            prop = neg.get("recommended_position", "")
            
            if not orig or neg.get("priority") == "ACCEPTABLE":
                continue
                
            diff_res = compute_clause_diff(orig, prop)
            redline_entry = {
                "id": f"redline-{idx+1}",
                "clause_type": neg.get("clause_type", "Clause"),
                "original_text": orig,
                "proposed_text": prop,
                "fallback_text": neg.get("fallback_position", ""),
                "diff_html": diff_res["diff_html"],
                "reason": neg.get("problem", ""),
                "status": "pending",  # pending | accepted | rejected | modified
                "stats": {
                    "added": diff_res["added_words"],
                    "removed": diff_res["removed_words"]
                }
            }
            redlines.append(redline_entry)
            
            findings.append(AgentFindingModel(
                dimension="Legal",
                risk_level="INFORMATIONAL",
                risk_score=20,
                clause_type=f"Redline: {neg.get('clause_type')}",
                clause_text=orig[:150],
                page_number=1,
                reason=f"Generated visual redline track changes (+{diff_res['added_words']}, -{diff_res['removed_words']} words).",
                recommendation="Review and click Accept or Edit to adopt proposed redline.",
                citation_status="SUPPORTED",
                confidence=0.90
            ))

        return AgentResult(
            agent_name=self.name,
            status="success",
            confidence=0.90,
            summary=f"Generated {len(redlines)} clause redline(s) with visual difference tracking.",
            findings=findings,
            data={"redlines": redlines, "total_redlines": len(redlines)}
        )
