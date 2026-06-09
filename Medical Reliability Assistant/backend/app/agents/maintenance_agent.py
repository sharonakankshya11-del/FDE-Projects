"""
app/agents/maintenance_agent.py
Maintenance Agent — identifies maintenance patterns, recurrence frequency,
and equipment utilisation insights from retrieved incidents.
"""
from collections import Counter
from openai import OpenAI
from app.agents.state import AgentState, MessageRole
from app.core.config import get_settings
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

_client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)

MAINTENANCE_PROMPT = """You are a hospital biomedical engineering maintenance specialist.

Equipment query: {query}

Failure type distribution from similar past incidents:
{failure_dist}

Retrieved incident context:
{context}

Correlation analysis:
{correlation}

Provide:
1. Key maintenance patterns observed (2-3 bullet points)
2. Recurring failure modes to watch for
3. Recommended maintenance schedule adjustment (if warranted)
4. Equipment utilisation concern (if any)

Be specific, actionable, and concise."""


def run_maintenance_agent(state: AgentState) -> AgentState:
    """Identify maintenance patterns from retrieved incidents."""
    state.add_message(MessageRole.MAINTENANCE, "Identifying maintenance patterns...")

    try:
        # Count failure type distribution
        failure_counts = Counter(
            inc.failure_type for inc in state.retrieved_incidents
            if inc.failure_type and inc.failure_type != "No Failure"
        )
        state.similar_cases_count = len(state.retrieved_incidents)

        failure_dist = "\n".join(
            f"  {ftype}: {count} occurrences"
            for ftype, count in failure_counts.most_common(5)
        ) or "  No failures in retrieved incidents."

        prompt = MAINTENANCE_PROMPT.format(
            query=state.sanitised_query,
            failure_dist=failure_dist,
            context=state.retrieval_context[:2000],
            correlation=state.correlation_summary,
        )

        response = _client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        state.maintenance_patterns = response.choices[0].message.content.strip()

        state.add_message(
            MessageRole.MAINTENANCE,
            f"Maintenance patterns identified. {state.similar_cases_count} similar cases analysed.",
            similar_cases=state.similar_cases_count,
        )

    except Exception as e:
        logger.error(f"Maintenance agent error: {e}", exc_info=True)
        state.trigger_fallback("maintenance_agent", str(e))
        state.maintenance_patterns = "Maintenance pattern analysis unavailable."

    return state
