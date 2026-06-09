"""
app/core/hybrid_search.py
Hybrid retrieval: BM25 (keyword) + ChromaDB (vector) fused via RRF.

RRF formula: score(d) = Σ 1 / (k + rank(d))
where k=60 is a constant that dampens the impact of high ranks.
"""
from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi
from app.core.embeddings import embed_query
from app.core.pinecone_client import query_pinecone
from app.core.config import get_settings

settings = get_settings()

# In-memory BM25 corpus (loaded at startup from ingest)
_bm25_index: Optional[BM25Okapi] = None
_bm25_corpus: List[Dict[str, Any]] = []  # list of {id, text, metadata}


def build_bm25_index(corpus: List[Dict[str, Any]]) -> None:
    """Build BM25 index from a list of {id, text, metadata} dicts."""
    global _bm25_index, _bm25_corpus
    _bm25_corpus = corpus
    tokenised = [doc["text"].lower().split() for doc in corpus]
    _bm25_index = BM25Okapi(tokenised)


def _bm25_search(query: str, top_k: int) -> List[Dict[str, Any]]:
    if _bm25_index is None:
        return []
    tokens = query.lower().split()
    scores = _bm25_index.get_scores(tokens)
    ranked = sorted(
        enumerate(scores), key=lambda x: x[1], reverse=True
    )[:top_k]
    return [
        {
            "id": _bm25_corpus[i]["id"],
            "score": float(s),
            "metadata": _bm25_corpus[i]["metadata"],
            "text": _bm25_corpus[i]["text"],
        }
        for i, s in ranked
        if s > 0
    ]


def _vector_search(
    query: str,
    top_k: int,
    filter: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    vec = embed_query(query)
    results = query_pinecone(vec, top_k=top_k, filter=filter)
    return results


def reciprocal_rank_fusion(
    *ranked_lists: List[Dict[str, Any]],
    k: int = 60,
) -> List[Dict[str, Any]]:
    """Merge multiple ranked lists using RRF."""
    rrf_scores: Dict[str, float] = {}
    doc_data: Dict[str, Dict[str, Any]] = {}

    for ranked_list in ranked_lists:
        for rank, doc in enumerate(ranked_list):
            doc_id = doc["id"]
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
            if doc_id not in doc_data:
                doc_data[doc_id] = doc

    fused = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    return [
        {**doc_data[doc_id], "rrf_score": score}
        for doc_id, score in fused
    ]


def hybrid_search(
    query: str,
    top_k: int = None,
    filter: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Full hybrid search pipeline:
    1. BM25 keyword search
    2. Pinecone vector search
    3. RRF fusion
    Returns top_k_retrieval results before reranking.
    """
    if top_k is None:
        top_k = settings.top_k_retrieval

    bm25_results = _bm25_search(query, top_k=top_k)
    vector_results = _vector_search(query, top_k=top_k, filter=filter)

    # Enrich vector results with text (stored in metadata by ChromaDB upsert)
    corpus_map = {d["id"]: d.get("text", "") for d in _bm25_corpus}
    for r in vector_results:
        if "text" not in r or not r["text"]:
            r["text"] = corpus_map.get(r["id"], r.get("metadata", {}).get("text", ""))

    fused = reciprocal_rank_fusion(vector_results, bm25_results, k=settings.rrf_k)
    return fused[:top_k]
