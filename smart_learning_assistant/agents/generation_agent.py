"""
agents/generation_agent.py
Step 6 — Answer Generation Agent

Uses retrieved context + user intent to produce:
  • Explanations
  • Summaries / notes
  • Code examples
  • Quiz questions (MCQ)
"""

import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Intent-specific system prompts
# ---------------------------------------------------------------------------

PROMPTS = {
    "explain_concept": """
You are an expert educator. Explain the concept clearly and simply.
Structure your response with:
1. Simple definition (1-2 sentences)
2. Core idea / analogy
3. Key components or steps
4. Real-world example
5. Common misconceptions (if any)

Use ONLY the provided context. If context is insufficient, say so and use general knowledge.
""",

    "generate_quiz": """
You are a quiz generator. Create 5 multiple-choice questions based on the context.
Format each question as:
Q1. [Question]
A) [Option]
B) [Option]
C) [Option]
D) [Option]
Answer: [Letter] — [Brief explanation]

Cover different difficulty levels. Base all questions on the provided context.
""",

    "summarize_document": """
You are a document summarizer. Provide a structured summary with:
• Main topic
• Key points (bullet list)
• Important details
• Conclusion / takeaway

Be concise but comprehensive. Use ONLY the provided context.
""",

    "generate_notes": """
You are a note-taking expert. Generate well-structured study notes with:
# Topic Title
## Key Concepts
- Concept 1: explanation
- Concept 2: explanation
## Important Formulas / Definitions
## Summary
## Review Questions

Use the provided context as source material.
""",

    "recommend_topics": """
You are a learning advisor. Based on the user's query and context, suggest:
1. What to learn next (3-5 topics)
2. Why each topic is relevant
3. Recommended learning order
4. Resources to explore (general types, not specific URLs)
""",

    "general_question": """
You are a knowledgeable learning assistant. Answer the question thoroughly.
- Use the provided context as your primary source.
- Structure your answer clearly.
- Provide examples where helpful.
- Indicate if you are using general knowledge vs. retrieved documents.
""",
}

DEFAULT_PROMPT = PROMPTS["general_question"]


def generation_agent(state: AgentState) -> AgentState:
    """
    Generates a response using the retrieved context and detected intent.
    """
    query = state.get("sanitized_query", "")
    context = state.get("retrieval_context", "")
    intent = state.get("intent", "general_question")
    history = state.get("conversation_history", [])
    logs = [f"[GenerationAgent] Generating response (intent={intent})..."]

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

    system_prompt = PROMPTS.get(intent, DEFAULT_PROMPT)

    # Build conversation history string (last 4 turns for context)
    history_text = ""
    if history:
        recent = history[-4:]
        history_text = "Previous conversation:\n" + "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in recent
        )

    user_message = f"""
{history_text}

RETRIEVED CONTEXT:
{context}

USER QUERY:
{query}

Please provide a thorough, accurate response based on the context above.
""".strip()

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message),
    ]

    try:
        response = llm.invoke(messages)
        generated = response.content.strip()
        logs.append(f"[GenerationAgent] Generated {len(generated)} characters")
    except Exception as exc:
        logger.error("Generation failed: %s", exc)
        generated = "I encountered an error generating a response. Please try again."
        logs.append(f"[GenerationAgent] ERROR: {exc}")

    return {
        **state,
        "generated_response": generated,
        "logs": logs,
    }
