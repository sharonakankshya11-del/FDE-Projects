from __future__ import annotations

from .base import BaseAgent
from ..state import StrategyState


class CompetitorAnalysisAgent(BaseAgent):
    name = "Competitor Analysis Agent"
    output_key = "competitor_analysis"
    persona = (
        "You are a Competitive Intelligence Analyst. You assess how the product line "
        "stacks up against typical market competitors, inferring positioning from price "
        "points, ratings and category mix. When competitor documents are provided you use them."
    )

    def build_prompt(self, state: StrategyState) -> str:
        return (
            f"{self.context_block(state)}"
            "Structured analytics (use ratings, margins and category mix as proxies for "
            "competitive positioning):\n"
            f"{self.fmt_summary(state)}\n\n"
            "Market research findings from the team:\n"
            f"{state.get('market_research', '(not yet available)')}\n\n"
            "Produce a COMPETITOR ANALYSIS REPORT in markdown with:\n"
            "1. Likely competitive positioning per category (premium / value / mid-market).\n"
            "2. Where the portfolio appears strong vs. vulnerable to competitors.\n"
            "3. Competitive threats to watch.\n"
            "4. 2-3 differentiation moves.\n"
            "If no competitor documents were uploaded, state assumptions explicitly. Be concise."
        )
