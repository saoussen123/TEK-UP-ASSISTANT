"""
scripts/test_pipeline.py
Quick smoke-test of the full pipeline (no Streamlit needed).
Usage: python scripts/test_pipeline.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.embeddings  import load_vectorstore, vectorstore_exists
from exam.generator  import generate_questions
from exam.evaluator  import evaluate_answer, compute_final_score

def main():
    print("\n=== TEK-UP Pipeline Test ===\n")

    if not vectorstore_exists():
        print("⚠ No vector store found. Run scripts/index_courses.py first.")
        return

    vs = load_vectorstore()
    print("✔ Vector store loaded.\n")

    print("Generating 2 MCQ questions…")
    questions = generate_questions(vs, domain="general", num_questions=2, difficulty=1, question_type="MCQ")
    if not questions:
        print("✘ No questions generated. Check your GROQ_API_KEY.")
        return

    results = []
    for i, q in enumerate(questions):
        print(f"\nQ{i+1}: {q.get('question','')}")
        choices = q.get("choices", {})
        for k, v in choices.items():
            print(f"  {k}: {v}")
        answer = input("Your answer (A/B/C/D): ").strip().upper()
        result = evaluate_answer(q, answer, vs)
        result["question"]       = q.get("question","")
        result["correct_answer"] = q.get("correct_answer","")
        result["student_answer"] = answer
        results.append(result)
        icon = "✅" if result.get("is_correct") else "❌"
        print(f"{icon} Score: {result.get('score')}/10 — {result.get('feedback','')}")
        if not result.get("is_correct"):
            print(f"💡 {result.get('explanation','')}")

    stats = compute_final_score(results)
    print(f"\n=== Final Score: {stats['percentage']}% ({stats['correct']}/{stats['total']}) ===")

if __name__ == "__main__":
    main()