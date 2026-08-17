"""
Privacy & PII Detection Agent
Detects sensitive personal data (Aadhaar, PAN, emails, phone numbers, bank accounts)
and supports zero-leakage Privacy Mode redaction.
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult, AgentFindingModel
from agent_tools.document_tools import detect_and_redact_pii


class PrivacyIntelligenceAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Privacy & PII Agent",
            description="Audits document for personally identifiable information (PII), PAN, Aadhaar, bank credentials, and provides privacy protections.",
            capabilities=["pii_detection", "privacy_mode", "data_masking"]
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        text = context.get("text", "")
        privacy_mode = context.get("privacy_mode", False)
        
        pii_res = detect_and_redact_pii(text, apply_redaction=privacy_mode)
        findings = []

        if pii_res["has_pii"]:
            for det in pii_res["detections"]:
                findings.append(AgentFindingModel(
                    dimension="Privacy",
                    risk_level="HIGH" if det["type"] in ["Indian Aadhaar Number", "Bank Account Number"] else "MEDIUM",
                    risk_score=75 if det["type"] in ["Indian Aadhaar Number", "Bank Account Number"] else 45,
                    clause_type=f"PII: {det['type']}",
                    clause_text=f"Detected {det['count']} instance(s) of {det['type']} (e.g., {', '.join(det['samples'])}).",
                    page_number=1,
                    reason="Under Indian DPDP Act 2023 and Section 43A of IT Act 2000, sensitive financial and personal identifiers require reasonable security safeguards.",
                    recommendation="Enable Privacy Mode before transmitting external summaries, or redact personal identifiers from public records.",
                    citation_status="SUPPORTED",
                    confidence=0.95
                ))
        else:
            findings.append(AgentFindingModel(
                dimension="Privacy",
                risk_level="LOW",
                risk_score=10,
                clause_type="PII Audit",
                clause_text="No exposed Aadhaar, PAN, bank accounts, or sensitive identity tokens detected.",
                page_number=1,
                reason="Document is clear of unmasked sensitive personal financial credentials.",
                recommendation="Maintain standard data confidentiality handling.",
                citation_status="SUPPORTED",
                confidence=0.92
            ))

        return AgentResult(
            agent_name=self.name,
            status="success",
            confidence=0.95,
            summary=f"Privacy scan complete: {pii_res['total_sensitive_items']} sensitive identifier(s) detected across {len(pii_res['detections'])} category(ies). Privacy Mode: {'ACTIVE' if privacy_mode else 'DISABLED'}.",
            findings=findings,
            data={
                "has_pii": pii_res["has_pii"],
                "total_sensitive_items": pii_res["total_sensitive_items"],
                "detections": pii_res["detections"],
                "privacy_mode": privacy_mode,
                "redacted_text": pii_res["redacted_text"] if privacy_mode else None
            }
        )
