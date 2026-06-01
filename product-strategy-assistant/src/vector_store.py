"""Vector store for retrieval-augmented chat.

Uses ChromaDB with OpenAI embeddings when a key is available. When offline it
falls back to a lightweight keyword-overlap retriever so the chat still works.
"""
from __future__ import annotations

import re
import uuid
from typing import Any, Dict, List

from .config import settings
from .llm import embed_query, embed_texts


def _tokens(text: str) -> set:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


class VectorStore:
    def __init__(self) -> None:
        self._online = settings.has_api_key
        self._docs: List[Dict[str, Any]] = []  # always kept for fallback / display
        self._collection = None
        if self._online:
            import chromadb

            client = chromadb.EphemeralClient()
            self._collection = client.create_collection(
                name=f"insights_{uuid.uuid4().hex[:8]}",
                metadata={"hnsw:space": "cosine"},
            )

    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        if not documents:
            return
        self._docs.extend(documents)
        if self._online and self._collection is not None:
            texts = [d["text"] for d in documents]
            embeddings = embed_texts(texts)
            self._collection.add(
                ids=[uuid.uuid4().hex for _ in texts],
                documents=texts,
                embeddings=embeddings,
                metadatas=[d.get("metadata", {}) for d in documents],
            )

    def search(self, query: str, k: int = 5) -> List[str]:
        if not self._docs:
            return []
        if self._online and self._collection is not None:
            res = self._collection.query(
                query_embeddings=[embed_query(query)],
                n_results=min(k, len(self._docs)),
            )
            return res.get("documents", [[]])[0]
        # Offline keyword overlap.
        q = _tokens(query)
        scored = sorted(
            self._docs,
            key=lambda d: len(q & _tokens(d["text"])),
            reverse=True,
        )
        return [d["text"] for d in scored[:k]]

    @property
    def size(self) -> int:
        return len(self._docs)
