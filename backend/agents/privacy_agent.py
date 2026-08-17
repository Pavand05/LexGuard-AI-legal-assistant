"""
Privacy & PII Detection Agent (LexGuard-MA)
Performs PII detection (emails, phones, PAN, Aadhaar, SSN, bank accounts)
and applies jurisdiction-grounded privacy framework analysis.
Never hardcodes Indian DPDP Act onto foreign (US / UK / EU) documents.
"""
import re
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult, AgentFindingModel
from agent_tools.document_tools import detect_and_redact_pii


class PrivacyIntelligenceAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Privacy & PII Agent",
            description="Audits document for personally identifiable information (PII) and evaluates jurisdiction-appropriate data protection safeguards.",
            capabilities=["pii_detection", "privacy_mode", "data_masking", "jurisdiction_grounded_privacy"]
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        text = context.get("text", "")
        privacy_mode = context.get("privacy_mode", False)
        applicable_law = context.get("applicable_law", "")
        court_jur = context.get("jurisdiction", "")
        
        # 1. Resolve Privacy Jurisdiction
        combined_jur = f"{applicable_law} {court_jur} {text[:1500]}".lower()
        if any(k in combined_jur for k in ["delaware", "california", "new york", "united states", "u.s.a.", "laws of the state of"]):
            privacy_framework = "US State Privacy & Commercial Data Safeguards"
            statutory_note = "Under standard U.S. commercial privacy and data security practices, unencrypted personal identifiers and financial account details should be protected against unauthorized disclosure."
        elif any(k in combined_jur for k in ["england and wales", "laws of england", "uk", "european union", "gdpr"]):
            privacy_framework = "GDPR / UK Data Protection Act 2018"
            statutory_note = "Under the General Data Protection Regulation (GDPR) and UK Data Protection Act 2018, personal identifiers require technical and organizational security measures."
        elif any(k in combined_jur for k in ["india", "bharat", "bengaluru", "delhi", "mumbai", "chennai", "kolkata"]):
            privacy_framework = "DPDP Act 2023 / Section 43A IT Act"
            statutory_note = "Under the Digital Personal Data Protection (DPDP) Act 2023 and Section 43A of IT Act 2000, sensitive personal and financial identifiers require reasonable security safeguards."
        else:
            privacy_framework = "General Commercial Data Confidentiality"
            statutory_note = "Personal identifiers detected; specific statutory privacy-law framework not established for this jurisdiction."

        # 2. Perform PII Detection
        pii_res = detect_and_redact_pii(text, apply_redaction=privacy_mode)
        findings: List[AgentFindingModel] = []

        if pii_res["has_pii"]:
            for det in pii_res["detections"]:
                det_type = det["type"]
                is_high = det_type in ["Indian Aadhaar Number", "Social Security Number (SSN)", "Bank Account Number"]
                
                findings.append(AgentFindingModel(
                    id=f"pii-{len(findings)+1}",
                    agent="Privacy & PII Agent",
                    dimension="Privacy",
                    category="Personal Data Protection",
                    severity="HIGH" if is_high else "MEDIUM",
                    risk_score=75 if is_high else 45,
                    clause_type=f"PII: {det_type}",
                    clause_text=f"Detected {det['count']} instance(s) of {det_type} (e.g., {', '.join(det['samples'])}).",
                    page_number=1,
                    evidence=f"Matched {det['count']} pattern(s) in document text.",
                    claim=f"Exposed personal identifier under {privacy_framework}.",
                    reason=statutory_note,
                    recommendation="Enable Privacy Mode before transmitting external summaries, or redact personal identifiers from public records.",
                    source_type="DOCUMENT_TEXT",
                    verification_status="TEXT_SUPPORTED",
                    confidence=0.95
                ))
        else:
            findings.append(AgentFindingModel(
                id="pii-clean-01",
                agent="Privacy & PII Agent",
                dimension="Privacy",
                category="PII Audit",
                severity="INFORMATIONAL",
                risk_score=10,
                clause_type="PII Hygiene Audit",
                clause_text=f"No exposed government identity tokens, SSN, PAN, Aadhaar, or bank credentials detected. (Framework: {privacy_framework})",
                page_number=1,
                evidence="Full regex scan for sensitive identity tokens and credentials.",
                claim="Document is clear of unmasked sensitive credentials.",
                reason="No high-risk personal identification numbers detected in document body.",
                recommendation="Maintain standard data confidentiality handling.",
                source_type="DOCUMENT_TEXT",
                verification_status="TEXT_SUPPORTED",
                confidence=0.92
            ))

        return AgentResult(
            agent_name=self.name,
            status="success",
            confidence=0.94,
            summary=f"Privacy scan complete ({privacy_framework}): {pii_res['total_sensitive_items']} sensitive item(s) detected. Privacy Mode: {'ACTIVE' if privacy_mode else 'DISABLED'}.",
            findings=findings,
            data={
                "has_pii": pii_res["has_pii"],
                "total_sensitive_items": pii_res["total_sensitive_items"],
                "detections": pii_res["detections"],
                "privacy_framework": privacy_framework,
                "privacy_mode": privacy_mode,
                "redacted_text": pii_res["redacted_text"] if privacy_mode else None
            }
        )
