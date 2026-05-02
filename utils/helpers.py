"""
utils/helpers.py
Shared utility functions.
"""
import streamlit as st
from langchain_community.vectorstores import Chroma
from rag.embeddings import build_vectorstore, load_vectorstore, vectorstore_exists
from rag.ingestion  import ingest


def get_or_build_vectorstore() -> Chroma:
    """Load existing vector store or build a new one from data/cours."""
    if vectorstore_exists():
        return load_vectorstore()
    else:
        chunks = ingest()
        return build_vectorstore(chunks)


def score_color(percentage: float) -> str:
    """Return a CSS color string based on score percentage."""
    if percentage >= 80:
        return "#4ade80"   # green
    elif percentage >= 50:
        return "#fbbf24"   # amber
    else:
        return "#f87171"   # red


def score_label(percentage: float) -> str:
    if percentage >= 80:
        return "Excellent ✦"
    elif percentage >= 60:
        return "Good ✔"
    elif percentage >= 40:
        return "Keep practicing"
    else:
        return "Needs revision ✗"


def difficulty_label(level: int) -> str:
    return {1: "Beginner", 2: "Intermediate", 3: "Advanced"}.get(level, "Beginner")