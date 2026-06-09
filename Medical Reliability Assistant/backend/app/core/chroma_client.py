"""
app/core/chroma_client.py
ChromaDB collection management: create, upsert, query, delete.
Drop-in replacement for the former pinecone_client.
"""
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import get_settings
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

_client: Optional[chromadb.PersistentClient] = None
_collection = None


def _convert_filter(pinecone_style: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Convert Pinecone-style filter {"field": {"$eq": val}, ...}
    to a ChromaDB where clause. Multiple keys need $and wrapping.
    """
    if not pinecone_style:
        return None
    conditions = [{k: v} for k, v in pinecone_style.items()]
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}


def get_chroma_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        _collection = _client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            f"ChromaDB collection '{settings.chroma_collection_name}' ready "
            f"({_collection.count()} vectors)"
        )
    return _collection


def upsert_documents(
    ids: List[str],
    vectors: List[List[float]],
    metadatas: List[Dict[str, Any]],
    batch_size: int = 100,
) -> None:
    collection = get_chroma_collection()
    for i in range(0, len(ids), batch_size):
        end = min(i + batch_size, len(ids))
        batch_ids   = ids[i:end]
        batch_vecs  = vectors[i:end]
        batch_metas = metadatas[i:end]
        # Store the text as ChromaDB document for native text retrieval support
        batch_docs  = [m.get("text", "") for m in batch_metas]
        collection.upsert(
            ids=batch_ids,
            embeddings=batch_vecs,
            metadatas=batch_metas,
            documents=batch_docs,
        )
    logger.info(f"Upserted {len(ids)} vectors to ChromaDB")


def query_chroma(
    query_vector: List[float],
    top_k: int = 20,
    filter: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Returns list of {id, score, metadata} dicts — same shape as the former query_pinecone."""
    collection = get_chroma_collection()
    where = _convert_filter(filter)
    kwargs: Dict[str, Any] = {
        "query_embeddings": [query_vector],
        "n_results": min(top_k, max(collection.count(), 1)),
        "include": ["metadatas", "distances", "documents"],
    }
    if where:
        kwargs["where"] = where

    response = collection.query(**kwargs)

    ids        = response["ids"][0]
    distances  = response["distances"][0]
    metadatas  = response["metadatas"][0]

    # ChromaDB cosine distance = 1 - cosine_similarity  → invert to get similarity score
    return [
        {
            "id":       ids[j],
            "score":    round(1.0 - distances[j], 6),
            "metadata": metadatas[j],
        }
        for j in range(len(ids))
    ]


def get_all_documents() -> List[Dict[str, Any]]:
    """Fetch every stored document (used to rebuild the BM25 index on startup)."""
    collection = get_chroma_collection()
    total = collection.count()
    if total == 0:
        return []
    data = collection.get(include=["metadatas", "documents"])
    corpus = []
    for doc_id, meta, doc_text in zip(data["ids"], data["metadatas"], data["documents"]):
        text = doc_text or meta.get("text", "")
        if text:
            corpus.append({"id": doc_id, "text": text, "metadata": meta})
    return corpus


def delete_all() -> None:
    global _collection
    collection = get_chroma_collection()
    all_ids = collection.get()["ids"]
    if all_ids:
        collection.delete(ids=all_ids)
    logger.warning("Deleted all vectors from ChromaDB collection")
