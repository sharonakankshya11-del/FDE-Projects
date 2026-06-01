"""Context-aware chat over the ingested data + generated insights."""
from __future__ import annotations

from typing import Dict, List

from .llm import complete
from .vector_store import VectorStore

CHAT_PERSONA = (
    "You are the Product Strategy Assistant. Answer the Product Manager's questions "
    "using ONLY the provided context (retrieved data snippets and the analysis reports). "
    "If the context does not contain the answer, say so plainly. Be concise, concrete and "
    "cite which report or data the answer comes from when relevant."
)

INSIGHT_KEYS = [
    ("Customer Insights", "customer_feedback"),
    ("Market Research", "market_research"),
    ("Competitor Analysis", "competitor_analysis"),
    ("SWOT", "swot"),
    ("Opportunities", "opportunities"),
    ("Feature Prioritization", "feature_prioritization"),
    ("Strategy & Roadmap", "strategy"),
    ("Executive Summary", "executive_summary"),
]


def answer_question(question: str, vstore: VectorStore, insights: Dict[str, str]) -> str:
    snippets: List[str] = vstore.search(question, k=5)
    data_ctx = "\n".join(f"- {s}" for s in snippets) or "(no matching data)"

    report_ctx_parts = []
    for label, key in INSIGHT_KEYS:
        val = insights.get(key)
        if val:
            report_ctx_parts.append(f"## {label}\n{val[:1500]}")
    report_ctx = "\n\n".join(report_ctx_parts) or "(no reports generated yet)"

    prompt = (
        f"Question: {question}\n\n"
        f"=== Retrieved data snippets ===\n{data_ctx}\n\n"
        f"=== Generated analysis reports ===\n{report_ctx}\n\n"
        "Answer the question now."
    )
    return complete(CHAT_PERSONA, prompt)
