"""
agents/input_guardrail.py
Input Guardrail — First line of defence before any agent runs.

Checks (in order, short-circuits on first failure):
  1. Length validation     — query must be 3–2000 characters
  2. Prompt injection      — detect jailbreak / override patterns
  3. Harmful content       — block dangerous topic keywords
  4. PII detection         — flag personal data in the query
  5. Profanity filter      — block explicit / offensive language
  6. Topic relevance       — ensure query is education-related (LLM-based, fast)

On any failure → sets is_safe=False, populates final_response with a safe
message, and the graph routes directly to END without running any other agent.
"""

import re
import logging
from typing import Dict, Any, Tuple
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Check 1 — Length
# ---------------------------------------------------------------------------
MIN_LEN = 3
MAX_LEN = 2000

def _check_length(text: str) -> Tuple[bool, str]:
    if len(text.strip()) < MIN_LEN:
        return False, f"Query too short (min {MIN_LEN} characters)."
    if len(text) > MAX_LEN:
        return False, f"Query too long ({len(text)} chars; max {MAX_LEN})."
    return True, ""


# ---------------------------------------------------------------------------
# Check 2 — Prompt injection
# ---------------------------------------------------------------------------
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"reveal\s+(your\s+)?(system\s+prompt|instructions|prompt)",
    r"forget\s+(everything|all|your\s+instructions)",
    r"you\s+are\s+now\s+",
    r"act\s+as\s+(a\s+)?(different|new|unrestricted)",
    r"\bjailbreak\b",
    r"disregard\s+(your\s+)?(guidelines|rules|policies)",
    r"do\s+anything\s+now",
    r"\bdan\s+mode\b",
    r"override\s+(safety|content|system)",
    r"pretend\s+(you\s+are|to\s+be)",
    r"bypass\s+(filter|restriction|guard|safety)",
    r"simulate\s+(an?\s+)?(evil|unrestricted|unfiltered)",
]

def _check_injection(text: str) -> Tuple[bool, str]:
    lower = text.lower()
    for pat in INJECTION_PATTERNS:
        if re.search(pat, lower):
            return False, f"Prompt injection pattern detected: '{pat[:40]}'"
    return True, ""


# ---------------------------------------------------------------------------
# Check 3 — Harmful content
# ---------------------------------------------------------------------------
HARMFUL_PHRASES = [
    "how to make a bomb", "build a weapon", "synthesize drugs",
    "hack into", "malware", "ransomware", "child exploitation",
    "self harm", "suicide method", "how to kill", "poison someone",
    "illegal firearm", "make explosives", "distribute malware",
    "phishing attack", "sql injection attack", "ddos attack",
]

def _check_harmful(text: str) -> Tuple[bool, str]:
    lower = text.lower()
    for phrase in HARMFUL_PHRASES:
        if phrase in lower:
            return False, f"Harmful content detected: '{phrase}'"
    return True, ""


# ---------------------------------------------------------------------------
# Check 4 — PII detection
# ---------------------------------------------------------------------------
PII_PATTERNS = {
    "email":        r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Z|a-z]{2,}\b",
    "phone":        r"\b(\+?\d[\d\s\-().]{7,}\d)\b",
    "ssn":          r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b",
    "credit_card":  r"\b(?:\d[ \-]?){13,16}\b",
    "ip_address":   r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
    "passport":     r"\b[A-Z]{1,2}\d{6,9}\b",
}

def _check_pii(text: str) -> Tuple[bool, str]:
    """Warn if PII is detected in the query (don't block, just flag & redact)."""
    found = []
    for pii_type, pattern in PII_PATTERNS.items():
        if re.search(pattern, text):
            found.append(pii_type)
    if found:
        return False, f"PII detected in query: {', '.join(found)}"
    return True, ""


# ---------------------------------------------------------------------------
# Check 5 — Profanity / offensive language
# ---------------------------------------------------------------------------
PROFANITY_WORDS = [
    r"\bfuck\b", r"\bshit\b", r"\basshole\b", r"\bbitch\b",
    r"\bcunt\b",  r"\bdick\b", r"\bprick\b",  r"\bwanker\b",
    r"\bfaggot\b",r"\bnigger\b",r"\bkike\b",  r"\bspic\b",
]

