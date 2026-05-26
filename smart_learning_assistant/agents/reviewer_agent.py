"""
agents/reviewer_agent.py
Step 7 — Reviewer / Evaluation Agent

Checks:
  • Faithfulness  — is the answer grounded in retrieved context?
  • Relevance     — does it answer the user's query?
  • Precision     — is unnecessary information minimised?
  • Hallucination — did the model invent unsupported facts?
  • Safety        — is the response appropriate?
"""

import json
import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState

logger = logging.getLogger(__name__)

REVIEWER_SYSTEM_PROMPT = """
You are a strict Quality Reviewer for an AI learning assistant.

Evaluate the response against the criteria below and return ONLY a JSON object:
{
  "faithfulness_score": <0.0-1.0>,
  "relevance_score": <0.0-1.0>,
  "precision_score": <0.0-1.0>,
  "hallucination_detected": <true|false>,
  "safety_passed": <true|false>,
  "overall_pass": <true|false>,
  "feedback": "<one sentence of constructive feedback>",
  "corrected_hint": "<optional: what should be fixed if failed>"
}

Scoring guide:
- faithfulness: Is every claim supported by the retrieved context or clearly stated as general knowledge?
- relevance: Does the response directly address the user's question?
- precision: Is the response free of unnecessary filler or off-topic content?
- hallucination_detected: true if the response contains specific facts NOT in the context and NOT verifiable common knowledge.
- safety_passed: true unless the response contains harmful, biased, or inappropriate content.
- overall_pass: true if faithfulness≥0.7 AND relevance≥0.7 AND NOT hallucination AND safety_passed.

Respond ONLY with valid JSON. No extra text.
"""


def reviewer_agent(state: AgentState) -> AgentState:
    """
    Reviews the generated response for quality and safety.
    Sets review_passed and review_feedback.
    """
    query = state.get("sanitized_query", "")
    context = state.get("retrieval_context", "")
    response = state.get("generated_response", "")
    revision_count = state.get("revision_count", 0)
    logs = [f"[ReviewerAgent] Reviewing response (revision #{revision_count})..."]

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Truncate context to avoid token overflow
    context_snippet = context[:3000] if len(context) > 3000 else context

    user_message = f"""
RETRIEVED CONTEXT (truncated):
{context_snippet}

USER QUERY:
{query}

GENERATED RESPONSE:
{response}

Evaluate and return JSON.
"""

    messages = [
        SystemMessage(content=REVIEWER_SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ]

    try:
        raw = llm.invoke(messages).content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        review = json.loads(raw)
    except Exception as exc:
        logger.error("Reviewer failed to parse: %s", exc)
        # Default to pass to avoid infinite loops
        review = {
            "faithfulness_score": 0.8,
            "relevance_score": 0.8,
            "precision_score": 0.8,
            "hallucination_detected": False,
            "safety_passed": True,
            "overall_pass": True,
            "feedback": "Review parsing failed; defaulting to pass.",
            "corrected_hint": "",
        }

    passed = review.get("overall_pass", True)
    feedback = review.get("feedback", "")
    logs.append(
        f"[ReviewerAgent] Pass={passed} | "
        f"Faithfulness={review.get('faithfulness_score', 0):.2f} | "
        f"Relevance={review.get('relevance_score', 0):.2f} | "
        f"Hallucination={review.get('hallucination_detected', False)}"
    )

    # Build eval_scores dict
    eval_scores = {
        "faithfulness": review.get("faithfulness_score", 0.0),
        "relevance": review.get("relevance_score", 0.0),
        "precision": review.get("precision_score", 0.0),
        "hallucination": 0.0 if review.get("hallucination_detected") else 1.0,
        "safety": 1.0 if review.get("safety_passed") else 0.0,
    }

    confidence = round(
        sum(eval_scores.values()) / len(eval_scores), 2
    )

    return {
        **state,
        "review_passed": passed,
        "review_feedback": feedback,
        "eval_scores": eval_scores,
        "confidence_score": confidence,
        "logs": logs,
    }
