"""LLM + embedding helpers.

Uses OpenAI (gpt-4o-mini / text-embedding-3-small) via LangChain when an API
key is configured. If no key is present the helpers degrade gracefully so the
rest of the app (data dashboard, structured analytics) still runs.
"""
from __future__ import annotations

from functools import lru_cache
from typing import List

from .config import settings

OFFLINE_NOTICE = (
    "_AI narrative unavailable: no `OPENAI_API_KEY` configured. "
    "Add a key in `.env` to enable generated insights. "
    "The structured analytics below are computed directly from your data._"
)


@lru_cache(maxsize=1)
def get_chat_model():
    """Return a cached LangChain ChatOpenAI instance, or None if offline."""
    if not settings.has_api_key:
        return None
    from langchain_openai import ChatOpenAI

    kwargs = dict(
        model=settings.llm_model,
        temperature=settings.temperature,
        api_key=settings.openai_api_key,
        timeout=60,
        max_retries=2,
    )
    if settings.openai_base_url:
        kwargs["base_url"] = settings.openai_base_url
    return ChatOpenAI(**kwargs)


@lru_cache(maxsize=1)
def get_embeddings():
    """Return a cached embeddings client, or None when using a custom gateway.

    Custom gateways (non-OpenAI base URLs) typically only expose chat
    completions, not the embeddings endpoint, so we skip embeddings there.
    """
    if not settings.has_api_key or settings.openai_base_url:
        return None
    from langchain_openai import OpenAIEmbeddings

    return OpenAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.openai_api_key,
    )


def complete(system_prompt: str, user_prompt: str) -> str:
    """Single-turn completion. Returns the model text, or an offline notice."""
    model = get_chat_model()
    if model is None:
        return OFFLINE_NOTICE
    from langchain_core.messages import HumanMessage, SystemMessage

    resp = model.invoke(
        [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
    )
    return resp.content.strip()


def embed_texts(texts: List[str]) -> List[List[float]]:
    emb = get_embeddings()
    if emb is None:
        # Deterministic placeholder vectors keep the pipeline functional offline.
        return [[0.0] * 8 for _ in texts]
    return emb.embed_documents(texts)


def embed_query(text: str) -> List[float]:
    emb = get_embeddings()
    if emb is None:
        return [0.0] * 8
    return emb.embed_query(text)
