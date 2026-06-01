from __future__ import annotations

from .base import BaseAgent
from ..state import StrategyState


class OpportunityAgent(BaseAgent):
    name = "Opportunity Analysis Agent"
    output_key = "opportunities"
    persona = (
        "You are a Growth/Opportunity Analyst. You identify the highest-value product "
        "and market opportunities and score them so the team can compare them objectively."
    )

    def build_prompt(self, state: StrategyState) -> str:
        return (
            f"{self.context_block(state)}"
            f"SWOT:\n{state.get('swot', '(n/a)')}\n\n"
            f"MARKET RESEARCH:\n{state.get('market_research', '(n/a)')}\n\n"
            f"CUSTOMER FEEDBACK:\n{state.get('customer_feedback', '(n/a)')}\n\n"
            "Identify 4-6 strategic opportunities. Produce a PRODUCT OPPORTUNITY "
            "ASSESSMENT in markdown. For EACH opportunity provide a one-line description "
            "and an Opportunity Score out of 100 derived from Impact, Confidence and "
            "Strategic-fit (briefly justify the score). Present them as a ranked markdown "
            "table sorted by score (columns: Opportunity, Impact, Confidence, Fit, Score), "
            "followed by a 2-sentence rationale for the top opportunity. Be concise."
        )
