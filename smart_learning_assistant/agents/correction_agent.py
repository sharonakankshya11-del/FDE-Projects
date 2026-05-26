"""
agents/correction_agent.py
Reflection / Self-Correction Workflow — Correction Agent

When the Reviewer flags issues, this agent refines the generated response
using the reviewer's feedback before another review pass.
"""

import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState

logger = logging.getLogger(__name__)

CORRECTION_SYSTEM_PROMPT = """
You are a Response Refinement Agent for a Smart Learning Assistant.

You will receive:
1. The original user query
2. The retrieved context
3. A flawed response
4. Reviewer feedback explaining what's wrong

Your job is to produce a corrected, improved response that:
- Addresses the reviewer's concerns
- Stays faithful to the retrieved context
- Answers the user's question accurately
- Removes hallucinated or unsupported claims
- Is clear, concise, and educational

Return ONLY the corrected response text.
"""


def correction_agent(state: AgentState) -> AgentState:
    """
    Refines the generated response based on reviewer feedback.
    Increments revision_count to prevent infinite loops.
    """
    query = state.get("sanitized_query", "")
    context = state.get("retrieval_context", "")
    bad_response = state.get("generated_response", "")
    feedback = state.get("review_feedback", "")
    revision_count = state.get("revision_count", 0)
    logs = [f"[CorrectionAgent] Revising response (attempt {revision_count + 1})..."]

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

    context_snippet = context[:3000]

    user_message = f"""
USER QUERY:
{query}

RETRIEVED CONTEXT:
{context_snippet}

PREVIOUS RESPONSE (flawed):
{bad_response}

REVIEWER FEEDBACK:
{feedback}

Please produce a corrected, improved response.
"""

    messages = [
        SystemMessage(content=CORRECTION_SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ]

    try:
        corrected = llm.invoke(messages).content.strip()
        logs.append(f"[CorrectionAgent] Corrected response generated ({len(corrected)} chars)")
    except Exception as exc:
        logger.error("Correction agent failed: %s", exc)
        corrected = bad_response  # fall back to original
        logs.append(f"[CorrectionAgent] ERROR: {exc} — keeping original")

    return {
        **state,
        "generated_response": corrected,
        "revision_count": revision_count + 1,
        "logs": logs,
    }
