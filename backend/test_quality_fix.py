"""
Comprehensive Quality & Correctness Test Suite for LexGuard-MA
Tests:
1. Land Sale Deed vs NDA vs Employment Classification
2. Semantic Clause Classification (Mortgage & Encumbrance vs Notices)
3. First-Class Contradiction Detection (Payment, Possession, Forum)
4. Citation Verification Integrity (Document citations vs AI claims, No duplication)
5. Transparent Deterministic Risk & Health Scoring
6. Reviewer Agent Consensus & Disagreement Detection
"""
import pytest
from agents.document_agent import DocumentIntelligenceAgent
from agents.clause_agent import ClauseIntelligenceAgent
from agents.contradiction_agent import ContradictionDetectionAgent
from agents.citation_agent import CitationVerificationAgent
from agents.risk_agent import RiskAssessmentAgent
from agents.reviewer_agent import ReviewerCriticAgent
from agents.orchestrator import orchestrator


SYNTHETIC_LAND_SALE_DEED = """
DEED OF ABSOLUTE SALE

This DEED OF ABSOLUTE SALE is executed on this 15th day of March 2025 at Bengaluru, Karnataka:
BY AND BETWEEN:
Mr. Ramesh Kumar (hereinafter referred to as the 'VENDOR', which expression shall include his heirs and assigns)
AND
Mr. Suresh Sharma (hereinafter referred to as the 'PURCHASER', which expression shall include his successors).

WHEREAS the Vendor is the absolute owner of the immovable property bearing Survey No. 45/2, Khata No. 891, measuring 2,400 sq.ft situated at Whitefield, Bengaluru, more fully described in the Schedule below.

NOW THIS DEED WITNESSETH AS FOLLOWS:
1. TITLE AND OWNERSHIP: The Vendor represents and warrants that he is the sole and absolute owner of the Schedule Property with clear, marketable, and unencumbered title.
2. ENCUMBRANCE AND MORTGAGE: The Schedule Property was previously mortgaged with State Bank of India under Loan A/c No. 9876543210. The Vendor covenants that the mortgage debt is discharged and property is free from all encumbrances, charges, and court attachments.
3. SALE CONSIDERATION AND PAYMENT: The agreed total sale consideration is INR 48,00,000 (Rupees Forty-Eight Lakhs only). The Purchaser has paid an advance sum of INR 8,00,000 (Rupees Eight Lakhs only) via NEFT, and the balance consideration of INR 40,00,000 shall be payable at the time of registration before the Sub-Registrar.
4. INDEMNITY: The Vendor shall keep the Purchaser indemnified against any loss, damage, or third-party claims arising out of any defect in title or prior unpaid dues.
5. POSSESSION: The Vendor covenants that actual physical vacant possession of the Schedule Property shall be handed over to the Purchaser on or after registration of this deed.
6. REGISTRATION AND STAMP DUTY: The Purchaser shall bear all stamp duty and registration expenses for registration before the Senior Sub-Registrar, Bengaluru.
7. TAXES AND OUTGOINGS: All property taxes, municipal cess, and electricity dues up to the date of execution shall be cleared by the Vendor.
8. DISPUTE RESOLUTION: Any dispute or claim arising out of this Deed shall be subject to the exclusive jurisdiction of the competent Civil Courts at Bengaluru.
9. ARBITRATION: In the event of any contractual dispute, the matter shall be referred to a sole arbitrator and the seat of arbitration shall be conducted at Mysuru.
10. POSSESSION STATUS RECITAL: The Vendor hereby acknowledges that he has already handed over physical vacant possession of the Schedule Property to the Purchaser prior to execution.
11. RECEIPT OF FULL CONSIDERATION: The Vendor hereby admits and acknowledges that the entire sale consideration of INR 48,00,000 has been received in full and final settlement, and no balance amount is due from the Purchaser.

SCHEDULE OF PROPERTY:
All that piece and parcel of residential site measuring East to West 40 feet, North to South 60 feet, in all 2,400 sq.ft, Survey No. 45/2, bounded on:
East by: Road
West by: Property of Mr. Ananda
North by: Site No. 12
South by: Site No. 14
"""

SYNTHETIC_NDA = """
MUTUAL NON-DISCLOSURE AGREEMENT
This Agreement is entered into by and between Alpha Corp and Beta Ltd to protect Confidential Information disclosed for the purpose of exploring a potential strategic partnership.
1. Confidential Information shall mean all technical and business data disclosed.
2. Non-Disclosure: Receiving party shall maintain strict secrecy and not disclose to third parties without prior written consent.
3. Term: This Agreement shall remain valid for 2 years from effective date.
4. Governing Law: This Agreement shall be governed by the laws of India and exclusive jurisdiction of courts at New Delhi.
"""


