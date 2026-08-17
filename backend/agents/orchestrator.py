"""
Central Multi-Agent Orchestrator (LexGuard-MA)
Supports Single-Agent Baseline, Sequential, Parallel, and Debate workflows.
Features:
- Dynamic Agent Routing Layer (AgentRouter)
- Pluggable Domain Playbooks
- Open-Set Document Taxonomy Support
- Observability Traces and Human-in-the-Loop Triggers
"""
import re
import time
import uuid
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

from .base_agent import AgentResult, AgentMessage, AgentFindingModel
from .document_agent import DocumentIntelligenceAgent
from .clause_agent import ClauseIntelligenceAgent
from .risk_agent import RiskAssessmentAgent
from .compliance_agent import ComplianceIntelligenceAgent
from .contradiction_agent import ContradictionDetectionAgent
from .missing_clause_agent import MissingClauseIntelligenceAgent
from .research_agent import LegalResearchAgent
from .citation_agent import CitationVerificationAgent
from .obligation_agent import ObligationExtractionAgent
from .negotiation_agent import NegotiationStrategyAgent
from .redlining_agent import RedliningIntelligenceAgent
from .privacy_agent import PrivacyIntelligenceAgent
from .reviewer_agent import ReviewerCriticAgent
from .router import AgentRouter


