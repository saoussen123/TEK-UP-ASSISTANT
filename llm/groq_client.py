"""
llm/groq_client.py
Initialise and return the GROQ LLM via LangChain.
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-70b-8192")


def get_llm(temperature: float = 0.7) -> ChatGroq:
    """Return a configured ChatGroq instance."""

    if not GROQ_API_KEY:
        raise ValueError(
            "❌ GROQ_API_KEY is missing. Please add it to your .env file."
        )

    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model=GROQ_MODEL,
        temperature=temperature,
        max_tokens=2048,
    )

    return llm