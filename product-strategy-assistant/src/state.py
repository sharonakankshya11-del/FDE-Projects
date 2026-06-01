"""Shared state passed through the multi-agent graph (a 'blackboard').

Each agent reads upstream agents' results from this state and writes its own,
which is how agents collaborate without calling each other directly.
"""
from __future__ import annotations

from typing import Any, Dict, List, TypedDict


class StrategyState(TypedDict, total=False):
    # Inputs
    structured_summary: Dict[str, Any]
    documents: List[Dict[str, Any]]
    product_context: str  # short free-text description of the product / company

    # Agent outputs (filled progressively)
    customer_feedback: str
    market_research: str
    competitor_analysis: str
    swot: str
    opportunities: str
    feature_prioritization: str
    strategy: str
    executive_summary: str

    # Trace of which agents ran (for the UI timeline)
    trace: List[str]
