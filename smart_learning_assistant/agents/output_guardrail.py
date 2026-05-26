"""
agents/output_guardrail.py
Output Guardrail — Last gate before the response reaches the user.

Checks (all run; multiple failures are accumulated):
  1. PII leakage        — scrub personal data accidentally included in response
  2. Toxicity / policy  — detect harmful/biased content in the response
  3. Confidence gate    — suppress very-low-confidence responses
  4. Response length    — ensure response is neither empty nor absurdly long
  5. Hallucination flag — escalate if reviewer detected hallucination
  6. Disclaimer inject  — append a learning disclaimer when no sources retrieved

On failure → replaces final_response with a safe fallback message and sets
output_guardrail_passed = False with detailed per-check results.
"""

import re
import logging
from typing import Dict, Any, Tuple
from core.state import AgentState

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Check 1 — PII leakage in response
# ---------------------------------------------------------------------------
PII_PATTERNS = {
    "email":       r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Z|a-z]{2,}\b",
    "phone":       r"\b(\+?\d[\d\s\-().]{7,}\d)\b",
    "ssn":         r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b",
    "credit_card": r"\b(?:\d[ \-]?){13,16}\b",
    "ip_address":  r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
}

def _redact_pii(text: str) -> Tuple[str, bool, str]:
    """Redact PII from text. Returns (redacted_text, pii_found, detail)."""
    found = []
    redacted = text
    for pii_type, pattern in PII_PATTERNS.items():
        matches = re.findall(pattern, redacted)
        if matches:
            found.append(pii_type)
            redacted = re.sub(pattern, f"[{pii_type.upper()} REDACTED]", redacted)
    if found:
        return redacted, True, f"PII redacted from response: {', '.join(found)}"
    return redacted, False, ""


# ---------------------------------------------------------------------------
# Check 2 — Toxicity / policy violations in response
# ---------------------------------------------------------------------------
TOXIC_PATTERNS = [
    r"\b(kill|murder|assassinate)\s+(yourself|himself|herself|people)\b",
    r"\b(hate|despise)\s+(all\s+)?(jews|muslims|christians|blacks|whites|gays)\b",
    r"(step[- ]by[- ]step|instructions?)\s+(to|for)\s+(make|build|create)\s+(bomb|weapon|poison|drug)",
    r"\b(n[i1]gg[e3]r|f[a4]gg[o0]t|ch[i1]nk|sp[i1][c])\b",
]

def _check_toxicity(text: str) -> Tuple[bool, str]:
    lower = text.lower()
    for pat in TOXIC_PATTERNS:
        if re.search(pat, lower):
            return False, f"Toxic/policy-violating content detected in response."
    return True, ""


# ---------------------------------------------------------------------------
# Check 3 — Confidence gate
# ---------------------------------------------------------------------------
CONFIDENCE_THRESHOLD = 0.30   # below this → too uncertain to show

def _check_confidence(confidence: float) -> Tuple[bool, str]:
    if confidence < CONFIDENCE_THRESHOLD:
        return False, (
            f"Response confidence {confidence:.0%} is below the minimum "
            f"threshold of {CONFIDENCE_THRESHOLD:.0%}."
        )
    return True, ""


# ---------------------------------------------------------------------------
# Check 4 — Response length
# ---------------------------------------------------------------------------
MIN_RESPONSE_LEN = 20    # characters
MAX_RESPONSE_LEN = 15000

def _check_length(text: str) -> Tuple[bool, str]:
    n = len(text.strip())
    if n < MIN_RESPONSE_LEN:
        return False, f"Response too short ({n} chars; min {MIN_RESPONSE_LEN})."
    if n > MAX_RESPONSE_LEN:
        return False, f"Response too long ({n} chars; max {MAX_RESPONSE_LEN})."
    return True, ""


# ---------------------------------------------------------------------------
# Check 5 — Hallucination flag from reviewer
# ---------------------------------------------------------------------------
def _check_hallucination(eval_scores: Dict[str, float]) -> Tuple[bool, str]:
    """
    The reviewer stores hallucination as a score:
      1.0 = no hallucination detected
      0.0 = hallucination detected
    """
    hallu_score = eval_scores.get("hallucination", 1.0)
    if hallu_score < 0.5:   # hallucination was flagged
        return False, "Reviewer detected potential hallucination in the response."
    return True, ""


# ---------------------------------------------------------------------------
# Check 6 — Disclaimer injection (non-blocking, always appended when needed)
# ---------------------------------------------------------------------------
DISCLAIMER = (
    "\n\n---\n"
    "⚠️ *This answer is based on general knowledge — "
    "no specific documents were retrieved from the knowledge base. "
    "Please verify important facts independently.*"
)

