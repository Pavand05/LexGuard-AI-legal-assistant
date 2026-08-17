"""
Missing Clause Intelligence Agent (LexGuard-MA)
Performs canonical gap analysis by comparing:
expected_canonical_ids (from domain playbook) vs detected_canonical_ids (from Clause Agent).
Eliminates false-positive missing clause findings caused by literal string mismatches.
"""
from typing import Dict, Any, List, Set
from .base_agent import BaseAgent, AgentResult, AgentFindingModel
from .clause_taxonomy import CANONICAL_CLAUSE_DEFINITIONS, normalize_to_canonical_id
from .playbooks import resolve_domain_playbook, DomainPlaybook


class MissingClauseIntelligenceAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Missing Clause Agent",
            description="Performs canonical playbook gap analysis to detect genuinely absent protective provisions.",
            capabilities=["canonical_gap_analysis", "playbook_verification", "completeness_audit"]
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        doc_type = context.get("document_type", "OTHER_LEGAL_DOCUMENT")
        detected_domains = context.get("detected_domains", ["GENERAL_COMMERCIAL"])
        clauses = context.get("clauses", [])
        
        # 1. Resolve domain playbook and expected canonical IDs
        playbook: DomainPlaybook = resolve_domain_playbook(doc_type, detected_domains)
        expected_canonical_ids: List[str] = list(playbook.expected_canonical_ids)
        
        # 2. Extract detected canonical IDs from clauses
        detected_canonical_ids: Set[str] = set()
        for c in clauses:
            # Check explicit canonical_id field
            cid = c.get("canonical_id")
            if cid and cid in CANONICAL_CLAUSE_DEFINITIONS:
                detected_canonical_ids.add(cid)
            else:
                # Normalize category or type
                norm_cid = normalize_to_canonical_id(c.get("category") or c.get("type") or c.get("heading"))
                if norm_cid:
                    detected_canonical_ids.add(norm_cid)

        # 3. Canonical Set Difference
        missing_canonical_ids = [cid for cid in expected_canonical_ids if cid not in detected_canonical_ids]
        missing_display_names = [
            CANONICAL_CLAUSE_DEFINITIONS.get(cid, {}).get("display", cid)
            for cid in missing_canonical_ids
        ]
        
        findings: List[AgentFindingModel] = []

        for cid in missing_canonical_ids:
            defn = CANONICAL_CLAUSE_DEFINITIONS.get(cid, {})
            display_name = defn.get("display", cid)
            dimension = defn.get("dimension", "Legal")
            
            findings.append(AgentFindingModel(
                id=f"missing-{len(findings)+1}",
                agent="Missing Clause Agent",
                dimension=dimension,
                category="Missing Clause Gap",
                severity="MEDIUM",
                risk_score=45,
                clause_type=f"Missing: {display_name}",
                clause_text=f"Standard expected provision '{display_name}' ({cid}) was not detected in this {playbook.display_name} ({doc_type}).",
                page_number=1,
                evidence=f"Canonical scan: {cid} was not detected across {len(detected_canonical_ids)} present canonical categories.",
                claim=f"Document omits explicit '{display_name}' section.",
                reason=f"Standard contracting practice under the {playbook.display_name} playbook includes explicit '{display_name}' covenants to prevent statutory ambiguity.",
                recommendation=f"Incorporate standard '{display_name}' provision outlining clear rights and default remedies.",
                source_type="AI_INFERENCE",
                verification_status="TEXT_SUPPORTED",
                confidence=0.91
            ))

        if not missing_canonical_ids:
            findings.append(AgentFindingModel(
                id="missing-clean-01",
                agent="Missing Clause Agent",
                dimension="Legal",
                category="Playbook Completeness",
                severity="INFORMATIONAL",
                risk_score=10,
                clause_type="Playbook Completeness",
                clause_text=f"All {len(expected_canonical_ids)} expected standard provisions for {playbook.display_name} are present.",
                page_number=1,
                evidence=f"Complete canonical match across all expected categories: {', '.join(expected_canonical_ids)}.",
                claim="Document satisfies standard structural completeness.",
                reason="Document contains all core expected boilerplate and substantive clauses for this domain.",
                recommendation="Review individual clause wording for balanced mutual terms.",
                source_type="AI_INFERENCE",
                verification_status="TEXT_SUPPORTED",
                confidence=0.94
            ))

        total_expected = max(1, len(expected_canonical_ids))
        completeness_pct = int(100 * (total_expected - len(missing_canonical_ids)) / total_expected)

        return AgentResult(
            agent_name=self.name,
            status="success",
            confidence=0.92,
            summary=f"Playbook completeness for {playbook.display_name}: {completeness_pct}% ({len(missing_canonical_ids)} missing clause(s)).",
            findings=findings,
            data={
                "doc_type": doc_type,
                "playbook_domain": playbook.domain_name,
                "completeness_pct": completeness_pct,
                "missing_clauses": missing_display_names,
                "missing_canonical_ids": missing_canonical_ids,
                "expected_canonical_ids": expected_canonical_ids,
                "expected_clauses": playbook.expected_clause_categories,
                "detected_canonical_ids": list(detected_canonical_ids)
            }
        )
