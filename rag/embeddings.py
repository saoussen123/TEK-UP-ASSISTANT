"""
rag/embeddings.py
Build and persist the vector store (ChromaDB) from document chunks.
"""

import os
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

EMBED_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./db/chroma_store")


def get_embeddings():
    """Return HuggingFace embedding model."""
    print(f"[Embeddings] Loading model: {EMBED_MODEL}")

    return HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def build_vectorstore(chunks: List[Document]) -> Chroma:
    """Create and persist Chroma vector store."""
    if not chunks:
        raise ValueError("No chunks provided to build vector store")

    Path(CHROMA_PERSIST_DIR).mkdir(parents=True, exist_ok=True)

    embeddings = get_embeddings()

    print(f"[Embeddings] Building vector store with {len(chunks)} chunks...")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PERSIST_DIR,
        collection_name="tekup_courses",
    )

    # Modern Chroma versions auto-persist, but this is still safe
    vectorstore.persist()

    print(f"[Embeddings] ✔ Vector store saved to: {CHROMA_PERSIST_DIR}")

    return vectorstore


def load_vectorstore() -> Chroma:
    """Load existing Chroma vector store from disk."""
    embeddings = get_embeddings()

    if not vectorstore_exists():
        raise FileNotFoundError("Vector store not found. Run ingestion first.")

    vectorstore = Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=embeddings,
        collection_name="tekup_courses",
    )

    print(f"[Embeddings] ✔ Loaded vector store from: {CHROMA_PERSIST_DIR}")

    return vectorstore


def vectorstore_exists() -> bool:
    """Check if vector store already exists."""
    path = Path(CHROMA_PERSIST_DIR)

    return path.exists() and any(path.iterdir())