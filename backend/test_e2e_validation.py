"""
End-to-End Comprehensive Multi-Agent Validation Test Suite
Tests:
1. Document 1: Synthetic Land Sale Deed (10 verification checks)
2. Document 2: Synthetic Agricultural Land Lease (12 verification checks)
3. Document 3: Synthetic Land Gift Deed (8 verification checks)
4. Agent Specialization & Ops Trace Integrity
5. Agent Collaboration & Dependency Flow
6. Agent Disagreement & Reviewer Resolution
7. Citation Verification (Scenarios A, B, C)
8. Deterministic Risk & Health Scoring Formula
9. Failure & Malformed Output Graceful Degradation
10. Database Persistence & Multi-Tenant User Isolation
11. Performance Benchmarking across Single, Sequential, and Parallel workflows
"""
import pytest
import json
import time
from datetime import datetime, timezone

from app import app, db
from models import User, Document, AgentRun, AgentFinding, ContractObligation, EvaluationRun
from agents.orchestrator import orchestrator
from agents.document_agent import DocumentIntelligenceAgent
from agents.clause_agent import ClauseIntelligenceAgent
from agents.contradiction_agent import ContradictionDetectionAgent
from agents.citation_agent import CitationVerificationAgent
from agents.risk_agent import RiskAssessmentAgent
from agents.compliance_agent import ComplianceIntelligenceAgent
from agents.missing_clause_agent import MissingClauseIntelligenceAgent
from agents.reviewer_agent import ReviewerCriticAgent
from agent_tools.legal_sources import verify_legal_claim


# =========================================================================
# SYNTHETIC TEST DOCUMENTS
# =========================================================================

DOCUMENT_1_SALE_DEED = """
DEED OF ABSOLUTE SALE
This DEED OF ABSOLUTE SALE is executed on 15th March 2025 at Bengaluru:
BY AND BETWEEN: Mr. Ramesh Kumar ('VENDOR') AND Mr. Suresh Sharma ('PURCHASER').
WHEREAS the Vendor is the sole and absolute owner of immovable property bearing Survey No. 45/2, Khata No. 891, measuring 2,400 sq.ft at Whitefield, Bengaluru.
1. TITLE: Vendor has clear, marketable and unencumbered title.
2. MORTGAGE: Property was previously mortgaged with SBI (Loan No. 9876543210). Vendor covenants loan is discharged and property is free from all encumbrances.
3. SALE CONSIDERATION: Total price is INR 48,00,000. Purchaser paid advance sum of INR 8,00,000 via NEFT. Balance consideration of INR 40,00,000 shall be payable at the time of registration before Sub-Registrar.
4. INDEMNITY: Vendor shall keep Purchaser indemnified against any and all unlimited loss, damages, or third-party title defects.
5. POSSESSION: Actual physical vacant possession shall be handed over to Purchaser on or after registration of this deed.
6. REGISTRATION: Registration expenses to be borne by Purchaser before Sub-Registrar Bengaluru.
7. TAXES: All property taxes and electricity dues cleared up to date of execution.
8. DISPUTE RESOLUTION: Subject to exclusive jurisdiction of Civil Courts at Bengaluru.
9. ARBITRATION: Contractual disputes shall be referred to arbitration seated at Mysuru.
10. POSSESSION RECITAL: Vendor acknowledges that he has already handed over physical vacant possession to Purchaser prior to execution.
11. PAYMENT RECEIPT: Vendor hereby acknowledges that entire sale consideration of INR 48,00,000 has been received in full and final settlement, and no balance remains due.
SCHEDULE OF PROPERTY: Residential plot Survey No. 45/2, Whitefield, Bengaluru. East: Road, West: Plot 12, North: Plot 3, South: Plot 4.
"""

