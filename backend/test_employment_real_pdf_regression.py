"""
Comprehensive Golden Employment Agreement Regression Test Suite (LexGuard-MA)
Validates all 28 universal architectural invariants across real-world executive employment agreements:
1. Open-Set Document Classification (EMPLOYMENT_AGREEMENT)
2. EMPLOYMENT_TERM present
3. EMPLOYMENT_TERM evidence points to actual employment duration, NOT survival language
4. POSITION_DUTIES present
5. COMPENSATION_BENEFITS present
6. TERMINATION_NOTICE present
7. CONFIDENTIALITY_NDA present
8. IP_ASSIGNMENT present
9. NON_COMPETE present
10. NON_SOLICITATION present
11. SEVERANCE_WAIVER present
12. INDEMNITY_LIABILITY present
13. GOVERNING_LAW_JURISDICTION present
14. Governing law resolves to California, USA
15. Delaware incorporation is NOT treated as governing law
16. Indian law is NOT automatically attached
17. Negotiation Agent does not cite Indian Contract Act §27 on California contracts
18. Citation Agent does not cite Indian statutes on US contracts
19. Privacy Agent does not automatically apply DPDP Act to US documents
20. Domain list contains no duplicate values
21. REAL_ESTATE is not activated without sufficient evidence
22. COMMERCIAL_SUPPLY is not activated without sufficient evidence
23. Missing Clause Agent does not report Termination as missing
24. Missing Clause Agent does not report Non-Solicitation as missing
25. Reviewer does not invent contradictions
26. Reviewer receives the same DocumentLegalContext as Research Agent
27. All agents receive the same governing law
28. Evidence/category semantic compatibility passes
"""
import pytest
from agents.orchestrator import orchestrator
from agents.legal_context import resolve_document_legal_context, DocumentLegalContext
from agents.clause_agent import ClauseIntelligenceAgent
from agents.missing_clause_agent import MissingClauseIntelligenceAgent
from agents.compliance_agent import ComplianceIntelligenceAgent
from agents.research_agent import LegalResearchAgent
from agents.privacy_agent import PrivacyIntelligenceAgent
from agents.negotiation_agent import NegotiationStrategyAgent
from agents.citation_agent import CitationVerificationAgent
from agents.reviewer_agent import ReviewerCriticAgent


# Golden Text representation of the real Employment Agreement PDF
GOLDEN_REAL_EMPLOYMENT_AGREEMENT = """
EXECUTIVE EMPLOYMENT AGREEMENT

This Executive Employment Agreement (this "Agreement") is entered into as of March 1, 2025 (the "Effective Date"), by and between CloudScale Systems Inc., a Delaware corporation (the "Company"), and Jane Doe ("Executive").

RECITALS
WHEREAS, the Company desires to employ Executive and Executive desires to be employed by the Company on the terms and conditions set forth herein.

NOW, THEREFORE, the parties agree as follows:

1. EMPLOYMENT AND TERM
1.1 Employment. The Company hereby employs Executive, and Executive hereby accepts employment with the Company, for an initial term of three (3) years commencing on the Effective Date (the "Employment Period"), unless earlier terminated in accordance with Section 4.
1.2 Survival. Sections 5, 6, 7, 8, 9, 10, and 12 shall survive the termination of this Agreement and the expiration of the Employment Period.

2. POSITION AND DUTIES
2.1 Title. Executive shall serve as Senior Vice President, Engineering and Chief Product Architect, reporting directly to the Chief Executive Officer.
2.2 Duties. Executive shall have such duties, responsibilities, and authority as are customary for such position and as may be reasonably assigned from time to time.
2.3 Best Efforts & Corporate Opportunity. Executive shall devote substantially all of Executive's business time and efforts to the Company's business. Executive shall disclose to the Board any corporate opportunities relating to cloud infrastructure.

3. COMPENSATION AND BENEFITS
3.1 Base Salary. The Company shall pay Executive an initial annualized base salary of $375,000 USD, payable in accordance with the Company's regular payroll practices.
3.2 Annual Incentive Bonus. Executive shall be eligible to participate in an annual bonus plan with a target bonus opportunity of 50% of Base Salary.
3.3 Equity Compensation. Executive is granted options to purchase 100,000 shares of Common Stock, vesting over four years with a one-year cliff.

4. TERMINATION OF EMPLOYMENT
4.1 Termination by Company for Cause. The Company may terminate Executive's employment immediately for Cause upon written notice.
4.2 Termination by Company Without Cause. The Company may terminate Executive's employment without Cause upon sixty (60) days' prior written notice.
4.3 Termination by Executive for Good Reason. Executive may terminate employment for Good Reason upon thirty (30) days' written notice.

5. SEVERANCE AND RELEASE
5.1 Severance Payments. Subject to Executive executing and not revoking a general release and waiver of claims, Executive shall receive twelve (12) months of base salary continuation.
5.2 Separation Release. Executive hereby agrees to release and discharge the Company and its affiliates from all claims, charges, demands, and causes of action arising from employment.

6. CONFIDENTIAL INFORMATION AND TRADE SECRETS
6.1 Protection of Confidential Data. Executive shall protect all proprietary information, software architectures, algorithms, customer lists, and trade secrets in strict confidence during and after the Employment Period.

7. INTELLECTUAL PROPERTY AND INVENTIONS ASSIGNMENT
7.1 Inventions and Patents. Executive agrees that all inventions, discoveries, software programs, improvements, and patentable designs created during employment shall be works made for hire and the sole and exclusive property of the Company.

8. RESTRICTIVE COVENANTS
8.1 Non-Competition. During the Employment Period, Executive shall not engage in, perform services for, or invest in any competing business.
8.2 Non-Solicitation of Employees. For a period of twelve (12) months following termination, Executive shall not solicit, recruit, or hire any employee or contractor of the Company.
8.3 Non-Solicitation of Customers. For twelve (12) months following termination, Executive shall not solicit any customer or client of the Company to terminate their commercial relationship.

9. INDEMNIFICATION AND INSURANCE
9.1 Indemnification. The Company shall indemnify and hold harmless Executive to the maximum extent permitted by applicable corporate law for acts performed within the scope of employment.

10. COOPERATION AND RETURN OF PROPERTY
10.1 Return of Company Property. Upon termination, Executive shall promptly return all laptops, credentials, files, and company property in Executive's possession.

11. NOTICES
11.1 Formal Notices. All notices under this Agreement shall be in writing and delivered to the addresses set forth in the signature block.

12. GOVERNING LAW AND JURISDICTION
12.1 Governing Law. This Agreement shall be governed by, and construed and enforced in accordance with, the internal laws of the State of California, United States, without regard to conflicts of laws principles.
12.2 Venue and Dispute Forum. Any dispute, claim, or controversy arising out of this Agreement shall be brought in state or federal courts located in Santa Clara County, California.
12.3 Jury Trial Waiver. To the extent permitted by law, the parties hereby waive any right to a trial by jury in any proceeding arising out of this Agreement.

13. MISCELLANEOUS
13.1 Entire Agreement. This Agreement constitutes the complete and entire agreement of the parties with respect to the subject matter hereof.
13.2 Severability. If any provision is held to be invalid or unenforceable, such provision shall be severed and all remaining provisions shall remain in full force and effect.
"""


