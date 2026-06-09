"""
app/core/pinecone_client.py
Pinecone index management: create, upsert, query, delete.
"""
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
from app.core.config import get_settings
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

_pc: Optional[Pinecone] = None
_index = None


def get_pinecone_index():
    global _pc, _index
    if _index is None:
        _pc = Pinecone(api_key=settings.pinecone_api_key)
        existing = [i.name for i in _pc.list_indexes()]
        if settings.pinecone_index_name not in existing:
            logger.info(f"Creating Pinecone index: {settings.pinecone_index_name}")
            _pc.create_index(
                name=settings.pinecone_index_name,
                dimension=settings.embedding_dimension,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
        _index = _pc.Index(settings.pinecone_index_name)
    return _index


def upsert_documents(
    ids: List[str],
    vectors: List[List[float]],
    metadatas: List[Dict[str, Any]],
    batch_size: int = 100,
) -> None:
    index = get_pinecone_index()
    for i in range(0, len(ids), batch_size):
        batch = [
            {
                "id": ids[j],
                "values": vectors[j],
                "metadata": metadatas[j],
            }
            for j in range(i, min(i + batch_size, len(ids)))
        ]
        index.upsert(vectors=batch)
    logger.info(f"Upserted {len(ids)} vectors to Pinecone")


def query_pinecone(
    query_vector: List[float],
    top_k: int = 20,
    filter: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Returns list of {id, score, metadata} dicts."""
    index = get_pinecone_index()
    kwargs: Dict[str, Any] = {
        "vector": query_vector,
        "top_k": top_k,
        "include_metadata": True,
    }
    if filter:
        kwargs["filter"] = filter
    response = index.query(**kwargs)
    return [
        {"id": m.id, "score": m.score, "metadata": m.metadata}
        for m in response.matches
    ]


def delete_all() -> None:
    index = get_pinecone_index()
    index.delete(delete_all=True)
    logger.warning("Deleted all vectors from Pinecone index")
