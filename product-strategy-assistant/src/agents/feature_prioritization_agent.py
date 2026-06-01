from __future__ import annotations

from .base import BaseAgent
from ..state import StrategyState


class FeaturePrioritizationAgent(BaseAgent):
    name = "Feature Prioritization Agent"
    output_key = "feature_prioritization"
    persona = (
        "You are a Senior Product Manager who prioritises features using the RICE "
        "framework (Reach, Impact, Confidence, Effort). You translate insights into a "
        "concrete, defensible backlog."
    )

    def build_prompt(self, state: StrategyState) -> str:
        return (
            f"{self.context_block(state)}"
            f"OPPORTUNITIES:\n{state.get('opportunities', '(n/a)')}\n\n"
            f"CUSTOMER FEEDBACK:\n{state.get('customer_feedback', '(n/a)')}\n\n"
            f"SWOT:\n{state.get('swot', '(n/a)')}\n\n"
            "Propose 6-8 candidate features/initiatives that address the findings. "
            "Produce FEATURE PRIORITIZATION RECOMMENDATIONS in markdown as a table with "
            "columns: Feature, Reach (1-10), Impact (1-5), Confidence (%), Effort "
            "(person-months), RICE Score. Compute RICE = (Reach*Impact*Confidence)/Effort "
            "and sort descending. After the table, give a short 'Build now / Next / Later' "
            "grouping. Be concise and realistic."
        )