def _maybe_add_disclaimer(text: str, sources: list) -> str:
    """Append a knowledge-base disclaimer when no documents were retrieved."""
    if not sources and DISCLAIMER not in text:
        return text + DISCLAIMER
    return text


# ---------------------------------------------------------------------------
# Fallback response templates
# ---------------------------------------------------------------------------
FALLBACK = {
    "toxicity":    "🚫 The generated response was blocked by the output safety guardrail. Please rephrase your question.",
    "confidence":  "🤔 I'm not confident enough in my answer for this query. Could you rephrase or add more context?",
    "length":      "⚠️ The response could not be formatted correctly. Please try again.",
    "hallucination": (
        "⚠️ The response was flagged for potentially containing unverified information. "
        "Please ask with more specific context or try a different phrasing."
    ),
}


# ---------------------------------------------------------------------------
# LangGraph node
# ---------------------------------------------------------------------------

def output_guardrail(state: AgentState) -> AgentState:
    """
    Validates and optionally transforms the final response before it
    reaches the user.

    Non-destructive checks (PII redaction, disclaimer) modify the response
    in-place. Blocking checks (toxicity, confidence, length, hallucination)
    replace the response with a safe fallback.
    """
    response    = state.get("final_response", "")
    confidence  = state.get("confidence_score", 1.0)
    eval_scores = state.get("eval_scores", {})
    sources     = state.get("sources", [])
    logs        = ["[OutputGuardrail] Running output checks…"]

    checks: Dict[str, Any] = {}
    blocked_reason = ""

    # ── 1. PII redaction (always run, non-blocking) ───────────────────────────
    response, pii_found, pii_detail = _redact_pii(response)
    checks["pii_leakage"] = {"passed": not pii_found, "detail": pii_detail or "No PII found"}
    logs.append(f"[OutputGuardrail] pii_leakage: {'⚠ redacted' if pii_found else '✓'} {pii_detail}")

    # ── 2. Toxicity check ────────────────────────────────────────────────────
    tox_ok, tox_detail = _check_toxicity(response)
    checks["toxicity"] = {"passed": tox_ok, "detail": tox_detail or "No toxic content"}
    logs.append(f"[OutputGuardrail] toxicity: {'✓' if tox_ok else '✗'} {tox_detail}")
    if not tox_ok:
        blocked_reason = tox_detail
        response = FALLBACK["toxicity"]

    # ── 3. Confidence gate ───────────────────────────────────────────────────
    conf_ok, conf_detail = _check_confidence(confidence)
    checks["confidence_gate"] = {"passed": conf_ok, "detail": conf_detail or f"Confidence {confidence:.0%} OK"}
    logs.append(f"[OutputGuardrail] confidence_gate: {'✓' if conf_ok else '✗'} {conf_detail}")
    if not conf_ok and not blocked_reason:
        blocked_reason = conf_detail
        response = FALLBACK["confidence"]

    # ── 4. Length check ───────────────────────────────────────────────────────
    len_ok, len_detail = _check_length(response)
    checks["length"] = {"passed": len_ok, "detail": len_detail or "Length OK"}
    logs.append(f"[OutputGuardrail] length: {'✓' if len_ok else '✗'} {len_detail}")
    if not len_ok and not blocked_reason:
        blocked_reason = len_detail
        response = FALLBACK["length"]

    # ── 5. Hallucination flag ─────────────────────────────────────────────────
    hallu_ok, hallu_detail = _check_hallucination(eval_scores)
    checks["hallucination_flag"] = {"passed": hallu_ok, "detail": hallu_detail or "No hallucination detected"}
    logs.append(f"[OutputGuardrail] hallucination_flag: {'✓' if hallu_ok else '✗'} {hallu_detail}")
    if not hallu_ok and not blocked_reason:
        blocked_reason = hallu_detail
        response = FALLBACK["hallucination"]

    # ── 6. Disclaimer injection (non-blocking) ────────────────────────────────
    response = _maybe_add_disclaimer(response, sources)
    checks["disclaimer"] = {
        "passed": True,
        "detail": "Disclaimer injected (no sources)" if not sources else "Sources present — no disclaimer needed",
    }
    logs.append(f"[OutputGuardrail] disclaimer: {checks['disclaimer']['detail']}")

    # ── Summary ───────────────────────────────────────────────────────────────
    overall_passed = not bool(blocked_reason)
    if overall_passed:
        logs.append("[OutputGuardrail] All output checks passed ✓")
    else:
        logger.warning("Output guardrail BLOCKED: %s", blocked_reason)
        logs.append(f"[OutputGuardrail] BLOCKED — {blocked_reason}")

    return {
        **state,
        "final_response":          response,
        "output_guardrail_passed": overall_passed,
        "output_guardrail_checks": checks,
        "output_guardrail_reason": blocked_reason,
        "logs":                    logs,
    }
