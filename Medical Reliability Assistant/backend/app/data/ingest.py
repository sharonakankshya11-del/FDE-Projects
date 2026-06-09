"""
app/data/ingest.py
Full ingestion pipeline:
  1. Load CSVs
  2. Generate incident narratives
  3. Recursive text split (chunking)
  4. Embed with text-embedding-3-small
  5. Upsert to ChromaDB
  6. Build BM25 index in memory
"""
import csv
import uuid
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.data.narrative_generator import generate_narratives
from app.core.embeddings import embed_texts
from app.core.pinecone_client import upsert_documents
from app.core.hybrid_search import build_bm25_index
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Chunk settings - narratives are ~200-400 tokens so one chunk covers most,
# but splitting ensures no truncation at the embedding model limit.
_splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=64,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def _load_csv(path: str) -> List[Dict[str, Any]]:
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    return rows


def _chunk_documents(
    docs: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Split each narrative doc into chunks; propagate metadata."""
    chunks = []
    for doc in docs:
        splits = _splitter.split_text(doc["text"])
        for i, chunk_text in enumerate(splits):
            chunk_id = f"{doc['id']}-c{i}"
            meta = {**doc["metadata"], "chunk_index": i, "text": chunk_text}
            chunks.append({"id": chunk_id, "text": chunk_text, "metadata": meta})
    return chunks


def run_ingestion(csv_path1: str, csv_path2: str) -> int:
    """
    Full pipeline. Returns total number of vectors upserted.
    """
    # 1. Load
    logger.info(f"Loading {csv_path1}...")
    rows1 = _load_csv(csv_path1)
    logger.info(f"  ✓ {len(rows1)} rows from ai4i2020")

    logger.info(f"Loading {csv_path2}...")
    rows2 = _load_csv(csv_path2)
    logger.info(f"  ✓ {len(rows2)} rows from predictive_maintenance")

    # 2. Generate narratives
    logger.info("Generating incident narratives...")
    docs1 = generate_narratives(rows1, source="ai4i")
    docs2 = generate_narratives(rows2, source="pred_maint")
    all_docs = docs1 + docs2
    logger.info(f"  ✓ {len(all_docs)} narrative documents")

    # 3. Chunk
    logger.info("Chunking documents...")
    chunks = _chunk_documents(all_docs)
    logger.info(f"  ✓ {len(chunks)} chunks")

    # 4. Embed (batched)
    logger.info("Embedding chunks (this may take a few minutes)...")
    texts = [c["text"] for c in chunks]
    vectors = embed_texts(texts, batch_size=100)
    logger.info(f"  ✓ {len(vectors)} vectors generated")

    # 5. Upsert to ChromaDB
    logger.info("Upserting to Pinecone...")
    ids = [c["id"] for c in chunks]
    metas = [c["metadata"] for c in chunks]
    upsert_documents(ids, vectors, metas)
    logger.info("  ✓ Pinecone upsert complete")

    # 6. Build BM25 in memory (use original docs, not chunks, for recall)
    logger.info("Building BM25 index...")
    bm25_corpus = [
        {"id": c["id"], "text": c["text"], "metadata": c["metadata"]}
        for c in chunks
    ]
    build_bm25_index(bm25_corpus)
    logger.info(f"  ✓ BM25 index built with {len(bm25_corpus)} documents")

    return len(chunks)
