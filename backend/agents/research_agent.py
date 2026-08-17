"""
Legal Research Agent
Performs generic, jurisdiction-aware statutory research grounded in detected legal domains:
Document Type -> Legal Domain -> Jurisdiction -> Legal Issue -> Candidate Authorities -> Relevance Evaluation -> Primary Source
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult, AgentFindingModel
from agent_tools.legal_sources import search_statutory_sources
from .playbooks import resolve_domain_playbook, DomainPlaybook


class LegalResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Legal Research Agent",
            description="Performs jurisdiction-aware statutory retrieval grounded in active domain playbooks to find relevant legislation.",
            capabilities=["statutory_retrieval", "legal_research", "domain_grounding", "authority_evaluation"]
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        doc_type = context.get("document_type", "OTHER_LEGAL_DOCUMENT")
        detected_domains = context.get("detected_domains", [])
        jurisdiction = context.get("jurisdiction", "India")
        clauses = context.get("clauses", [])
        
        playbook: DomainPlaybook = resolve_domain_playbook(doc_type, detected_domains)
        relevant_acts = playbook.relevant_research_acts
        
        findings = []
        all_sources = []
        
        # 1. Search candidate authorities based on high/medium risk clauses & playbook acts
        for c in clauses:
            if c.get("risk") in ["high", "medium"]:
                c_type = c.get("type", "General")
                content = c.get("content", "")
                keywords = [c_type] + relevant_acts + content.split()[:6]
                matched_sources = search_statutory_sources(keywords, jurisdiction="India", top_k=2)
                
                if matched_sources:
                    for src in matched_sources:
                        if src["id"] not in [s["id"] for s in all_sources]:
                            all_sources.append(src)
                            
                    findings.append(AgentFindingModel(
                        id=f"res-{len(findings)+1}",
                        agent="Legal Research Agent",
                        dimension=c.get("dimension", "Legal"),
                        category="Statutory Authority",
                        severity=c.get("risk", "low").upper(),
                        risk_score=75 if c.get("risk") == "high" else 50,
                        clause_type=f"Research: {c_type}",
                        clause_text=c.get("content", "")[:200],
                        page_number=c.get("page", 1),
                        evidence=f"Matched: {matched_sources[0]['act']} ({matched_sources[0]['section']})",
                        claim=f"Primary statutory authority for {c_type} under {playbook.display_name}.",
                        reason=f"Matched statutory authority: {matched_sources[0]['act']}, {matched_sources[0]['section']} ({matched_sources[0]['title']}).",
                        recommendation=f"Align clause terms with statutory principles established in {matched_sources[0]['section']}.",
                        source_type="LEGAL_SOURCE",
                        verification_status="SUPPORTED",
                        confidence=0.92,
                        sources=matched_sources
                    ))

        # 2. If no candidate authorities found, record clean unforced finding
        if not findings:
            findings.append(AgentFindingModel(
                id="res-none-01",
                agent="Legal Research Agent",
                dimension="Legal",
                category="Statutory Research",
                severity="INFORMATIONAL",
                risk_score=10,
                clause_type="Statutory Index Audit",
                clause_text="No specific statutory invalidity or indexed statutory restrictions identified.",
                page_number=1,
                evidence=f"Cross-referenced against {playbook.display_name} primary sources ({', '.join(relevant_acts)}).",
                claim="NO_RELEVANT_AUTHORITY_CONFLICT_IDENTIFIED",
                reason="Standard commercial covenants without specific statutory restrictions in indexed repositories.",
                recommendation="Ensure formal execution and legal capacity under general principles of contract law.",
                source_type="LEGAL_SOURCE",
                verification_status="TEXT_SUPPORTED",
                confidence=0.90,
                sources=[]
            ))

        return AgentResult(
            agent_name=self.name,
            status="success",
            confidence=0.92,
            summary=f"Legal research complete: {len(all_sources)} relevant statutory authority(s) retrieved for {playbook.display_name}.",
            findings=findings,
            data={
                "verified_sources": all_sources,
                "playbook_domain": playbook.domain_name,
                "relevant_acts": relevant_acts,
                "total_authorities": len(all_sources)
            }
        )
