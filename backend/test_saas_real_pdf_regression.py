"""
SaaS Agreement Real-PDF Regression & Universal Generalization Test Suite (LexGuard-MA)

Validates the forensic resolution of the 10 systemic generalization failures identified
in the blind testing of the real Software as a Service Agreement (Verizon / Digital Turbine):
1. Primary vs Referenced Agreements (SaaS vs Referenced NDA)
2. Accurate Governing Law & Court Jurisdiction (New York precedence over California addresses)
3. Financial Applicability vs Financial Risk (fees, revenue share, taxes, audit)
4. Hard Normalization of All Risk Scores (0-100 mathematical invariant)
5. Dispute Resolution Taxonomy (Court Jurisdiction vs Arbitration gap handling)
6. Traceable Evidence-to-Finding Binding (Section 21.1 -> Governing Law)
7. Data Security Safeguards vs PII Leakage Distinction
8. Comprehensive SaaS Canonical Clause Category Extraction
9. Referenced Agreement Metadata Extraction
10. US / New York Statutory Grounding without Indian statutory hallucination
"""
import pytest
from agents.document_agent import DocumentIntelligenceAgent
from agents.clause_agent import ClauseIntelligenceAgent
from agents.risk_agent import RiskAssessmentAgent
from agents.missing_clause_agent import MissingClauseIntelligenceAgent
from agents.privacy_agent import PrivacyIntelligenceAgent
from agents.research_agent import LegalResearchAgent
from agents.citation_agent import CitationVerificationAgent
from agents.reviewer_agent import ReviewerCriticAgent
from agents.orchestrator import MultiAgentOrchestrator
from agents.legal_context import resolve_document_legal_context