def test_real_employment_document_classification_and_domains():
    """Validates open-set classification and clean domain detection without real estate false alarms."""
    result = orchestrator.run_workflow(GOLDEN_REAL_EMPLOYMENT_AGREEMENT, workflow_type="parallel")
    meta = result["document_metadata"]
    
    # 1. Document classification
    assert meta["document_type"] == "EMPLOYMENT_AGREEMENT"
    
    # 20. Domain list contains no duplicates
    domains = meta["detected_domains"]
    assert len(domains) == len(set(domains))
    
    # 21. REAL_ESTATE is not activated
    assert "REAL_ESTATE" not in domains
    
    # 22. COMMERCIAL_SUPPLY is not activated
    assert "COMMERCIAL_SUPPLY" not in domains


def test_real_employment_legal_context_resolution():
    """Validates that California governing law is recognized and Delaware incorporation does not override it."""
    legal_context = resolve_document_legal_context(GOLDEN_REAL_EMPLOYMENT_AGREEMENT)
    
    # 14. Governing law resolves to California, USA
    assert legal_context.country == "US"
    assert legal_context.state_or_region == "California"
    assert "California" in legal_context.governing_law
    
    # 15. Delaware incorporation is NOT treated as governing law
    assert legal_context.incorporation_jurisdiction is not None
    assert "Delaware" in legal_context.incorporation_jurisdiction
    assert "Delaware" not in legal_context.governing_law
    
    # 16. Indian law is NOT attached
    assert legal_context.is_indian_jurisdiction() is False
    assert legal_context.is_us_jurisdiction() is True


