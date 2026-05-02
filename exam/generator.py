"""
exam/generator.py
Tool 1 — Question Generator
Retrieves relevant course chunks and asks the LLM to generate exam questions.
"""
import json
import re
from typing import List, Optional

from langchain_community.vectorstores import Chroma

from llm.groq_client import get_llm
from llm.prompts     import QUESTION_GENERATOR_PROMPT
from rag.retriever   import retrieve_context, format_context


DIFFICULTY_LABELS = {
    1: "beginner",
    2: "intermediate",
    3: "advanced",
}

QUESTION_TYPES = ["MCQ", "True/False", "Open"]


def generate_questions(
    vectorstore: Chroma,
    domain: str        = "general",
    num_questions: int = 5,
    difficulty: int    = 1,
    question_type: str = "MCQ",
) -> List[dict]:
    """
    Generate exam questions from course material.

    Args:
        vectorstore:    The loaded ChromaDB vector store.
        domain:         Certification domain (used as search filter & label).
        num_questions:  Number of questions to generate (1–10).
        difficulty:     1 = beginner, 2 = intermediate, 3 = advanced.
        question_type:  'MCQ', 'True/False', or 'Open'.

    Returns:
        List of question dicts parsed from the LLM JSON output.
    """
    difficulty_label = DIFFICULTY_LABELS.get(difficulty, "beginner")

    # 1. Retrieve relevant course context
    query = f"{domain} {difficulty_label} certification exam questions {question_type}"
    docs  = retrieve_context(query, vectorstore, top_k=5, domain_filter=domain)
    if not docs:
        docs = retrieve_context(query, vectorstore, top_k=5)  # fallback: no filter

    context = format_context(docs)

    # 2. Build prompt and call LLM
    llm    = get_llm(temperature=0.7)
    prompt = QUESTION_GENERATOR_PROMPT.format(
        context       = context,
        num_questions = num_questions,
        difficulty    = difficulty_label,
        domain        = domain,
        question_type = question_type,
    )

    response = llm.invoke(prompt)
    raw      = response.content if hasattr(response, "content") else str(response)

    # 3. Parse JSON output
    questions = _parse_questions(raw)
    return questions


def _parse_questions(raw: str) -> List[dict]:
    """Extract JSON from LLM output robustly."""
    # Strip markdown code fences if present
    raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("```").strip()

    try:
        data = json.loads(raw)
        return data.get("questions", [])
    except json.JSONDecodeError:
        # Try to extract JSON object with regex
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
                return data.get("questions", [])
            except Exception:
                pass
    return []