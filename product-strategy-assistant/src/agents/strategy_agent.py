from __future__ import annotations

from .base import BaseAgent
from ..state import StrategyState


class StrategyAgent(BaseAgent):
    name = "Strategy Recommendation Agent"
    output_key = "strategy"
    persona = (
        "You are a Head of Product Strategy. You turn analysis into a clear strategic "
        "action plan and a phased product roadmap that leadership can act on."
    )

    def build_prompt(self, state: StrategyState) -> str:
        return (
            f"{self.context_block(state)}"
            f"SWOT:\n{state.get('swot', '(n/a)')}\n\n"
            f"OPPORTUNITIES:\n{state.get('opportunities', '(n/a)')}\n\n"
            f"PRIORITISED FEATURES:\n{state.get('feature_prioritization', '(n/a)')}\n\n"
            "Produce two sections in markdown:\n"
            "### Strategic Action Plan — 4-6 prioritised initiatives, each with the goal, "
            "the owner-type, and a success metric (KPI).\n"
            "### Product Roadmap — a phased roadmap with three horizons: Now (0-3 mo), "
            "Next (3-9 mo), Later (9-18 mo); 2-4 items per horizon mapped to the initiatives. "
            "Be concrete and concise."
        )
