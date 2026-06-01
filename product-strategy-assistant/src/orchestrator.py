"""Multi-agent orchestration.

Primary path builds a LangGraph ``StateGraph`` where each agent is a node that
reads and writes a shared :class:`StrategyState` blackboard. Agents collaborate
through this shared state — each one enriches it for the next:

    Customer Feedback -> Market Research -> Competitor Analysis -> SWOT ->
    Opportunities -> Feature Prioritization -> Strategy -> Executive Report

Downstream agents (SWOT, Opportunities, Strategy, Executive) explicitly consume
the outputs written by upstream agents, so this is genuine collaboration rather
than eight isolated calls. If LangGraph is unavailable the same agents run
sequentially with identical results, so the app always works.
"""
from __future__ import annotations

import operator
from typing import Annotated, Callable, Dict, List, Optional

from typing_extensions import TypedDict

from .agents import (
    CompetitorAnalysisAgent,
    CustomerFeedbackAgent,
    ExecutiveReportAgent,
    FeaturePrioritizationAgent,
    MarketResearchAgent,
    OpportunityAgent,
    StrategyAgent,
    SWOTAgent,
)

# Ordered for the sequential fallback and the UI timeline.
AGENT_PIPELINE = [
    CustomerFeedbackAgent(),
    MarketResearchAgent(),
    CompetitorAnalysisAgent(),
    SWOTAgent(),
    OpportunityAgent(),
    FeaturePrioritizationAgent(),
    StrategyAgent(),
    ExecutiveReportAgent(),
]

ProgressCb = Optional[Callable[[str], None]]


class _GraphState(TypedDict, total=False):
    structured_summary: dict
    documents: list
    product_context: str
    customer_feedback: str
    market_research: str
    competitor_analysis: str
    swot: str
    opportunities: str
    feature_prioritization: str
    strategy: str
    executive_summary: str
    trace: Annotated[List[str], operator.add]


def _node(agent):
    def fn(state):
        result = agent.run(state)
        # Normalise trace to a single-element contribution for the add-reducer.
        return {agent.output_key: result[agent.output_key], "trace": [agent.name]}

    return fn


def build_graph():
    from langgraph.graph import END, START, StateGraph

    g = StateGraph(_GraphState)
    for agent in AGENT_PIPELINE:
        g.add_node(agent.name, _node(agent))

    # Linear chain over shared state: each agent enriches the blackboard the
    # next one reads. This is deterministic and runs every agent exactly once.
    names = [a.name for a in AGENT_PIPELINE]
    g.add_edge(START, names[0])
    for a, b in zip(names, names[1:]):
        g.add_edge(a, b)
    g.add_edge(names[-1], END)
    return g.compile()


def run_analysis(state: Dict, progress_cb: ProgressCb = None) -> Dict:
    """Run the full multi-agent pipeline, returning the populated state."""
    state.setdefault("trace", [])
    try:
        graph = build_graph()
        final: Dict = dict(state)
        for step in graph.stream(state, stream_mode="updates"):
            for node_name, update in step.items():
                update = dict(update)
                update.pop("trace", None)  # rebuilt below from execution order
                final.update(update)
                final["trace"] = list(final.get("trace", [])) + [node_name]
                if progress_cb:
                    progress_cb(node_name)
        return final
    except Exception:
        return _run_sequential(state, progress_cb)


def _run_sequential(state: Dict, progress_cb: ProgressCb = None) -> Dict:
    for agent in AGENT_PIPELINE:
        out = agent.run(state)
        state[agent.output_key] = out[agent.output_key]
        state["trace"] = list(state.get("trace", [])) + [agent.name]
        if progress_cb:
            progress_cb(agent.name)
    return state
