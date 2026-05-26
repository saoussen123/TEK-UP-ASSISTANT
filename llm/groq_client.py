"""
llm/groq_client.py
Initialise and return the GROQ LLM via LangChain.
Optimized for Groq free tier (100k tokens/day limit).
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# llama3-70b-8192 decommissioned → replaced by llama-3.3-70b-versatile
GROQ_MODEL   = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def get_llm(temperature: float = 0.5, model: str = None) -> ChatGroq:
    """Return a configured ChatGroq instance."""

    if not GROQ_API_KEY:
        raise ValueError(
            "❌ GROQ_API_KEY is missing. Please add it to your .env file."
        )

    return ChatGroq(
        api_key=GROQ_API_KEY,
        model=model or GROQ_MODEL,
        temperature=temperature,
        max_tokens=1024,   # reduced from 2048 to save daily token budget
    )