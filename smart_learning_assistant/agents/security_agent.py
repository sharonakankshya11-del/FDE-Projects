"""
agents/security_agent.py
Step 2 — Input Validation & Security Layer

Performs:
  • Prompt-injection detection
  • Harmful content filtering
  • Input sanitization
  • Tool-access control check
"""

import re
import logging
from core.state import AgentState

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Patterns that indicate prompt-injection or policy violations
# ---------------------------------------------------------------------------
INJECTION_PATTERNS = [
    r"ignore (all )?(previous|prior|above) instructions",
    r"reveal (your )?(system prompt|instructions|prompt)",
    r"forget (everything|all|your instructions)",
    r"you are now",
    r"act as (a )?(different|new|unrestricted)",
    r"jailbreak",
    r"disregard (your )?(guidelines|rules|policies)",
    r"do anything now",
    r"dan mode",
]

HARMFUL_KEYWORDS = [
    "how to make a bomb",
    "synthesize drugs",
    "hack into",
    "malware",
    "child exploitation",
    "self harm",
]


def _check_injection(text: str) -> tuple[bool, str]:
    """Return (is_injection, reason)."""
    lowered = text.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, lowered):
            return True, f"Prompt injection detected: pattern '{pattern}'"
    return False, ""


def _check_harmful(text: str) -> tuple[bool, str]:
    """Return (is_harmful, reason)."""
    lowered = text.lower()
    for kw in HARMFUL_KEYWORDS:
        if kw in lowered:
            return True, f"Harmful content detected: '{kw}'"
    return False, ""


def _sanitize(text: str) -> str:
    """Basic sanitization: strip excess whitespace and control characters."""
    text = re.sub(r"[\x00-\x1f\x7f]", " ", text)   # control chars
    text = re.sub(r"\s+", " ", text).strip()
    return text[:2000]   # hard cap to prevent token-overflow attacks


# ---------------------------------------------------------------------------
# LangGraph node
# ---------------------------------------------------------------------------

def security_agent(state: AgentState) -> AgentState:
    """
    Validates and sanitizes the user query.
    Sets state['is_safe'] = False and returns early if a violation is found.
    """
    query = state.get("user_query", "")
    logs = [f"[SecurityAgent] Checking query: {query[:60]}..."]

    # 1. Prompt-injection check
    injected, reason = _check_injection(query)
    if injected:
        logger.warning("Security block — injection: %s", reason)
        return {
            **state,
            "is_safe": False,
            "security_reason": reason,
            "sanitized_query": "",
            "final_response": (
                "⚠️  I'm unable to process that request. "
                "It appears to contain instructions that could compromise the system. "
                "Please ask a genuine learning question!"
            ),
            "logs": logs + [f"[SecurityAgent] BLOCKED — {reason}"],
        }

    # 2. Harmful content check
    harmful, reason = _check_harmful(query)
    if harmful:
        logger.warning("Security block — harmful: %s", reason)
        return {
            **state,
            "is_safe": False,
            "security_reason": reason,
            "sanitized_query": "",
            "final_response": (
                "⚠️  I can't help with that topic. "
                "Please ask about something educational!"
            ),
            "logs": logs + [f"[SecurityAgent] BLOCKED — {reason}"],
        }

    # 3. Sanitize
    clean = _sanitize(query)
    logs.append("[SecurityAgent] Query passed all checks ✓")

    return {
        **state,
        "is_safe": True,
        "security_reason": "",
        "sanitized_query": clean,
        "logs": logs,
    }
