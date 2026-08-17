"""
Dynamic Agent Routing Layer (LexGuard-MA)
Selects universal and domain-specialist agents dynamically based on:
- Document Type & Classification Confidence
- Detected Legal Domains
- Governing Jurisdiction
- Extracted Clauses & Privacy Sensitivity
"""
from typing import Dict, Any, List, Set
from .playbooks import resolve_domain_playbook, DomainPlaybook, GENERAL_PLAYBOOK


class AgentRouter:
    # Universal agents that run for every legal document
    UNIVERSAL_AGENTS = [
        "Document Intelligence Agent",
        "Clause Intelligence Agent",
        "Contradiction Agent",
        "Risk Assessment Agent",
        "Missing Clause Agent",
        "Legal Research Agent",
        "Citation Verification Agent",
        "Reviewer Agent"
    ]

    @staticmethod
    def route_agents(
        document_type: str,
        detected_domains: List[str] = None,
        jurisdiction: str = "India",
        clauses: List[Dict[str, Any]] = None,
        privacy_mode: bool = False,
        confidence: float = 0.90
    ) -> Dict[str, Any]:
        """
        Dynamically determine the active agent pipeline, playbook, and risk dimensions.
        """
        playbook: DomainPlaybook = resolve_domain_playbook(document_type, detected_domains)
        clauses = clauses or []
        clause_types = set(c.get("type", "") for c in clauses)
        
        active_agents: List[str] = list(AgentRouter.UNIVERSAL_AGENTS)
        active_dimensions: List[str] = list(playbook.applicable_risk_dimensions)
        specialist_modules: List[str] = []

        # 1. Privacy & PII Protection Agent
        needs_privacy = (
            privacy_mode or
            playbook.domain_name in ["DATA_PRIVACY", "EMPLOYMENT_LABOR"] or
            any("Data Protection" in ct or "Privacy" in ct or "Confidential" in ct for ct in clause_types) or
            document_type in ["DATA_PROCESSING_AGREEMENT", "DPA", "PRIVACY_POLICY"]
        )
        if needs_privacy and "Privacy & PII Agent" not in active_agents:
            active_agents.append("Privacy & PII Agent")
            specialist_modules.append("PII Masking & DPDP Safeguards")
            if "Privacy" not in active_dimensions:
                active_dimensions.append("Privacy")

        # 2. Compliance Intelligence Agent
        needs_compliance = (
            "Compliance Agent" in playbook.applicable_specialist_agents or
            len(playbook.relevant_research_acts) > 0 or
            any("Non-Compete" in ct or "Registration" in ct or "Restraint" in ct for ct in clause_types)
        )
        if needs_compliance and "Compliance Agent" not in active_agents:
            active_agents.append("Compliance Agent")
            specialist_modules.append(f"Statutory Audit ({', '.join(playbook.relevant_research_acts[:2])})")
            if "Compliance" not in active_dimensions:
                active_dimensions.append("Compliance")

        # 3. Obligation Extraction Agent
        # Runs for all transactional/bilateral contracts with party commitments
        is_unilateral_policy = document_type in ["PRIVACY_POLICY", "TERMS_OF_SERVICE", "LEGAL_DECLARATION"]
        if not is_unilateral_policy and "Obligation Extraction Agent" not in active_agents:
            active_agents.append("Obligation Extraction Agent")
            specialist_modules.append("Party-wise Duty & Deadline Tracking")

        # 4. Negotiation & Redlining Agents
        # Active when commercial clauses require bilateral negotiation
        has_negotiable_clauses = any(
            c.get("risk") in ["high", "medium"] or
            c.get("dimension") in ["Financial", "Legal", "Operational"]
            for c in clauses
        )
        if has_negotiable_clauses and not is_unilateral_policy:
            if "Negotiation Agent" not in active_agents:
                active_agents.append("Negotiation Agent")
                specialist_modules.append("Strategic Concession & Fallback Playbook")
            if "Redlining Agent" not in active_agents:
                active_agents.append("Redlining Agent")
                specialist_modules.append("Tracked Changes & Word-level Visual Diff")

        # 5. Open-set / Unknown Document Routing
        is_unknown = document_type in ["OTHER_LEGAL_DOCUMENT", "OTHER"] or confidence < 0.50
        if is_unknown:
            specialist_modules.append("Universal Baseline Analysis (Open-Set Fallback)")

        return {
            "playbook_domain": playbook.domain_name,
            "playbook_display": playbook.display_name,
            "active_agents": active_agents,
            "applicable_risk_dimensions": active_dimensions,
            "specialist_modules": specialist_modules,
            "expected_clauses": playbook.expected_clause_categories,
            "relevant_acts": playbook.relevant_research_acts,
            "is_unknown_type": is_unknown
        }
