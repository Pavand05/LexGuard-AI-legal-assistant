"""
Privacy & PII Detection Agent (LexGuard-MA)
Performs PII detection and distinguishes:
1. PII_ACTUALLY_EXPOSED: Actual exposed identity numbers, emails, phone numbers, account digits.
2. PII_REFERENCE: Merely textual references to personal data categories (e.g. "bank account details for direct deposit").
Applies jurisdiction-grounded privacy framework analysis. Never hardcodes Indian DPDP Act on foreign documents.
"""
import re
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult, AgentFindingModel
from agent_tools.document_tools import detect_and_redact_pii
from .legal_context import DocumentLegalContext


class PrivacyIntelligenceAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Privacy & PII Agent",
            description="Audits document for personally identifiable information (PII), distinguishes exposed credentials from textual references, and evaluates jurisdiction-grounded safeguards.",
            capabilities=["pii_detection", "privacy_mode", "data_masking", "jurisdiction_grounded_privacy"]
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        text = context.get("text", "")
        privacy_mode = context.get("privacy_mode", False)
        legal_context: DocumentLegalContext = context.get("legal_context")
        if not legal_context:
            from .legal_context import resolve_document_legal_context
            legal_context = resolve_document_legal_context(text)

        is_us = legal_context.is_us_jurisdiction()
        is_indian = legal_context.is_indian_jurisdiction()
        gov_law = legal_context.governing_law

        # 1. Resolve Privacy Jurisdiction
        if is_us:
            privacy_framework = "US State Privacy & Commercial Data Safeguards"
            statutory_note = f"Under U.S. and {legal_context.state_or_region or 'State'} commercial data privacy standards, unencrypted personal credentials require reasonable technical safeguards."
        elif is_indian:
            privacy_framework = "DPDP Act 2023 / Section 43A IT Act"
            statutory_note = "Under the Digital Personal Data Protection (DPDP) Act 2023 and Section 43A of IT Act 2000, sensitive personal and financial identifiers require reasonable security safeguards."
        elif "uk" in (legal_context.country or "").lower() or "england" in gov_law.lower():
            privacy_framework = "GDPR / UK Data Protection Act 2018"
            statutory_note = "Under the GDPR and UK Data Protection Act 2018, personal identifiers require technical and organizational security measures."
        else:
            privacy_framework = "General Commercial Data Confidentiality"
            statutory_note = f"Personal identifiers detected; specific statutory privacy framework not established for {gov_law}."

        # 2. Perform PII Detection
        pii_res = detect_and_redact_pii(text, apply_redaction=privacy_mode)
        findings: List[AgentFindingModel] = []
        exposed_items = []
        reference_items = []

        if pii_res["has_pii"]:
            for det in pii_res["detections"]:
                det_type = det["type"]
                samples = det.get("samples", [])
                
                # Distinguish actually exposed values from mere textual references
                is_actual_exposed = False
                for s in samples:
                    # If sample contains actual digits or @ domain, it is actually exposed
                    if "@" in s or re.search(r"\d{3,}", s):
                        is_actual_exposed = True
                        break
                        
                if is_actual_exposed:
                    exposed_items.append(det)
                    is_high = det_type in ["Indian Aadhaar Number", "Social Security Number (SSN)", "Bank Account Number"]
                    findings.append(AgentFindingModel(
                        id=f"pii-exposed-{len(findings)+1}",
                        agent="Privacy & PII Agent",
                        dimension="Privacy",
                        category="Personal Data Protection",
                        severity="HIGH" if is_high else "MEDIUM",
                        risk_score=75 if is_high else 45,
                        clause_type=f"PII Actually Exposed: {det_type}",
                        clause_text=f"Detected {det['count']} instance(s) of {det_type} (e.g., {', '.join(det['samples'])}).",
                        page_number=1,
                        evidence=f"Exposed token matches: {', '.join(det['samples'])} ({privacy_framework})",
                        claim="Exposed personal credential identified in document text.",
                        reason=statutory_note,
                        recommendation="Enable Privacy Mode before transmitting external summaries, or redact personal identifiers from public records.",
                        source_type="DOCUMENT_TEXT",
                        verification_status="TEXT_SUPPORTED",
                        confidence=0.95
                    ))
                else:
                    reference_items.append(det)
                    findings.append(AgentFindingModel(
                        id=f"pii-ref-{len(findings)+1}",
                        agent="Privacy & PII Agent",
                        dimension="Privacy",
                        category="PII Reference",
                        severity="INFORMATIONAL",
                        risk_score=15,
                        clause_type=f"PII Text Reference: {det_type}",
                        clause_text=f"Document references data category '{det_type}' without exposing actual live credentials.",
                        page_number=1,
                        evidence=f"Textual mention of data category: {det_type}",
                        claim="Textual reference to personal data categories.",
                        reason="Document mentions data category in covenants without leaking actual live personal identification numbers.",
                        recommendation="Ensure data transmission adheres to agreed confidentiality procedures.",
                        source_type="DOCUMENT_TEXT",
                        verification_status="TEXT_SUPPORTED",
                        confidence=0.90
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
            summary=f"Privacy scan complete ({privacy_framework}): {len(exposed_items)} exposed credential(s), {len(reference_items)} textual reference(s). Privacy Mode: {'ACTIVE' if privacy_mode else 'DISABLED'}.",
            findings=findings,
            data={
                "has_pii": len(exposed_items) > 0,
                "total_sensitive_items": pii_res["total_sensitive_items"],
                "exposed_items": exposed_items,
                "reference_items": reference_items,
                "privacy_framework": privacy_framework,
                "privacy_mode": privacy_mode,
                "redacted_text": pii_res["redacted_text"] if privacy_mode else None
            }
        )
