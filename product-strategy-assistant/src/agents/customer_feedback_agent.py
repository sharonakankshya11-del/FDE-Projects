from __future__ import annotations

from .base import BaseAgent
from ..state import StrategyState


class CustomerFeedbackAgent(BaseAgent):
    name = "Customer Feedback Agent"
    output_key = "customer_feedback"
    persona = (
        "You are a Customer Insights Analyst. You read customer reviews, ratings and "
        "return data to surface what customers love, what frustrates them, and which "
        "products are at risk. You are precise, evidence-based and quantitative."
    )

    def build_prompt(self, state: StrategyState) -> str:
        reviews = [
            d["text"]
            for d in state.get("documents", [])
            if d.get("metadata", {}).get("source") == "customer_review"
        ][:60]
        review_block = "\n".join(f"- {r}" for r in reviews) or "(no review text available)"
        return (
            f"{self.context_block(state)}"
            "Structured analytics:\n"
            f"{self.fmt_summary(state)}\n\n"
            "Customer reviews (sample):\n"
            f"{review_block}\n\n"
            "Produce a CUSTOMER INSIGHTS REPORT in markdown with:\n"
            "1. Overall sentiment summary (reference the sentiment counts and avg rating).\n"
            "2. Top 3 strengths customers praise (with product examples).\n"
            "3. Top 3 pain points / complaints (with product examples).\n"
            "4. Products at risk (tie to lowest ratings / highest returns).\n"
            "5. 3 concrete, actionable recommendations.\n"
            "Be concise and use bullet points."
        )
