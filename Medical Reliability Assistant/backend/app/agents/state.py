"""
app/agents/state.py
Shared typed state object passed between all agents in the LangGraph graph.
A2A (agent-to-agent) communication uses typed AgentMessage objects
appended to the messages list; the supervisor routes based on escalation flags.
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from enum import Enum


# ── A2A Message Types ─────────────────────────────────────────────────────────

class MessageRole(str, Enum):
    USER = "user"
    RETRIEVAL = "retrieval_agent"
    ANALYSIS = "analysis_agent"
    MAINTENANCE = "maintenance_agent"
    RECOMMENDATION = "recommendation_agent"
    SUPERVISOR = "supervisor"
    HUMAN = "human"


class AgentMessage(BaseModel):
    role: MessageRole
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ── Retrieved Incident ─────────────────────────────────────────────────────────

class RetrievedIncident(BaseModel):
    id: str
    text: str
    equipment_type: str = ""
    hospital_unit: str = ""
    severity: str = ""
    failure_type: str = ""
    score: float = 0.0
    rerank_score: Optional[float] = None


# ── Anomaly Detection Result ──────────────────────────────────────────────────

class AnomalyResult(BaseModel):
    field: str
    value: float
    z_score: float
    is_anomaly: bool
    direction: str  # "high" | "low"


# ── Human Review ──────────────────────────────────────────────────────────────

class HumanReviewAction(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    EDIT = "edit"
    SKIP = "skip"


# ── Main Graph State ──────────────────────────────────────────────────────────

class AgentState(BaseModel):
    # Input
    session_id: str
    original_query: str
    sanitised_query: str = ""
    equipment_filter: Optional[str] = None
    unit_filter: Optional[str] = None
    severity_filter: Optional[str] = None

    # A2A messages (agent conversation log)
    messages: List[AgentMessage] = Field(default_factory=list)

    # Retrieval
    retrieved_incidents: List[RetrievedIncident] = Field(default_factory=list)
    retrieval_context: str = ""  # concatenated top-k texts for LLM prompt

    # Analysis
    anomalies: List[AnomalyResult] = Field(default_factory=list)
    correlation_summary: str = ""
    failure_probability: float = 0.0

    # Maintenance
    maintenance_patterns: str = ""
    similar_cases_count: int = 0

    # Recommendation
    recommendation: str = ""
    root_cause: str = ""
    confidence: float = 0.0
    citations: List[str] = Field(default_factory=list)

    # Escalation flag (A2A)
    escalation_triggered: bool = False
    escalation_reason: str = ""

    # Human-in-the-loop
    awaiting_human_review: bool = False
    human_review_action: Optional[HumanReviewAction] = None
    human_edited_response: Optional[str] = None

    # Output guardrail
    output_safe: bool = True
    output_warning: str = ""

    # Fallback
    fallback_triggered: bool = False
    fallback_message: str = ""

    # Error tracking
    errors: List[str] = Field(default_factory=list)

    # Final response
    final_response: str = ""

    def add_message(self, role: MessageRole, content: str, **meta) -> None:
        self.messages.append(AgentMessage(role=role, content=content, metadata=meta))

    def trigger_escalation(self, reason: str) -> None:
        self.escalation_triggered = True
        self.escalation_reason = reason
        self.add_message(
            MessageRole.SUPERVISOR,
            f"[ESCALATION] {reason}",
            escalation=True,
        )

    def trigger_fallback(self, agent: str, reason: str) -> None:
        self.fallback_triggered = True
        self.fallback_message = f"Agent '{agent}' failed: {reason}. Fallback response provided."
        self.errors.append(f"{agent}: {reason}")
