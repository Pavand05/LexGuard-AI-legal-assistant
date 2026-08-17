"""
Forensic Corrections & Generalization Regression Test Suite
Directly tests the resolution of the 12 forensic failure modes found during unseen U.S. Employment Agreement testing:
A. Employment Period must NOT classify as Lease Term
B. Compensation & Option Forfeiture must NOT classify as Default & Forfeiture
C. Property in Executive's Possession must NOT classify as Real Estate Possession
D. Release of claims, charges, demands, liens must NOT classify as Encumbrance & Mortgage
E. Existing Position & Duties must NOT be reported as missing
F. Existing Compensation & Benefits must NOT be reported as missing
G. Existing Termination & Notice must NOT be reported as missing
H. Existing Confidentiality & NDA must NOT be reported as missing
I. Existing IP Assignment must NOT be reported as missing
J. U.S. Delaware agreement must NOT receive Indian statutory authorities
K. Privacy Agent must NOT cite Indian DPDP Act on U.S. agreement
L. Reviewer must NOT claim "Contradictory Recitals" when contradiction count is zero
"""
import pytest
from agents.orchestrator import orchestrator
from agents.clause_agent import ClauseIntelligenceAgent
from agents.missing_clause_agent import MissingClauseIntelligenceAgent
from agents.research_agent import LegalResearchAgent
from agents.privacy_agent import PrivacyIntelligenceAgent
from agents.reviewer_agent import ReviewerCriticAgent


# Unseen Real-world style U.S. Executive Employment Agreement
UNSEEN_US_EMPLOYMENT_AGREEMENT = """
EXECUTIVE EMPLOYMENT AND CONFIDENTIALITY AGREEMENT
This Executive Employment Agreement ('Agreement') is made and entered into as of January 15, 2025, by and between Apex Global Technologies Inc., a Delaware corporation ('Company'), and John C. Smith ('Executive').

ARTICLE 1. EMPLOYMENT PERIOD
1.1 Period of Employment: The Company hereby employs Executive, and Executive hereby accepts employment with the Company, for an initial fixed term of three (3) years commencing on the Effective Date, unless earlier terminated pursuant to Article 4 herein.

ARTICLE 2. POSITION AND DUTIES
2.1 Title & Scope: Executive shall serve as Senior Vice President of Engineering, reporting directly to the Chief Executive Officer. Executive shall perform all duties, responsibilities, and management functions customary for such executive position.

ARTICLE 3. COMPENSATION AND BENEFITS
3.1 Base Salary: Executive shall receive an annualized base salary of $350,000 USD, payable in regular semi-monthly installments.
3.2 Annual Incentive Bonus: Executive shall be eligible for an annual target bonus of 40% of Base Salary.
3.3 Equity Incentive: Executive is granted 50,000 stock options subject to 4-year vesting. Unvested options shall be forfeited upon termination of employment.

ARTICLE 4. TERMINATION AND NOTICE PERIOD
4.1 Termination Without Cause: The Company may terminate Executive's employment without Cause upon providing sixty (60) calendar days prior written notice, or payment in lieu of notice.
4.2 Termination for Cause: The Company may immediately terminate Executive's employment for Cause upon written notice specifying the grounds.

ARTICLE 5. CONFIDENTIALITY AND PROPRIETARY INFORMATION
5.1 Confidential Information: Executive shall maintain in strict confidence and shall not disclose, copy, or use any trade secrets, customer lists, software algorithms, or proprietary data of the Company.

ARTICLE 6. INTELLECTUAL PROPERTY ASSIGNMENT
6.1 Inventions Assignment: Executive agrees that all inventions, software, patents, copyrights, and works of authorship created during employment shall be works made for hire and the sole and exclusive property of the Company.

ARTICLE 7. EXECUTIVE COOPERATION AND RETURN OF PROPERTY
7.1 Return of Materials: Upon termination, Executive shall promptly deliver to the Company all laptops, access keys, files, and company property in Executive's possession.

ARTICLE 8. RELEASE AND SEVERANCE
8.1 Separation Release: In exchange for severance payments, Executive hereby fully releases and discharges the Company from any and all claims, charges, demands, liens, and causes of action arising out of employment.

ARTICLE 9. RESTRICTIVE COVENANTS
9.1 Non-Solicitation: For a period of twelve (12) months following termination, Executive shall not solicit any employees or clients of the Company.

ARTICLE 10. GOVERNING LAW AND JURISDICTION
10.1 Applicable Law: This Agreement shall be governed by, and construed in accordance with, the laws of the State of Delaware, United States, without regard to conflicts of law principles. Exclusive jurisdiction shall lie with state and federal courts in Wilmington, Delaware.
"""


