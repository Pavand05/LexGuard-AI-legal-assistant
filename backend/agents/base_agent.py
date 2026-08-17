import time
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class AgentFindingModel(BaseModel):
    id: Optional[str] = None
    dimension: str = "Legal"  # Legal | Financial | Compliance | Privacy | Operational | IP | Reputational
    risk_level: str = "LOW"   # HIGH | MEDIUM | LOW | INFORMATIONAL
    risk_score: int = 0       # 0 - 100
    clause_type: str = "General"
    clause_text: str = ""
    page_number: int = 1
    reason: str = ""
    recommendation: str = ""
    citation_status: str = "UNVERIFIED"  # SUPPORTED | PARTIALLY_SUPPORTED | NOT_SUPPORTED | UNVERIFIED
    confidence: float = 0.85
    sources: List[Dict[str, Any]] = Field(default_factory=list)


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