# ── REAL SAAS AGREEMENT REPRESENTATIVE BENCHMARK TEXT ────────────────────────
REAL_SAAS_AGREEMENT_TEXT = """
SOFTWARE AS A SERVICE AGREEMENT

This SOFTWARE AS A SERVICE AGREEMENT (the "Agreement") is entered into as of October 15, 2023 (the "Effective Date"),
by and between Cellco Partnership, a Delaware general partnership d/b/a Verizon Wireless, with its principal office at
One Verizon Way, Basking Ridge, NJ 07920 ("Verizon"), and Digital Turbine USA, Inc., a Delaware corporation,
having offices at 110 San Jose Blvd, Suite 400, San Jose, CA 95110 ("Provider" or "Digital Turbine").

RECITALS
WHEREAS, Provider has developed and operates a proprietary cloud-based content delivery and application management platform; and
WHEREAS, Verizon desires to obtain access to the hosted platform services, and Provider desires to provide such services; and
WHEREAS, prior to this Agreement, the Parties executed that certain Mutual Non-Disclosure Agreement dated January 12, 2023 ("NDA"),
which is hereby incorporated by reference with respect to historical exchanges of proprietary information.

NOW, THEREFORE, in consideration of the mutual covenants contained herein, the Parties agree as follows:

SECTION 1. DEFINITIONS AND SERVICE SCOPE
1.1 "Platform Services" means the Software-as-a-Service (SaaS) application and cloud infrastructure hosted and maintained by Provider.
1.2 Provider shall provide Verizon and its authorized affiliates access to the Platform Services in accordance with the specifications set forth in Schedule A.

SECTION 2. SOFTWARE LICENSE AND GRANT OF RIGHTS
2.1 Provider grants to Verizon a non-exclusive, non-transferable, worldwide license during the Term to access and use the Platform Services,
including permitted API access for up to 5,000 authorized concurrent administrative users.
2.2 Verizon shall not reverse engineer, decompile, or disassemble any binary components of the Platform Services.

SECTION 3. HOSTING, AVAILABILITY AND SLA
3.1 Provider shall maintain server hosting and system availability for the Platform Services with an uptime commitment of not less than 99.9% per calendar month, excluding scheduled maintenance.
3.2 In the event Provider fails to meet the uptime commitment, Verizon shall be entitled to receive service credits in accordance with the SLA set forth in Exhibit B.

SECTION 4. FEES, REVENUE SHARING AND PAYMENT TERMS
4.1 Verizon shall pay Provider a monthly subscription fee of $45,000 for platform maintenance and support tier access.
4.2 In addition to subscription fees, the Parties agree to a gross revenue share under which Verizon shall remit 18% of all net monetization receipts derived from platform distributions.
4.3 All invoices shall be payable net forty-five (45) days from receipt. All applicable sales taxes and indirect taxes shall be separately stated.

SECTION 5. FINANCIAL AUDIT AND INSPECTION OF RECORDS
5.1 Upon thirty (30) days prior written notice, Verizon or its certified independent public accountant shall have the right to audit and inspect Provider's books and accounting records relating to revenue share calculations and subscription charges.

SECTION 6. DATA SECURITY AND SUBSCRIBER PRIVACY
6.1 Provider shall implement and maintain administrative, physical, and technical safeguards to ensure the security, confidentiality, and integrity of all Verizon Customer Data and Subscriber Information.
6.2 Provider shall not collect, process, or transmit subscriber information or user device telemetry except as strictly required to perform the Platform Services.
6.3 In the event of any unauthorized access to Customer Data, Provider shall notify Verizon in writing within twenty-four (24) hours of becoming aware of the security incident.

SECTION 7. INTELLECTUAL PROPERTY OWNERSHIP
7.1 As between the Parties, Provider retains all right, title, and interest in and to the Platform Services, underlying software, and all intellectual property rights therein.
7.2 Verizon retains all right, title, and interest in and to Verizon Customer Data, subscriber records, and Verizon trademarks.

SECTION 8. CONFIDENTIALITY
8.1 Each Party agrees to maintain in strict confidence and not disclose to third parties any Confidential Information received from the other Party, using at least the same degree of care it uses to protect its own confidential materials of like nature, but not less than reasonable care.

SECTION 9. INDEMNIFICATION
9.1 Provider shall defend, indemnify, and hold harmless Verizon, its affiliates, directors, officers, and employees from and against any third-party claims, liabilities, losses, and damages arising out of any allegation that the Platform Services infringe any patent, copyright, trademark, or trade secret of any third party.

SECTION 10. LIMITATION OF LIABILITY
10.1 EXCEPT FOR BREACHES OF SECTION 8 (CONFIDENTIALITY) OR INDEMNIFICATION OBLIGATIONS UNDER SECTION 9, NEITHER PARTY SHALL BE LIABLE FOR ANY INDIRECT, INCIDENTAL, CONSEQUENTIAL, SPECIAL, OR PUNITIVE DAMAGES.
10.2 EACH PARTY'S AGGREGATE LIABILITY UNDER THIS AGREEMENT SHALL BE CAPPED AT AND SHALL NOT EXCEED THE TOTAL FEES PAID OR PAYABLE IN THE TWELVE (12) MONTHS PRECEDING THE CLAIM.

SECTION 11. TERM AND TERMINATION
11.1 This Agreement shall commence on the Effective Date and shall continue for an initial term of three (3) years (the "Term"), unless earlier terminated in accordance with this Section 11.
11.2 Either Party may terminate this Agreement for cause if the other Party materially breaches any provision and fails to cure such breach within thirty (30) days of receiving written notice thereof.

SECTION 12. SURVIVAL
12.1 The provisions of Section 4 (Fees & Payment), Section 5 (Audit), Section 7 (IP Ownership), Section 8 (Confidentiality), Section 9 (Indemnification), Section 10 (Limitation of Liability), Section 12 (Survival), and Section 21 (Governing Law) shall survive any expiration or termination of this Agreement.

SECTION 21. GOVERNING LAW AND JURISDICTION
21.1 This Agreement will be construed and controlled by the laws of the State of New York, without giving effect to any principles of conflicts of law.
21.2 The Parties hereby submit to the exclusive jurisdiction and venue in the federal courts sitting in the Southern District of New York for the resolution of all disputes arising under or in connection with this Agreement.

SECTION 22. NOTICES
All notices hereunder shall be in writing and sent by certified mail or overnight courier to the addresses specified in the preamble.
"""


