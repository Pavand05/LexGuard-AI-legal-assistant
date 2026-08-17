import time
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class AgentFindingModel(BaseModel):
    id: Optional[str] = None
    agent: Optional[str] = None           # Agent identifier
    agent_name: Optional[str] = None      # Backward compatibility alias
    dimension: str = "Legal"              # Legal | Financial | Compliance | Privacy | Operational | IP | Reputational
    category: Optional[str] = None        # Category (e.g. encumbrance, payment, title, consideration)
    severity: str = "LOW"                 # CRITICAL | HIGH | MEDIUM | LOW | INFORMATIONAL
    risk_level: str = "LOW"               # Backward compatibility alias for severity
    risk_score: int = 0                   # 0 - 100
    clause_reference: Optional[str] = None # e.g. "Clause 3", "Section 4.2"
    clause_type: str = "General"
    clause_text: str = ""
    page_number: int = 1
    page: Optional[int] = None            # Alias for page_number
    evidence: str = ""                    # Exact textual snippet or factual basis
    claim: Optional[str] = None           # Legal or analytical assertion
    reason: str = ""
    recommendation: str = ""
    source_type: str = "DOCUMENT_TEXT"    # DOCUMENT_TEXT | LEGAL_SOURCE | AI_INFERENCE | USER_INPUT
    verification_status: str = "UNVERIFIED" # TEXT_SUPPORTED | SUPPORTED | PARTIALLY_SUPPORTED | NOT_SUPPORTED | UNVERIFIED
    citation_status: str = "UNVERIFIED"   # Backward compatibility alias for verification_status
    confidence: float = 0.85
    status: str = "active"                # active | resolved | dismissed | review_needed
    sources: List[Dict[str, Any]] = Field(default_factory=list)

    def __init__(self, **data):
        # Auto-sync aliases
        if "risk_level" in data and "severity" not in data:
            data["severity"] = data["risk_level"]
        elif "severity" in data and "risk_level" not in data:
            data["risk_level"] = data["severity"]
        if "agent_name" in data and "agent" not in data:
            data["agent"] = data["agent_name"]
        elif "agent" in data and "agent_name" not in data:
            data["agent_name"] = data["agent"]
        if "page_number" in data and "page" not in data:
            data["page"] = data["page_number"]
        elif "page" in data and "page_number" not in data:
            data["page_number"] = data["page"]
        if "citation_status" in data and "verification_status" not in data:
            data["verification_status"] = data["citation_status"]
        elif "verification_status" in data and "citation_status" not in data:
            data["citation_status"] = data["verification_status"]
        if "clause_type" in data and "category" not in data:
            data["category"] = data["clause_type"]
        elif "category" in data and "clause_type" not in data:
            data["clause_type"] = data["category"]
        if "reason" in data and "evidence" not in data:
            data["evidence"] = data.get("clause_text", "")
        super().__init__(**data)


class AgentMessage(BaseModel):
    run_id: str
    parent_run_id: Optional[str] = None
    sender: str
    receiver: str = "orchestrator"
    message_type: str = "analysis"  # analysis | critique | verification | escalation | failure
    document_id: Optional[int] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.9
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AgentResult(BaseModel):
    agent_name: str
    status: str = "success"  # success | warning | failure | skipped
    duration_ms: int = 0
    confidence: float = 0.85
    summary: str = ""
    findings: List[AgentFindingModel] = Field(default_factory=list)
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class BaseAgent:
    def __init__(self, name: str, description: str, capabilities: List[str] = None):
        self.name = name
        self.description = description
        self.capabilities = capabilities or []
        self.tools = {}

    def register_tool(self, tool_name: str, tool_fn):
        self.tools[tool_name] = tool_fn

    def get_tool(self, tool_name: str):
        return self.tools.get(tool_name)

    def run(self, context: Dict[str, Any]) -> AgentResult:
        start_time = time.time()
        try:
            result = self.execute(context)
            duration = int((time.time() - start_time) * 1000)
            result.duration_ms = duration
            return result
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            return AgentResult(
                agent_name=self.name,
                status="failure",
                duration_ms=duration,
                confidence=0.0,
                summary=f"Agent {self.name} encountered an error: {str(e)}",
                error=str(e)
            )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        raise NotImplementedError("Subclasses must implement execute()")

    def call_llm(self, user_prompt: str, system_prompt: str = "") -> str:
        """Helper to invoke LLM with fallback support."""
        groq_key = os.environ.get("GROQ_API_KEY", "").strip()
        if groq_key and groq_key != "your_groq_api_key_here":
            try:
                from langchain_groq import ChatGroq
                from langchain_core.prompts import ChatPromptTemplate
                from langchain_core.output_parsers import StrOutputParser

                model_name = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
                llm = ChatGroq(api_key=groq_key, model_name=model_name, temperature=0.1)
                
                messages = []
                if system_prompt:
                    messages.append(("system", system_prompt))
                messages.append(("human", user_prompt))
                
                prompt = ChatPromptTemplate.from_messages(messages)
                chain = prompt | llm | StrOutputParser()
                return chain.invoke({})
            except Exception as e:
                print(f"[{self.name}] LLM invocation failed ({e}), using deterministic fallback.")
        return ""