def test_us_employment_agreement_clause_classification():
    """Validates that clause classification does NOT falsely trigger real estate categories."""
    agent = ClauseIntelligenceAgent()
    context = {
        "text": UNSEEN_US_EMPLOYMENT_AGREEMENT,
        "document_type": "EMPLOYMENT_AGREEMENT",
        "detected_domains": ["EMPLOYMENT_LABOR"]
    }
    result = agent.run(context)
    clauses = result.data["clauses"]
    canonical_ids = [c["canonical_id"] for c in clauses]

    # A. Employment Period must be EMPLOYMENT_TERM (NOT LEASE_TERM_RENEWAL)
    assert "EMPLOYMENT_TERM" in canonical_ids
    assert "LEASE_TERM_RENEWAL" not in canonical_ids

    # B. Compensation must be COMPENSATION_BENEFITS (NOT DEFAULT_FORFEITURE)
    assert "COMPENSATION_BENEFITS" in canonical_ids
    assert "DEFAULT_FORFEITURE" not in canonical_ids

    # C. Executive cooperation must be COOPERATION_HANDOVER (NOT POSSESSION_REAL_ESTATE)
    assert "COOPERATION_HANDOVER" in canonical_ids
    assert "POSSESSION_REAL_ESTATE" not in canonical_ids

    # D. Release of claims, charges, liens must be SEVERANCE_WAIVER (NOT ENCUMBRANCE_MORTGAGE)
    assert "SEVERANCE_WAIVER" in canonical_ids
    assert "ENCUMBRANCE_MORTGAGE" not in canonical_ids


def test_us_employment_agreement_missing_clauses():
    """Validates that existing employment clauses are NOT reported as missing."""
    result = orchestrator.run_workflow(UNSEEN_US_EMPLOYMENT_AGREEMENT, workflow_type="parallel")
    missing_data = result["missing_clauses"]
    missing_cids = missing_data.get("missing_canonical_ids", [])
    missing_names = missing_data.get("missing_clauses", [])

    # E. Duties & Position must NOT be missing
    assert "POSITION_DUTIES" not in missing_cids

    # F. Compensation & Benefits must NOT be missing
    assert "COMPENSATION_BENEFITS" not in missing_cids

    # G. Termination & Notice must NOT be missing
    assert "TERMINATION_NOTICE" not in missing_cids

    # H. Confidentiality must NOT be missing
    assert "CONFIDENTIALITY_NDA" not in missing_cids

    # I. IP Assignment must NOT be missing
    assert "IP_ASSIGNMENT" not in missing_cids

    # Overall completeness for this comprehensive agreement should be high (>= 85%)
    assert missing_data["completeness_pct"] >= 85


def test_us_employment_agreement_jurisdiction_grounding():
    """Validates that U.S. Delaware agreement does NOT receive Indian statutory authorities."""
    result = orchestrator.run_workflow(UNSEEN_US_EMPLOYMENT_AGREEMENT, workflow_type="parallel")
    
    # Check legal research finding
    research_findings = [f for f in result["findings"] if f.get("agent_name") == "Legal Research Agent" or f.get("agent") == "Legal Research Agent"]
    assert len(research_findings) > 0
    
    # J. Must NOT contain Indian Contract Act, Registration Act, or Specific Relief Act
    for f in research_findings:
        text_content = f"{f.get('clause_text', '')} {f.get('reason', '')} {f.get('evidence', '')}".lower()
        assert "indian contract act" not in text_content
        assert "registration act" not in text_content
        assert "specific relief act" not in text_content


def test_us_employment_agreement_privacy_framework():
    """Validates that Privacy Agent cites US/State privacy and does NOT cite Indian DPDP Act on Delaware document."""
    privacy_agent = PrivacyIntelligenceAgent()
    context = {
        "text": UNSEEN_US_EMPLOYMENT_AGREEMENT,
        "applicable_law": "Laws of the State of Delaware, United States",
        "jurisdiction": "Wilmington, Delaware"
    }
    result = privacy_agent.run(context)
    
    # K. Privacy framework must reflect US jurisdiction
    assert "US" in result.data["privacy_framework"] or "Commercial" in result.data["privacy_framework"]
    for f in result.findings:
        assert "dpdp act 2023" not in f.reason.lower()


def test_reviewer_health_grade_without_contradictions():
    """Validates that Reviewer does NOT claim 'Contradictory Recitals' when contradictions are zero."""
    result = orchestrator.run_workflow(UNSEEN_US_EMPLOYMENT_AGREEMENT, workflow_type="parallel")
    
    # L. No contradictions in this agreement
    assert result["contradictions"]["conflicts_detected"] == 0
    
    # Reviewer health description must NOT claim contradictory recitals
    health_desc = result["contract_health"]["description"].lower()
    assert "contradictory recitals" not in health_desc
    assert "irreconcilable contradiction" not in health_desc


def test_paraphrased_property_documents_remain_functional():
    """Ensures regression safety: Real estate documents still detect their correct categories."""
    land_text = """
    DEED OF SALE
    1. SCHEDULE OF PROPERTY: Residential plot Survey No. 45/2, Whitefield, Bengaluru.
    2. TITLE: Vendor has clear, marketable and unencumbered title.
    3. MORTGAGE: Property was previously mortgaged with SBI; loan is discharged.
    4. POSSESSION: Actual physical vacant possession handed over on registration.
    5. CONSIDERATION: Total sale price is INR 48,00,000.
    """
    res = orchestrator.run_workflow(land_text, workflow_type="parallel")
    assert res["document_metadata"]["document_type"] == "LAND_SALE_DEED"
    
    clause_types = [c["type"] for c in res["clauses"]]
    assert "Title & Ownership" in clause_types
    assert "Encumbrance & Mortgage" in clause_types
    assert "Possession" in clause_types


if __name__ == "__main__":
    pytest.main(["-v", __file__])
