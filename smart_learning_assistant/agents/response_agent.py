"""
agents/response_agent.py
Step 9 — Final Response Layer

Assembles the validated response with:
  • Confidence score
  • Evaluation metrics
  • Sources / references
  • Suggested follow-up topics
"""

import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState

logger = logging.getLogger(__name__)

FOLLOWUP_SYSTEM_PROMPT = """
You are a learning advisor. Given a user's question and the response they received,
suggest 3 natural follow-up questions or topics they might want to explore next.

Return ONLY a JSON array of strings. Example:
["What is backpropagation?", "How does gradient descent work?", "What are activation functions?"]

No extra text. Just the JSON array.
"""


def response_agent(state: AgentState) -> AgentState:
    """
    Assembles the final response and generates follow-up suggestions.
    Updates conversation history.
    """
    query = state.get("sanitized_query", "")
    generated = state.get("generated_response", "")
    sources = state.get("sources", [])
    confidence = state.get("confidence_score", 0.0)
    eval_scores = state.get("eval_scores", {})
    history = state.get("conversation_history", [])
    logs = ["[ResponseAgent] Assembling final response..."]

    # ── Generate follow-up suggestions ──────────────────────────────────────
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.4)
    try:
        import json
        resp = llm.invoke([
            SystemMessage(content=FOLLOWUP_SYSTEM_PROMPT),
            HumanMessage(content=f"User asked: {query}\n\nResponse given: {generated[:500]}"),
        ])
        raw = resp.content.strip().replace("```json", "").replace("```", "").strip()
        follow_ups = json.loads(raw)
        if not isinstance(follow_ups, list):
            follow_ups = []
    except Exception:
        follow_ups = []

    # ── Build final formatted response ──────────────────────────────────────
    final_parts = [generated]

    if sources:
        final_parts.append("\n\n**📚 Sources:**")
        for i, src in enumerate(sources, 1):
            final_parts.append(f"  {i}. {src}")

    if follow_ups:
        final_parts.append("\n\n**🔍 Suggested Follow-up Topics:**")
        for q in follow_ups[:3]:
            final_parts.append(f"  • {q}")

    final_response = "\n".join(final_parts)

    # ── Update conversation history ──────────────────────────────────────────
    new_history = [
        {"role": "user", "content": query},
        {"role": "assistant", "content": generated},
    ]

    logs.append(
        f"[ResponseAgent] Final response ready | "
        f"Confidence={confidence:.2f} | Sources={len(sources)}"
    )

    return {
        **state,
        "final_response": final_response,
        "follow_up_topics": follow_ups,
        "conversation_history": new_history,   # appended via Annotated[List, add]
        "logs": logs,
    }
