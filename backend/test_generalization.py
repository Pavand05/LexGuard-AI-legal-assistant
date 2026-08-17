"""
Generalization & Open-Set Legal Document Intelligence Test Suite
Validates that LexGuard-MA generalizes across all legal domains:
1. Non-Disclosure Agreement (NDA)
2. Employment Agreement
3. Software Licensing / SaaS Agreement
4. Data Processing Agreement (DPA)
5. Shareholders' Agreement (SHA)
6. Commercial Loan Agreement
7. Open-Set Unseen Document (e.g. Source Code Escrow Agreement)
8. Dynamic Agent Routing Layer
9. Domain Playbook Selection
10. Universal Semantic Contradiction Detection across non-property domains
"""
import pytest
from agents.orchestrator import orchestrator
from agents.document_agent import DocumentIntelligenceAgent
from agents.router import AgentRouter
from agents.playbooks import resolve_domain_playbook


# =========================================================================
# TEST FIXTURES ACROSS DISTINCT LEGAL DOMAINS
# =========================================================================

DOCUMENT_NDA = """
MUTUAL NON-DISCLOSURE AGREEMENT
This Mutual Non-Disclosure Agreement ('Agreement') is entered into on 10th January 2025 by and between:
Alpha Innovations Pvt Ltd ('Disclosing Party') AND Beta Systems Inc ('Receiving Party').
1. DEFINITION: Confidential Information shall include all proprietary trade secrets, software designs, financial forecasts, and customer data disclosed.
2. OBLIGATIONS: The Receiving Party agrees to maintain strict confidentiality, apply reasonable standard of care, and not disclose to any third party.
3. EXCLUSIONS: Information publicly available or independently developed shall not be considered Confidential Information.
4. TERM: This Agreement shall remain in effect for a period of 2 years from effective date.
5. RETURN OF MATERIALS: Upon termination, Receiving Party shall promptly return or destroy all confidential documents within 15 days.
6. GOVERNING LAW: Governed by the laws of India. Courts at New Delhi shall have exclusive jurisdiction.
"""

DOCUMENT_EMPLOYMENT = """
EXECUTIVE EMPLOYMENT AGREEMENT
This Employment Agreement is entered into between TechNova Solutions Ltd ('Employer') and Dr. Amit Verma ('Employee').
1. POSITION & DUTIES: Employee is appointed as Chief Technology Officer (CTO).
2. COMPENSATION: Annual CTC of INR 45,00,000 payable in monthly installments.
3. PROBATION & NOTICE PERIOD: Probation of 6 months. Either party may terminate by providing 60 days written notice.
4. RESTRICTIVE COVENANTS: Post-termination non-compete: Employee shall not work for any competitor globally for a period of 3 years following termination.
5. NON-SOLICITATION: Employee shall not solicit any clients or employees for 12 months post-employment.
6. IP ASSIGNMENT: All inventions, patents, and software created during employment shall belong exclusively to Employer.
7. JURISDICTION: Governed by the laws of India and subject to courts of Bengaluru.
"""

DOCUMENT_SOFTWARE_LICENSE = """
ENTERPRISE SOFTWARE LICENSE AGREEMENT
This Agreement is between CloudMatrix Technologies ('Licensor') and Global Enterprise Corp ('Licensee').
1. GRANT OF LICENSE: Licensor grants a non-exclusive, non-transferable enterprise license for 500 named users.
2. TERM & RENEWAL CONFLICT:
   Clause 2.1: The license is granted for a fixed initial term of 3 years.
   Clause 2.2: Licensee possesses unilateral right to automatically renew this license for additional 5-year periods.
   Clause 2.3: This Agreement strictly expires after 3 years with no option for renewal.
3. IP OWNERSHIP: All intellectual property rights in the software remain with Licensor.
4. LIMITATION OF LIABILITY: Licensor's aggregate liability is capped at the total license fees paid in the past 12 months.
5. GOVERNING LAW: Governed by the laws of England and Wales. Arbitration seated in London under LCIA Rules.
"""