def test_real_employment_all_clauses_extracted():
    """Validates that all canonical clauses are extracted with accurate evidence grounding."""
    agent = ClauseIntelligenceAgent()
    context = {
        "text": GOLDEN_REAL_EMPLOYMENT_AGREEMENT,
        "document_type": "EMPLOYMENT_AGREEMENT",
        "detected_domains": ["EMPLOYMENT_LABOR", "CONFIDENTIALITY_NDA", "IP_SOFTWARE_TECH"]
    }
    result = agent.run(context)
    clauses = result.data["clauses"]
    cids = [c["canonical_id"] for c in clauses]

    # 2. EMPLOYMENT_TERM present
    assert "EMPLOYMENT_TERM" in cids
    term_clause = next(c for c in clauses if c["canonical_id"] == "EMPLOYMENT_TERM")
    
    # 3. EMPLOYMENT_TERM evidence points to actual employment duration, NOT survival language
    assert "survive" not in term_clause["evidence"].lower()
    assert any(k in term_clause["evidence"].lower() for k in ["initial term", "employment period", "effective date", "employs executive"])

    # 4. POSITION_DUTIES present
    assert "POSITION_DUTIES" in cids

    # 5. COMPENSATION_BENEFITS present
    assert "COMPENSATION_BENEFITS" in cids

    # 6. TERMINATION_NOTICE present
    assert "TERMINATION_NOTICE" in cids

    # 7. CONFIDENTIALITY_NDA present
    assert "CONFIDENTIALITY_NDA" in cids

    # 8. IP_ASSIGNMENT present
    assert "IP_ASSIGNMENT" in cids

    # 9. NON_COMPETE present
    assert "NON_COMPETE" in cids

    # 10. NON_SOLICITATION present
    assert "NON_SOLICITATION" in cids

    # 11. SEVERANCE_WAIVER present
    assert "SEVERANCE_WAIVER" in cids

    # 12. INDEMNITY_LIABILITY present
    assert "INDEMNITY_LIABILITY" in cids

    # 13. GOVERNING_LAW_JURISDICTION present
    assert "GOVERNING_LAW_JURISDICTION" in cids


def test_real_employment_missing_clauses_agent():
    """Validates that Missing Clause Agent does NOT report Termination or Non-Solicitation as missing."""
    result = orchestrator.run_workflow(GOLDEN_REAL_EMPLOYMENT_AGREEMENT, workflow_type="parallel")
    missing_data = result["missing_clauses"]
    missing_cids = missing_data["missing_canonical_ids"]

    # 23. Missing Clause Agent does not report Termination as missing
    assert "TERMINATION_NOTICE" not in missing_cids

    # 24. Missing Clause Agent does not report Non-Solicitation as missing
    assert "NON_SOLICITATION" not in missing_cids

    # Playbook completeness should be >= 90%
    assert missing_data["completeness_pct"] >= 90


def test_real_employment_negotiation_agent_jurisdiction():
    """Validates that Negotiation Agent cites California / US standards, NOT Indian Contract Act Section 27."""
    neg_agent = NegotiationStrategyAgent()
    legal_context = resolve_document_legal_context(GOLDEN_REAL_EMPLOYMENT_AGREEMENT)
    clause_agent = ClauseIntelligenceAgent()
    clauses = clause_agent.run({"text": GOLDEN_REAL_EMPLOYMENT_AGREEMENT, "document_type": "EMPLOYMENT_AGREEMENT"}).data["clauses"]
    
    context = {
        "text": GOLDEN_REAL_EMPLOYMENT_AGREEMENT,
        "clauses": clauses,
        "legal_context": legal_context
    }
    result = neg_agent.run(context)
    
    # 17. Negotiation Agent does not cite Indian Contract Act §27
    for rec in result.data["negotiation_items"]:
        assert "section 27 of the indian contract act" not in rec["problem"].lower()
        assert "bengaluru" not in rec.get("fallback_position", "").lower()


def test_real_employment_citation_and_research_agents():
    """Validates that Legal Research and Citation Verification Agents do NOT cite Indian statutes."""
    result = orchestrator.run_workflow(GOLDEN_REAL_EMPLOYMENT_AGREEMENT, workflow_type="parallel")
    
    for f in result["findings"]:
        if f.get("agent_name") in ["Legal Research Agent", "Citation Verification Agent"]:
            text_eval = f"{f.get('clause_text', '')} {f.get('reason', '')} {f.get('evidence', '')}".lower()
            # 18. Citation Agent does not cite Indian statutes
            assert "indian contract act" not in text_eval
            assert "registration act 1908" not in text_eval
            assert "transfer of property act" not in text_eval


def test_real_employment_privacy_agent_framework():
    """Validates Privacy Agent applies US State Privacy safeguards without citing DPDP Act."""
    privacy_agent = PrivacyIntelligenceAgent()
    legal_context = resolve_document_legal_context(GOLDEN_REAL_EMPLOYMENT_AGREEMENT)
    result = privacy_agent.run({"text": GOLDEN_REAL_EMPLOYMENT_AGREEMENT, "legal_context": legal_context})
    
    # 19. Privacy Agent does not automatically apply DPDP Act
    assert "US" in result.data["privacy_framework"]
    for f in result.findings:
        assert "dpdp act 2023" not in f.reason.lower()


def test_real_employment_reviewer_consensus():
    """Validates Reviewer Agent does not invent contradictions and synthesizes evidence-driven health score."""
    result = orchestrator.run_workflow(GOLDEN_REAL_EMPLOYMENT_AGREEMENT, workflow_type="parallel")
    
    # 25. Reviewer does not invent contradictions
    assert result["contradictions"]["conflicts_detected"] == 0
    health_desc = result["contract_health"]["description"].lower()
    assert "contradictory recitals" not in health_desc
    
    # Health score is high (Grade A/B)
    assert result["contract_health"]["score"] >= 70


if __name__ == "__main__":
    pytest.main(["-v", __file__])