def test_saas_document_classification_and_referenced_nda():
    """TEST 1 & 9: SaaS agreement is classified as SAAS_AGREEMENT, not NDA; NDA is marked as referenced/incorporated."""
    agent = DocumentIntelligenceAgent()
    res = agent.run({"text": REAL_SAAS_AGREEMENT_TEXT, "filename": "Saas agreement_1.pdf"})
    
    assert res.status == "success"
    data = res.data
    # Must be classified as SAAS_AGREEMENT (primary document type)
    assert data["document_type"] == "SAAS_AGREEMENT"
    assert data["primary_type"] == "SAAS_AGREEMENT"
    assert data["primary_domain"] == "IP_SOFTWARE_TECH"
    assert data["classification_confidence"] >= 0.90
    
    # Referenced NDA must be captured in referenced_documents, NOT hijacking primary classification
    ref_docs = data.get("referenced_documents", [])
    assert len(ref_docs) >= 1
    nda_refs = [r for r in ref_docs if r["type"] == "NDA"]
    assert len(nda_refs) >= 1
    assert nda_refs[0]["status"] in ["INCORPORATED", "REFERENCED"]


def test_saas_governing_law_and_court_jurisdiction():
    """TEST 2: Explicit New York governing law and Southern District of New York courts take precedence over CA address."""
    ctx = resolve_document_legal_context(REAL_SAAS_AGREEMENT_TEXT)
    
    assert ctx.country == "US"
    assert ctx.state_or_region == "New York"
    assert "New York" in ctx.governing_law
    assert "Southern District of New York" in (ctx.court_jurisdiction or "")
    assert ctx.venue is not None and "Southern District of New York" in ctx.venue
    assert ctx.governing_law_source == "Explicit Governing Law Clause"


def test_saas_financial_applicability_and_risk():
    """TEST 3: Agreement containing revenue share/fees/taxes/audit has financial_applicable = True and valid score."""
    clause_agent = ClauseIntelligenceAgent()
    c_res = clause_agent.run({
        "text": REAL_SAAS_AGREEMENT_TEXT,
        "document_type": "SAAS_AGREEMENT",
        "detected_domains": ["IP_SOFTWARE_TECH", "COMMERCIAL_SUPPLY"]
    })
    clauses = c_res.data["clauses"]
    
    risk_agent = RiskAssessmentAgent()
    r_res = risk_agent.run({
        "text": REAL_SAAS_AGREEMENT_TEXT,
        "document_type": "SAAS_AGREEMENT",
        "detected_domains": ["IP_SOFTWARE_TECH", "COMMERCIAL_SUPPLY"],
        "clauses": clauses,
        "findings": c_res.findings
    })
    
    assert r_res.status == "success"
    r_data = r_res.data
    assert r_data["financial_applicable"] is True
    dim_breakdown = r_data["dimension_breakdown"]
    assert "Financial" in dim_breakdown
    assert dim_breakdown["Financial"] > 0  # Financial must not be 0/100


def test_saas_risk_scores_hard_normalized_0_to_100():
    """TEST 4: Every single risk dimension and overall score MUST strictly be between 0 and 100."""
    clause_agent = ClauseIntelligenceAgent()
    c_res = clause_agent.run({
        "text": REAL_SAAS_AGREEMENT_TEXT,
        "document_type": "SAAS_AGREEMENT",
        "detected_domains": ["IP_SOFTWARE_TECH"]
    })
    
    risk_agent = RiskAssessmentAgent()
    r_res = risk_agent.run({
        "text": REAL_SAAS_AGREEMENT_TEXT,
        "document_type": "SAAS_AGREEMENT",
        "detected_domains": ["IP_SOFTWARE_TECH"],
        "clauses": c_res.data["clauses"],
        "findings": c_res.findings
    })
    
    overall = r_res.data["overall_risk_score"]
    assert 0 <= overall <= 100, f"Overall risk score {overall} is outside 0-100"
    
    for dim, score in r_res.data["dimension_breakdown"].items():
        assert 0 <= score <= 100, f"Dimension {dim} score {score} is outside 0-100"


