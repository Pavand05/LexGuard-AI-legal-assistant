"""
Compliance Intelligence Agent (LexGuard-MA)
Verifies contract compliance against applicable statutory frameworks based on DocumentLegalContext:
- India: DPDP Act 2023, Section 27 & 28 Indian Contract Act 1872, Registration Act 1908, Transfer of Property Act 1882
- US / California: California B&P Code § 16600 (Non-compete prohibition), US State Privacy Safeguards
- Foreign / Other: Jurisdictional notice without false statutory cross-contamination
"""
import re
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult, AgentFindingModel
from agent_tools.legal_sources import STATUTORY_KNOWLEDGE_BASE
from .legal_context import DocumentLegalContext


class ComplianceIntelligenceAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Compliance Agent",
            description="Audits statutory compliance under jurisdiction-grounded regulatory frameworks without cross-jurisdiction false citations.",
            capabilities=["dpdp_compliance", "property_statutory_checks", "restraint_checks", "preliminary_compliance_audit", "jurisdiction_grounded_compliance"]
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        text = context.get("text", "")
        doc_type = context.get("document_type", "Commercial Contract")
        lower = text.lower()
        findings: List[AgentFindingModel] = []
        
        legal_context: DocumentLegalContext = context.get("legal_context")
        if not legal_context:
            from .legal_context import resolve_document_legal_context
            legal_context = resolve_document_legal_context(text)

        is_indian = legal_context.is_indian_jurisdiction()
        is_us = legal_context.is_us_jurisdiction()
        is_california = is_us and "california" in (legal_context.state_or_region or "").lower()
        gov_law = legal_context.governing_law

        # 1. Personal Data Protection & Breach Notification Audit
        has_dpdp = any(k in lower for k in ["personal data", "data protection", "dpdp", "data fiduciary", "security safeguards"])
        has_breach_notice = any(k in lower for k in ["breach notification", "notify within", "security breach", "data breach"])
        has_data_erasure = any(k in lower for k in ["erasure", "deletion of data", "return or destroy", "data retention"])
        
        if is_indian:
            dpdp_sec8 = next((s for s in STATUTORY_KNOWLEDGE_BASE if s["id"] == "DPDP-SEC-8"), None)
            if has_dpdp and not has_breach_notice:
                findings.append(AgentFindingModel(
                    id="comp-dpdp-01",
                    agent="Compliance Agent",
                    dimension="Compliance",
                    category="Data Protection",
                    severity="HIGH",
                    risk_score=75,
                    clause_type="DPDP Breach Notification Gap",
                    clause_text="Data processing terms present without mandatory security breach notification timeline.",
                    page_number=1,
                    evidence="Document governs personal data handling but omits statutory breach escalation procedure.",
                    claim="Section 8 of DPDP Act 2023 mandates reasonable security safeguards and timely notification of personal data breaches to the Data Protection Board.",
                    reason="Lack of formal breach notification procedure violates statutory standards under Section 8 of the Digital Personal Data Protection Act 2023.",
                    recommendation="Insert explicit breach notification obligation requiring notification to the Data Fiduciary within 72 hours of discovery.",
                    source_type="LEGAL_SOURCE",
                    verification_status="SUPPORTED",
                    confidence=0.91,
                    sources=[dpdp_sec8] if dpdp_sec8 else []
                ))
                
            if has_dpdp and not has_data_erasure:
                findings.append(AgentFindingModel(
                    id="comp-dpdp-02",
                    agent="Compliance Agent",
                    dimension="Compliance",
                    category="Data Protection",
                    severity="MEDIUM",
                    risk_score=50,
                    clause_type="Data Retention & Erasure",
                    clause_text="Contract lacks explicit post-termination data return or destruction obligations.",
                    page_number=1,
                    evidence="Document contains ongoing personal data processing without explicit data lifecycle / erasure mandate.",
                    claim="DPDP Act 2023 requires erasure of personal data once the specified purpose is fulfilled.",
                    reason="Statutory principle of storage limitation requires unambiguous data disposal mechanisms.",
                    recommendation="Include clear post-termination data deletion, return, or certificate of destruction terms.",
                    source_type="LEGAL_SOURCE",
                    verification_status="SUPPORTED",
                    confidence=0.88,
                    sources=[dpdp_sec8] if dpdp_sec8 else []
                ))

        # 2. Restraint of Trade & Non-Compete Compliance
        has_non_compete = any(k in lower for k in ["non-compete", "restraint of trade", "not engage in any competing", "not work for any competitor", "covenant not to compete"])
        if has_non_compete:
            if is_indian:
                ica_sec27 = next((s for s in STATUTORY_KNOWLEDGE_BASE if s["id"] == "ICA-SEC-27"), None)
                findings.append(AgentFindingModel(
                    id="comp-ica-27",
                    agent="Compliance Agent",
                    dimension="Legal",
                    category="Restraint of Trade",
                    severity="HIGH",
                    risk_score=85,
                    clause_type="Non-Compete Restraint of Trade",
                    clause_text="Post-termination non-compete restriction detected.",
                    page_number=1,
                    evidence="Clause restricts counterparty/employee from engaging in lawful trade, business, or profession.",
                    claim="Under Section 27 of the Indian Contract Act 1872, every agreement in restraint of trade is void ab initio to that extent.",
                    reason="Indian courts consistently refuse to enforce post-employment non-compete covenants (Percept D'Mark v. Zaheer Khan).",
                    recommendation="Replace void post-termination non-compete with enforceable client non-solicitation and strict non-disclosure protections.",
                    source_type="LEGAL_SOURCE",
                    verification_status="SUPPORTED",
                    confidence=0.95,
                    sources=[ica_sec27] if ica_sec27 else []
                ))
            elif is_california:
                findings.append(AgentFindingModel(
                    id="comp-cal-16600",
                    agent="Compliance Agent",
                    dimension="Legal",
                    category="Restraint of Trade",
                    severity="HIGH",
                    risk_score=85,
                    clause_type="California Statutory Non-Compete Prohibition",
                    clause_text="Post-employment non-compete restriction under California governing law.",
                    page_number=1,
                    evidence=f"Governing Law is {gov_law}. Post-employment restrictive covenant identified.",
                    claim="Under California Business and Professions Code § 16600, every contract by which anyone is restrained from engaging in a lawful profession, trade, or business of any kind is to that extent void.",
                    reason="California maintains a strict statutory public policy prohibiting post-employment non-compete restrictions, extending even to out-of-state employers employing California workers.",
                    recommendation="Remove post-termination non-compete covenant; rely on protection of trade secrets and reasonable client non-solicitation.",
                    source_type="LEGAL_SOURCE",
                    verification_status="SUPPORTED",
                    confidence=0.95,
                    sources=[]
                ))
            elif is_us:
                findings.append(AgentFindingModel(
                    id="comp-us-restraint",
                    agent="Compliance Agent",
                    dimension="Legal",
                    category="Restraint of Trade",
                    severity="MEDIUM",
                    risk_score=60,
                    clause_type="Restrictive Covenant Reasonableness Review",
                    clause_text=f"Post-employment restrictive covenant under {gov_law}.",
                    page_number=1,
                    evidence=f"Restraint of trade covenant under {gov_law}.",
                    claim=f"Restrictive covenants are evaluated under {gov_law} for reasonable geographic and temporal scope.",
                    reason=f"Under {gov_law}, covenants not to compete must protect legitimate business interests and be strictly limited in time and geography.",
                    recommendation="Ensure duration does not exceed 12 months and geographic scope is tightly defined.",
                    source_type="AI_INFERENCE",
                    verification_status="TEXT_SUPPORTED",
                    confidence=0.90,
                    sources=[]
                ))

        # 3. Immovable Property Conveyance & Compulsory Registration (Indian Jurisdiction Only)
        if is_indian and doc_type in ["LAND_SALE_DEED", "LAND_LEASE", "GIFT_DEED", "MORTGAGE_DEED"]:
            has_registration_clause = any(k in lower for k in ["registration", "sub-registrar", "registered under", "stamp act"])
            reg_sec17 = next((s for s in STATUTORY_KNOWLEDGE_BASE if s["id"] == "REG-SEC-17"), None)
            
            if not has_registration_clause or "unregistered" in lower:
                findings.append(AgentFindingModel(
                    id="comp-reg-17",
                    agent="Compliance Agent",
                    dimension="Compliance",
                    category="Compulsory Registration",
                    severity="HIGH",
                    risk_score=90,
                    clause_type="Registration Mandate",
                    clause_text="Immovable property conveyance instrument requires mandatory registration.",
                    page_number=1,
                    evidence=f"Document Type: {doc_type}. Value involves immovable property rights.",
                    claim="Section 17(1)(b) of the Registration Act 1908 mandates compulsory registration for non-testamentary instruments creating right, title, or interest in immovable property valued at ₹100 or more.",
                    reason="Failure to register renders the document inadmissible in evidence under Section 49 and incapable of conferring title.",
                    recommendation="Execute instrument on requisite non-judicial stamp paper and register before the jurisdictional Sub-Registrar within 4 months.",
                    source_type="LEGAL_SOURCE",
                    verification_status="SUPPORTED",
                    confidence=0.97,
                    sources=[reg_sec17] if reg_sec17 else []
                ))

        if not findings:
            findings.append(AgentFindingModel(
                id="comp-clean-01",
                agent="Compliance Agent",
                dimension="Compliance",
                category="Statutory Compliance",
                severity="INFORMATIONAL",
                risk_score=10,
                clause_type="Compliance Hygiene",
                clause_text=f"No overt statutory non-compliance or void covenants detected under {gov_law}.",
                page_number=1,
                evidence=f"Cross-statutory review under {gov_law}.",
                claim="Instrument adheres to standard statutory contracting parameters.",
                reason="Document does not contain facially void covenants or statutory registration omissions for its category.",
                recommendation="Proceed with standard execution and enforceability review.",
                source_type="AI_INFERENCE",
                verification_status="TEXT_SUPPORTED",
                confidence=0.92,
                sources=[]
            ))

        return AgentResult(
            agent_name=self.name,
            status="success",
            confidence=0.93,
            summary=f"Compliance audit complete ({gov_law}): {len(findings)} statutory finding(s) evaluated.",
            findings=findings,
            data={
                "governing_law": gov_law,
                "country": legal_context.country,
                "findings_count": len(findings)
            }
        )
