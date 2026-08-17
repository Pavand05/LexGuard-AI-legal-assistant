"""
Missing Clause Intelligence Agent
Dynamically evaluates contract completeness against domain playbooks:
Real Estate, Employment, NDAs, SaaS/IP, Privacy/DPA, Corporate/SHA, Commercial Supply, and Open-Set Documents.
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult, AgentFindingModel
from .playbooks import resolve_domain_playbook, DomainPlaybook


class MissingClauseIntelligenceAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Missing Clause Agent",
            description="Checks document completeness against dynamic domain playbooks to detect missing protective provisions and structural gaps.",
            capabilities=["gap_analysis", "playbook_verification", "completeness_audit"]
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        doc_type = context.get("document_type", "OTHER_LEGAL_DOCUMENT")
        detected_domains = context.get("detected_domains", [])
        clauses = context.get("clauses", [])
        
        # Dynamically resolve playbook for this document type / domain
        playbook: DomainPlaybook = resolve_domain_playbook(doc_type, detected_domains)
        expected = playbook.expected_clause_categories
        
        present_categories = set(c.get("category", c.get("type", "")) for c in clauses)
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
                clause_text=f"Standard expected provision '{m}' was not detected in this {playbook.display_name} ({doc_type}).",
                page_number=1,
                evidence=f"Clause inventory scan against {playbook.domain_name} completeness playbook.",
                claim=f"Document omits explicit '{m}' section.",
                reason=f"Standard contracting / conveyancing practice under the {playbook.display_name} playbook includes explicit '{m}' terms to avoid default statutory ambiguities.",
                recommendation=f"Incorporate standard '{m}' provision outlining clear reciprocal rights, warranties, and default remedies.",
                source_type="AI_INFERENCE",
                verification_status="TEXT_SUPPORTED",
                confidence=0.89
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
                clause_text=f"All key standard provisions for {playbook.display_name} are present.",
                page_number=1,
                evidence=f"Complete match across all {len(expected)} expected categories.",
                claim="Document satisfies standard structural completeness.",
                reason="Document contains all core expected boilerplate and substantive clauses for this domain.",
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
            summary=f"Playbook completeness for {playbook.display_name}: {completeness_pct}% ({len(missing)} missing clause(s)).",
            findings=findings,
            data={
                "doc_type": doc_type,
                "playbook_domain": playbook.domain_name,
                "completeness_pct": completeness_pct,
                "missing_clauses": missing,
                "expected_clauses": expected
            }
        )