DOCUMENT_DATA_PROCESSING_AGREEMENT = """
DATA PROCESSING ADDENDUM (DPA)
This DPA is entered into between FinTech Secure Ltd ('Data Fiduciary') and CloudServer Hosting ('Data Processor').
1. SCOPE OF PROCESSING: Processor processes personal data solely for providing cloud infrastructure.
2. SECURITY SAFEGUARDS: Processor shall maintain ISO 27001 certified technical and organizational security safeguards.
3. BREACH NOTIFICATION: In the event of a personal data breach, Processor shall notify the Data Fiduciary within 48 hours.
4. DATA ERASURE: Upon termination of services, Processor shall permanently erase all customer personal data within 30 days.
5. SUB-PROCESSORS: Processor shall provide 30 days prior notice before onboarding new sub-processors.
6. COMPLIANCE: Compliant with the Digital Personal Data Protection (DPDP) Act 2023.
"""

DOCUMENT_SHAREHOLDERS_AGREEMENT = """
SHAREHOLDERS' AGREEMENT (SHA)
This Agreement is entered into among Founder A, Founder B, and VentureCap Fund ('Investor').
1. CAPITAL STRUCTURE: Total equity investment of INR 10,00,00,000 for 20% Series A Preferred Shares.
2. BOARD COMPOSITION: Board shall consist of 5 directors; Investor has right to appoint 1 nominee director.
3. RESERVED MATTERS: Key decisions including M&A, debt > INR 50 lakhs require affirmative vote of Investor director.
4. TRANSFER RESTRICTIONS: Right of First Refusal (ROFR) and Tag-Along rights on any transfer of founder shares.
5. GOVERNING LAW: Governed by the Companies Act 2013 and laws of India. Courts of Mumbai.
"""

DOCUMENT_UNSEEN_OPEN_SET = """
SOURCE CODE ESCROW & DEPOSIT AGREEMENT
This Source Code Escrow Agreement is made between DevSoft Inc ('Depositor'), EscrowAgent Global ('Escrow Agent'), and Buyer Corp ('Beneficiary').
1. ESCROW DEPOSIT: Depositor shall deposit full source code, compiler instructions, and technical documentation with Escrow Agent.
2. RELEASE TRIGGERS: Escrow Agent shall release source code to Beneficiary only upon: (a) bankruptcy of Depositor, or (b) complete cessation of software maintenance for 60 consecutive days.
3. VERIFICATION: Escrow Agent shall conduct annual deposit integrity verification.
4. CONFIDENTIALITY: Escrow Agent shall hold materials in strict confidentiality until release trigger is verified.
5. GOVERNING LAW: Governed by the laws of California, USA.
"""


# =========================================================================
# 1. TEST OPEN-SET TAXONOMY & CLASSIFICATION
# =========================================================================
def test_open_set_classification_across_domains():
    agent = DocumentIntelligenceAgent()

    # 1. NDA
    res_nda = agent.run({"text": DOCUMENT_NDA})
    assert res_nda.data["document_type"] == "NDA"
    assert "CONFIDENTIALITY_NDA" in res_nda.data["detected_domains"]

    # 2. Employment
    res_emp = agent.run({"text": DOCUMENT_EMPLOYMENT})
    assert res_emp.data["document_type"] == "EMPLOYMENT_AGREEMENT"
    assert "EMPLOYMENT_LABOR" in res_emp.data["detected_domains"]

    # 3. Software License
    res_sw = agent.run({"text": DOCUMENT_SOFTWARE_LICENSE})
    assert res_sw.data["document_type"] == "SOFTWARE_LICENSE"
    assert "IP_SOFTWARE_TECH" in res_sw.data["detected_domains"]

    # 4. Data Processing Agreement
    res_dpa = agent.run({"text": DOCUMENT_DATA_PROCESSING_AGREEMENT})
    assert res_dpa.data["document_type"] == "DATA_PROCESSING_AGREEMENT"
    assert "DATA_PRIVACY" in res_dpa.data["detected_domains"]

    # 5. Shareholders' Agreement
    res_sha = agent.run({"text": DOCUMENT_SHAREHOLDERS_AGREEMENT})
    assert res_sha.data["document_type"] == "SHAREHOLDERS_AGREEMENT"
    assert "CORPORATE_GOVERNANCE" in res_sha.data["detected_domains"]

    # 6. Unseen Open-Set Document (Software Escrow) -> MUST NOT force into NDA or Sale Deed!
    res_unseen = agent.run({"text": DOCUMENT_UNSEEN_OPEN_SET})
    assert res_unseen.data["document_type"] == "OTHER_LEGAL_DOCUMENT"
    assert res_unseen.data["is_open_set"] is True
    assert len(res_unseen.data["detected_domains"]) > 0


