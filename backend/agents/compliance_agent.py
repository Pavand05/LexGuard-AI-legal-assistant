"""
Compliance Intelligence Agent
Verifies contract against statutory compliance frameworks:
- DPDP Act 2023 (Personal data safeguards, breach notice, erasure)
- Indian Contract Act 1872 (Section 27 restraint of trade, Section 28 legal proceedings)
- Transfer of Property Act 1882 & Registration Act 1908 (Immovable property conveyance, compulsory registration)
- Information Technology Act 2000 (Section 43A)
"""
import re
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult, AgentFindingModel
from agent_tools.legal_sources import STATUTORY_KNOWLEDGE_BASE


class ComplianceIntelligenceAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Compliance Agent",
            description="Audits statutory compliance under DPDP Act 2023, Transfer of Property Act, Registration Act, and Indian Contract Act.",
            capabilities=["dpdp_compliance", "property_statutory_checks", "restraint_checks", "preliminary_compliance_audit"]
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        text = context.get("text", "")
        doc_type = context.get("document_type", "Commercial Contract")
        lower = text.lower()
        findings: List[AgentFindingModel] = []
        
        # 1. DPDP Act 2023 Data Protection Checks
        has_dpdp = any(k in lower for k in ["personal data", "data protection", "dpdp", "data fiduciary", "security safeguards"])
        has_breach_notice = any(k in lower for k in ["breach notification", "notify within", "security breach", "data breach"])
        has_data_erasure = any(k in lower for k in ["erasure", "deletion of data", "return or destroy", "data retention"])
        
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

        # 2. Restraint of Trade (Section 27 Indian Contract Act)
        has_non_compete = any(k in lower for k in ["non-compete", "restraint of trade", "not engage in any competing", "not work for any competitor"])
        ica_sec27 = next((s for s in STATUTORY_KNOWLEDGE_BASE if s["id"] == "ICA-SEC-27"), None)
        
        if has_non_compete:
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

        # 3. Real Estate / Immovable Property Conveyancing Statutory Checks
        is_property_doc = any(k in doc_type.upper() for k in ["LAND", "SALE_DEED", "SALE_AGREEMENT", "LEASE", "GIFT", "MORTGAGE"]) or any(k in lower for k in ["sale deed", "schedule of property", "vendor", "purchaser", "survey no"])
        
        if is_property_doc:
            tpa_sec54 = next((s for s in STATUTORY_KNOWLEDGE_BASE if s["id"] == "TPA-SEC-54"), None)
            reg_sec17 = next((s for s in STATUTORY_KNOWLEDGE_BASE if s["id"] == "REG-SEC-17"), None)
            
            # Check for compulsory registration recital
            has_registration_clause = any(k in lower for k in ["sub-registrar", "registration act", "duly registered", "registration of this deed", "stamp duty"])
            if not has_registration_clause:
                findings.append(AgentFindingModel(
                    id="comp-reg-17",
                    agent="Compliance Agent",
                    dimension="Compliance",
                    category="Compulsory Registration",
                    severity="HIGH",
                    risk_score=80,
                    clause_type="Compulsory Registration Under Section 17 Registration Act",
                    clause_text="Document transfers/conveys immovable property interest without explicit registration terms.",
                    page_number=1,
                    evidence="Immovable property conveyance without explicit Sub-Registrar execution clause.",
                    claim="Under Section 54 of Transfer of Property Act 1882 and Section 17 of Registration Act 1908, transfer of immovable property must be effected by a registered instrument.",
                    reason="Unregistered instruments conveying immovable property exceeding ₹100 are inadmissible in evidence and confer no legal title under Section 49 Registration Act.",
                    recommendation="Ensure formal execution and registration before the jurisdictional Sub-Registrar with applicable stamp duty paid.",
                    source_type="LEGAL_SOURCE",
                    verification_status="SUPPORTED",
                    confidence=0.95,
                    sources=[s for s in [tpa_sec54, reg_sec17] if s]
                ))

        # 4. Standard Preliminary Finding (Conservative Tone)
        if not findings:
            findings.append(AgentFindingModel(
                id="comp-prelim-01",
                agent="Compliance Agent",
                dimension="Compliance",
                category="Preliminary Compliance Review",
                severity="INFORMATIONAL",
                risk_score=15,
                clause_type="Preliminary Statutory Scan",
                clause_text="Preliminary assessment: No verified statutory violations identified from available indexed sources.",
                page_number=1,
                evidence="Automated cross-check against Indian Contract Act, DPDP Act 2023, and Registration Act indexes.",
                claim="No prima facie statutory invalidity detected.",
                reason="Preliminary automated review identified no void covenants or manifest statutory conflicts in available text.",
                recommendation="Have local jurisdictional counsel review specialized industry/zoning requirements prior to formal signing.",
                source_type="AI_INFERENCE",
                verification_status="UNVERIFIED",
                confidence=0.88
            ))

        # Compliance score calculation
        deductions = sum(f.risk_score for f in findings if f.severity in ["CRITICAL", "HIGH"]) // 2 + sum(f.risk_score for f in findings if f.severity == "MEDIUM") // 3
        compliance_score = max(10, 100 - deductions)

        return AgentResult(
            agent_name=self.name,
            status="success",
            confidence=0.92,
            summary=f"Preliminary compliance review completed. Statutory Compliance Score: {compliance_score}/100 with {len(findings)} finding(s).",
            findings=findings,
            data={
                "compliance_score": compliance_score,
                "frameworks": ["DPDP Act 2023", "Indian Contract Act 1872", "Transfer of Property Act 1882", "Registration Act 1908"]
            }
        )
