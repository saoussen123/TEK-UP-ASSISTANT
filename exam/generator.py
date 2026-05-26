"""
exam/generator.py
Question Generator — batch-based, no question limit, optimized for Groq free tier.
"""
import json
import re
import random
from typing import List

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

QUERY_TEMPLATES = [
    "technical concepts services features {domain}",
    "key services use cases {domain}",
    "security networking storage compute {domain}",
    "definitions best practices {domain}",
    "core services features {domain}",
    "advanced configuration deployment {domain}",
    "monitoring logging troubleshooting {domain}",
    "pricing models cost optimization {domain}",
    "integration authentication authorization {domain}",
    "architecture patterns scalability {domain}",
]

# Max questions per single LLM call — keeps response within token limits
BATCH_SIZE = 5


def generate_questions(
    vectorstore: Chroma,
    domain: str        = "general",
    num_questions: int = 5,
    difficulty: int    = 1,
    question_type: str = "MCQ",
    asked_questions: List[str] = None,
) -> List[dict]:
    """
    Generate exactly `num_questions` questions with no upper limit.
    Internally splits into batches of BATCH_SIZE to stay within Groq token limits.
    """
    asked_questions = asked_questions or []
    all_questions: List[dict] = []
    already_seen: List[str] = list(asked_questions)  # track across batches
    max_retries = 3  # max retries per batch before giving up

    remaining = num_questions

    while remaining > 0:
        batch_size = min(BATCH_SIZE, remaining)

        batch = None
        for attempt in range(max_retries):
            batch = _generate_batch(
                vectorstore   = vectorstore,
                domain        = domain,
                num_questions = batch_size,
                difficulty    = difficulty,
                question_type = question_type,
                asked_questions = already_seen,
            )
            if batch:
                break
            # On failure, slightly vary temperature via a new LLM call in _generate_batch

        if not batch:
            # Could not generate this batch after retries — stop gracefully
            break

        all_questions.extend(batch)
        # Add new questions to exclusion list for next batch
        already_seen.extend(q["question"] for q in batch)
        remaining -= len(batch)

    return all_questions


def _generate_batch(
    vectorstore,
    domain: str,
    num_questions: int,
    difficulty: int,
    question_type: str,
    asked_questions: List[str],
) -> List[dict]:
    """
    Single LLM call for a small batch (≤ BATCH_SIZE questions).
    Uses a different random query template each time for variety.
    """
    difficulty_label = DIFFICULTY_LABELS.get(difficulty, "beginner")

    # Rotate query template for variety across batches
    query = random.choice(QUERY_TEMPLATES).format(
        domain=domain, difficulty=difficulty_label
    )

    docs = retrieve_context(query, vectorstore, top_k=4, domain_filter=domain)
    if not docs:
        docs = retrieve_context(query, vectorstore, top_k=4)

    random.shuffle(docs)

    # Compact context — 2000 chars is enough for 5 questions
    context = _build_compact_context(docs, max_chars=2000)

    # Exclusion hint — only last 20 to keep prompt lean
    exclusion_hint = ""
    if asked_questions:
        sample = asked_questions[-20:]
        exclusion_hint = (
            "\n\nDo NOT repeat these questions:\n"
            + "\n".join(f"- {q}" for q in sample)
        )

    llm = get_llm(temperature=round(random.uniform(0.6, 0.9), 2))

    prompt = QUESTION_GENERATOR_PROMPT.format(
        context       = context + exclusion_hint,
        num_questions = num_questions,
        difficulty    = difficulty_label,
        domain        = domain,
        question_type = question_type,
    )

    try:
        response = llm.invoke(prompt)
        raw = response.content if hasattr(response, "content") else str(response)
        questions = _parse_questions(raw)
        questions = [_normalize_question(q) for q in questions]
        questions = _filter_duplicates(questions, asked_questions)
        return questions
    except Exception as e:
        print(f"[generator] Batch error: {e}")
        return []


# ─── Helpers ────────────────────────────────────────────────────────────────

def _build_compact_context(docs, max_chars: int = 2000) -> str:
    """Build a compact context string, trimming each chunk to save tokens."""
    parts = []
    total = 0
    for i, doc in enumerate(docs, 1):
        source  = doc.metadata.get("source_file", "unknown")
        content = doc.page_content.strip()
        if len(content) > 500:
            content = content[:500] + "..."
        entry = f"[Source {i} — {source}]\n{content}"
        if total + len(entry) > max_chars:
            break
        parts.append(entry)
        total += len(entry)
    return "\n\n".join(parts)


def _filter_duplicates(questions: List[dict], asked: List[str]) -> List[dict]:
    if not asked:
        return questions
    asked_lower = [q.lower().strip() for q in asked]
    filtered = []
    for q in questions:
        q_text = q.get("question", "").lower().strip()
        is_dup = any(
            q_text == a or (len(q_text) > 20 and (q_text in a or a in q_text))
            for a in asked_lower
        )
        if not is_dup:
            filtered.append(q)
    return filtered if filtered else questions


def _normalize_question(q: dict) -> dict:
    if "choices" in q and "options" not in q:
        choices = q["choices"]
        if isinstance(choices, dict):
            q["options"] = list(choices.values())
            correct = q.get("correct_answer", "")
            if correct in choices:
                q["correct_answer"] = choices[correct]
        del q["choices"]
    elif "options" in q and isinstance(q["options"], dict):
        choices = q["options"]
        q["options"] = list(choices.values())
        correct = q.get("correct_answer", "")
        if correct in choices:
            q["correct_answer"] = choices[correct]
    if q.get("type") == "True/False" and "options" not in q:
        q["options"] = ["True", "False"]
    return q


def _parse_questions(raw: str) -> List[dict]:
    raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("```").strip()
    try:
        data = json.loads(raw)
        return data.get("questions", [])
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
                return data.get("questions", [])
            except Exception:
                pass
    return []