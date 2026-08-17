"""
Missing Clause Intelligence Agent
Evaluates contract completeness against industry-standard legal playbooks for specific contract types.
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult, AgentFindingModel


class MissingClauseIntelligenceAgent(BaseAgent):
    CONTRACT_PLAYBOOKS = {
        "Non-Disclosure Agreement (NDA)": [
            "Confidentiality", "Dispute Resolution & Arbitration", "Governing Law & Jurisdiction", "Termination", "Intellectual Property"
        ],
        "Employment Agreement": [
            "Termination", "Payment & Invoicing", "Confidentiality", "Governing Law & Jurisdiction", "Intellectual Property", "Non-Solicitation"
        ],
        "Commercial Contract": [
            "Liability", "Termination", "Payment & Invoicing", "Governing Law & Jurisdiction", "Dispute Resolution & Arbitration", "Force Majeure", "Warranties & Representations"
        ],
        "Master Services Agreement (MSA)": [
            "Liability", "Termination", "Payment & Invoicing", "Intellectual Property", "Confidentiality", "SLA & Service Credits", "Governing Law & Jurisdiction"
        ],
        "Lease & Tenancy Agreement": [
            "Payment & Invoicing", "Termination", "Governing Law & Jurisdiction", "Force Majeure", "Notices & Formal Communications"
        ],
        "Software License / SaaS Agreement": [
            "Intellectual Property", "Liability", "Termination", "Data Protection & Privacy", "SLA & Service Credits", "Governing Law & Jurisdiction"
        ]
    }

    def __init__(self):
        super().__init__(
            name="Missing Clause Agent",
            description="Checks contract against standard playbooks to detect missing protective provisions.",
            capabilities=["gap_analysis", "playbook_verification", "completeness_audit"]
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        doc_type = context.get("document_type", "Commercial Contract")
        clauses = context.get("clauses", [])
        
        present_types = set(c.get("type", "") for c in clauses)
        expected = self.CONTRACT_PLAYBOOKS.get(doc_type, self.CONTRACT_PLAYBOOKS["Commercial Contract"])
        
        missing = [req for req in expected if req not in present_types]
        findings = []

        for m in missing:
            findings.append(AgentFindingModel(
                dimension="Legal",
                risk_level="MEDIUM",
                risk_score=50,
                clause_type=f"Missing: {m}",
                clause_text=f"Standard expected clause '{m}' was not detected in this {doc_type}.",
                page_number=1,
                reason=f"Standard practice for a {doc_type} includes explicit '{m}' terms to avoid statutory ambiguity or default common law rules.",
                recommendation=f"Add an explicit '{m}' section outlining reciprocal rights, obligations, and limitations.",
                citation_status="SUPPORTED",
                confidence=0.88
            ))

        if not missing:
            findings.append(AgentFindingModel(
                dimension="Legal",
                risk_level="LOW",
                risk_score=10,
                clause_type="Playbook Completeness",
                clause_text=f"All key standard provisions for {doc_type} are present.",
                page_number=1,
                reason="Document contains all core expected boilerplate and substantive clauses.",
                recommendation="Review individual clauses for balanced mutual terms.",
                citation_status="SUPPORTED",
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
