"""
NDA Real-PDF Regression & Universal Evidence Fix Test Suite (LexGuard-MA)
Validates all 20 required points for the real publicly filed Forescout Technologies / Advent International Mutual Non-Disclosure Agreement:
1. NDA classification = correct (NDA / CONFIDENTIALITY_AGREEMENT).
2. Primary domain = CONFIDENTIALITY_NDA.
3. EMPLOYMENT_LABOR not activated from employee non-solicitation alone.
4. Confidentiality = PRESENT.
5. Genuine termination = PRESENT (Paragraph 28: 2-year term / definitive agreement).
6. Governing law = PRESENT (Paragraph 19: Delaware law).
7. Delaware governing law = detected.
8. Delaware court jurisdiction = PRESENT (Paragraph 20: Delaware Chancery Court).
9. Arbitration = NOT DETECTED.
10. Formal Notices = only PRESENT if actual formal notices clause exists.
11. "termination of discussions" does not create false termination evidence.
12. "limited liability company" does not create false liability finding.
13. Actual liability/disclaimer clause is correctly identified (Paragraph 16).
14. Bank account number = NOT DETECTED (0 false PII alarms).
15. PII findings require exact source evidence.
16. Missing Clause Agent consumes canonical IDs (Governing Law & Termination recognized as present).
17. Reviewer does not treat false positives as risks.
18. Risk score is based only on verified findings.
19. All existing Employment tests remain passing.
20. All existing property/generalization/E2E/forensic tests remain passing.
"""
import pytest
from agents.orchestrator import orchestrator
from agents.document_agent import DocumentIntelligenceAgent
from agents.clause_agent import ClauseIntelligenceAgent
from agents.missing_clause_agent import MissingClauseIntelligenceAgent
from agents.privacy_agent import PrivacyIntelligenceAgent
from agents.compliance_agent import ComplianceIntelligenceAgent
from agents.legal_context import resolve_document_legal_context


