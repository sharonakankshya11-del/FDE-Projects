"""
agents/supervisor_agent.py
Step 3 — Supervisor / Planner Agent

Responsibilities:
  • Understand user intent
  • Delegate to the correct sub-agents (Hierarchical Workflow)
  • Decide which agents to activate based on intent
  • Maintain shared state / memory

Hierarchical Workflow:
  The Supervisor sits at the top of the hierarchy. Based on the detected
  intent it explicitly decides which sub-agents are needed and in what order,
  rather than blindly running every agent every time.

  Intent → agents_to_run mapping:
    explain_concept     → [retrieval, generation, reviewer]
    generate_quiz       → [retrieval, generation, reviewer]
    summarize_document  → [retrieval, generation, reviewer]
    generate_notes      → [retrieval, generation, reviewer]
    recommend_topics    → [generation, reviewer]          # no retrieval needed
    general_question    → [retrieval, generation, reviewer]
"""

import json
import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState

logger = logging.getLogger(__name__)

SUPERVISOR_SYSTEM_PROMPT = """
You are the Supervisor Agent of a Smart Learning Assistant.
You operate in a HIERARCHICAL workflow: you sit at the top of the agent
hierarchy and explicitly delegate work to the appropriate sub-agents.

Analyse the user's query and return ONLY a JSON object with:
{
  "intent": "<one of: explain_concept | generate_quiz | summarize_document | generate_notes | recommend_topics | general_question>",
  "workflow_type": "hierarchical",
  "agents_to_run": ["retrieval", "generation", "reviewer"]
}

Delegation rules (hierarchical decision-making):
- For "recommend_topics": set agents_to_run to ["generation", "reviewer"]
  (topic recommendations come from the model's knowledge, no retrieval needed)
- For ALL other intents: set agents_to_run to ["retrieval", "generation", "reviewer"]
  (must retrieve context before generating an answer)
- workflow_type is ALWAYS "hierarchical" — never change this value.
- Respond ONLY with valid JSON. No extra text.
"""


def supervisor_agent(state: AgentState) -> AgentState:
    """
    Analyses the sanitized query and decides orchestration strategy.
    """
    query = state.get("sanitized_query", "")
    history = state.get("conversation_history", [])
    logs = [f"[SupervisorAgent] Analysing intent for: {query[:60]}..."]

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Build context from recent conversation history (last 4 turns)
    history_text = ""
    if history:
        recent = history[-4:]
        history_text = "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in recent
        )

    messages = [
        SystemMessage(content=SUPERVISOR_SYSTEM_PROMPT),
        HumanMessage(
            content=f"Conversation history:\n{history_text}\n\nCurrent query: {query}"
        ),
    ]

    try:
        response = llm.invoke(messages)
        raw = response.content.strip()
        # Strip markdown fences if present
        raw = raw.replace("```json", "").replace("```", "").strip()
        decision = json.loads(raw)
    except Exception as exc:
        logger.error("Supervisor failed: %s", exc)
        decision = {
            "intent": "general_question",
            "workflow_type": "sequential",
            "agents_to_run": ["retrieval", "generation", "reviewer"],
        }

    # Enforce hierarchical workflow_type regardless of LLM output
    decision["workflow_type"] = "hierarchical"

    logs.append(
        f"[SupervisorAgent] Intent={decision['intent']} | "
        f"Workflow=hierarchical | "
        f"Delegating to={decision['agents_to_run']}"
    )

    return {
        **state,
        "intent": decision["intent"],
        "workflow_type": decision["workflow_type"],
        "agents_to_run": decision["agents_to_run"],
        "logs": logs,
    }
