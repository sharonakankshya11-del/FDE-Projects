from __future__ import annotations

from .base import BaseAgent
from ..state import StrategyState


class MarketResearchAgent(BaseAgent):
    name = "Market Research Agent"
    output_key = "market_research"
    persona = (
        "You are a Market Research Analyst. You interpret sales performance across "
        "categories, regions and time to explain market dynamics, demand patterns and "
        "where growth is concentrated. You combine the numbers with sensible market reasoning."
    )

    def build_prompt(self, state: StrategyState) -> str:
        docs = [
            d["text"]
            for d in state.get("documents", [])
            if d.get("metadata", {}).get("source") not in {"customer_review", "kpi_summary"}
        ][:15]
        doc_block = "\n".join(f"- {d}" for d in docs) or "(no external market documents uploaded)"
        return (
            f"{self.context_block(state)}"
            "Structured analytics:\n"
            f"{self.fmt_summary(state)}\n\n"
            "Uploaded market/research material (if any):\n"
            f"{doc_block}\n\n"
            "Produce a MARKET RESEARCH SUMMARY in markdown with:\n"
            "1. Which categories and regions are driving revenue and profit.\n"
            "2. Demand patterns and notable concentrations or risks.\n"
            "3. Margin observations (where the business makes vs. loses money).\n"
            "4. 3 market-level takeaways for the product strategy.\n"
            "Ground every claim in the data above. Be concise."
        )