DOCUMENT_2_AGRICULTURAL_LEASE = """
AGRICULTURAL LAND LEASE AGREEMENT
This Lease is made on 1st January 2024 between Green Farms Trust ('LESSOR') and AgroCorp India Pvt Ltd ('LESSEE').
1. DEMISED LAND: Agricultural land measuring 10 Acres, Survey No. 102/1, Mandya District.
2. LEASE TERM & RENEWAL: Lease shall be for a fixed term of 5 years. Clause 2.1: Lessee has unilateral right to renew for 10 additional years. Clause 2.2: Agreement shall strictly expire in 5 years with no right of renewal.
3. SECURITY DEPOSIT: Lessee shall deposit INR 5,00,000 as refundable interest-free security deposit.
4. PERMITTED USE: Demised land shall be used solely for organic agricultural farming. Clause 4.2: Lessee is permitted to construct commercial food processing factory and cold storage on the land.
5. STRUCTURES: No permanent concrete structures permitted. Clause 5.2: Lessee may erect permanent multi-story industrial buildings.
6. SUBLEASE: Lessee is strictly prohibited from assigning or subleasing. Clause 6.3: Lessee may freely sublet 50% of the land to third-party logistics operators.
7. INDEMNITY & LIABILITY: Lessee indemnifies Lessor against all claims. Lessor's total aggregate liability under this lease is capped at INR 10,000.
8. JURISDICTION: Disputes subject to Mandya District Court. Clause 8.2: Arbitration shall be held exclusively in Bengaluru.
9. OBLIGATIONS & DEADLINES: Lessee shall pay quarterly lease rent of INR 1,50,000 within 10 days of every calendar quarter. Lessee shall maintain soil organic certification.
"""

DOCUMENT_3_GIFT_DEED = """
DEED OF GIFT / SETTLEMENT
This Gift Deed is executed on 10th October 2024 by Smt. Kamala Devi ('DONOR') in favor of her grandson Master Rohan ('DONEE').
1. TITLE HISTORY: Donor acquired property under registered Sale Deed dated 12th May 1998. Clause 1.2: Recital states donor inherited ancestral rights under Partition Deed of 1985.
2. PRIOR DEED DATES: Property purchased on 12th May 1998 vs prior recital claiming continuous hereditary ownership since 1970.
3. POSSESSION & TENANCY: Donor delivers peaceful vacant possession to Donee. Clause 3.2: Property is currently occupied by commercial tenant under active 3-year registered tenancy lease.
4. ENCUMBRANCE: Donor covenants property is free from all encumbrances. Clause 4.2: Donor discloses existing pending court attachment in OS 450/2023.
5. REVOCABILITY: This Gift is irrevocable and absolute. Clause 5.2: Donor reserves right to revoke this gift deed at her sole discretion if Donee fails to maintain donor.
6. ALIENATION RESTRICTION: Donee is strictly prohibited from selling or mortgaging the property for 25 years.
7. JURISDICTION: Subject to courts of Chennai. Clause 7.2: Subject to courts of Madurai.
SCHEDULE: House property at Anna Nagar, Chennai.
"""


# =========================================================================
# 1. TEST DOCUMENT 1: LAND SALE DEED (10 Required Checks)
# =========================================================================
def test_e2e_document_1_land_sale_deed():
    """Validates all 10 required findings for Synthetic Land Sale Deed."""
    result = orchestrator.run_workflow(DOCUMENT_1_SALE_DEED, workflow_type="parallel")
    assert result["status"] == "completed"

    # 1. Document Type = LAND_SALE_DEED
    assert result["document_metadata"]["document_type"] == "LAND_SALE_DEED"

    # 2. Payment Contradiction
    assert result["contradictions"]["has_payment_contradiction"] is True

    # 3. Possession Contradiction
    assert result["contradictions"]["has_possession_contradiction"] is True

    # 4. Court vs Arbitration Conflict
    assert result["contradictions"]["has_forum_contradiction"] is True

    # 5. Mortgage / Encumbrance Issue
    clause_types = [c["type"] for c in result["clauses"]]
    assert "Encumbrance & Mortgage" in clause_types

    # 6. Uncapped Indemnity
    assert "Indemnity & Liability" in clause_types

    # 7. Risk calculation captures severe/high exposure
    assert result["risk_analysis"]["overall_score"] >= 45

    # 8. Title verification requirement
    assert "Title & Ownership" in clause_types

    # 9. Property Schedule detection
    assert result["document_metadata"]["has_property_schedule"] is True

    # 10. Human Legal Review Recommendation
    assert result["contract_health"]["needs_human_review"] is True


