"""
agents/retrieval_agent.py
Step 5 — Retrieval & Knowledge Layer

Hierarchical Workflow — this agent is only invoked when the Supervisor
explicitly delegates to it (i.e. "retrieval" is in agents_to_run).

Implements:
  • Semantic vector search via ChromaDB (text-embedding-3-small)
  • Metadata-aware filtering based on detected intent
  • Graceful fallback to LLM knowledge when the vector store is empty
"""

import logging
import os
from typing import List, Dict, Any

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from core.state import AgentState

logger = logging.getLogger(__name__)

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
COLLECTION_NAME = "learning_materials"
TOP_K = 5


# ---------------------------------------------------------------------------
# LangGraph node
# ---------------------------------------------------------------------------

def retrieval_agent(state: AgentState) -> AgentState:
    """
    Performs semantic retrieval from ChromaDB.

    Only reached when the Supervisor (top of hierarchy) has included
    'retrieval' in agents_to_run — i.e. the query requires grounded context.
    """
    query = state.get("sanitized_query", "")
    intent = state.get("intent", "general_question")
    logs = [f"[RetrievalAgent] Supervisor delegated retrieval for: {query[:60]}..."]

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # ── Semantic search via ChromaDB ─────────────────────────────────────────
    try:
        vectorstore = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=CHROMA_PERSIST_DIR,
        )

        # Broad coverage for quizzes; no filter otherwise
        filter_dict = {}

        semantic_results: List[Document] = vectorstore.similarity_search(
            query, k=TOP_K, filter=filter_dict if filter_dict else None
        )
        logs.append(f"[RetrievalAgent] Semantic search returned {len(semantic_results)} docs")

    except Exception as exc:
        logger.warning("Semantic search failed: %s", exc)
        semantic_results = []
        logs.append(f"[RetrievalAgent] Semantic search error: {exc}")

    # ── Format context string ────────────────────────────────────────────────
    if semantic_results:
        context_parts = []
        sources = []
        retrieved_docs = []

        for i, doc in enumerate(semantic_results):
            source = doc.metadata.get("source", f"Document {i+1}")
            page   = doc.metadata.get("page", "")
            page_str = f" (page {page})" if page else ""
            context_parts.append(
                f"[Source {i+1}: {source}{page_str}]\n{doc.page_content}"
            )
            sources.append(f"{source}{page_str}")
            retrieved_docs.append(
                {"content": doc.page_content, "source": source, "page": page}
            )

        retrieval_context = "\n\n---\n\n".join(context_parts)

    else:
        # No documents found — delegate to LLM general knowledge
        retrieval_context = (
            "No specific documents found in the knowledge base. "
            "Answer from general knowledge."
        )
        sources       = []
        retrieved_docs = []
        logs.append("[RetrievalAgent] No docs found — falling back to LLM knowledge")

    return {
        **state,
        "retrieved_docs":    retrieved_docs,
        "retrieval_context": retrieval_context,
        "sources":           sources,
        "logs":              logs,
    }
