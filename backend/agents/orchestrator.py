"""
Central Multi-Agent Orchestrator (LexGuard-MA)
Supports Single-Agent Baseline, Sequential, Parallel, and Debate workflows.
Enforces structured agent communication, observability traces, and Human-in-the-loop triggers.
"""
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


class MultiAgentOrchestrator:
    def __init__(self):
        # Initialize all specialized agents
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
        Execute the specified multi-agent workflow over the legal document.
        Returns full trace, agent steps, structured findings, and contract metrics.
        """
        start_overall = time.time()
        run_id = f"run-{uuid.uuid4().hex[:10]}"
        agent_traces: List[Dict[str, Any]] = []
        agent_messages: List[Dict[str, Any]] = []
        all_findings: List[Dict[str, Any]] = []
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
                all_findings.append(f_dict)
                
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

        # ── 1. SINGLE AGENT BASELINE WORKFLOW ───────────────────────────────
        if workflow_type == "single":
            # Baseline uses single doc & clause processing
            doc_res = self.doc_agent.run(context)
            record_agent_step(doc_res, sender="Document Intelligence Agent")
            context["document_type"] = doc_res.data.get("document_type", "Commercial Contract")
            context["parties"] = doc_res.data.get("parties", [])
            context["jurisdiction"] = doc_res.data.get("jurisdiction", "India")

            clause_res = self.clause_agent.run(context)
            record_agent_step(clause_res, sender="Clause Intelligence Agent")
            context["clauses"] = clause_res.data.get("clauses", [])

            risk_res = self.risk_agent.run(context)
            record_agent_step(risk_res, sender="Risk Assessment Agent")

        # ── 2. PARALLEL MULTI-AGENT WORKFLOW (Default High-Performance) ─────
        elif workflow_type == "parallel":
            # Stage 1: Document Intelligence
            doc_res = self.doc_agent.run(context)
            record_agent_step(doc_res, sender="Document Intelligence Agent")
            context["document_type"] = doc_res.data.get("document_type", "Commercial Contract")
            context["parties"] = doc_res.data.get("parties", [])
            context["jurisdiction"] = doc_res.data.get("jurisdiction", "India")

            # Stage 2: Clause Intelligence
            clause_res = self.clause_agent.run(context)
            record_agent_step(clause_res, sender="Clause Intelligence Agent")
            context["clauses"] = clause_res.data.get("clauses", [])

            # Stage 3: Concurrent execution of independent agents
            parallel_agents = [
                self.risk_agent,
                self.compliance_agent,
                self.contradiction_agent,
                self.missing_agent,
                self.obligation_agent,
                self.privacy_agent
            ]
            with ThreadPoolExecutor(max_workers=6) as executor:
                future_to_agent = {executor.submit(agent.run, context): agent for agent in parallel_agents}
                for future in as_completed(future_to_agent):
                    res = future.result()
                    record_agent_step(res, sender=res.agent_name)

            # Stage 4: Legal Research & Citation Verification
            research_res = self.research_agent.run(context)
            record_agent_step(research_res, sender="Legal Research Agent")

            context["findings"] = all_findings.copy()
            citation_res = self.citation_agent.run(context)
            record_agent_step(citation_res, sender="Citation Verification Agent")

            # Stage 5: Negotiation & Redlining
            neg_res = self.negotiation_agent.run(context)
            record_agent_step(neg_res, sender="Negotiation Agent")
            context["negotiation_items"] = neg_res.data.get("negotiation_items", [])

            redline_res = self.redline_agent.run(context)
            record_agent_step(redline_res, sender="Redlining Agent")

            # Stage 6: Consensus Reviewer & Health Scoring
            context["agent_results"] = results_by_agent
            reviewer_res = self.reviewer_agent.run(context)
            record_agent_step(reviewer_res, sender="Reviewer Agent")

        # ── 3. SEQUENTIAL MULTI-AGENT WORKFLOW ──────────────────────────────
        elif workflow_type == "sequential":
            # Stage 1: Document Agent
            doc_res = self.doc_agent.run(context)
            record_agent_step(doc_res, sender="Document Intelligence Agent")
            context["document_type"] = doc_res.data.get("document_type", "Commercial Contract")
            context["parties"] = doc_res.data.get("parties", [])
            context["jurisdiction"] = doc_res.data.get("jurisdiction", "India")

            # Stage 2: Clause Agent
            clause_res = self.clause_agent.run(context)
            record_agent_step(clause_res, sender="Clause Intelligence Agent")
            context["clauses"] = clause_res.data.get("clauses", [])

            # Sequential pipeline
            for agent in [
                self.risk_agent,
                self.compliance_agent,
                self.contradiction_agent,
                self.missing_agent,
                self.research_agent,
                self.obligation_agent,
                self.privacy_agent,
                self.negotiation_agent
            ]:
                res = agent.run(context)
                record_agent_step(res, sender=res.agent_name)
                if agent == self.negotiation_agent:
                    context["negotiation_items"] = res.data.get("negotiation_items", [])

            citation_res = self.citation_agent.run({"findings": all_findings.copy()})
            record_agent_step(citation_res, sender="Citation Verification Agent")

            redline_res = self.redline_agent.run(context)
            record_agent_step(redline_res, sender="Redlining Agent")

            context["agent_results"] = results_by_agent
            reviewer_res = self.reviewer_agent.run(context)
            record_agent_step(reviewer_res, sender="Reviewer Agent")

        # ── 4. DEBATE / CRITIC WORKFLOW ─────────────────────────────────────
        elif workflow_type == "debate":
            # Stage 1: Base Analysis
            doc_res = self.doc_agent.run(context)
            record_agent_step(doc_res, sender="Document Intelligence Agent")
            context["document_type"] = doc_res.data.get("document_type", "Commercial Contract")
            context["parties"] = doc_res.data.get("parties", [])
            context["jurisdiction"] = doc_res.data.get("jurisdiction", "India")

            clause_res = self.clause_agent.run(context)
            record_agent_step(clause_res, sender="Clause Intelligence Agent")
            context["clauses"] = clause_res.data.get("clauses", [])

            risk_res = self.risk_agent.run(context)
            record_agent_step(risk_res, sender="Risk Assessment Agent (Analyst)")

            comp_res = self.compliance_agent.run(context)
            record_agent_step(comp_res, sender="Compliance Agent (Analyst)")

            # Critic Phase: Citation Agent challenges claims
            context["findings"] = all_findings.copy()
            citation_res = self.citation_agent.run(context)
            record_agent_step(citation_res, sender="Citation Verification Agent (Critic)")

            # Re-evaluation by Reviewer
            context["agent_results"] = results_by_agent
            reviewer_res = self.reviewer_agent.run(context)
            record_agent_step(reviewer_res, sender="Reviewer Agent (Adjudicator)")

        total_duration_ms = int((time.time() - start_overall) * 1000)

        # Aggregate final payload
        risk_data = results_by_agent.get("Risk Assessment Agent")
        reviewer_data = results_by_agent.get("Reviewer Agent")
        doc_data = results_by_agent.get("Document Intelligence Agent")
        clause_data = results_by_agent.get("Clause Intelligence Agent")
        comp_data = results_by_agent.get("Compliance Agent")
        obligations_data = results_by_agent.get("Obligation Extraction Agent")
        redlines_data = results_by_agent.get("Redlining Agent")
        privacy_data = results_by_agent.get("Privacy & PII Agent")

        final_response = {
            "run_id": run_id,
            "workflow_type": workflow_type,
            "status": "completed",
            "total_duration_ms": total_duration_ms,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "document_metadata": doc_data.data if doc_data else {},
            "clauses": clause_data.data.get("clauses", []) if clause_data else [],
            "risk_analysis": {
                "overall_score": risk_data.data.get("overall_score", 30) if risk_data else 30,
                "overall_tier": risk_data.data.get("overall_tier", "LOW") if risk_data else "LOW",
                "dimensions": risk_data.data.get("dimensions", {}) if risk_data else {},
                "legacy_risks": risk_data.data.get("legacy_risks", {"high": 0, "medium": 0, "low": 0, "total": 0}) if risk_data else {}
            },
            "contract_health": {
                "score": reviewer_data.data.get("health_score", 85) if reviewer_data else 85,
                "grade": reviewer_data.data.get("health_grade", "A (Standard)") if reviewer_data else "A",
                "needs_human_review": reviewer_data.data.get("needs_human_review", False) if reviewer_data else False,
                "disagreements": reviewer_data.data.get("disagreements", []) if reviewer_data else []
            },
            "compliance": comp_data.data if comp_data else {},
            "obligations": obligations_data.data.get("obligations", []) if obligations_data else [],
            "redlines": redlines_data.data.get("redlines", []) if redlines_data else [],
            "privacy": privacy_data.data if privacy_data else {},
            "agent_traces": agent_traces,
            "agent_messages": agent_messages,
            "findings": all_findings
        }
        return final_response


# Global orchestrator instance
orchestrator = MultiAgentOrchestrator()
