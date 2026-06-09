"""
app/core/embeddings.py
OpenAI text-embedding-3-small wrapper with batching.
"""
from typing import List
import httpx
import openai
from app.core.config import get_settings

settings = get_settings()
_client = openai.OpenAI(
    api_key=settings.openai_api_key,
    base_url=settings.openai_base_url,
    http_client=httpx.Client(verify=False),
)


def embed_texts(texts: List[str], batch_size: int = 100) -> List[List[float]]:
    """Embed a list of strings; returns list of 1536-dim float vectors."""
    all_vectors: List[List[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = _client.embeddings.create(
            model=settings.embedding_model,
            input=batch,
        )
        all_vectors.extend([item.embedding for item in response.data])
    return all_vectors


def embed_query(text: str) -> List[float]:
    """Embed a single query string."""
    return embed_texts([text])[0]
