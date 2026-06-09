"""
app/guardrails/input_guardrails.py
Input guardrails applied BEFORE the agent pipeline.
Checks:
  1. Length validation
  2. Empty / gibberish detection
  3. Prompt injection detection (heuristic)
  4. Topic relevance (medical/equipment domain check via LLM)
  5. PII already stripped by middleware, but double-checked here
"""
import re
from openai import OpenAI
from app.core.config import get_settings
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

_client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)

# Common injection patterns
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"you\s+are\s+now\s+(a\s+)?",
    r"disregard\s+.{0,30}instructions",
    r"system\s+prompt",
    r"jailbreak",
    r"<\s*script",
    r"DROP\s+TABLE",
    r";\s*--",
]

MEDICAL_TOPIC_PROMPT = """Classify this query as VALID or INVALID.

VALID: queries about medical equipment, hospital devices, maintenance, reliability, 
       failures, sensors, biomedical engineering, or equipment anomalies.
INVALID: queries about unrelated topics, personal advice, harmful content, or 
         questions with no relevance to hospital equipment operations.

Query: {query}

Respond with exactly one word: VALID or INVALID"""


class GuardrailResult:
    def __init__(self, passed: bool, reason: str = "", sanitised: str = ""):
        self.passed = passed
        self.reason = reason
        self.sanitised = sanitised


def check_input(query: str) -> GuardrailResult:
    """Run all input checks. Returns GuardrailResult."""

    # 1. Empty / too short
    stripped = query.strip()
    if len(stripped) < settings.min_query_length:
        return GuardrailResult(False, "Query is too short. Please describe the equipment issue.")

    # 2. Too long
    if len(stripped) > settings.max_query_length:
        return GuardrailResult(
            False,
            f"Query exceeds maximum length ({settings.max_query_length} chars). Please be more concise.",
        )

    # 3. Injection detection
    lower = stripped.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, lower):
            logger.warning(f"Injection pattern detected in query: {pattern}")
            return GuardrailResult(False, "Invalid query format detected.")

    # 4. Topic relevance (LLM classification using Haiku for speed/cost)
    try:
        response = _client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=5,
            messages=[{"role": "user", "content": MEDICAL_TOPIC_PROMPT.format(query=stripped[:500])}],
        )
        verdict = response.choices[0].message.content.strip().upper()
        if "INVALID" in verdict:
            return GuardrailResult(
                False,
                "Query does not appear to be related to medical equipment or maintenance. "
                "Please describe an equipment reliability or maintenance issue.",
            )
    except Exception as e:
        logger.warning(f"Topic classification failed (allowing through): {e}")
        # Fail open — don't block valid queries due to LLM error

    return GuardrailResult(True, sanitised=stripped)