def test_saas_dispute_resolution_court_vs_arbitration():
    """TEST 5: Court jurisdiction is present, arbitration is not detected; missing clause agent does not falsely report missing dispute resolution."""
    clause_agent = ClauseIntelligenceAgent()
    c_res = clause_agent.run({
        "text": REAL_SAAS_AGREEMENT_TEXT,
        "document_type": "SAAS_AGREEMENT",
        "detected_domains": ["IP_SOFTWARE_TECH"]
    })
    
    missing_agent = MissingClauseIntelligenceAgent()
    m_res = missing_agent.run({
        "text": REAL_SAAS_AGREEMENT_TEXT,
        "document_type": "SAAS_AGREEMENT",
        "detected_domains": ["IP_SOFTWARE_TECH"],
        "clauses": c_res.data["clauses"]
    })
    
    missing_ids = m_res.data.get("missing_canonical_ids", [])
    # Dispute resolution is satisfied via New York federal courts
    assert "DISPUTE_RESOLUTION_ARBITRATION" not in missing_ids
    assert "ARBITRATION" not in missing_ids


def test_saas_evidence_binding_to_governing_law_section():
    """TEST 6: Governing law finding is bound to Section 21 / Governing Law, NOT to revenue share or payment."""
    clause_agent = ClauseIntelligenceAgent()
    c_res = clause_agent.run({
        "text": REAL_SAAS_AGREEMENT_TEXT,
        "document_type": "SAAS_AGREEMENT",
        "detected_domains": ["IP_SOFTWARE_TECH"]
    })
    clauses = c_res.data["clauses"]
    
    gov_clauses = [c for c in clauses if c.get("canonical_id") in ["GOVERNING_LAW_JURISDICTION", "GOVERNING_LAW", "COURT_JURISDICTION"]]
    assert len(gov_clauses) >= 1
    gov_clause = gov_clauses[0]
    
    # Check that evidence mentions New York / laws / courts, not revenue share
    ev = gov_clause.get("evidence", "").lower()
    full = gov_clause.get("full_text", "").lower()
    assert "new york" in ev or "new york" in full
    assert "revenue share" not in ev


def test_saas_data_security_no_false_pii_leakage():
    """TEST 7: Contractual data security requirements do not trigger false positive PII leakage findings."""
    privacy_agent = PrivacyIntelligenceAgent()
    p_res = privacy_agent.run({
        "text": REAL_SAAS_AGREEMENT_TEXT,
        "document_type": "SAAS_AGREEMENT",
        "detected_domains": ["IP_SOFTWARE_TECH"]
    })
    
    assert p_res.status == "success"
    # No actual Aadhaar, PAN, SSN, or bank account is exposed in the contract text
    assert p_res.data.get("has_pii") is False
    assert len(p_res.data.get("exposed_items", [])) == 0


def test_saas_full_orchestration_and_schema():
    """TEST 8 & 10: Complete multi-agent pipeline extracts all SaaS categories, produces valid 0-100 scores, and applies US law."""
    orch = MultiAgentOrchestrator()
    result = orch.run_workflow(
        document_text=REAL_SAAS_AGREEMENT_TEXT,
        workflow_type="parallel",
        privacy_mode=False
    )
    
    assert result["status"] == "completed"
    
    # 1. Document Classification
    doc_info = result["document"]
    assert doc_info["primary_type"] == "SAAS_AGREEMENT"
    assert doc_info["primary_domain"] == "IP_SOFTWARE_TECH"
    assert "New York" in doc_info["governing_law"]["jurisdiction"]
    assert doc_info["governing_law"]["country"] == "US"
    
    # 2. Dispute Resolution
    disp = result["dispute_resolution"]
    assert "Southern District of New York" in (disp["court_jurisdiction"] or "")
    assert disp["arbitration"] == "NOT_DETECTED"
    
    # 3. Financial Applicability & Score
    fin = result["financial"]
    assert fin["applicable"] is True
    assert 0 <= fin["risk_score"] <= 100
    
    # 4. Risk Analysis Normalization
    risk = result["risk_analysis"]
    assert 0 <= risk["overall_risk_score"] <= 100
    for dim, score in risk["dimensions"].items():
        assert 0 <= score <= 100, f"Dimension {dim} score {score} out of bounds"
        
    # 5. Contract Health
    health = result["contract_health"]
    assert 0 <= health["score"] <= 100
    
    # 6. Clause Categories
    extracted_canonical = set(c.get("canonical_id") for c in result["clauses"])
    assert "SERVICE_SCOPE" in extracted_canonical or "SOFTWARE_LICENSE" in extracted_canonical
    assert "INDEMNITY_LIABILITY" in extracted_canonical or "INDEMNIFICATION" in extracted_canonical
    assert "TERMINATION_NOTICE" in extracted_canonical
