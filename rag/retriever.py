"""
rag/retriever.py
Semantic retrieval: query the vector store and return top-k relevant chunks.
"""

import os
from typing import List, Optional

from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()

TOP_K = int(os.getenv("TOP_K", 4))


def get_retriever(vectorstore: Chroma, top_k: int = TOP_K):
    """Return a LangChain retriever from the vector store."""
    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": top_k},
    )


def retrieve_context(
    query: str,
    vectorstore: Chroma,
    top_k: int = TOP_K,
    domain_filter: Optional[str] = None,
) -> List[Document]:
    """
    Retrieve most relevant chunks for a query.
    Optionally filter by domain metadata.
    """

    if domain_filter:
        # Chroma metadata filter
        docs = vectorstore.similarity_search(
            query,
            k=top_k,
            filter={"domain": domain_filter},
        )
    else:
        docs = vectorstore.similarity_search(query, k=top_k)

    return docs


def format_context(docs: List[Document]) -> str:
    """Format retrieved docs into a single prompt context string."""
    if not docs:
        return ""

    formatted_parts = []

    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source_file", "unknown")
        content = doc.page_content.strip()

        formatted_parts.append(
            f"[Source {i} — {source}]\n{content}"
        )

    return "\n\n".join(formatted_parts)


def get_available_domains(vectorstore: Chroma) -> List[str]:
    """Return unique domains from stored metadata."""
    try:
        collection = vectorstore._collection
        data = collection.get()

        metadatas = data.get("metadatas", [])

        domains = sorted({
            m.get("domain", "general")
            for m in metadatas
            if m
        })

        return domains if domains else ["general"]

    except Exception:
        return ["general"]