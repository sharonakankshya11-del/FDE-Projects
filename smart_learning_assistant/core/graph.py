"""
core/graph.py
LangGraph Workflow Orchestration — Hierarchical Workflow with Guardrails

Full pipeline:

  [INPUT GUARDRAIL]
       ↓ pass                    ↓ fail → END
  [SUPERVISOR]  ← detects intent, delegates agents
       ↓ retrieval needed        ↓ no retrieval (recommend_topics)
  [RETRIEVAL]               [GENERATION]
       ↓                         ↓
  [GENERATION]             [REVIEWER]
       ↓                         ↓
  [REVIEWER]              [RESPONSE]
       ↓                         ↓
  [RESPONSE]           [OUTPUT GUARDRAIL] → END
       ↓
  [OUTPUT GUARDRAIL] → END

Two routing decisions:
  A. route_after_input_guardrail  — block unsafe queries immediately
  B. route_after_supervisor       — skip retrieval for recommend_topics
"""

import logging
from typing import Literal
from langgraph.graph import StateGraph, END

from core.state import AgentState
from agents.input_guardrail  import input_guardrail
from agents.supervisor_agent import supervisor_agent
from agents.retrieval_agent  import retrieval_agent
from agents.generation_agent import generation_agent
from agents.reviewer_agent   import reviewer_agent
from agents.response_agent   import response_agent
from agents.output_guardrail import output_guardrail

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Routing functions
# ---------------------------------------------------------------------------

def route_after_input_guardrail(
    state: AgentState,
) -> Literal["supervisor", "end"]:
    """
    If the input guardrail blocked the query → go straight to END
    (final_response is already set to the block message).
    Otherwise → hand off to the Supervisor.
    """
    if state.get("is_safe", False):
        return "supervisor"
    logger.info("[Graph] Input guardrail blocked query — routing to END")
    return "end"


def route_after_supervisor(
    state: AgentState,
) -> Literal["retrieval", "generation"]:
    """
    Hierarchical delegation:
      • 'retrieval' in agents_to_run → fetch context first (Path A)
      • otherwise                    → skip retrieval      (Path B)
    """
    agents = state.get("agents_to_run", [])
    if "retrieval" in agents:
        return "retrieval"
    return "generation"


# ---------------------------------------------------------------------------
# Build graph
# ---------------------------------------------------------------------------

def build_graph() -> StateGraph:
    """
    Compiles the full hierarchical multi-agent graph with input and
    output guardrails bookending the pipeline.
    """
    builder = StateGraph(AgentState)

    # ── Register nodes ───────────────────────────────────────────────────────
    builder.add_node("input_guardrail",  input_guardrail)
    builder.add_node("supervisor",       supervisor_agent)
    builder.add_node("retrieval",        retrieval_agent)
    builder.add_node("generation",       generation_agent)
    builder.add_node("reviewer",         reviewer_agent)
    builder.add_node("response",         response_agent)
    builder.add_node("output_guardrail", output_guardrail)

    # ── Entry point ──────────────────────────────────────────────────────────
    builder.set_entry_point("input_guardrail")

    # ── Edge: Input Guardrail → Supervisor | END ─────────────────────────────
    builder.add_conditional_edges(
        "input_guardrail",
        route_after_input_guardrail,
        {"supervisor": "supervisor", "end": END},
    )

    # ── Edge: Supervisor → Retrieval | Generation (hierarchical routing) ─────
    builder.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {"retrieval": "retrieval", "generation": "generation"},
    )

    # ── Edge: Retrieval → Generation ─────────────────────────────────────────
    builder.add_edge("retrieval", "generation")

    # ── Edge: Generation → Reviewer ──────────────────────────────────────────
    builder.add_edge("generation", "reviewer")

    # ── Edge: Reviewer → Response ────────────────────────────────────────────
    builder.add_edge("reviewer", "response")

    # ── Edge: Response → Output Guardrail ────────────────────────────────────
    builder.add_edge("response", "output_guardrail")

    # ── Edge: Output Guardrail → END ─────────────────────────────────────────
    builder.add_edge("output_guardrail", END)

    return builder.compile()


# ---------------------------------------------------------------------------
# Convenience runner
# ---------------------------------------------------------------------------

def run_query(query: str, history: "list | None" = None) -> AgentState:
    """
    Run the full guardrailed hierarchical pipeline for a single query.
    """
    graph = build_graph()

    initial_state: AgentState = {
        "user_query":              query,
        "sanitized_query":         "",
        "is_safe":                 False,
        "security_reason":         "",
        "input_guardrail_checks":  {},
        "intent":                  "",
        "workflow_type":           "hierarchical",
        "agents_to_run":           [],
        "retrieved_docs":          [],
        "retrieval_context":       "",
        "generated_response":      "",
        "review_passed":           False,
        "review_feedback":         "",
        "revision_count":          0,
        "eval_scores":             {},
        "eval_passed":             False,
        "final_response":          "",
        "confidence_score":        0.0,
        "sources":                 [],
        "follow_up_topics":        [],
        "output_guardrail_passed": True,
        "output_guardrail_checks": {},
        "output_guardrail_reason": "",
        "conversation_history":    history or [],
        "error":                   None,
        "logs":                    [],
    }

    return graph.invoke(initial_state)
