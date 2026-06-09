"""
app/api/routes.py
FastAPI route handlers for all endpoints.
"""
import uuid
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.api.schemas import (
    QueryRequest, QueryResponse, SearchRequest, SearchResponse,
    ReviewRequest, ReviewResponse, HealthResponse, IngestResponse,
    EvalRequest, IncidentResult,
)
from app.agents.state import AgentState, HumanReviewAction
from app.agents.supervisor import get_graph
from app.guardrails.input_guardrails import check_input
from app.core.hybrid_search import hybrid_search, _bm25_corpus
from app.core.reranker import rerank
from app.core.config import get_settings
from app.core.langsmith_client import build_run_config, log_hitl_feedback
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["Medical Equipment Reliability"])

# In-memory session store for HITL resumption {session_id: (AgentState, langsmith_run_id)}
_sessions: Dict[str, AgentState] = {}
_run_ids:  Dict[str, str]        = {}   # session_id → LangSmith run_id


# ── Query endpoint ────────────────────────────────────────────────────────────

@router.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """
    Main query endpoint. Runs the full multi-agent pipeline.
    Returns recommendation, incidents, anomalies, and evaluation scores.
    """
    # Input guardrails
    guard = check_input(request.query)
    if not guard.passed:
        raise HTTPException(status_code=422, detail=guard.reason)

    session_id = request.session_id or str(uuid.uuid4())

    # Build initial state
    state = AgentState(
        session_id=session_id,
        original_query=request.query,
        sanitised_query=guard.sanitised or request.query,
        equipment_filter=request.equipment_type,
        unit_filter=request.hospital_unit,
        severity_filter=request.severity,
    )

    # Run graph — config includes LangSmith run metadata + HITL thread_id
    graph = get_graph()
    run_config = build_run_config(
        session_id=session_id,
        equipment_type=request.equipment_type,
        hospital_unit=request.hospital_unit,
        severity=request.severity,
    )
    try:
        result_dict = await graph.ainvoke(state, config=run_config)
        result_state = AgentState(**result_dict) if isinstance(result_dict, dict) else result_dict
    except Exception as e:
        logger.error(f"Graph execution error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Agent pipeline error: {str(e)}")

    # Store session for HITL (run_id captured for LangSmith feedback)
    _sessions[session_id] = result_state
    _run_ids[session_id]  = run_config.get("run_id", session_id)

    # Build response
    incidents = [
        IncidentResult(
            id=inc.id,
            equipment_type=inc.equipment_type,
            hospital_unit=inc.hospital_unit,
            severity=inc.severity,
            failure_type=inc.failure_type,
            text=inc.text[:300],
            score=inc.score,
            rerank_score=inc.rerank_score,
        )
        for inc in result_state.retrieved_incidents
    ]

    return QueryResponse(
        session_id=session_id,
        recommendation=result_state.final_response or result_state.recommendation,
        root_cause=result_state.root_cause,
        confidence=result_state.confidence,
        failure_probability=result_state.failure_probability,
        escalation_triggered=result_state.escalation_triggered,
        escalation_reason=result_state.escalation_reason,
        retrieved_incidents=incidents,
        citations=result_state.citations,
        anomalies=[a.model_dump() for a in result_state.anomalies],
        correlation_summary=result_state.correlation_summary,
        maintenance_patterns=result_state.maintenance_patterns,
        output_warning=result_state.output_warning,
        fallback_triggered=result_state.fallback_triggered,
        awaiting_human_review=result_state.awaiting_human_review,
        agent_messages=[
            {"role": m.role.value, "content": m.content}
            for m in result_state.messages[-10:]
        ],
    )


# ── Search-only endpoint ──────────────────────────────────────────────────────

@router.post("/search", response_model=SearchResponse)
async def search_endpoint(request: SearchRequest):
    """Hybrid search + rerank only (no agent pipeline)."""
    guard = check_input(request.query)
    if not guard.passed:
        raise HTTPException(status_code=422, detail=guard.reason)

    pinecone_filter = {}
    if request.equipment_type:
        pinecone_filter["equipment_type"] = {"$eq": request.equipment_type}
    if request.hospital_unit:
        pinecone_filter["hospital_unit"] = {"$eq": request.hospital_unit}

    raw = hybrid_search(
        query=request.query,
        top_k=min(request.top_k * 3, 20),
        filter=pinecone_filter or None,
    )
    reranked = rerank(request.query, raw, top_k=request.top_k)

    results = [
        IncidentResult(
            id=r["id"],
            equipment_type=r.get("metadata", {}).get("equipment_type", ""),
            hospital_unit=r.get("metadata", {}).get("hospital_unit", ""),
            severity=r.get("metadata", {}).get("severity", ""),
            failure_type=r.get("metadata", {}).get("failure_type", ""),
            text=r.get("text", "")[:300],
            score=r.get("rrf_score", r.get("score", 0.0)),
            rerank_score=r.get("rerank_score"),
        )
        for r in reranked
    ]
    return SearchResponse(results=results, total=len(results))


