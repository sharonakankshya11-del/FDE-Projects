"""
main.py — FastAPI application entry point.

Startup sequence:
  1. Initialise LangSmith tracing (if API key configured)
  2. Warm BM25 index from Pinecone metadata
  3. Register PII middleware + CORS
  4. Mount API routes
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os

from app.api.routes import router
from app.middleware.pii_middleware import PIIMiddleware
from app.core.config import get_settings
from app.core.langsmith_client import init_langsmith
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

# Initialise LangSmith tracing immediately (before any LangChain imports)
_langsmith_enabled = init_langsmith()


async def _warm_bm25():
    """Rebuild BM25 index from Pinecone metadata on startup."""
    try:
        from app.core.pinecone_client import get_pinecone_index
        from app.core.hybrid_search import build_bm25_index

        logger.info("Warming BM25 index from Pinecone metadata...")
        index = get_pinecone_index()
        stats = index.describe_index_stats()
        total = stats.total_vector_count

        if total == 0:
            logger.warning("Pinecone index is empty. Run ingestion first.")
            return

        sample_ids_response = index.list(limit=500)
        ids = list(sample_ids_response)
        if not ids:
            logger.warning("Could not fetch IDs for BM25 warm-up")
            return

        fetch_response = index.fetch(ids=ids[:500])
        corpus = []
        for vid, vec_data in fetch_response.vectors.items():
            meta = vec_data.metadata or {}
            text = meta.get("text", "")
            if text:
                corpus.append({"id": vid, "text": text, "metadata": meta})

        if corpus:
            build_bm25_index(corpus)
            logger.info(f"BM25 index warmed with {len(corpus)} documents")
    except Exception as e:
        logger.warning(f"BM25 warm-up failed (will work without keyword search): {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting DR. BLEEP — Medical Equipment Reliability Assistant...")
    logger.info(f"LangSmith tracing: {'ENABLED' if _langsmith_enabled else 'DISABLED'}")
    await _warm_bm25()
    logger.info("✓ Startup complete")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Medical Equipment Reliability Intelligence Assistant",
    description=(
        "AI-powered multi-agent system for hospital biomedical engineers "
        "to investigate equipment reliability using natural language."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── Middleware ────────────────────────────────────────────────────────────────

app.add_middleware(PIIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────

app.include_router(router)


@app.get("/")
async def root():
    return {
        "service": "Medical Equipment Reliability Intelligence Assistant",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
        "architecture": "/architecture",
    }


@app.get("/architecture", response_class=FileResponse)
async def architecture():
    path = os.path.join(os.path.dirname(__file__), "..", "docs", "architecture.html")
    return FileResponse(os.path.abspath(path), media_type="text/html")


@app.get("/techstack", response_class=FileResponse)
async def techstack():
    path = os.path.join(os.path.dirname(__file__), "..", "docs", "techstack.html")
    return FileResponse(os.path.abspath(path), media_type="text/html")