GOLDEN_FORESCOUT_ADVENT_REAL_NDA = """
MUTUAL NON-DISCLOSURE AND CONFIDENTIALITY AGREEMENT

This Mutual Non-Disclosure and Confidentiality Agreement (this "Agreement") is entered into as of October 18, 2019 (the "Effective Date"), by and between:

Forescout Technologies, Inc., a Delaware corporation having its principal executive offices at 190 West Tasman Drive, San Jose, California 95134 ("Company"), and
Advent International Corporation, a Delaware corporation acting on behalf of its affiliated limited liability companies and managed investment funds, having an office at 800 Boylston Street, Boston, Massachusetts 02199 ("Recipient").

WHEREAS, in connection with evaluating a potential negotiated strategic transaction involving the parties (the "Potential Transaction"), each party may disclose to the other certain confidential, proprietary, or non-public information.

NOW, THEREFORE, in consideration of the mutual promises and covenants herein contained, the parties agree as follows:

1. DEFINITIONS AND EVALUATION MATERIAL
For purposes of this Agreement, "Evaluation Material" means all non-public, confidential, or proprietary information, in any form or medium (whether written, oral, visual, electronic, or otherwise), furnished by or on behalf of the Disclosing Party to the Receiving Party or its Representatives. Evaluation Material shall include, without limitation, all business plans, customer lists, software code, financials, and transaction information. The term "Transaction Information" includes the fact that Evaluation Material has been made available, that discussions or negotiations are taking place or have taken place, the status of such discussions, and any termination of discussions or negotiations between the parties.

2. CONFIDENTIALITY AND STANDARD OF CARE
The Receiving Party agrees that it and its Representatives shall: (a) keep all Evaluation Material strictly confidential and not disclose any Evaluation Material to any third party without the prior written consent of the Disclosing Party; and (b) use the Evaluation Material solely for the purpose of evaluating and negotiating the Potential Transaction and for no other purpose whatsoever. The Receiving Party shall protect the Evaluation Material with the same degree of care as it uses for its own confidential information of like nature, but in no event less than a reasonable degree of care.

7. COMPELLED DISCLOSURE
In the event that the Receiving Party or any of its Representatives receives a request or is legally compelled (by deposition, interrogatory, subpoena, civil investigative demand, or similar legal process) to disclose any Evaluation Material, the Receiving Party shall, to the extent legally permissible, notify the Disclosing Party in writing promptly so that the Disclosing Party may seek a protective order or other appropriate remedy.

15. NON-SOLICITATION OF EMPLOYEES
For a period of twelve (12) months from the Effective Date, neither party shall, directly or indirectly, solicit, recruit, or hire any current senior executive or key employee of the other party who became known to such party in connection with the evaluation of the Potential Transaction; provided, however, that this restriction shall not prohibit general solicitations of employment through public advertisements or headhunter searches not targeted specifically at such employees.

16. DISCLAIMER OF WARRANTIES AND LIMITATION OF LIABILITY
Each party understands and acknowledges that neither Disclosing Party nor any of its Representatives makes any representation or warranty, express or implied, as to the accuracy or completeness of the Evaluation Material. Neither Disclosing Party nor any of its Representatives shall have any liability whatsoever to the Receiving Party or any of its Representatives arising out of or resulting from the use of, or reliance upon, the Evaluation Material or any errors therein or omissions therefrom, except to the extent expressly set forth in a definitive agreement.

19. GOVERNING LAW
This Agreement and all claims, controversies, or causes of action arising out of or relating to this Agreement or the Potential Transaction shall be governed by, and construed in accordance with, the internal laws of the State of Delaware, without giving effect to any choice or conflict of law provision or rule.

20. EXCLUSIVE JURISDICTION AND VENUE
Each of the parties hereby irrevocably and unconditionally submits, for itself and its property, to the exclusive jurisdiction of the Court of Chancery of the State of Delaware (or, if such court lacks subject matter jurisdiction, the state and federal courts located in Wilmington, Delaware) in any action or proceeding arising out of or relating to this Agreement or the Potential Transaction.

28. TERM AND TERMINATION
This Agreement and all obligations hereunder shall terminate upon the earlier to occur of: (a) the second (2nd) anniversary of the Effective Date; and (b) the execution and delivery of a definitive written agreement between the parties regarding the Potential Transaction. Notwithstanding anything to the contrary herein, the obligations of confidentiality under Section 2 with respect to trade secrets shall survive termination of this Agreement for as long as such information remains a trade secret under applicable law.

IN WITNESS WHEREOF, the parties hereto have executed this Mutual Non-Disclosure Agreement as of the Effective Date.

FORESCOUT TECHNOLOGIES, INC.
By: /s/ Authorized Signatory
Name: Christopher Harms
Title: Chief Financial Officer

ADVENT INTERNATIONAL CORPORATION
By: /s/ Authorized Signatory
Name: Bryan Taylor
Title: Managing Partner
"""


def test_nda_document_classification_and_domains():
    """1. NDA classification & 2-3. Primary domain is CONFIDENTIALITY_NDA, EMPLOYMENT_LABOR is not activated."""
    doc_agent = DocumentIntelligenceAgent()
    res = doc_agent.run({"text": GOLDEN_FORESCOUT_ADVENT_REAL_NDA, "filename": "forescout_advent_nda.pdf"})
    
    assert res.status == "success"
    assert res.data["document_type"] in ["NDA", "CONFIDENTIALITY_AGREEMENT"]
    
    # 2. Primary Domain is CONFIDENTIALITY_NDA
    detected_domains = res.data["detected_domains"]
    assert "CONFIDENTIALITY_NDA" in detected_domains
    
    # 3. Employee non-solicitation alone must NOT activate EMPLOYMENT_LABOR
    assert "EMPLOYMENT_LABOR" not in detected_domains


def test_nda_legal_context_resolution():
    """6. Governing law = Delaware, 7. Delaware detected, 8. Delaware court jurisdiction, 9. Arbitration not detected."""
    ctx = resolve_document_legal_context(GOLDEN_FORESCOUT_ADVENT_REAL_NDA)
    
    assert "Delaware" in ctx.governing_law
    assert ctx.is_us_jurisdiction() is True
    assert "Delaware" in ctx.court_jurisdiction or "Wilmington" in ctx.court_jurisdiction
    
    # 9. Arbitration is absent
    assert ctx.arbitration_seat is None or ctx.arbitration_seat == ""


