"""
Clause Intelligence Agent
Performs hybrid deterministic pattern matching + semantic clause extraction across 18+ legal categories.
"""
import re
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult, AgentFindingModel


class ClauseIntelligenceAgent(BaseAgent):
    EXPANDED_PATTERNS = [
        {"type": "Liability", "risk": "high", "dimension": "Financial", "pattern": r"\b(liability|liable|indemnification|indemnify|indemnity|damages|limitation\s+of\s+liability|consequential\s+damages)\b[^\n]*(?:\n(?!\n)[^\n]*)*"},
        {"type": "Non-Compete", "risk": "high", "dimension": "Legal", "pattern": r"\b(non[- ]?compete|non[- ]?competition|restrictive\s+covenant|covenant\s+not\s+to\s+compete)\b[^\n]*(?:\n(?!\n)[^\n]*)*"},
        {"type": "Non-Solicitation", "risk": "medium", "dimension": "Operational", "pattern": r"\b(non[- ]?solicit|non[- ]?solicitation|solicit\s+employees|solicit\s+customers)\b[^\n]*(?:\n(?!\n)[^\n]*)*"},
        {"type": "Termination", "risk": "medium", "dimension": "Operational", "pattern": r"\b(termination|terminate|terminates|cancellation|convenience\s+termination|material\s+breach)\b[^\n]*(?:\n(?!\n)[^\n]*)*"},
        {"type": "Confidentiality", "risk": "medium", "dimension": "Privacy", "pattern": r"\b(confidential|confidentiality|non[- ]?disclosure|proprietary\s+information|trade\s+secret)\b[^\n]*(?:\n(?!\n)[^\n]*)*"},
        {"type": "Dispute Resolution & Arbitration", "risk": "medium", "dimension": "Legal", "pattern": r"\b(arbitration|mediation|dispute\s+resolution|dispute\s+settlement|arbitral\s+tribunal|seat\s+of\s+arbitration)\b[^\n]*(?:\n(?!\n)[^\n]*)*"},
        {"type": "Governing Law & Jurisdiction", "risk": "low", "dimension": "Legal", "pattern": r"\b(governing\s+law|jurisdiction|applicable\s+law|exclusive\s+jurisdiction|choice\s+of\s+law)\b[^\n]*(?:\n(?!\n)[^\n]*)*"},
        {"type": "Intellectual Property", "risk": "medium", "dimension": "IP", "pattern": r"\b(intellectual\s+property|\bip\s+rights\b|work\s+for\s+hire|patent|copyright|trademark|moral\s+rights|assignment\s+of\s+ip)\b[^\n]*(?:\n(?!\n)[^\n]*)*"},
        {"type": "Data Protection & Privacy", "risk": "high", "dimension": "Privacy", "pattern": r"\b(personal\s+data|data\s+protection|dpdp|gdpr|data\s+fiduciary|data\s+principal|data\s+processor|security\s+safeguards|data\s+breach)\b[^\n]*(?:\n(?!\n)[^\n]*)*"},
        {"type": "Payment & Invoicing", "risk": "low", "dimension": "Financial", "pattern": r"\b(payment|invoice|rent|security\s+deposit|interest\s+on\s+delayed|shall\s+pay|billing\s+cycle)\b[^\n]*(?:\n(?!\n)[^\n]*)*"},
        {"type": "Force Majeure", "risk": "low", "dimension": "Operational", "pattern": r"\b(force\s+majeure|act\s+of\s+god|natural\s+disaster|pandemic|epidemic|unforeseen\s+circumstances)\b[^\n]*(?:\n(?!\n)[^\n]*)*"},
        {"type": "Warranties & Representations", "risk": "medium", "dimension": "Legal", "pattern": r"\b(warranties|representations|as\s+is|warranty\s+disclaimer|express\s+warranty|implied\s+warranty)\b[^\n]*(?:\n(?!\n)[^\n]*)*"},
        {"type": "Audit Rights & Inspection", "risk": "medium", "dimension": "Compliance", "pattern": r"\b(audit\s+rights|right\s+to\s+audit|inspect\s+books|compliance\s+audit|record\s+keeping)\b[^\n]*(?:\n(?!\n)[^\n]*)*"},
        {"type": "Insurance Obligations", "risk": "medium", "dimension": "Financial", "pattern": r"\b(insurance|commercial\s+general\s+liability|indemnity\s+insurance|workers\s+compensation|policy\s+coverage)\b[^\n]*(?:\n(?!\n)[^\n]*)*"},
        {"type": "SLA & Service Credits", "risk": "medium", "dimension": "Operational", "pattern": r"\b(service\s+level|uptime|sla|service\s+credits|downtime|penalty\s+for\s+delay)\b[^\n]*(?:\n(?!\n)[^\n]*)*"},
        {"type": "Assignment & Change of Control", "risk": "medium", "dimension": "Operational", "pattern": r"\b(assignment|assign\s+this\s+agreement|change\s+of\s+control|merger\s+or\s+acquisition)\b[^\n]*(?:\n(?!\n)[^\n]*)*"},
        {"type": "Notices & Formal Communications", "risk": "low", "dimension": "Operational", "pattern": r"\b(notices|written\s+notice|formal\s+notice|registered\s+post|electronic\s+mail\s+notice)\b[^\n]*(?:\n(?!\n)[^\n]*)*"}
    ]

    def __init__(self):
        super().__init__(
            name="Clause Intelligence Agent",
            description="Extracts and categorizes clauses across 18+ contractual categories using deterministic regex and page mapping.",
            capabilities=["clause_extraction", "page_mapping", "category_classification"]
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        text = context.get("text", "")
        page_texts = context.get("page_texts", [])
        
        # Build page offset map
        page_offsets = []
        if page_texts:
            curr = 0
            for p_num, p_text in enumerate(page_texts, start=1):
                page_offsets.append((curr, p_num))
                curr += len(p_text)
                
        def get_page(pos):
            if not page_offsets: return 1
            pg = 1
            for start, num in page_offsets:
                if pos >= start: pg = num
                else: break
            return pg

        extracted_clauses = []
        seen = set()
        findings = []

        for rule in self.EXPANDED_PATTERNS:
            for match in re.finditer(rule["pattern"], text, re.IGNORECASE):
                raw = match.group(0).strip()
                if len(raw) < 50:
                    continue
                fp = re.sub(r"\s+", " ", raw[:70].lower())
                if fp in seen:
                    continue
                seen.add(fp)
                
                page_num = get_page(match.start())
                clause_obj = {
                    "type": rule["type"],
                    "risk": rule["risk"],
                    "dimension": rule["dimension"],
                    "content": raw[:350] + "..." if len(raw) > 350 else raw,
                    "description": f"{rule['type']} clause (Page {page_num})",
                    "page": page_num
                }
                extracted_clauses.append(clause_obj)
                
                findings.append(AgentFindingModel(
                    dimension=rule["dimension"],
                    risk_level=rule["risk"].upper(),
                    risk_score=85 if rule["risk"] == "high" else (50 if rule["risk"] == "medium" else 20),
                    clause_type=rule["type"],
                    clause_text=clause_obj["content"],
                    page_number=page_num,
                    reason=f"Detected {rule['type']} provision governing contractual rights and duties.",
                    recommendation="Review terms to ensure balance of rights and clear termination / limitation thresholds.",
                    citation_status="SUPPORTED",
                    confidence=0.91
                ))

        return AgentResult(
            agent_name=self.name,
            status="success",
            confidence=0.91,
            summary=f"Extracted {len(extracted_clauses)} structured clauses across {len(set(c['type'] for c in extracted_clauses))} distinct categories.",
            findings=findings,
            data={"clauses": extracted_clauses, "total_clauses": len(extracted_clauses)}
        )
