"""
rag/ingestion.py
Robust ingestion pipeline (PDF / DOCX / TXT)
Fixed for better PDF extraction (PyMuPDF instead of PyPDFLoader)
Handles empty files, scanned PDFs fallback warning, and safe chunking.
"""

import os
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyMuPDFLoader,   # ✅ FIXED (better than PyPDFLoader)
    Docx2txtLoader,
    TextLoader,
)

from dotenv import load_dotenv

load_dotenv()

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))

DATA_DIR = Path("data/cours")

SUPPORTED = {
    ".pdf": PyMuPDFLoader,   # ✅ FIXED HERE
    ".docx": Docx2txtLoader,
    ".txt": TextLoader,
}


# ─────────────────────────────────────────────────────────────
# LOAD FILES
# ─────────────────────────────────────────────────────────────
def load_documents(directory: str | Path) -> List[Document]:
    directory = Path(directory)
    docs: List[Document] = []

    if not directory.exists():
        print(f"❌ Directory not found: {directory}")
        return []

    for filepath in directory.rglob("*"):
        suffix = filepath.suffix.lower()

        if suffix not in SUPPORTED:
            continue

        try:
            loader = SUPPORTED[suffix](str(filepath))
            loaded_docs = loader.load()

            # ⚠ if still empty → likely scanned PDF
            if not loaded_docs:
                print(f"⚠ EMPTY FILE (maybe scanned PDF): {filepath.name}")
                continue

            cleaned = []

            for doc in loaded_docs:
                text = doc.page_content.strip() if doc.page_content else ""

                if not text:
                    continue

                doc.metadata["source_file"] = filepath.name
                doc.metadata["domain"] = filepath.parent.name
                cleaned.append(doc)

            if cleaned:
                docs.extend(cleaned)
                print(f"✔ Loaded: {filepath.name} ({len(cleaned)} pages)")

        except Exception as e:
            print(f"✘ Error loading {filepath.name}: {e}")

    print(f"\n→ Total documents loaded: {len(docs)}")
    return docs


# ─────────────────────────────────────────────────────────────
# SPLIT INTO CHUNKS
# ─────────────────────────────────────────────────────────────
def split_documents(docs: List[Document]) -> List[Document]:
    if not docs:
        print("⚠ No documents found for splitting")
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""],
    )

    chunks = splitter.split_documents(docs)

    print(f"→ Total chunks created: {len(chunks)}")
    return chunks


# ─────────────────────────────────────────────────────────────
# MAIN PIPELINE
# ─────────────────────────────────────────────────────────────
def ingest(directory: str | Path = DATA_DIR) -> List[Document]:
    print(f"\n🚀 Ingestion started: {directory}")

    docs = load_documents(directory)

    if not docs:
        print("❌ No readable documents found (likely scanned PDFs → need OCR)")
        return []

    chunks = split_documents(docs)

    if not chunks:
        print("❌ No chunks created from documents")
        return []

    print(f"✅ Ingestion complete → {len(chunks)} chunks")
    return chunks