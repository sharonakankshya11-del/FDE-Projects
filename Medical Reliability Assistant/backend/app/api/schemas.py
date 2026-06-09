"""
app/api/schemas.py
Pydantic models for all API request/response bodies.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.agents.state import HumanReviewAction


# ── Request models ────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=5, max_length=1000, description="Equipment issue description")
    equipment_type: Optional[str] = Field(None, description="Filter by equipment type")
    hospital_unit: Optional[str] = Field(None, description="Filter by hospital unit")
    severity: Optional[str] = Field(None, description="Filter by severity: low/medium/high")
    session_id: Optional[str] = Field(None, description="Session ID for checkpoint resumption")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "MRI machine heat dissipation failure in ICU",
                "equipment_type": "MRI System",
                "hospital_unit": "ICU",
                "severity": "high",
                "session_id": "eng-001",
            }
        }


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=5, max_length=1000)
    top_k: int = Field(5, ge=1, le=20)
    equipment_type: Optional[str] = None
    hospital_unit: Optional[str] = None


class ReviewRequest(BaseModel):
    session_id: str
    action: HumanReviewAction
    edited_response: Optional[str] = None


class EvalRequest(BaseModel):
    run_full_suite: bool = True
    query_results: Optional[List[Dict[str, Any]]] = None


# ── Response models ───────────────────────────────────────────────────────────

class IncidentResult(BaseModel):
    id: str
    equipment_type: str
    hospital_unit: str
    severity: str
    failure_type: str
    text: str
    score: float
    rerank_score: Optional[float] = None


class QueryResponse(BaseModel):
    session_id: str
    recommendation: str
    root_cause: str
    confidence: float
    failure_probability: float
    escalation_triggered: bool
    escalation_reason: str
    retrieved_incidents: List[IncidentResult]
    citations: List[str]
    anomalies: List[Dict[str, Any]]
    correlation_summary: str
    maintenance_patterns: str
    output_warning: str
    fallback_triggered: bool
    awaiting_human_review: bool
    agent_messages: List[Dict[str, str]]
    eval_scores: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    results: List[IncidentResult]
    total: int


class ReviewResponse(BaseModel):
    session_id: str
    action: str
    final_response: str
    status: str


class HealthResponse(BaseModel):
    status: str
    vectordb: str
    bm25_index_size: int


class IngestResponse(BaseModel):
    status: str
    vectors_upserted: int
    message: str
