"""
scripts/index_courses.py
Standalone script to index all course materials without launching the app.
Usage: python scripts/index_courses.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.ingestion  import ingest
from rag.embeddings import build_vectorstore, vectorstore_exists

def main():
    if vectorstore_exists():
        ans = input("Vector store already exists. Rebuild? [y/N]: ").strip().lower()
        if ans != "y":
            print("Aborted.")
            return

    print("\n=== TEK-UP Course Indexer ===\n")
    chunks = ingest("data/cours")
    if not chunks:
        print("\n⚠ No documents found in data/cours/. Add your PDFs and retry.")
        return
    print(f"\nBuilding vector store from {len(chunks)} chunks…")
    build_vectorstore(chunks)
    print("\n✔ Indexing complete. You can now run the app.")

if __name__ == "__main__":
    main()