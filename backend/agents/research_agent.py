"""
Legal Research Agent (LexGuard-MA)
Performs generic, jurisdiction-grounded statutory research:
Document Type -> Legal Domain -> Governing Jurisdiction -> Candidate Authorities -> Relevance Check -> Grounded Citations
Never assumes Indian jurisdiction for foreign (e.g. US / UK / Delaware) legal documents.
"""
import re
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentResult, AgentFindingModel
from agent_tools.legal_sources import search_statutory_sources
from .playbooks import resolve_domain_playbook, DomainPlaybook


class LegalResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Legal Research Agent",
            description="Performs jurisdiction-grounded statutory retrieval without cross-jurisdiction false positives.",
            capabilities=["statutory_retrieval", "jurisdiction_grounding", "domain_research", "authority_evaluation"]
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        doc_type = context.get("document_type", "OTHER_LEGAL_DOCUMENT")
        detected_domains = context.get("detected_domains", ["GENERAL_COMMERCIAL"])
        applicable_law = context.get("applicable_law", "")
        court_jurisdiction = context.get("jurisdiction", "")
        text = context.get("text", "")
        clauses = context.get("clauses", [])
        
        playbook: DomainPlaybook = resolve_domain_playbook(doc_type, detected_domains)
        
        # 1. Resolve Document Jurisdiction Hierarchy
        resolved_country = "UNKNOWN"
        combined_jur_text = f"{applicable_law} {court_jurisdiction} {text[:1500]}".lower()
        
        if any(k in combined_jur_text for k in ["delaware", "california", "new york", "united states", "u.s.a.", "laws of the state of", "lcia", "under us law"]):
            resolved_country = "US"
        elif any(k in combined_jur_text for k in ["england and wales", "laws of england", "uk", "london"]):
            resolved_country = "UK"
        elif any(k in combined_jur_text for k in ["singapore", "siac", "laws of singapore"]):
            resolved_country = "SINGAPORE"
        elif any(k in combined_jur_text for k in ["india", "bharat", "high court", "supreme court of india", "bengaluru", "delhi", "mumbai", "chennai", "kolkata", "hyderabad", "sub-registrar"]):
            resolved_country = "INDIA"
        else:
            resolved_country = "INDIA"  # Default fallback only when completely neutral

        # 2. Check if the resolved jurisdiction is indexed in local primary database
        # Currently, statutory database indexes Indian Central Acts
        if resolved_country != "INDIA":
            finding = AgentFindingModel(
                id="res-foreign-01",
                agent="Legal Research Agent",
                dimension="Legal",
                category="Jurisdiction Analysis",
                severity="INFORMATIONAL",
                risk_score=15,
                clause_type="Foreign Jurisdiction Grounding",
                clause_text=f"Governing Law / Jurisdiction: {applicable_law or court_jurisdiction or resolved_country}.",
                page_number=1,
                evidence=f"Detected governing jurisdiction: {resolved_country} ({applicable_law}).",
                claim="NO_INDEXED_AUTHORITY_FOR_DETECTED_JURISDICTION",
                reason=f"Document is governed by {resolved_country} law ({applicable_law}). LexGuard primary statutory repository currently indexes Central Acts of India. Cross-jurisdiction Indian statutes were not applied to avoid false positive invalidation.",
                recommendation=f"Retain qualified local legal counsel licensed in {applicable_law or resolved_country} for statutory compliance review.",
                source_type="LEGAL_SOURCE",
                verification_status="TEXT_SUPPORTED",
                confidence=0.95,
                sources=[]
            )
            return AgentResult(
                agent_name=self.name,
                status="success",
                confidence=0.95,
                summary=f"Jurisdiction identified as {resolved_country} ({applicable_law}). No foreign statutory conflict detected in local index.",
                findings=[finding],
                data={
                    "resolved_country": resolved_country,
                    "applicable_law": applicable_law,
                    "verified_sources": [],
                    "total_authorities": 0
                }
            )

        # 3. For Indian jurisdiction documents, search matching playbook acts
        relevant_acts = playbook.get_statutes_for_jurisdiction("INDIA")
        findings: List[AgentFindingModel] = []
        all_sources: List[Dict[str, Any]] = []

        for c in clauses:
            if c.get("risk") in ["high", "medium"]:
                c_type = c.get("type", "General")
                content = c.get("content", "")
                keywords = [c_type] + relevant_acts + content.split()[:5]
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
                        risk_score=70 if c.get("risk") == "high" else 45,
                        clause_type=f"Statutory Audit: {c_type}",
                        clause_text=c.get("content", "")[:200],
                        page_number=c.get("page", 1),
                        evidence=f"Matched: {matched_sources[0]['act']} ({matched_sources[0]['section']})",
                        claim=f"Primary statutory authority for {c_type} under Indian law.",
                        reason=f"Matched statutory provision: {matched_sources[0]['act']}, {matched_sources[0]['section']} ({matched_sources[0]['title']}).",
                        recommendation=f"Ensure covenants adhere to Section {matched_sources[0]['section']} of {matched_sources[0]['act']}.",
                        source_type="LEGAL_SOURCE",
                        verification_status="SUPPORTED",
                        confidence=0.92,
                        sources=matched_sources
                    ))

        if not findings:
            findings.append(AgentFindingModel(
                id="res-clean-01",
                agent="Legal Research Agent",
                dimension="Legal",
                category="Statutory Research",
                severity="INFORMATIONAL",
                risk_score=10,
                clause_type="Statutory Index Audit",
                clause_text="No specific statutory invalidity or indexed statutory restrictions identified.",
                page_number=1,
                evidence=f"Cross-referenced against {playbook.display_name} primary sources.",
                claim="NO_RELEVANT_AUTHORITY_CONFLICT_IDENTIFIED",
                reason="Standard commercial covenants without specific statutory restrictions in indexed repositories.",
                recommendation="Ensure formal execution and legal capacity under general principles of contract law.",
                source_type="LEGAL_SOURCE",
                verification_status="TEXT_SUPPORTED",
                confidence=0.92,
                sources=[]
            ))

        return AgentResult(
            agent_name=self.name,
            status="success",
            confidence=0.93,
            summary=f"Legal research complete: {len(all_sources)} relevant statutory authority(s) retrieved for {resolved_country}.",
            findings=findings,
            data={
                "resolved_country": resolved_country,
                "applicable_law": applicable_law,
                "verified_sources": all_sources,
                "total_authorities": len(all_sources)
            }
        )
