"""
app/agents/recommendation_agent.py
Recommendation Agent — synthesises all agent outputs into a final
explainable recommendation with citations and confidence score.
Uses Claude Sonnet (full model) for highest quality output.
"""
import re
from openai import OpenAI
from app.agents.state import AgentState, MessageRole
from app.core.config import get_settings
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

_client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)

RECOMMENDATION_PROMPT = """You are a senior biomedical engineer providing a formal equipment reliability assessment.

## Engineer's Query
{query}

## Retrieved Historical Incidents ({n} incidents retrieved)
{context}

## Anomaly Analysis
{anomalies}

## Maintenance Patterns
{maintenance}

## Failure Probability Estimate
{prob:.0%}

## Escalation Status
{escalation}

---

Provide a structured reliability recommendation with these sections:

**ROOT CAUSE ANALYSIS**
Identify the most probable root cause(s) with supporting evidence from retrieved incidents.

**IMMEDIATE ACTIONS**
List 2-3 specific corrective actions the biomedical engineer should take now.

**PREVENTIVE RECOMMENDATIONS**
List 2-3 preventive measures to reduce recurrence risk.

**CONFIDENCE ASSESSMENT**
State your confidence (0–100%) and what additional data would improve it.

**CITATIONS**
Reference the most relevant incident IDs that support this analysis.

Use professional clinical engineering language. Be specific and actionable.
Do NOT fabricate data not present in the retrieved incidents."""


def _extract_confidence(text: str) -> float:
    """Parse confidence percentage from recommendation text."""
    patterns = [r"confidence[:\s]+(\d+)%", r"(\d+)%\s+confident"]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return int(m.group(1)) / 100.0
    return 0.75  # default


def _extract_citations(incidents, text: str):
    """Find incident IDs mentioned in the recommendation."""
    cited = []
    for inc in incidents:
        if inc.id in text:
            cited.append(inc.id)
    return cited[:5]  # cap at 5


def run_recommendation_agent(state: AgentState) -> AgentState:
    """Generate final explainable recommendation."""
    state.add_message(MessageRole.RECOMMENDATION, "Generating final recommendation...")

    try:
        anomaly_summary = "\n".join(
            f"  • {a.field}: z={a.z_score:.2f} ({a.direction})"
            for a in state.anomalies if a.is_anomaly
        ) or "  No critical sensor anomalies."

        escalation_note = (
            f"⚠️ ESCALATION TRIGGERED: {state.escalation_reason}"
            if state.escalation_triggered
            else "No escalation required."
        )

        prompt = RECOMMENDATION_PROMPT.format(
            query=state.sanitised_query,
            n=len(state.retrieved_incidents),
            context=state.retrieval_context[:4000],
            anomalies=anomaly_summary,
            maintenance=state.maintenance_patterns,
            prob=state.failure_probability,
            escalation=escalation_note,
        )

        response = _client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        recommendation_text = response.choices[0].message.content.strip()

        state.recommendation = recommendation_text
        state.root_cause = _extract_root_cause(recommendation_text)
        state.confidence = _extract_confidence(recommendation_text)
        state.citations = _extract_citations(state.retrieved_incidents, recommendation_text)

        state.add_message(
            MessageRole.RECOMMENDATION,
            f"Recommendation generated. Confidence: {state.confidence:.0%}. "
            f"Citations: {len(state.citations)} incidents.",
            confidence=state.confidence,
        )

    except Exception as e:
        logger.error(f"Recommendation agent error: {e}", exc_info=True)
        state.trigger_fallback("recommendation_agent", str(e))
        state.recommendation = (
            "Unable to generate recommendation due to a system error. "
            "Please consult manual maintenance records and escalate to senior engineering staff."
        )
        state.confidence = 0.0

    return state


def _extract_root_cause(text: str) -> str:
    """Extract root cause section from recommendation text."""
    lines = text.split("\n")
    capture = False
    parts = []
    for line in lines:
        if "ROOT CAUSE" in line.upper():
            capture = True
            continue
        if capture and line.strip().startswith("**") and "ROOT CAUSE" not in line.upper():
            break
        if capture and line.strip():
            parts.append(line.strip())
    return " ".join(parts[:3]) if parts else text[:200]
