"""
utils/ingest.py
Document Ingestion Pipeline

Loads PDFs and text files into ChromaDB for retrieval.

Usage:
    python -m utils.ingest --path ./data/sample_docs/
    python -m utils.ingest --path ./my_notes.pdf
"""

import argparse
import logging
import os
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s — %(message)s")
logger = logging.getLogger(__name__)

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
COLLECTION_NAME = "learning_materials"

SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def load_documents(path: str):
    """Load documents from a file or directory."""
    p = Path(path)

    if p.is_dir():
        logger.info("Loading all PDFs and .txt files from directory: %s", path)
        loaders = []
        # PDF files
        for pdf in p.rglob("*.pdf"):
            loaders.append(PyPDFLoader(str(pdf)))
        # Text files
        for txt in p.rglob("*.txt"):
            loaders.append(TextLoader(str(txt), encoding="utf-8"))
        docs = []
        for loader in loaders:
            docs.extend(loader.load())
    elif p.suffix.lower() == ".pdf":
        logger.info("Loading PDF: %s", path)
        docs = PyPDFLoader(path).load()
    elif p.suffix.lower() in (".txt", ".md"):
        logger.info("Loading text file: %s", path)
        docs = TextLoader(path, encoding="utf-8").load()
    else:
        raise ValueError(f"Unsupported file type: {p.suffix}")

    return docs


def ingest(path: str) -> int:
    """
    Ingest documents at `path` into ChromaDB.
    Returns the number of chunks stored.
    """
    raw_docs = load_documents(path)
    logger.info("Loaded %d raw documents", len(raw_docs))

    chunks = SPLITTER.split_documents(raw_docs)
    logger.info("Split into %d chunks", len(chunks))

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PERSIST_DIR,
    )
    vectorstore.persist()

    logger.info(
        "✅ Ingested %d chunks into ChromaDB at '%s'", len(chunks), CHROMA_PERSIST_DIR
    )
    return len(chunks)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest documents into the vector store")
    parser.add_argument(
        "--path",
        required=True,
        help="Path to a PDF file, text file, or directory",
    )
    args = parser.parse_args()
    total = ingest(args.path)
    print(f"\n✅ Done — {total} chunks stored in ChromaDB")