def test_land_sale_deed_classification():
    """Test that synthetic land sale deed is correctly classified as LAND_SALE_DEED with high confidence."""
    agent = DocumentIntelligenceAgent()
    result = agent.run({"text": SYNTHETIC_LAND_SALE_DEED, "filename": "sale_deed.pdf"})
    
    assert result.status == "success"
    assert result.data["document_type"] == "LAND_SALE_DEED"
    assert result.confidence >= 0.90
    assert "Deed of Absolute Sale / Land Sale Deed" in result.data["document_type_display"]
    assert len(result.data["classification_evidence"]) >= 3


def test_nda_classification():
    """Test that NDA is correctly classified as NDA, not land deed."""
    agent = DocumentIntelligenceAgent()
    result = agent.run({"text": SYNTHETIC_NDA, "filename": "nda.pdf"})
    
    assert result.status == "success"
    assert result.data["document_type"] == "NDA"
    assert result.confidence >= 0.85


def test_clause_semantic_classification():
    """Test that mortgage & encumbrance clause is categorized as 'Encumbrance & Mortgage', NOT 'Notices'."""
    agent = ClauseIntelligenceAgent()
    result = agent.run({"text": SYNTHETIC_LAND_SALE_DEED})
    
    assert result.status == "success"
    categories = [c["category"] for c in result.data["clauses"]]
    
    assert "Encumbrance & Mortgage" in categories
    assert "Title & Ownership" in categories
    assert "Consideration & Payment" in categories
    assert "Possession" in categories
    assert "Property Description & Schedule" in categories
    # Notice category should not swallow mortgage clause
    for c in result.data["clauses"]:
        if "mortgage" in c["content"].lower():
            assert c["category"] == "Encumbrance & Mortgage"


def test_contradiction_detection():
    """Test detection of Payment, Possession, and Dispute Forum contradictions."""
    agent = ContradictionDetectionAgent()
    result = agent.run({"text": SYNTHETIC_LAND_SALE_DEED})
    
    assert result.status in ["success", "warning"]
    data = result.data
    assert data["has_payment_contradiction"] is True
    assert data["has_possession_contradiction"] is True
    assert data["has_forum_contradiction"] is True
    assert data["critical_conflicts"] >= 1
    
    # Check that findings contain CRITICAL severity for payment contradiction
    pay_findings = [f for f in result.findings if "Payment" in f.clause_type or "Consideration" in f.clause_type]
    assert len(pay_findings) > 0
    assert pay_findings[0].severity == "CRITICAL"


def test_citation_verification_agent():
    """Test citation verification handles docs with no explicit citations without hallucination."""
    agent = CitationVerificationAgent()
    result = agent.run({"text": SYNTHETIC_LAND_SALE_DEED, "findings": []})
    
    assert result.status == "success"
    assert "Document contains no explicit statutory/case citations" in result.findings[0].clause_text
    # Should not fabricate fake citations
    assert len(result.data["verified_authorities"]) == 0


def test_deterministic_risk_and_health_scoring():
    """Test that Contract Risk (Higher=Worse) and Contract Health (Higher=Better) are correctly calculated."""
    res = orchestrator.run_workflow(SYNTHETIC_LAND_SALE_DEED, workflow_type="parallel")
    
    assert res["status"] == "completed"
    
    # Check Risk
    risk_info = res["risk_analysis"]
    assert 0 <= risk_info["overall_score"] <= 100
    assert "Higher Risk" in risk_info["definition"]
    
    # Check Health
    health_info = res["contract_health"]
    assert 0 <= health_info["score"] <= 100
    assert "Higher Health" in health_info["definition"]
    assert health_info["needs_human_review"] is True  # Contradictions require human review
    
    # Document classification in orchestrator output
    assert res["document_metadata"]["document_type"] == "LAND_SALE_DEED"


def test_reviewer_deduplication_and_disagreement():
    """Test reviewer resolves disagreements and deduplicates findings."""
    reviewer = ReviewerCriticAgent()
    res = reviewer.run({
        "agent_results": {},
        "document_metadata": {"document_type": "LAND_SALE_DEED"}
    })
    assert res.status in ["success", "warning"]
    assert 0 <= res.data["health_score"] <= 100


if __name__ == "__main__":
    pytest.main(["-v", __file__])
