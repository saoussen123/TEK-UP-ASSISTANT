"""
llm/prompts.py
All prompt templates used by the application.
"""

from langchain_core.prompts import PromptTemplate

# ─── 1. Question Generator ──────────────────────────────────────────────────

QUESTION_GENERATOR_PROMPT = PromptTemplate(
    input_variables=["context", "num_questions", "difficulty", "domain", "question_type"],
    template="""You are an expert exam creator for TEK-UP certification courses.

Based ONLY on the course material below, generate {num_questions} {question_type} questions.
Difficulty level: {difficulty}
Domain / Certification: {domain}

COURSE MATERIAL:
{context}

INSTRUCTIONS:
- Each question must be directly based on the provided course material.
- For MCQ: provide 4 answer choices (A, B, C, D), mark the correct one.
- For True/False: state the answer clearly.
- For open questions: provide a model answer.
- Always cite which source passage supports the answer.
- Format your output as valid JSON like this:

{{
  "questions": [
    {{
      "id": 1,
      "type": "{question_type}",
      "question": "...",
      "choices": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
      "correct_answer": "A",
      "explanation": "...",
      "source_hint": "brief quote from the course material"
    }}
  ]
}}

For True/False or open questions, omit the "choices" field.
Respond ONLY with the JSON object. No extra text.
""",
)

# ─── 2. Answer Evaluator ────────────────────────────────────────────────────

ANSWER_EVALUATOR_PROMPT = PromptTemplate(
    input_variables=["question", "student_answer", "correct_answer", "context"],
    template="""You are a strict but fair TEK-UP certification exam evaluator.

QUESTION: {question}
CORRECT ANSWER: {correct_answer}
STUDENT ANSWER: {student_answer}

COURSE CONTEXT:
{context}

Evaluate the student's answer and respond ONLY with this JSON:

{{
  "score": <integer 0–10>,
  "is_correct": <true or false>,
  "feedback": "short feedback sentence (1–2 lines)",
  "correct_answer_restated": "the correct answer in plain language"
}}
""",
)

# ─── 3. Error Explainer ─────────────────────────────────────────────────────

ERROR_EXPLAINER_PROMPT = PromptTemplate(
    input_variables=["question", "student_answer", "correct_answer", "context"],
    template="""You are a TEK-UP course tutor. A student made a mistake. Help them understand why.

QUESTION: {question}
STUDENT'S WRONG ANSWER: {student_answer}
CORRECT ANSWER: {correct_answer}

RELEVANT COURSE PASSAGE:
{context}

Write a clear, educational explanation (3–5 sentences) that:
1. States what was wrong and why.
2. Explains the correct concept using the course material.
3. Gives a memory tip or analogy to remember it.

Be encouraging and pedagogical. Do NOT repeat the question word for word.
""",
)

# ─── 4. Agent System Prompt ─────────────────────────────────────────────────

AGENT_SYSTEM_PROMPT = """You are the TEK-UP AI Exam Assistant.
You help students prepare for TEK-UP certification exams by:
- Generating practice questions from official course materials
- Evaluating student answers and providing scores
- Explaining mistakes with detailed, course-backed explanations

Always base your answers on the retrieved course context.
Be precise, educational, and encouraging.
"""