def _check_profanity(text: str) -> Tuple[bool, str]:
    lower = text.lower()
    for pat in PROFANITY_WORDS:
        if re.search(pat, lower):
            return False, "Offensive or profane language detected."
    return True, ""


# ---------------------------------------------------------------------------
# Check 6 — Topic relevance (LLM-based, lightweight)
# ---------------------------------------------------------------------------
RELEVANCE_SYSTEM_PROMPT = """
You are a topic relevance classifier for an educational AI assistant.
Determine if the user's query is related to learning, education, knowledge,
science, technology, programming, mathematics, history, or any academic subject.

Reply with ONLY one word: "relevant" or "irrelevant".
- "relevant": the query is about learning something or an academic/technical topic.
- "irrelevant": the query is completely off-topic (e.g. personal chats, commercial
  requests, adult content, entertainment only, etc.)
"""

def _check_topic_relevance(text: str) -> Tuple[bool, str]:
    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_tokens=5)
        result = llm.invoke([
            SystemMessage(content=RELEVANCE_SYSTEM_PROMPT),
            HumanMessage(content=text),
        ]).content.strip().lower()
        if "irrelevant" in result:
            return False, "Query does not appear to be education or learning related."
    except Exception as exc:
        logger.warning("Topic relevance check failed (%s) — defaulting to relevant", exc)
    return True, ""


# ---------------------------------------------------------------------------
# Sanitizer
# ---------------------------------------------------------------------------
def _sanitize(text: str) -> str:
    text = re.sub(r"[\x00-\x1f\x7f]", " ", text)  # control chars
    text = re.sub(r"\s+", " ", text).strip()
    return text[:MAX_LEN]


# ---------------------------------------------------------------------------
# LangGraph node
# ---------------------------------------------------------------------------

CHECK_ORDER = [
    ("length",          _check_length),
    ("injection",       _check_injection),
    ("harmful",         _check_harmful),
    ("pii",             _check_pii),
    ("profanity",       _check_profanity),
    ("topic_relevance", _check_topic_relevance),
]

BLOCK_MESSAGES = {
    "length":          "⚠️ Your query is too short or too long. Please rephrase it.",
    "injection":       "🚫 Your message appears to contain instructions that could compromise the system. Please ask a genuine learning question.",
    "harmful":         "🚫 I can't help with that topic. Please ask about something educational.",
    "pii":             "⚠️ Your query contains personal information (email, phone, etc.). Please remove it and try again.",
    "profanity":       "⚠️ Please keep the conversation respectful. Rephrase without offensive language.",
    "topic_relevance": "🎓 I'm an educational assistant. Please ask me a learning or knowledge-based question.",
}


def input_guardrail(state: AgentState) -> AgentState:
    """
    Runs all input checks in sequence.
    Short-circuits and blocks on the first failed check.
    Sets is_safe, input_guardrail_checks, and (if blocked) final_response.
    """
    query = state.get("user_query", "")
    logs  = ["[InputGuardrail] Running input checks…"]

    checks: Dict[str, Any] = {}

    for check_name, check_fn in CHECK_ORDER:
        passed, detail = check_fn(query)
        checks[check_name] = {"passed": passed, "detail": detail or "OK"}
        logs.append(f"[InputGuardrail] {check_name}: {'✓' if passed else '✗'} {detail or ''}")

        if not passed:
            logger.warning("Input guardrail BLOCKED at '%s': %s", check_name, detail)
            block_msg = BLOCK_MESSAGES.get(check_name, "⚠️ Request blocked by input guardrail.")
            return {
                **state,
                "is_safe":               False,
                "security_reason":       f"[{check_name}] {detail}",
                "sanitized_query":       "",
                "input_guardrail_checks": checks,
                "final_response":        block_msg,
                "logs":                  logs + [f"[InputGuardrail] BLOCKED — {check_name}"],
            }

    # All checks passed
    clean = _sanitize(query)
    logs.append("[InputGuardrail] All checks passed ✓")
    return {
        **state,
        "is_safe":               True,
        "security_reason":       "",
        "sanitized_query":       clean,
        "input_guardrail_checks": checks,
        "logs":                  logs,
    }
