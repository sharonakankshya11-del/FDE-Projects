"""
core/state.py
Defines the shared AgentState used across all LangGraph nodes.
Includes fields for Input Guardrail and Output Guardrail checks.
"""

from typing import TypedDict, Annotated, List, Optional, Dict, Any
from operator import add


class AgentState(TypedDict):
    """
    Shared state passed between all agents in the LangGraph workflow.
    Fields are updated by each node as the graph executes.

    Guardrail flow:
      input_guardrail → supervisor → retrieval → generation
                                                     → reviewer → response
                                                                    → output_guardrail → END
    """

    # --- Input ---
    user_query: str                         # Raw user input
    sanitized_query: str                    # Cleaned / validated query

    # --- Input Guardrail ---
    is_safe: bool                           # Passed all input guardrail checks?
    security_reason: str                    # Why blocked (if any)
    input_guardrail_checks: Dict[str, Any]  # Detailed per-check results
    #   keys: injection, harmful, pii, profanity, length, topic_relevance
    #   each value: {"passed": bool, "detail": str}

    # --- Supervisor decisions ---
    intent: str                             # Detected intent label
    workflow_type: str                      # hierarchical
    agents_to_run: List[str]               # Which agents to activate

    # --- Retrieval ---
    retrieved_docs: List[Dict[str, Any]]   # Documents from vector DB
    retrieval_context: str                  # Formatted context string for LLM

    # --- Generation ---
    generated_response: str                 # Raw LLM output

    # --- Review ---
    review_passed: bool                     # Reviewer approved?
    review_feedback: str                    # Reviewer notes
    revision_count: int                     # How many self-correction loops

    # --- Evaluation ---
    eval_scores: Dict[str, float]           # Metric name → score
    eval_passed: bool                       # Overall pass/fail

    # --- Final output ---
    final_response: str                     # What we show the user
    confidence_score: float                 # 0.0 – 1.0
    sources: List[str]                      # Document references
    follow_up_topics: List[str]             # Suggested next questions

    # --- Output Guardrail ---
    output_guardrail_passed: bool           # Passed all output guardrail checks?
    output_guardrail_checks: Dict[str, Any] # Detailed per-check results
    #   keys: pii_leakage, toxicity, confidence_gate, length, hallucination_flag, policy
    #   each value: {"passed": bool, "detail": str}
    output_guardrail_reason: str            # Why blocked (if output is unsafe)

    # --- Memory (append-only conversation history) ---
    conversation_history: Annotated[List[Dict[str, str]], add]

    # --- Metadata ---
    error: Optional[str]                    # Any runtime error message
    logs: Annotated[List[str], add]         # Audit trail
