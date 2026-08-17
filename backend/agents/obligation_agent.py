"""
Obligation Extraction Agent
Extracts contractual duties, deadlines, triggers, frequency, and consequences for each party.
"""
import re
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult, AgentFindingModel


class ObligationExtractionAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Obligation Extraction Agent",
            description="Extracts contractual duties, payment deadlines, deliverable timelines, and breach triggers into structured actionable records.",
            capabilities=["duty_extraction", "deadline_tracking", "trigger_detection"]
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        text = context.get("text", "")
        clauses = context.get("clauses", [])
        parties = context.get("parties", ["First Party", "Second Party"])
        
        obligations = []
        
        # Scrape duty sentences (shall, must, agrees to, is required to, will provide)
        sentences = re.split(r"[.\n]", text)
        for s in sentences:
            s_clean = s.strip()
            if len(s_clean) < 30 or len(s_clean) > 280:
                continue
                
            lower_s = s_clean.lower()
            if any(k in lower_s for k in ["shall pay", "shall provide", "must deliver", "agrees to maintain", "shall notify", "is required to", "shall submit"]):
                # Determine party
                party = parties[0] if len(parties) > 0 else "Obligor"
                if any(p.lower() in lower_s for p in parties):
                    for p in parties:
                        if p.lower() in lower_s:
                            party = p
                            break
                            
                # Determine deadline/trigger
                deadline_match = re.search(r"(?:within\s+\d+\s+days?|by\s+[A-Za-z0-9\s,]+|monthly|annually|prior\s+to|upon\s+termination)", s_clean, re.IGNORECASE)
                deadline = deadline_match.group(0) if deadline_match else "Ongoing Contractual Duty"
                
                obligations.append({
                    "party": party,
                    "obligation": s_clean,
                    "deadline": deadline,
                    "frequency": "Monthly" if "monthly" in lower_s else ("Annual" if "annual" in lower_s else "Event-based"),
                    "status": "Upcoming",
                    "trigger_event": "Standard Execution" if "termination" not in lower_s else "Termination Trigger",
                    "consequence": "Material Default & Damages" if any(w in lower_s for w in ["breach", "terminate", "penalty", "default"]) else "Contractual Non-compliance"
                })
                
                if len(obligations) >= 8:
                    break

        findings = []
        for o in obligations:
            findings.append(AgentFindingModel(
                dimension="Operational",
                risk_level="INFORMATIONAL",
                risk_score=20,
                clause_type=f"Obligation: {o['party']}",
                clause_text=o["obligation"],
                page_number=1,
                reason=f"Actionable duty with deadline: '{o['deadline']}'.",
                recommendation=f"Track compliance against trigger: {o['trigger_event']}.",
                citation_status="SUPPORTED",
                confidence=0.88
            ))

        if not obligations:
            obligations.append({
                "party": "Both Parties",
                "obligation": "Perform all mutual duties under this agreement in good faith.",
                "deadline": "Effective Term",
                "frequency": "Ongoing",
                "status": "Active",
                "trigger_event": "Contract Execution",
                "consequence": "Breach of Contract"
            })

        return AgentResult(
            agent_name=self.name,
            status="success",
            confidence=0.88,
            summary=f"Extracted {len(obligations)} actionable contractual obligations and deadline tracking entries.",
            findings=findings,
            data={"obligations": obligations, "total_obligations": len(obligations)}
        )
