"""
exam/evaluator.py
Tool 2 — Answer Evaluator + Error Explainer
Evaluates student answers and generates detailed explanations for mistakes.
"""
import json
import re
from typing import Optional

from langchain_community.vectorstores import Chroma

from llm.groq_client import get_llm
from llm.prompts     import ANSWER_EVALUATOR_PROMPT, ERROR_EXPLAINER_PROMPT
from rag.retriever   import retrieve_context, format_context


def evaluate_answer(
    question: dict,
    student_answer: str,
    vectorstore: Chroma,
) -> dict:
    """
    Evaluate a student's answer against the correct one.

    Args:
        question:       A question dict from the generator (must have 'question' & 'correct_answer').
        student_answer: The student's raw answer string.
        vectorstore:    The loaded ChromaDB vector store.

    Returns:
        dict with keys: score, is_correct, feedback, correct_answer_restated, explanation
    """
    q_text  = question.get("question", "")
    correct = question.get("correct_answer", "")

    # Retrieve relevant context for this question
    docs    = retrieve_context(q_text, vectorstore, top_k=3)
    context = format_context(docs)

    llm    = get_llm(temperature=0.2)

    # Step 1: Score the answer
    eval_prompt = ANSWER_EVALUATOR_PROMPT.format(
        question       = q_text,
        student_answer = student_answer,
        correct_answer = correct,
        context        = context,
    )
    eval_response = llm.invoke(eval_prompt)
    eval_raw      = eval_response.content if hasattr(eval_response, "content") else str(eval_response)
    result        = _parse_eval(eval_raw)

    # Step 2: If wrong, generate a detailed explanation
    is_correct = result.get("is_correct", False)
    if not is_correct:
        explanation = explain_error(
            question       = q_text,
            student_answer = student_answer,
            correct_answer = correct,
            context        = context,
        )
        result["explanation"] = explanation
    else:
        result["explanation"] = "Well done! Your answer is correct."

    return result


def explain_error(
    question: str,
    student_answer: str,
    correct_answer: str,
    context: str,
) -> str:
    """Generate a pedagogical explanation for a wrong answer."""
    llm    = get_llm(temperature=0.5)
    prompt = ERROR_EXPLAINER_PROMPT.format(
        question       = question,
        student_answer = student_answer,
        correct_answer = correct_answer,
        context        = context,
    )
    response = llm.invoke(prompt)
    return response.content if hasattr(response, "content") else str(response)


def _parse_eval(raw: str) -> dict:
    """Parse the JSON evaluation response from the LLM."""
    raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("```").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
    # Fallback
    return {
        "score": 0,
        "is_correct": False,
        "feedback": raw[:200],
        "correct_answer_restated": "",
    }


def compute_final_score(results: list) -> dict:
    """Compute overall exam statistics from a list of evaluation results."""
    if not results:
        return {"total": 0, "correct": 0, "percentage": 0}

    total   = len(results)
    correct = sum(1 for r in results if r.get("is_correct", False))
    scores  = [r.get("score", 0) for r in results]
    avg     = round(sum(scores) / total, 1)

    return {
        "total":      total,
        "correct":    correct,
        "wrong":      total - correct,
        "percentage": round(correct / total * 100, 1),
        "avg_score":  avg,
    }