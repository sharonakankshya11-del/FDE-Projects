"""
app/guardrails/output_guardrails.py
Output guardrails applied AFTER recommendation generation.
Checks:
  1. Length / completeness sanity check
  2. Harmful content detection (no dangerous clinical directives)
  3. Hallucination / grounding check via GPT-4o-mini
  4. Confidence calibration warning
"""
import re
import openai
from app.agents.state import AgentState
from app.core.config import get_settings
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

_client = openai.OpenAI(
    api_key=settings.openai_api_key,
    base_url=settings.openai_base_url,
)

HALLUCINATION_PROMPT = """You are a medical AI safety reviewer.

Retrieved context provided to the AI:
---
{context}
---

AI-generated recommendation:
---
{recommendation}
---

Check: Does the recommendation make specific factual claims NOT supported by the retrieved context above?
Respond with JSON only: {{"hallucination_risk": "low|medium|high", "reason": "brief reason"}}"""

HARMFUL_PATTERNS = [
    r"administer\s+\w+\s+mg",    # drug dosage instructions
    r"diagnos[ei]s\s+of\s+",     # clinical diagnosis
    r"patient\s+should\s+take",  # patient medication instructions
    r"surgery\s+required",        # surgical recommendations beyond scope
]


def run_output_guardrails(state: AgentState) -> AgentState:
    """Check recommendation safety and grounding."""
    recommendation = state.recommendation

    # 1. Empty response
    if not recommendation or len(recommendation.strip()) < 50:
        state.output_safe = False
        state.output_warning = "Recommendation was empty or too short. Fallback triggered."
        state.trigger_fallback("output_guardrail", "Empty recommendation")
        return state

    # 2. Harmful content patterns
    lower = recommendation.lower()
    for pattern in HARMFUL_PATTERNS:
        if re.search(pattern, lower):
            logger.warning(f"Harmful output pattern detected: {pattern}")
            state.output_safe = False
            state.output_warning = (
                "Recommendation contained out-of-scope clinical content and was blocked. "
                "Please consult a licensed medical professional for patient care decisions."
            )
            state.recommendation = state.output_warning
            return state

    # 3. Hallucination check via GPT-4o-mini (only if we have context)
    if state.retrieval_context and len(state.retrieval_context) > 100:
        try:
            response = _client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=100,
                messages=[{
                    "role": "user",
                    "content": HALLUCINATION_PROMPT.format(
                        context=state.retrieval_context[:2000],
                        recommendation=recommendation[:1500],
                    )
                }],
            )
            text = response.choices[0].message.content.strip()
            if '"hallucination_risk": "high"' in text.lower():
                state.output_warning = (
                    "⚠ Note: This recommendation may contain statements not fully supported "
                    "by retrieved historical incidents. Please verify before acting."
                )
                logger.warning(f"High hallucination risk detected for session {state.session_id}")
        except Exception as e:
            logger.warning(f"Hallucination check failed (skipping): {e}")

    # 4. Low confidence warning
    if state.confidence < 0.6:
        state.output_warning = (
            (state.output_warning + " " if state.output_warning else "")
            + f"⚠ Low confidence ({state.confidence:.0%}). Additional inspection recommended."
        )

    state.output_safe = True
    return state