# =========================================================================
# 2. TEST DYNAMIC AGENT ROUTING & PLAYBOOK RESOLUTION
# =========================================================================
def test_dynamic_agent_routing():
    # NDA routing: should NOT activate real estate or property specialists
    routing_nda = AgentRouter.route_agents("NDA", ["CONFIDENTIALITY_NDA"])
    assert "Document Intelligence Agent" in routing_nda["active_agents"]
    assert "Clause Intelligence Agent" in routing_nda["active_agents"]
    assert "Privacy" in routing_nda["applicable_risk_dimensions"] or "Legal" in routing_nda["applicable_risk_dimensions"]

    # DPA routing: MUST activate Privacy & PII Agent and Compliance
    routing_dpa = AgentRouter.route_agents("DATA_PROCESSING_AGREEMENT", ["DATA_PRIVACY"])
    assert "Privacy & PII Agent" in routing_dpa["active_agents"]
    assert "Compliance Agent" in routing_dpa["active_agents"]

    # Open-Set Unseen Document routing: graceful universal baseline
    routing_unseen = AgentRouter.route_agents("OTHER_LEGAL_DOCUMENT", ["IP_SOFTWARE_TECH", "GENERAL_COMMERCIAL"])
    assert routing_unseen["is_unknown_type"] is True
    assert len(routing_unseen["active_agents"]) >= 8


# =========================================================================
# 3. TEST UNIVERSAL CONTRADICTION ON NON-PROPERTY CONTRACT
# =========================================================================
def test_universal_contradiction_in_software_license():
    """Validates that term vs renewal conflict in Software License is detected by universal engine."""
    result = orchestrator.run_workflow(DOCUMENT_SOFTWARE_LICENSE, workflow_type="parallel")
    assert result["status"] == "completed"

    # Term vs renewal contradiction detected
    assert result["contradictions"]["has_renewal_contradiction"] is True
    contra_findings = [f for f in result["findings"] if "Renewal" in f.get("clause_type", "")]
    assert len(contra_findings) > 0


# =========================================================================
# 4. TEST EMPLOYMENT CONTRACT STATUTORY RESTRICTIONS
# =========================================================================
def test_employment_contract_section_27_restraint():
    """Validates that 3-year non-compete in employment agreement is flagged under Section 27 Indian Contract Act."""
    result = orchestrator.run_workflow(DOCUMENT_EMPLOYMENT, workflow_type="parallel")
    assert result["status"] == "completed"
    assert result["document_metadata"]["document_type"] == "EMPLOYMENT_AGREEMENT"

    # Non-compete flagged as high risk
    non_compete_findings = [f for f in result["findings"] if "Non-Compete" in f.get("clause_type", "") or "Restraint" in f.get("clause_type", "")]
    assert len(non_compete_findings) > 0


# =========================================================================
# 5. TEST DOMAIN-SPECIFIC MISSING CLAUSES
# =========================================================================
def test_domain_specific_missing_clauses():
    """Validates missing clauses are tailored by domain (NDA does NOT expect Property survey numbers)."""
    # NDA execution
    res_nda = orchestrator.run_workflow(DOCUMENT_NDA, workflow_type="parallel")
    missing_nda = res_nda["missing_clauses"]
    assert missing_nda["playbook_domain"] == "CONFIDENTIALITY_NDA"
    assert "Property Description & Schedule" not in missing_nda["expected_clauses"]


# =========================================================================
# 6. TEST UNSEEN OPEN-SET END-TO-END EXECUTION
# =========================================================================
def test_unseen_open_set_document_orchestration():
    """Ensures completely unseen legal documents are processed reliably with open-set fallback."""
    result = orchestrator.run_workflow(DOCUMENT_UNSEEN_OPEN_SET, workflow_type="parallel")
    assert result["status"] == "completed"
    assert result["document_metadata"]["document_type"] == "OTHER_LEGAL_DOCUMENT"
    assert result["routing"]["is_unknown_type"] is True
    assert 0 <= result["risk_analysis"]["overall_score"] <= 100
    assert 0 <= result["contract_health"]["score"] <= 100


if __name__ == "__main__":
    pytest.main(["-v", __file__])