# ── Human review endpoint ─────────────────────────────────────────────────────

@router.post("/review", response_model=ReviewResponse)
async def review_endpoint(request: ReviewRequest):
    """
    Human-in-the-loop review endpoint.
    Resumes paused graph with Approve / Reject / Edit action.
    """
    state = _sessions.get(request.session_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Session {request.session_id} not found.")

    state.human_review_action    = request.action
    state.human_edited_response  = request.edited_response
    state.awaiting_human_review  = False

    # Apply action
    if request.action == HumanReviewAction.APPROVE:
        state.final_response = state.recommendation
    elif request.action == HumanReviewAction.EDIT and request.edited_response:
        state.final_response = request.edited_response
        state.recommendation = request.edited_response
    elif request.action == HumanReviewAction.REJECT:
        state.final_response = (
            "Recommendation rejected by reviewing engineer. Escalate to senior staff."
        )

    _sessions[request.session_id] = state

    # Log HITL decision to LangSmith as feedback signal
    run_id = _run_ids.get(request.session_id, "")
    if run_id:
        comment = request.edited_response[:200] if request.edited_response else ""
        log_hitl_feedback(run_id, request.action.value, comment)

    return ReviewResponse(
        session_id=request.session_id,
        action=request.action.value,
        final_response=state.final_response,
        status="completed",
    )


# ── Evaluation endpoint ───────────────────────────────────────────────────────

@router.post("/evaluate")
async def evaluate_endpoint(request: EvalRequest, background_tasks: BackgroundTasks):
    """Run DeepEval suite (async background task to avoid timeout)."""
    from app.evaluation.deepeval_suite import run_evaluation

    def _run():
        return run_evaluation(request.query_results)

    background_tasks.add_task(_run)
    return {
        "status": "Evaluation started in background",
        "message": "Results will be logged. Check /api/eval-results for status.",
    }


# ── Health check ──────────────────────────────────────────────────────────────

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """System health check."""
    from app.core.pinecone_client import get_pinecone_index

    try:
        idx = get_pinecone_index()
        stats = idx.describe_index_stats()
        vectordb_status = f"ok ({stats.total_vector_count} vectors)"
    except Exception as e:
        vectordb_status = f"error: {str(e)}"

    return HealthResponse(
        status="healthy",
        vectordb=vectordb_status,
        bm25_index_size=len(_bm25_corpus),
    )


# ── Device stats endpoint ─────────────────────────────────────────────────────

def _load_corpus_from_csv() -> list:
    """Load narratives directly from CSV files without embeddings."""
    import os
    import csv as csv_mod
    from app.data.narrative_generator import generate_narratives

    base = os.path.join(os.path.dirname(__file__), "..", "..", "data")
    csv1 = os.path.abspath(os.path.join(base, "ai4i2020.csv"))
    csv2 = os.path.abspath(os.path.join(base, "predictive_maintenance.csv"))

    rows = []
    for path, source in [(csv1, "ai4i"), (csv2, "pred_maint")]:
        if os.path.exists(path):
            with open(path, newline="", encoding="utf-8-sig") as f:
                rows += [(dict(r), source) for r in csv_mod.DictReader(f)]

    corpus = []
    for row, source in rows:
        try:
            doc = generate_narratives([row], source=source)[0]
            corpus.append(doc)
        except Exception:
            continue
    return corpus


@router.get("/device-stats")
async def device_stats():
    """Aggregate failure stats per device type for dashboard."""
    from collections import Counter
    from app.core.hybrid_search import _bm25_corpus

    corpus = _bm25_corpus
    if not corpus:
        corpus = _load_corpus_from_csv()

    if not corpus:
        return {"stats": [], "message": "Data not loaded yet"}

    failure_counts: Counter = Counter()
    device_counts: Counter = Counter()

    for doc in corpus:
        meta = doc.get("metadata", {})
        device = meta.get("equipment_type", "Unknown")
        failure = meta.get("machine_failure", 0)
        device_counts[device] += 1
        if int(failure) == 1:
            failure_counts[device] += 1

    stats = [
        {
            "device": device,
            "total": device_counts[device],
            "failures": failure_counts.get(device, 0),
            "failure_rate": round(failure_counts.get(device, 0) / max(device_counts[device], 1), 3),
        }
        for device in device_counts
    ]
    stats.sort(key=lambda x: x["failure_rate"], reverse=True)
    return {"stats": stats[:16]}
