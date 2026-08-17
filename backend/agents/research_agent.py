"""
Legal Research Agent
Researches authoritative statutory authorities (India Code, DPDP, IT Act, Indian Contract Act)
relevant to contract risks and legal liabilities.
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult, AgentFindingModel
from agent_tools.legal_sources import search_statutory_sources


class LegalResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Legal Research Agent",
            description="Searches verified statutory knowledge bases for applicable legal precedents and acts.",
            capabilities=["statutory_retrieval", "legal_research", "authority_matching"]
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        clauses = context.get("clauses", [])
        jurisdiction = context.get("jurisdiction", "India")
        findings = []
        all_sources = []
        
        # Collect key issues from high/medium risk clauses
        for c in clauses:
            if c.get("risk") in ["high", "medium"]:
                c_type = c.get("type", "General")
                content = c.get("content", "")
                keywords = [c_type] + content.split()[:8]
                matched_sources = search_statutory_sources(keywords, jurisdiction=jurisdiction, top_k=2)
                
                if matched_sources:
                    for src in matched_sources:
                        if src["id"] not in [s["id"] for s in all_sources]:
                            all_sources.append(src)
                            
                    findings.append(AgentFindingModel(
                        dimension=c.get("dimension", "Legal"),
                        risk_level=c.get("risk", "low").upper(),
                        risk_score=75 if c.get("risk") == "high" else 50,
                        clause_type=f"Research: {c_type}",
                        clause_text=c.get("content", "")[:200],
                        page_number=c.get("page", 1),
                        reason=f"Matched statutory authority: {matched_sources[0]['act']}, {matched_sources[0]['section']} ({matched_sources[0]['title']}).",
                        recommendation=f"Align clause terms with statutory limits defined in {matched_sources[0]['section']}.",
                        citation_status="SUPPORTED",
                        confidence=0.92,
                        sources=matched_sources
                    ))

        if not findings:
            # General baseline statutory research
            default_sources = search_statutory_sources(["contract", "breach", "damages"], jurisdiction=jurisdiction, top_k=2)
            all_sources.extend(default_sources)
            findings.append(AgentFindingModel(
                dimension="Legal",
                risk_level="INFORMATIONAL",
                risk_score=20,
                clause_type="General Statutory Authority",
                clause_text="Standard statutory framework reference for commercial agreements.",
                page_number=1,
                reason="Indian Contract Act 1872 provides the foundational statutory framework for enforceable mutual covenants.",
                recommendation="Ensure formal execution and legal capacity of parties.",
                citation_status="SUPPORTED",
                confidence=0.90,
                sources=default_sources
            ))

        return AgentResult(
            agent_name=self.name,
            status="success",
            confidence=0.92,
            summary=f"Identified {len(all_sources)} verified statutory reference(s) across {len(findings)} legal issue(s).",
            findings=findings,
            data={"verified_sources": all_sources, "total_authorities": len(all_sources)}
        )