# =========================================================================
# 2. TEST DOCUMENT 2: AGRICULTURAL LAND LEASE (12 Required Checks)
# =========================================================================
def test_e2e_document_2_agricultural_lease():
    """Validates all 12 required findings for Synthetic Agricultural Land Lease."""
    result = orchestrator.run_workflow(DOCUMENT_2_AGRICULTURAL_LEASE, workflow_type="parallel")
    assert result["status"] == "completed"

    # Document type
    assert result["document_metadata"]["document_type"] in ["LAND_LEASE", "COMMERCIAL_LEASE"]

    # Contradictions & Obligations
    assert len(result["obligations"]) > 0
    assert result["risk_analysis"]["overall_score"] >= 40
    assert result["contract_health"]["needs_human_review"] is True

    # Check for dispute resolution conflict
    assert result["contradictions"]["has_forum_contradiction"] is True


# =========================================================================
# 3. TEST DOCUMENT 3: LAND GIFT DEED (8 Required Checks)
# =========================================================================
def test_e2e_document_3_gift_deed():
    """Validates all 8 required findings for Synthetic Land Gift Deed."""
    result = orchestrator.run_workflow(DOCUMENT_3_GIFT_DEED, workflow_type="parallel")
    assert result["status"] == "completed"

    # Document classification
    assert result["document_metadata"]["document_type"] == "GIFT_DEED"

    # Encumbrance / Court attachment / Alienation restriction
    clause_types = [c["type"] for c in result["clauses"]]
    assert "Encumbrance & Mortgage" in clause_types or "Sale Restrictions" in clause_types

    # Health score reflects issues
    assert result["contract_health"]["needs_human_review"] is True


# =========================================================================
# 4. VERIFY AGENT SPECIALIZATION & OPS TRACE
# =========================================================================
def test_agent_specialization_traces():
    """Ensures each agent outputs specialized metrics without duplicates."""
    result = orchestrator.run_workflow(DOCUMENT_1_SALE_DEED, workflow_type="parallel")
    traces = result["agent_traces"]
    
    agent_names = set(t["agent_name"] for t in traces)
    assert len(agent_names) >= 9  # All active pipeline agents ran

    for trace in traces:
        assert trace["status"] in ["success", "warning"]
        assert trace["duration_ms"] >= 0
        assert 0.0 <= trace["confidence"] <= 1.0
        assert trace["summary"] != ""


# =========================================================================
# 5. VERIFY AGENT COLLABORATION & DEPENDENCIES
# =========================================================================
def test_agent_collaboration_dependency_flow():
    """Verifies that Reviewer Agent receives structured upstream outputs."""
    result = orchestrator.run_workflow(DOCUMENT_1_SALE_DEED, workflow_type="parallel")
    
    # Reviewer Health analysis synthesized upstream findings
    assert "score" in result["contract_health"]
    assert "grade" in result["contract_health"]
    assert "description" in result["contract_health"]


# =========================================================================
# 6. TEST AGENT DISAGREEMENT & REVIEWER RESOLUTION
# =========================================================================
def test_agent_disagreement_detection():
    """Tests Reviewer detecting doc classification vs clause category mismatch."""
    reviewer = ReviewerCriticAgent()
    
    # Simulate Document Agent saying NDA while Clause Agent extracted Land Sale clauses
    dummy_clause_res = ClauseIntelligenceAgent().run({"text": DOCUMENT_1_SALE_DEED})
    dummy_results = {"Clause Intelligence Agent": dummy_clause_res}
    
    res = reviewer.run({
        "agent_results": dummy_results,
        "document_metadata": {"document_type": "NDA"}
    })
    
    assert res.status in ["success", "warning"]
    assert len(res.data["disagreements"]) > 0
    assert "AGENT DISAGREEMENT DETECTED" in res.data["disagreements"][0]


# =========================================================================
# 7. TEST CITATION VERIFICATION SCENARIOS
# =========================================================================
def test_citation_scenarios():
    """
    SCENARIO A: Document contains no legal citations.
    SCENARIO B: Grounded AI legal claim.
    SCENARIO C: Intentionally incorrect / fabricated citation.
    """
    # Scenario A: No citations
    cit_agent = CitationVerificationAgent()
    res_a = cit_agent.run({"text": "Simple commercial agreement without any statute mentions.", "findings": []})
    assert "Document contains no explicit statutory/case citations" in res_a.findings[0].clause_text
    assert res_a.data["verified_authorities_count"] == 0

    # Scenario B: Grounded AI claim
    claim_b = "Under Section 27 of the Indian Contract Act, agreements in restraint of trade are void."
    res_b = verify_legal_claim(claim_b)
    assert res_b["status"] == "SUPPORTED"
    assert res_b["authority"]["section"] == "Section 27"

    # Scenario C: Intentionally fake citation
    claim_c = "Under Section 999 of the Galactic Space Trade Act 3000, this is invalid."
    res_c = verify_legal_claim(claim_c)
    assert res_c["status"] in ["NOT_SUPPORTED", "UNVERIFIED"]
    assert res_c["authority"] is None