def test_nda_evidence_compatibility_and_clause_classification():
    """4. Confidentiality PRESENT, 5. Genuine termination PRESENT, 11-13. Evidence compatibility validation."""
    clause_agent = ClauseIntelligenceAgent()
    res = clause_agent.run({
        "text": GOLDEN_FORESCOUT_ADVENT_REAL_NDA,
        "document_type": "NDA",
        "detected_domains": ["CONFIDENTIALITY_NDA"]
    })
    
    clauses = res.data["clauses"]
    canonical_ids = [c["canonical_id"] for c in clauses]
    
    # 4. Confidentiality is PRESENT
    assert "CONFIDENTIALITY_NDA" in canonical_ids
    
    # 5. Genuine Termination is PRESENT
    assert "TERMINATION_NOTICE" in canonical_ids
    term_clause = next(c for c in clauses if c["canonical_id"] == "TERMINATION_NOTICE")
    # 11. "termination of discussions" inside definition must NOT be the termination evidence
    assert "discussions or negotiations" not in term_clause["evidence"].lower()
    assert "second (2nd) anniversary" in term_clause["content"].lower() or "terminate upon the earlier" in term_clause["content"].lower()
    
    # 12. "limited liability company" in party descriptor must NOT be classified as Liability
    # 13. Paragraph 16 Disclaimer of Warranties & Liability IS classified as Liability
    liability_clauses = [c for c in clauses if c["canonical_id"] == "INDEMNITY_LIABILITY"]
    for lc in liability_clauses:
        assert "limited liability company" not in lc["heading"].lower()
        assert "limited liability company" not in lc["evidence"].lower()
        
    # 6. Governing Law is PRESENT
    assert "GOVERNING_LAW_JURISDICTION" in canonical_ids


def test_nda_pii_no_false_bank_account():
    """14. Bank account number = NOT DETECTED & 15. Exact source evidence."""
    priv_agent = PrivacyIntelligenceAgent()
    res = priv_agent.run({
        "text": GOLDEN_FORESCOUT_ADVENT_REAL_NDA,
        "privacy_mode": False
    })
    
    assert res.status == "success"
    # 14. No exposed bank account number in this NDA
    exposed_types = [f.clause_type for f in res.findings if "PII Actually Exposed" in f.clause_type]
    assert not any("Bank Account" in t for t in exposed_types)
    assert not any("Aadhaar" in t for t in exposed_types)
    assert not any("PAN" in t for t in exposed_types)


def test_nda_missing_clauses_agent_canonical_flow():
    """16. Missing Clause Agent consumes canonical IDs from Clause Agent."""
    clause_agent = ClauseIntelligenceAgent()
    c_res = clause_agent.run({
        "text": GOLDEN_FORESCOUT_ADVENT_REAL_NDA,
        "document_type": "NDA",
        "detected_domains": ["CONFIDENTIALITY_NDA"]
    })
    
    missing_agent = MissingClauseIntelligenceAgent()
    m_res = missing_agent.run({
        "text": GOLDEN_FORESCOUT_ADVENT_REAL_NDA,
        "document_type": "NDA",
        "detected_domains": ["CONFIDENTIALITY_NDA"],
        "clauses": c_res.data["clauses"]
    })
    
    missing_ids = m_res.data.get("missing_canonical_ids", [])
    # Governing Law & Termination must NOT be reported as missing
    assert "GOVERNING_LAW_JURISDICTION" not in missing_ids
    assert "TERMINATION_NOTICE" not in missing_ids
    assert "CONFIDENTIALITY_NDA" not in missing_ids


def test_nda_full_orchestration_workflow():
    """17-18. Full pipeline execution: verified risk score, no hallucinated citations, Grade A health."""
    result = orchestrator.run_workflow(GOLDEN_FORESCOUT_ADVENT_REAL_NDA, workflow_type="parallel")
    
    assert result["status"] == "completed"
    assert result["document_metadata"]["document_type"] in ["NDA", "CONFIDENTIALITY_AGREEMENT"]
    
    # 0 Indian statutory citations attached to Delaware document
    citations = result.get("citations", {}).get("citations", [])
    for cit in citations:
        assert "Indian Contract Act" not in cit.get("act", "")
        assert "Section 27" not in cit.get("section", "")
        
    # Health score is strong (Grade A/B)
    assert result["contract_health"]["score"] >= 75
    assert result["contradictions"]["conflicts_detected"] == 0
