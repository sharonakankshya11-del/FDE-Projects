"""
app/core/reranker.py
Cross-encoder reranking using sentence-transformers ms-marco-MiniLM-L-6-v2.
Scores (query, document) pairs; higher = more relevant.
"""
from typing import List, Dict, Any
from sentence_transformers import CrossEncoder
from app.core.config import get_settings
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

_cross_encoder: CrossEncoder = None


def get_cross_encoder() -> CrossEncoder:
    global _cross_encoder
    if _cross_encoder is None:
        logger.info("Loading cross-encoder model...")
        _cross_encoder = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2",
            max_length=512,
        )
    return _cross_encoder


def rerank(
    query: str,
    documents: List[Dict[str, Any]],
    top_k: int = None,
) -> List[Dict[str, Any]]:
    """
    Rerank documents using cross-encoder.
    Each doc must have a 'text' field.
    Returns top_k docs sorted by cross-encoder score descending.
    """
    if top_k is None:
        top_k = settings.top_k_rerank

    if not documents:
        return []

    encoder = get_cross_encoder()
    pairs = [(query, doc.get("text", "")) for doc in documents]
    scores = encoder.predict(pairs)

    scored = sorted(
        zip(documents, scores),
        key=lambda x: x[1],
        reverse=True,
    )

    result = []
    for doc, score in scored[:top_k]:
        result.append({**doc, "rerank_score": float(score)})

    return result
