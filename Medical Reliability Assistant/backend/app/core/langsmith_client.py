"""
app/core/langsmith_client.py
LangSmith observability integration.

Responsibilities:
  - Configure environment variables so LangGraph auto-traces every run
  - Provide a typed client for logging HITL feedback
  - Expose a helper to build per-query run metadata
"""
import os
from typing import Optional, Dict, Any
from app.core.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

_client = None   # lazy-initialised langsmith.Client


def init_langsmith() -> bool:
    """
    Set LangChain/LangSmith env vars from settings.
    Call once at app startup. Returns True if tracing is enabled.
    """
    if not settings.langchain_api_key or settings.langchain_api_key == "your-langsmith-api-key-here":
        logger.info("LangSmith tracing DISABLED — set LANGCHAIN_API_KEY in .env to enable")
        return False

    os.environ["LANGCHAIN_TRACING_V2"]  = "true"
    os.environ["LANGCHAIN_API_KEY"]      = settings.langchain_api_key
    os.environ["LANGCHAIN_PROJECT"]      = settings.langchain_project
    os.environ["LANGCHAIN_ENDPOINT"]     = settings.langchain_endpoint

    logger.info(
        f"LangSmith tracing ENABLED → project: '{settings.langchain_project}' "
        f"| endpoint: {settings.langchain_endpoint}"
    )
    return True


def get_client():
    """Return a cached langsmith.Client (only if tracing is active)."""
    global _client
    if _client is None and os.getenv("LANGCHAIN_API_KEY"):
        try:
            from langsmith import Client
            _client = Client(
                api_key=settings.langchain_api_key,
                api_url=settings.langchain_endpoint,
            )
        except Exception as e:
            logger.warning(f"LangSmith client init failed: {e}")
    return _client


def build_run_config(
    session_id: str,
    equipment_type: Optional[str] = None,
    hospital_unit: Optional[str] = None,
    severity: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build the LangGraph run config dict that attaches metadata and tags
    to every trace in LangSmith. Merges with the thread_id checkpoint config.
    """
    tags = ["dr-bleep", "query"]
    if equipment_type:
        tags.append(equipment_type.lower().replace(" ", "-"))
    if severity:
        tags.append(f"severity-{severity}")

    return {
        "configurable": {"thread_id": session_id},
        "run_name": f"query-{session_id[:8]}",
        "tags": tags,
        "metadata": {
            "session_id":     session_id,
            "equipment_type": equipment_type or "unspecified",
            "hospital_unit":  hospital_unit  or "unspecified",
            "severity":       severity        or "all",
            "project":        settings.langchain_project,
        },
    }


def log_hitl_feedback(
    run_id: str,
    action: str,
    comment: str = "",
) -> None:
    """
    Log the engineer's HITL decision (approve/edit/reject) as a
    feedback signal on the LangSmith run.

    Score mapping:
        approve → 1.0  (positive signal)
        edit    → 0.5  (partial signal — recommendation needed modification)
        reject  → 0.0  (negative signal)
    """
    client = get_client()
    if client is None:
        return

    score_map = {"approve": 1.0, "edit": 0.5, "reject": 0.0}
    score = score_map.get(action.lower(), 0.5)

    try:
        client.create_feedback(
            run_id=run_id,
            key="hitl_decision",
            score=score,
            value=action,
            comment=comment or f"Engineer action: {action}",
        )
        logger.info(f"LangSmith feedback logged: run={run_id[:8]} action={action} score={score}")
    except Exception as e:
        logger.warning(f"LangSmith feedback failed (non-critical): {e}")


def log_query_feedback(
    run_id: str,
    satisfied: bool,
    comment: str = "",
) -> None:
    """Generic user satisfaction feedback on a query run."""
    client = get_client()
    if client is None:
        return
    try:
        client.create_feedback(
            run_id=run_id,
            key="user_satisfaction",
            score=1.0 if satisfied else 0.0,
            comment=comment,
        )
    except Exception as e:
        logger.warning(f"LangSmith query feedback failed: {e}")
