from __future__ import annotations

from .base import BaseAgent
from ..state import StrategyState


class ExecutiveReportAgent(BaseAgent):
    name = "Executive Report Agent"
    output_key = "executive_summary"
    persona = (
        "You are a Chief Product Officer writing for the executive team. You distil all "
        "analysis into a crisp, decision-oriented executive summary."
    )

    def build_prompt(self, state: StrategyState) -> str:
        return (
            f"{self.context_block(state)}"
            "Write an EXECUTIVE SUMMARY (max ~250 words) for senior leadership that "
            "synthesises the analysis below. Open with a one-paragraph situation "
            "assessment, then '### Top 3 Recommendations' as bullets, then a closing line "
            "on expected impact. Avoid repeating tables verbatim.\n\n"
            f"CUSTOMER FEEDBACK:\n{state.get('customer_feedback', '(n/a)')}\n\n"
            f"MARKET RESEARCH:\n{state.get('market_research', '(n/a)')}\n\n"
            f"COMPETITOR ANALYSIS:\n{state.get('competitor_analysis', '(n/a)')}\n\n"
            f"SWOT:\n{state.get('swot', '(n/a)')}\n\n"
            f"OPPORTUNITIES:\n{state.get('opportunities', '(n/a)')}\n\n"
            f"STRATEGY & ROADMAP:\n{state.get('strategy', '(n/a)')}\n"
        )