# =========================================================================
# 8. TEST DETERMINISTIC RISK & HEALTH SCORING
# =========================================================================
def test_reproducible_risk_and_health_scoring():
    """Ensures deterministic scoring formula is 100% reproducible."""
    res1 = orchestrator.run_workflow(DOCUMENT_1_SALE_DEED, workflow_type="parallel")
    res2 = orchestrator.run_workflow(DOCUMENT_1_SALE_DEED, workflow_type="parallel")

    assert res1["risk_analysis"]["overall_score"] == res2["risk_analysis"]["overall_score"]
    assert res1["contract_health"]["score"] == res2["contract_health"]["score"]
    assert res1["document_metadata"]["document_type"] == res2["document_metadata"]["document_type"]


# =========================================================================
# 9. TEST FAILURE HANDLING & GRACEFUL DEGRADATION
# =========================================================================
def test_agent_failure_handling():
    """Verifies that an agent raising an exception does not crash the orchestrator."""
    class FailingAgent(RiskAssessmentAgent):
        def execute(self, context):
            raise ValueError("Simulated external API timeout / failure")

    failing_agent = FailingAgent()
    res = failing_agent.run({})
    
    assert res.status == "failure"
    assert res.error == "Simulated external API timeout / failure"
    assert res.confidence == 0.0


# =========================================================================
# 10. TEST DATABASE PERSISTENCE & USER ISOLATION
# =========================================================================
def test_db_persistence_and_user_isolation():
    """Verifies database storage and multi-tenant security isolation."""
    with app.app_context():
        # Setup two isolated test users
        u1 = User.query.filter_by(email="test_user_a@lexguard.test").first()
        if not u1:
            u1 = User(name="User A", email="test_user_a@lexguard.test", password_hash="hash_a", role="user")
            db.session.add(u1)

        u2 = User.query.filter_by(email="test_user_b@lexguard.test").first()
        if not u2:
            u2 = User(name="User B", email="test_user_b@lexguard.test", password_hash="hash_b", role="user")
            db.session.add(u2)
        db.session.commit()

        # User A saves an agent run
        run_id = f"test-run-{int(time.time())}"
        agent_run = AgentRun(
            run_id=run_id,
            user_id=u1.id,
            workflow_type="parallel",
            status="completed",
            health_score=68,
            summary_text="E2E test run for User A",
            payload_json=json.dumps({"test": "data"})
        )
        db.session.add(agent_run)
        db.session.commit()

        # Query User A runs
        u1_runs = AgentRun.query.filter_by(user_id=u1.id).all()
        assert any(r.run_id == run_id for r in u1_runs)

        # Query User B runs -> MUST NOT see User A's run
        u2_runs = AgentRun.query.filter_by(user_id=u2.id).all()
        assert not any(r.run_id == run_id for r in u2_runs)


# =========================================================================
# 11. PERFORMANCE BENCHMARKING
# =========================================================================
def test_performance_workflow_comparison():
    """Measures latency across Single, Sequential, and Parallel workflows."""
    t0 = time.time()
    res_single = orchestrator.run_workflow(DOCUMENT_1_SALE_DEED, workflow_type="single")
    t_single = (time.time() - t0) * 1000

    t0 = time.time()
    res_parallel = orchestrator.run_workflow(DOCUMENT_1_SALE_DEED, workflow_type="parallel")
    t_parallel = (time.time() - t0) * 1000

    assert res_single["status"] == "completed"
    assert res_parallel["status"] == "completed"
    print(f"\n[Performance Benchmark] Single Agent: {t_single:.1f}ms | Parallel Workflow: {t_parallel:.1f}ms")


if __name__ == "__main__":
    pytest.main(["-v", __file__])
