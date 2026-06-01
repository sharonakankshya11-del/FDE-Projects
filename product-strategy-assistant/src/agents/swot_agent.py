from __future__ import annotations

from .base import BaseAgent
from ..state import StrategyState


class SWOTAgent(BaseAgent):
    name = "SWOT Analysis Agent"
    output_key = "swot"
    persona = (
        "You are a Strategy Analyst who synthesises inputs from other analysts into a "
        "rigorous SWOT. You do not invent facts; you consolidate what upstream agents found."
    )

    def build_prompt(self, state: StrategyState) -> str:
        return (
            f"{self.context_block(state)}"
            "Synthesise the findings below into a SWOT analysis.\n\n"
            f"CUSTOMER FEEDBACK:\n{state.get('customer_feedback', '(n/a)')}\n\n"
            f"MARKET RESEARCH:\n{state.get('market_research', '(n/a)')}\n\n"
            f"COMPETITOR ANALYSIS:\n{state.get('competitor_analysis', '(n/a)')}\n\n"
            "Output a SWOT ANALYSIS in markdown with four clearly headed sections "
            "(### Strengths, ### Weaknesses, ### Opportunities, ### Threats), 3-5 bullets "
            "each, every bullet tied to specific evidence from above. Be concise."
        )
