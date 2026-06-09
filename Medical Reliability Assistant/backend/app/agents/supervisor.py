"""
app/agents/supervisor.py

Hierarchical Supervisor — LangGraph StateGraph orchestrating:
  retrieval → analysis → maintenance → recommendation → human_review

Features:
  • Checkpoint persistence (SQLite) for resumption
  • Human-in-the-loop interrupt before final response
  • Escalation routing (high severity → expedited path)
  • Agent fallback: if any agent fails, supervisor injects fallback message
  • Timeout guard per agent node
"""
from __future__ import annotations
import asyncio
from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from app.agents.state import AgentState, MessageRole, HumanReviewAction
from app.agents.retrieval_agent import run_retrieval_agent
from app.agents.analysis_agent import run_analysis_agent
from app.agents.maintenance_agent import run_maintenance_agent
from app.agents.recommendation_agent import run_recommendation_agent
from app.guardrails.output_guardrails import run_output_guardrails
from app.core.config import get_settings
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

AGENT_TIMEOUT = 45  # seconds per agent node


# ── Node wrappers (sync → async with timeout) ─────────────────────────────────

async def _with_timeout(fn, state: AgentState, agent_name: str) -> AgentState:
    """Run a sync agent function in a thread with timeout."""
    try:
        loop = asyncio.get_event_loop()
        result = await asyncio.wait_for(
            loop.run_in_executor(None, fn, state),
            timeout=AGENT_TIMEOUT,
        )
        return result
    except asyncio.TimeoutError:
        logger.error(f"{agent_name} timed out after {AGENT_TIMEOUT}s")
        state.trigger_fallback(agent_name, f"Timed out after {AGENT_TIMEOUT} seconds")
        return state
    except Exception as e:
        logger.error(f"{agent_name} unexpected error: {e}", exc_info=True)
        state.trigger_fallback(agent_name, str(e))
        return state


async def node_retrieval(state: AgentState) -> AgentState:
    state.add_message(MessageRole.SUPERVISOR, "→ Dispatching to Retrieval Agent")
    return await _with_timeout(run_retrieval_agent, state, "retrieval_agent")


async def node_analysis(state: AgentState) -> AgentState:
    state.add_message(MessageRole.SUPERVISOR, "→ Dispatching to Analysis Agent")
    return await _with_timeout(run_analysis_agent, state, "analysis_agent")


async def node_maintenance(state: AgentState) -> AgentState:
    state.add_message(MessageRole.SUPERVISOR, "→ Dispatching to Maintenance Agent")
    return await _with_timeout(run_maintenance_agent, state, "maintenance_agent")


async def node_recommendation(state: AgentState) -> AgentState:
    state.add_message(MessageRole.SUPERVISOR, "→ Dispatching to Recommendation Agent")
    return await _with_timeout(run_recommendation_agent, state, "recommendation_agent")


async def node_output_guardrail(state: AgentState) -> AgentState:
    """Run output safety check."""
    state = run_output_guardrails(state)
    return state


async def node_human_review(state: AgentState) -> AgentState:
    """
    Human-in-the-loop pause point.
    Graph will interrupt here; resumed via /api/review endpoint
    which sets state.human_review_action.
    """
    state.awaiting_human_review = True
    state.add_message(
        MessageRole.SUPERVISOR,
        "⏸ Awaiting human review. Engineer may Approve / Reject / Edit.",
    )
    return state


async def node_apply_human_review(state: AgentState) -> AgentState:
    """Apply human decision to final response."""
    action = state.human_review_action

    if action == HumanReviewAction.APPROVE or action == HumanReviewAction.SKIP:
        state.final_response = state.recommendation
        state.add_message(MessageRole.HUMAN, "✅ Recommendation approved.")

    elif action == HumanReviewAction.EDIT and state.human_edited_response:
        state.final_response = state.human_edited_response
        state.recommendation = state.human_edited_response
        state.add_message(MessageRole.HUMAN, "✏️ Recommendation edited and accepted.")

    elif action == HumanReviewAction.REJECT:
        state.final_response = (
            "This recommendation was rejected by the reviewing engineer. "
            "Please escalate to senior biomedical engineering staff."
        )
        state.add_message(MessageRole.HUMAN, "❌ Recommendation rejected.")

    else:
        # Default: auto-approve if no action set (e.g. async flow)
        state.final_response = state.recommendation

    state.awaiting_human_review = False
    return state


async def node_compile_fallback(state: AgentState) -> AgentState:
    """Build a safe fallback response if multiple agents failed."""
    state.final_response = (
        f"{state.fallback_message}\n\n"
        "Partial analysis results:\n"
        + (state.correlation_summary or "No analysis available.")
        + "\n\n"
        + "Please consult your CMMS and escalate to senior engineering staff."
    )
    state.add_message(MessageRole.SUPERVISOR, "⚠ Fallback response compiled.")
    return state


# ── Routing functions ─────────────────────────────────────────────────────────

def route_after_analysis(state: AgentState) -> Literal["maintenance", "fallback"]:
    if state.fallback_triggered and not state.correlation_summary:
        return "fallback"
    return "maintenance"


def route_after_recommendation(state: AgentState) -> Literal["output_guardrail", "fallback"]:
    if state.fallback_triggered and not state.recommendation:
        return "fallback"
    return "output_guardrail"


def route_after_guardrail(state: AgentState) -> Literal["human_review", "compile"]:
    if not state.output_safe:
        # Skip human review for unsafe output; go straight to safe compile
        return "compile"
    return "human_review"


def route_after_human(state: AgentState) -> Literal["apply_review", END]:
    if state.awaiting_human_review and state.human_review_action is None:
        return END  # graph paused; resumed by /api/review
    return "apply_review"


# ── Build graph ───────────────────────────────────────────────────────────────

def build_supervisor_graph(checkpointer=None) -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("retrieval", node_retrieval)
    graph.add_node("analysis", node_analysis)
    graph.add_node("maintenance", node_maintenance)
    graph.add_node("recommendation", node_recommendation)
    graph.add_node("output_guardrail", node_output_guardrail)
    graph.add_node("human_review", node_human_review)
    graph.add_node("apply_review", node_apply_human_review)
    graph.add_node("fallback", node_compile_fallback)

    graph.set_entry_point("retrieval")

    graph.add_edge("retrieval", "analysis")
    graph.add_conditional_edges("analysis", route_after_analysis, {
        "maintenance": "maintenance",
        "fallback": "fallback",
    })
    graph.add_edge("maintenance", "recommendation")
    graph.add_conditional_edges("recommendation", route_after_recommendation, {
        "output_guardrail": "output_guardrail",
        "fallback": "fallback",
    })
    graph.add_conditional_edges("output_guardrail", route_after_guardrail, {
        "human_review": "human_review",
        "compile": "apply_review",
    })
    graph.add_conditional_edges("human_review", route_after_human, {
        "apply_review": "apply_review",
        END: END,
    })
    graph.add_edge("apply_review", END)
    graph.add_edge("fallback", END)

    if checkpointer:
        return graph.compile(
            checkpointer=checkpointer,
            interrupt_before=["human_review"],
        )
    return graph.compile()


# Singleton compiled graph (no checkpointer for simple sync use)
_graph = None


def get_graph(checkpointer=None):
    global _graph
    if _graph is None:
        _graph = build_supervisor_graph(checkpointer)
    return _graph
