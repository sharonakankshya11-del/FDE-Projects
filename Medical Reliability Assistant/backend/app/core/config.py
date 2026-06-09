"""
app/core/config.py
Centralised settings loaded from environment / .env file.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # LLM — Anthropic is no longer required; guardrails and eval use GPT-4o-mini
    anthropic_api_key: str = "not-required"
    anthropic_model: str = "claude-sonnet-4-20250514"
    anthropic_haiku_model: str = "claude-haiku-4-5-20251001"

    # Embeddings
    openai_api_key: str
    openai_base_url: str = "https://api.openai.com/v1"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536

    # Pinecone
    pinecone_api_key: str
    pinecone_index_name: str = "medical-equipment"
    pinecone_environment: str = "us-east-1-aws"

    # Retrieval
    top_k_retrieval: int = 20
    top_k_rerank: int = 5
    rrf_k: int = 60

    # App
    app_env: str = "development"
    log_level: str = "INFO"
    checkpoint_db_path: str = "./checkpoints.db"

    # Guardrails
    max_query_length: int = 1000
    min_query_length: int = 5

    # LangSmith observability (optional — tracing disabled if api_key not set)
    langchain_tracing_v2: str = "false"
    langchain_api_key: str = ""
    langchain_project: str = "dr-bleep-medical-reliability"
    langchain_endpoint: str = "https://api.smith.langchain.com"


@lru_cache
def get_settings() -> Settings:
    return Settings()
