"""Base class for all analysis agents.

An agent is a focused specialist: it has a name, a system persona, and a
`run(state)` method that reads the shared state, calls the LLM with a built
prompt, and returns the section of state it owns.
"""
from __future__ import annotations

import json
from typing import Any, Dict

from ..llm import complete
from ..state import StrategyState


class BaseAgent:
    name: str = "Agent"
    output_key: str = "output"
    persona: str = "You are a helpful product analyst."

    def build_prompt(self, state: StrategyState) -> str:  # pragma: no cover - overridden
        raise NotImplementedError

    def run(self, state: StrategyState) -> Dict[str, Any]:
        prompt = self.build_prompt(state)
        result = complete(self.persona, prompt)
        trace = list(state.get("trace", [])) + [self.name]
        return {self.output_key: result, "trace": trace}

    # --- helpers available to all agents ---
    @staticmethod
    def fmt_summary(state: StrategyState) -> str:
        return json.dumps(state.get("structured_summary", {}), indent=2, default=str)

    @staticmethod
    def context_block(state: StrategyState) -> str:
        ctx = state.get("product_context", "").strip()
        return f"Product/company context provided by the PM:\n{ctx}\n\n" if ctx else ""
