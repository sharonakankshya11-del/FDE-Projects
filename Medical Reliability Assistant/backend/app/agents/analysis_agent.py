"""
app/agents/analysis_agent.py
Analysis Agent — anomaly detection on sensor parameters + LLM correlation summary.
Triggers escalation if high-severity anomalies found.
"""
from openai import OpenAI
from typing import List
from app.agents.state import AgentState, MessageRole
from app.utils.anomaly_detector import detect_anomalies
from app.core.config import get_settings
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

_client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)

ANALYSIS_PROMPT = """You are a biomedical equipment reliability engineer.

Equipment query: {query}

Retrieved historical incidents (top {n}):
{context}

Anomalies detected in sensor parameters:
{anomalies}

Based on this data:
1. Identify the most likely failure pattern and its probable cause
2. Note any correlations between sensor anomalies and failure types
3. Estimate failure probability (0.0–1.0) with brief justification
4. Flag if immediate intervention is required

Respond concisely in 3-4 sentences. End with: FAILURE_PROBABILITY: <float>"""


def run_analysis_agent(state: AgentState) -> AgentState:
    """Anomaly detection + correlation analysis."""
    state.add_message(MessageRole.ANALYSIS, "Running anomaly detection and correlation analysis...")

    try:
        # Extract numeric params from top retrieved incidents
        numeric_fields = {
            "air_temperature": [],
            "process_temperature": [],
            "rotational_speed": [],
            "torque": [],
            "tool_wear": [],
        }
        for inc in state.retrieved_incidents:
            # Parse from metadata via text if needed
            pass  # populated below

        # Use incidents metadata
        raw_data = []
        for inc in state.retrieved_incidents:
            # Each inc has metadata embedded in text; we re-parse from state
            raw_data.append({
                "air_temperature": 0,
                "process_temperature": 0,
                "rotational_speed": 0,
                "torque": 0,
                "tool_wear": 0,
            })

        # Run statistical anomaly detection
        anomalies = detect_anomalies(state.retrieved_incidents)
        state.anomalies = anomalies

        # Format anomalies for LLM
        anomaly_text = "\n".join(
            f"  • {a.field}: value={a.value:.2f}, z-score={a.z_score:.2f} ({a.direction})"
            for a in anomalies if a.is_anomaly
        ) or "  No significant statistical anomalies detected."

        # Check for high-severity escalation
        high_severity_incidents = [
            inc for inc in state.retrieved_incidents
            if inc.severity in ("high",)
        ]
        if len(high_severity_incidents) >= 2 or any(
            a.z_score > 3.0 for a in anomalies if a.is_anomaly
        ):
            state.trigger_escalation(
                f"High-severity pattern detected: {len(high_severity_incidents)} critical incidents, "
                f"extreme sensor anomalies present."
            )

        # LLM correlation analysis
        prompt = ANALYSIS_PROMPT.format(
            query=state.sanitised_query,
            n=len(state.retrieved_incidents),
            context=state.retrieval_context[:3000],
            anomalies=anomaly_text,
        )

        response = _client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        summary = response.choices[0].message.content.strip()

        # Extract failure probability
        failure_prob = 0.5
        for line in summary.split("\n"):
            if "FAILURE_PROBABILITY:" in line:
                try:
                    failure_prob = float(line.split(":")[1].strip())
                    summary = summary.replace(line, "").strip()
                except ValueError:
                    pass

        state.correlation_summary = summary
        state.failure_probability = min(max(failure_prob, 0.0), 1.0)

        state.add_message(
            MessageRole.ANALYSIS,
            f"Analysis complete. Failure probability: {state.failure_probability:.2f}. "
            f"Escalation: {state.escalation_triggered}.",
            failure_probability=state.failure_probability,
            escalation=state.escalation_triggered,
        )

    except Exception as e:
        logger.error(f"Analysis agent error: {e}", exc_info=True)
        state.trigger_fallback("analysis_agent", str(e))
        state.correlation_summary = "Analysis unavailable. Manual inspection recommended."
        state.failure_probability = 0.5

    return state
