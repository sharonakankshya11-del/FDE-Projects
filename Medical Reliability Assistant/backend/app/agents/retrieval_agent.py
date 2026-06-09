"""
app/agents/retrieval_agent.py
Retrieval Agent — executes hybrid search + cross-encoder reranking.
Populates state.retrieved_incidents and state.retrieval_context.
Sends A2A message to supervisor on completion.
"""
import asyncio
from typing import Dict, Any
from app.agents.state import AgentState, MessageRole, RetrievedIncident
from app.core.hybrid_search import hybrid_search
from app.core.reranker import rerank
from app.core.config import get_settings
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

AGENT_TIMEOUT = 30  # seconds


def _build_pinecone_filter(state: AgentState) -> Dict[str, Any]:
    filt = {}
    if state.equipment_filter:
        filt["equipment_type"] = {"$eq": state.equipment_filter}
    if state.unit_filter:
        filt["hospital_unit"] = {"$eq": state.unit_filter}
    if state.severity_filter and state.severity_filter != "all":
        filt["severity"] = {"$eq": state.severity_filter}
    return filt if filt else None


def run_retrieval_agent(state: AgentState) -> AgentState:
    """
    Synchronous retrieval node for LangGraph.
    Falls back to empty results with fallback flag on error.
    """
    state.add_message(MessageRole.RETRIEVAL, "Starting hybrid search...")

    try:
        pinecone_filter = _build_pinecone_filter(state)
        raw_results = hybrid_search(
            query=state.sanitised_query,
            top_k=settings.top_k_retrieval,
            filter=pinecone_filter,
        )

        if not raw_results:
            state.add_message(
                MessageRole.RETRIEVAL,
                "No results from hybrid search. Broadening to unfiltered search."
            )
            raw_results = hybrid_search(query=state.sanitised_query, top_k=settings.top_k_retrieval)

        # Cross-encoder rerank
        reranked = rerank(
            query=state.sanitised_query,
            documents=raw_results,
            top_k=settings.top_k_rerank,
        )

        incidents = []
        context_parts = []
        for doc in reranked:
            meta = doc.get("metadata", {})
            inc = RetrievedIncident(
                id=doc["id"],
                text=doc.get("text", meta.get("text", "")),
                equipment_type=meta.get("equipment_type", ""),
                hospital_unit=meta.get("hospital_unit", ""),
                severity=meta.get("severity", ""),
                failure_type=meta.get("failure_type", ""),
                score=doc.get("rrf_score", doc.get("score", 0.0)),
                rerank_score=doc.get("rerank_score"),
            )
            incidents.append(inc)
            context_parts.append(f"[Incident {inc.id}] {inc.text}")

        state.retrieved_incidents = incidents
        state.retrieval_context = "\n\n".join(context_parts)

        state.add_message(
            MessageRole.RETRIEVAL,
            f"Retrieved {len(incidents)} incidents after reranking. "
            f"Top incident: {incidents[0].failure_type if incidents else 'N/A'}",
            incident_count=len(incidents),
        )

        logger.info(f"Retrieval complete: {len(incidents)} incidents for session {state.session_id}")

    except Exception as e:
        logger.error(f"Retrieval agent error: {e}", exc_info=True)
        state.trigger_fallback("retrieval_agent", str(e))
        state.retrieval_context = "No historical incidents could be retrieved due to a system error."

    return state