class MultiAgentOrchestrator:
    def __init__(self):
        # Initialize all 13 specialized agents
        self.doc_agent = DocumentIntelligenceAgent()
        self.clause_agent = ClauseIntelligenceAgent()
        self.risk_agent = RiskAssessmentAgent()
        self.compliance_agent = ComplianceIntelligenceAgent()
        self.contradiction_agent = ContradictionDetectionAgent()
        self.missing_agent = MissingClauseIntelligenceAgent()
        self.research_agent = LegalResearchAgent()
        self.citation_agent = CitationVerificationAgent()
        self.obligation_agent = ObligationExtractionAgent()
        self.negotiation_agent = NegotiationStrategyAgent()
        self.redline_agent = RedliningIntelligenceAgent()
        self.privacy_agent = PrivacyIntelligenceAgent()
        self.reviewer_agent = ReviewerCriticAgent()

    def run_workflow(
        self,
        document_text: str,
        page_texts: Optional[List[str]] = None,
        filename: str = "document.pdf",
        workflow_type: str = "parallel",  # single | sequential | parallel | debate
        privacy_mode: bool = False,
        document_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute dynamic multi-agent workflow over any legal document.
        Returns full trace, agent steps, structured findings, and contract metrics.
        """
        start_overall = time.time()
        run_id = f"run-{uuid.uuid4().hex[:10]}"
        agent_traces: List[Dict[str, Any]] = []
        agent_messages: List[Dict[str, Any]] = []
        all_raw_findings: List[Dict[str, Any]] = []
        results_by_agent: Dict[str, AgentResult] = {}

        def record_agent_step(result: AgentResult, sender: str, receiver: str = "orchestrator"):
            results_by_agent[result.agent_name] = result
            agent_traces.append({
                "agent_name": result.agent_name,
                "status": result.status,
                "duration_ms": result.duration_ms,
                "confidence": result.confidence,
                "summary": result.summary,
                "findings_count": len(result.findings),
                "error": result.error
            })
            for f in result.findings:
                f_dict = f.model_dump()
                f_dict["agent_name"] = result.agent_name
                if not f_dict.get("agent"):
                    f_dict["agent"] = result.agent_name
                all_raw_findings.append(f_dict)
                
            msg = AgentMessage(
                run_id=run_id,
                sender=sender,
                receiver=receiver,
                message_type="analysis_output",
                document_id=document_id,
                payload={"summary": result.summary, "data_keys": list(result.data.keys())},
                confidence=result.confidence
            )
            agent_messages.append(msg.model_dump())

        # Base shared context
        context: Dict[str, Any] = {
            "text": document_text,
            "page_texts": page_texts or [document_text],
            "filename": filename,
            "privacy_mode": privacy_mode,
            "document_id": document_id,
            "run_id": run_id
        }

        # ── STAGE 1: DOCUMENT INTELLIGENCE & OPEN-SET CLASSIFICATION ───────
        doc_res = self.doc_agent.run(context)
        record_agent_step(doc_res, sender="Document Intelligence Agent")
        
        doc_type = doc_res.data.get("document_type", "OTHER_LEGAL_DOCUMENT")
        detected_domains = doc_res.data.get("detected_domains", ["GENERAL_COMMERCIAL"])
        classification_confidence = doc_res.data.get("classification_confidence", 0.85)
        
        context["document_type"] = doc_type
        context["document_metadata"] = doc_res.data
        context["detected_domains"] = detected_domains
        context["parties"] = doc_res.data.get("parties", [])
        context["jurisdiction"] = doc_res.data.get("court_jurisdiction", "India")
        context["applicable_law"] = doc_res.data.get("applicable_law", "Laws of India")

        # ── STAGE 2: CLAUSE INTELLIGENCE & STRUCTURE EXTRACTION ───────────
        clause_res = self.clause_agent.run(context)
        record_agent_step(clause_res, sender="Clause Intelligence Agent")
        clauses = clause_res.data.get("clauses", [])
        context["clauses"] = clauses
        context["findings"] = all_raw_findings.copy()

        # ── STAGE 3: DYNAMIC AGENT ROUTING ─────────────────────────────────
        routing_info = AgentRouter.route_agents(
            document_type=doc_type,
            detected_domains=detected_domains,
            jurisdiction=context["jurisdiction"],
            clauses=clauses,
            privacy_mode=privacy_mode,
            confidence=classification_confidence
        )
        context["routing_info"] = routing_info
        active_agent_names = set(routing_info["active_agents"])

        # ── 1. SINGLE AGENT BASELINE WORKFLOW ───────────────────────────────
        if workflow_type == "single":
            risk_res = self.risk_agent.run(context)
            record_agent_step(risk_res, sender="Risk Assessment Agent")

        # ── 2. PARALLEL MULTI-AGENT WORKFLOW (Default High-Performance) ─────
        elif workflow_type == "parallel":
            # Concurrent execution of independent analytical agents
            parallel_candidates = [
                (self.risk_agent, "Risk Assessment Agent"),
                (self.compliance_agent, "Compliance Agent"),
                (self.contradiction_agent, "Contradiction Agent"),
                (self.missing_agent, "Missing Clause Agent"),
                (self.obligation_agent, "Obligation Extraction Agent"),
                (self.privacy_agent, "Privacy & PII Agent")
            ]
            # Filter by dynamic routing
            selected_parallel = [agent for agent, name in parallel_candidates if name in active_agent_names]
            
            with ThreadPoolExecutor(max_workers=6) as executor:
                future_to_agent = {executor.submit(agent.run, context): agent for agent in selected_parallel}
                for future in as_completed(future_to_agent):
                    res = future.result()
                    record_agent_step(res, sender=res.agent_name)

            # Legal Research & Citation Verification
            if "Legal Research Agent" in active_agent_names:
                research_res = self.research_agent.run(context)
                record_agent_step(research_res, sender="Legal Research Agent")

            context["findings"] = all_raw_findings.copy()
            if "Citation Verification Agent" in active_agent_names:
                citation_res = self.citation_agent.run(context)
                record_agent_step(citation_res, sender="Citation Verification Agent")

            # Negotiation & Redlining
            if "Negotiation Agent" in active_agent_names:
                neg_res = self.negotiation_agent.run(context)
                record_agent_step(neg_res, sender="Negotiation Agent")
                context["negotiation_items"] = neg_res.data.get("negotiation_items", [])

            if "Redlining Agent" in active_agent_names:
                redline_res = self.redline_agent.run(context)
                record_agent_step(redline_res, sender="Redlining Agent")

            # Reviewer & Critic Agent (Cross-Agent Consensus)
            context["agent_results"] = results_by_agent
            reviewer_res = self.reviewer_agent.run(context)
            record_agent_step(reviewer_res, sender="Reviewer Agent")

        # ── 3. SEQUENTIAL MULTI-AGENT WORKFLOW ──────────────────────────────
        elif workflow_type == "sequential":
            sequential_pipeline = [
                (self.risk_agent, "Risk Assessment Agent"),
                (self.compliance_agent, "Compliance Agent"),
                (self.contradiction_agent, "Contradiction Agent"),
                (self.missing_agent, "Missing Clause Agent"),
                (self.research_agent, "Legal Research Agent"),
                (self.obligation_agent, "Obligation Extraction Agent"),
                (self.privacy_agent, "Privacy & PII Agent"),
                (self.negotiation_agent, "Negotiation Agent")
            ]
            for agent, name in sequential_pipeline:
                if name in active_agent_names:
                    res = agent.run(context)
                    record_agent_step(res, sender=res.agent_name)
                    if agent == self.negotiation_agent:
                        context["negotiation_items"] = res.data.get("negotiation_items", [])

            if "Citation Verification Agent" in active_agent_names:
                citation_res = self.citation_agent.run({"text": document_text, "findings": all_raw_findings.copy()})
                record_agent_step(citation_res, sender="Citation Verification Agent")

            if "Redlining Agent" in active_agent_names:
                redline_res = self.redline_agent.run(context)
                record_agent_step(redline_res, sender="Redlining Agent")

            context["agent_results"] = results_by_agent
            reviewer_res = self.reviewer_agent.run(context)
            record_agent_step(reviewer_res, sender="Reviewer Agent")

        # ── 4. DEBATE / CRITIC WORKFLOW ─────────────────────────────────────
        elif workflow_type == "debate":
            risk_res = self.risk_agent.run(context)
            record_agent_step(risk_res, sender="Risk Assessment Agent (Analyst)")

            comp_res = self.compliance_agent.run(context)
            record_agent_step(comp_res, sender="Compliance Agent (Analyst)")

            citation_res = self.citation_agent.run({"text": document_text, "findings": all_raw_findings.copy()})
            record_agent_step(citation_res, sender="Citation Verification Agent (Critic)")

            context["agent_results"] = results_by_agent
            reviewer_res = self.reviewer_agent.run(context)
            record_agent_step(reviewer_res, sender="Reviewer Agent (Adjudicator)")

        total_duration_ms = int((time.time() - start_overall) * 1000)

        # Deduplicate all raw findings for clean UI display
        deduplicated_findings: List[Dict[str, Any]] = []
        seen_fingerprints = set()
        for f in all_raw_findings:
            key = (f.get("agent_name", "") + f.get("clause_type", "") + f.get("reason", "")[:35]).lower()
            if key in seen_fingerprints:
                continue
            seen_fingerprints.add(key)
            deduplicated_findings.append(f)

        # Aggregate final payload
        risk_data = results_by_agent.get("Risk Assessment Agent")
        reviewer_data = results_by_agent.get("Reviewer Agent")
        comp_data = results_by_agent.get("Compliance Agent")
        contra_data = results_by_agent.get("Contradiction Agent")
        citation_data = results_by_agent.get("Citation Verification Agent")
        obligations_data = results_by_agent.get("Obligation Extraction Agent")
        redlines_data = results_by_agent.get("Redlining Agent")
        privacy_data = results_by_agent.get("Privacy & PII Agent")
        missing_data = results_by_agent.get("Missing Clause Agent")

        # Structured Section 23 Schema elements
        doc_meta = doc_res.data or {}
        l_ctx = doc_meta.get("legal_context", {})
        
        has_arbitration = any(c.get("canonical_id") in ["DISPUTE_RESOLUTION_ARBITRATION", "ARBITRATION"] for c in clauses)
        has_court = bool(l_ctx.get("court_jurisdiction") or any(c.get("canonical_id") in ["GOVERNING_LAW_JURISDICTION", "COURT_JURISDICTION"] for c in clauses))

        final_response = {
            "run_id": run_id,
            "workflow_type": workflow_type,
            "status": "completed",
            "total_duration_ms": total_duration_ms,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "routing": routing_info,
            "document": {
                "primary_type": doc_meta.get("primary_type") or doc_meta.get("document_type", "OTHER_LEGAL_DOCUMENT"),
                "secondary_types": doc_meta.get("secondary_types", []),
                "primary_domain": doc_meta.get("primary_domain") or detected_domains[0],
                "secondary_domains": doc_meta.get("secondary_domains", []),
                "governing_law": {
                    "jurisdiction": l_ctx.get("governing_law", "Laws of India"),
                    "country": l_ctx.get("country", "INDIA"),
                    "state_or_region": l_ctx.get("state_or_region"),
                    "source": l_ctx.get("governing_law_source", "Document Scan"),
                    "confidence": l_ctx.get("jurisdiction_confidence", 0.9)
                }
            },
            "referenced_documents": doc_meta.get("referenced_documents", []),
            "dispute_resolution": {
                "court_jurisdiction": l_ctx.get("court_jurisdiction"),
                "venue": l_ctx.get("venue"),
                "arbitration": "PRESENT" if has_arbitration else "NOT_DETECTED",
                "mediation": "PRESENT" if l_ctx.get("mediation_forum") else "NOT_DETECTED"
            },
            "financial": {
                "applicable": bool(risk_data.data.get("financial_applicable", True)) if risk_data else True,
                "risk_score": (risk_data.data.get("dimension_breakdown", {}).get("Financial", 20)) if risk_data else 20
            },
            "document_metadata": doc_res.data,
            "clauses": clauses,
            "risk_analysis": {
                "overall_score": (risk_data.data.get("overall_risk_score") or risk_data.data.get("overall_score", 20)) if risk_data else 20,
                "overall_risk_score": (risk_data.data.get("overall_risk_score") or risk_data.data.get("overall_score", 20)) if risk_data else 20,
                "overall_tier": risk_data.data.get("overall_tier", "LOW") if risk_data else "LOW",
                "risk_label": risk_data.data.get("risk_label", "Low Exposure") if risk_data else "Low Exposure",
                "dimensions": (risk_data.data.get("dimension_breakdown") or risk_data.data.get("dimensions", {})) if risk_data else {},
                "dimension_breakdown": (risk_data.data.get("dimension_breakdown") or risk_data.data.get("dimensions", {})) if risk_data else {},
                "dimension_status": risk_data.data.get("dimension_status", {}) if risk_data else {},
                "legacy_risks": (risk_data.data.get("risks") or risk_data.data.get("legacy_risks", {"high": 0, "medium": 0, "low": 0, "total": 0})) if risk_data else {},
                "definition": "Higher Risk (0-100) = Worse (Greater Legal / Financial Exposure)"
            },
            "contract_health": {
                "score": reviewer_data.data.get("health_score", 85) if reviewer_data else 85,
                "grade": reviewer_data.data.get("health_grade", "Grade A") if reviewer_data else "Grade A",
                "description": reviewer_data.data.get("health_description", "Standard enforceability") if reviewer_data else "Standard enforceability",
                "needs_human_review": reviewer_data.data.get("needs_human_review", False) if reviewer_data else False,
                "disagreements": reviewer_data.data.get("disagreements", []) if reviewer_data else [],
                "definition": "Higher Health (0-100) = Better (Greater Protection & Enforceability)"
            },
            "missing_clauses": missing_data.data if missing_data else {},
            "compliance": comp_data.data if comp_data else {},
            "contradictions": contra_data.data if contra_data else {},
            "citations": citation_data.data if citation_data else {},
            "obligations": obligations_data.data.get("obligations", []) if obligations_data else [],
            "redlines": redlines_data.data.get("redlines", []) if redlines_data else [],
            "privacy": privacy_data.data if privacy_data else {},
            "agent_traces": agent_traces,
            "agent_messages": agent_messages,
            "findings": deduplicated_findings
        }
        return final_response


# Global orchestrator instance
orchestrator = MultiAgentOrchestrator()
