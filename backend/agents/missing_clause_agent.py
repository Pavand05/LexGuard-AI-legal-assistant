"""
Missing Clause Intelligence Agent
Evaluates contract completeness against industry-standard legal playbooks for specific contract types,
including Land Sale Deeds, Agreements to Sell, Leases, NDAs, Employment, SaaS, and DPAs.
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult, AgentFindingModel


class MissingClauseIntelligenceAgent(BaseAgent):
    CONTRACT_PLAYBOOKS = {
        "LAND_SALE_DEED": [
            "Title & Ownership",
            "Consideration & Payment",
            "Encumbrance & Mortgage",
            "Possession",
            "Property Description & Schedule",
            "Registration & Stamp Duty",
            "Indemnity & Liability",
            "Taxes & Outgoings",
            "Dispute Resolution & Jurisdiction"
        ],
        "LAND_SALE_AGREEMENT": [
            "Title & Ownership",
            "Consideration & Payment",
            "Default & Forfeiture",
            "Property Description & Schedule",
            "Encumbrance & Mortgage",
            "Dispute Resolution & Jurisdiction"
        ],
        "COMMERCIAL_LEASE": [
            "Consideration & Payment",
            "Termination",
            "Possession",
            "Taxes & Outgoings",
            "Force Majeure",
            "Dispute Resolution & Jurisdiction",
            "Notices & Formal Communications"
        ],
        "NDA": [
            "Confidentiality",
            "Termination",
            "Governing Law & Jurisdiction",
            "Dispute Resolution & Arbitration"
        ],
        "EMPLOYMENT_AGREEMENT": [
            "Termination",
            "Consideration & Payment",
            "Confidentiality",
            "Representations & Warranties",
            "Governing Law & Jurisdiction",
            "Non-Solicitation"
        ],
        "VENDOR_AGREEMENT": [
            "Consideration & Payment",
            "Indemnity & Liability",
            "Termination",
            "Representations & Warranties",
            "Force Majeure",
            "Dispute Resolution & Arbitration"
        ],
        "SERVICE_AGREEMENT": [
            "Consideration & Payment",
            "Indemnity & Liability",
            "Termination",
            "Confidentiality",
            "Intellectual Property",
            "Dispute Resolution & Arbitration"
        ],
        "DPA": [
            "Data Protection & Privacy",
            "Confidentiality",
            "Termination",
            "Dispute Resolution & Arbitration"
        ],
        "OTHER": [
            "Consideration & Payment",
            "Indemnity & Liability",
            "Termination",
            "Governing Law & Jurisdiction",
            "Dispute Resolution & Arbitration"
        ]
    }

    def __init__(self):
        super().__init__(
            name="Missing Clause Agent",
            description="Checks contract against standard playbooks to detect missing protective provisions and completeness gaps.",
            capabilities=["gap_analysis", "playbook_verification", "completeness_audit"]
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        doc_type = context.get("document_type", "OTHER")
        clauses = context.get("clauses", [])
        
        present_categories = set(c.get("category", c.get("type", "")) for c in clauses)
        expected = self.CONTRACT_PLAYBOOKS.get(doc_type, self.CONTRACT_PLAYBOOKS["OTHER"])
        
        missing = [req for req in expected if req not in present_categories]
        findings: List[AgentFindingModel] = []

        for m in missing:
            findings.append(AgentFindingModel(
                id=f"missing-{len(findings)+1}",
                agent="Missing Clause Agent",
                dimension="Legal",
                category="Missing Clause Gap",
                severity="MEDIUM",
                risk_score=45,
                clause_type=f"Missing: {m}",
                clause_text=f"Standard expected provision '{m}' was not detected in this {doc_type}.",
                page_number=1,
                evidence=f"Clause inventory scan against {doc_type} completeness playbook.",
                claim=f"Document omits explicit '{m}' section.",
                reason=f"Standard conveyancing / contracting practice for a {doc_type} includes explicit '{m}' terms to prevent statutory ambiguity or common law default rules.",
                recommendation=f"Incorporate standard '{m}' provision outlining clear rights, warranties, and default remedies.",
                source_type="AI_INFERENCE",
                verification_status="TEXT_SUPPORTED",
                confidence=0.88
            ))

        if not missing:
            findings.append(AgentFindingModel(
                id="missing-clean-01",
                agent="Missing Clause Agent",
                dimension="Legal",
                category="Playbook Completeness",
                severity="INFORMATIONAL",
                risk_score=10,
                clause_type="Playbook Completeness",
                clause_text=f"All key standard provisions for {doc_type} are present.",
                page_number=1,
                evidence=f"Complete match across all {len(expected)} expected categories.",
                claim="Document satisfies standard structural completeness.",
                reason="Document contains all core expected boilerplate and substantive clauses.",
                recommendation="Review individual clause wording for balanced mutual terms.",
                source_type="AI_INFERENCE",
                verification_status="TEXT_SUPPORTED",
                confidence=0.92
            ))

        completeness_pct = int(100 * (len(expected) - len(missing)) / max(1, len(expected)))

        return AgentResult(
            agent_name=self.name,
            status="success",
            confidence=0.90,
            summary=f"Playbook completeness for {doc_type}: {completeness_pct}% ({len(missing)} missing clause(s)).",
            findings=findings,
            data={"doc_type": doc_type, "completeness_pct": completeness_pct, "missing_clauses": missing}
        )
