"""
exam/generator.py
Question Generator — batch-based, no question limit, topic-diverse, no repeated questions.
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

TOPIC_QUERIES = [
    "SaaS PaaS IaaS cloud service models definitions",
    "EC2 instance types pricing on-demand reserved spot",
    "S3 storage classes lifecycle policies versioning",
    "IAM users groups roles policies permissions MFA",
    "VPC subnets security groups NACL routing",
    "RDS Aurora DynamoDB database managed service",
    "Lambda serverless functions event-driven computing",
    "CloudFront CDN edge locations distribution",
    "Route 53 DNS routing policies failover",
    "CloudWatch monitoring metrics alarms logs",
    "Elastic Load Balancer ALB NLB auto scaling groups",
    "CloudFormation Elastic Beanstalk CodeDeploy infrastructure",
    "shared responsibility model security compliance",
    "pricing calculator total cost of ownership TCO",
    "support plans basic developer business enterprise",
    "Well-Architected Framework pillars reliability performance",
    "Global Infrastructure regions availability zones edge",
    "Trusted Advisor Cost Explorer billing budgets",
    "migration strategies lift and shift replatform",
    "CloudTrail Config GuardDuty Shield WAF security",
    "SNS SQS EventBridge messaging decoupling",
    "ECS EKS containers Docker Kubernetes",
    "Glacier backup disaster recovery storage",
    "Direct Connect VPN hybrid cloud networking",
    "Organizations accounts consolidated billing",
]

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
    Generate exactly `num_questions` questions.
    Each batch uses a DIFFERENT topic — guaranteed variety, no repeats.
    """
    asked_questions = asked_questions or []
    all_questions: List[dict] = []
    already_seen: List[str]   = list(asked_questions)

    # Build a shuffled topic rotation — enough topics for all batches
    num_batches = (num_questions + BATCH_SIZE - 1) // BATCH_SIZE
    # Repeat topic list if we need more batches than topics
    topic_pool = TOPIC_QUERIES.copy()
    random.shuffle(topic_pool)
    while len(topic_pool) < num_batches:
        extra = TOPIC_QUERIES.copy()
        random.shuffle(extra)
        topic_pool.extend(extra)

    topic_idx  = 0
    remaining  = num_questions
    max_empty  = 5   # stop after 5 consecutive empty batches

    consecutive_empty = 0

    while remaining > 0 and consecutive_empty < max_empty:
        batch_size = min(BATCH_SIZE, remaining)
        topic      = topic_pool[topic_idx % len(topic_pool)]
        topic_idx += 1

        batch = _generate_batch(
            vectorstore     = vectorstore,
            domain          = domain,
            num_questions   = batch_size,
            difficulty      = difficulty,
            question_type   = question_type,
            asked_questions = already_seen,
            topic_query     = topic,
        )

        if not batch:
            consecutive_empty += 1
            continue

        consecutive_empty = 0
        all_questions.extend(batch)
        already_seen.extend(q["question"] for q in batch)
        # ✅ FIX: subtract actual generated count, not requested batch_size
        remaining -= len(batch)

    return all_questions[:num_questions]


def _generate_batch(
    vectorstore,
    domain: str,
    num_questions: int,
    difficulty: int,
    question_type: str,
    asked_questions: List[str],
    topic_query: str = "",
) -> List[dict]:
    """Single LLM call for a small batch using a specific topic."""
    difficulty_label = DIFFICULTY_LABELS.get(difficulty, "beginner")

    query = topic_query or f"certification concepts {domain}"

    docs = retrieve_context(query, vectorstore, top_k=5, domain_filter=domain)
    if not docs:
        docs = retrieve_context(query, vectorstore, top_k=5)

    random.shuffle(docs)
    context = _build_compact_context(docs, max_chars=3000)

    exclusion_hint = ""
    if asked_questions:
        sample = asked_questions[-30:]
        exclusion_hint = (
            "\n\nCRITICAL — Do NOT generate questions similar to these already asked:\n"
            + "\n".join(f"- {q}" for q in sample)
            + "\n\nEach question MUST cover a DIFFERENT concept from the ones above."
        )

    llm = get_llm(temperature=round(random.uniform(0.7, 0.95), 2))

    prompt = QUESTION_GENERATOR_PROMPT.format(
        context       = context + exclusion_hint,
        num_questions = num_questions,
        difficulty    = difficulty_label,
        domain        = domain,
        question_type = question_type,
    )

    try:
        response  = llm.invoke(prompt)
        raw       = response.content if hasattr(response, "content") else str(response)
        questions = _parse_questions(raw)
        questions = [_normalize_question(q) for q in questions]
        questions = _filter_duplicates(questions, asked_questions)
        return questions
    except Exception as e:
        print(f"[generator] Batch error: {e}")
        return []


# ─── Helpers ────────────────────────────────────────────────────────────────

def _build_compact_context(docs, max_chars: int = 3000) -> str:
    parts = []
    total = 0
    for i, doc in enumerate(docs, 1):
        source  = doc.metadata.get("source_file", "unknown")
        content = doc.page_content.strip()
        if len(content) > 700:
            content = content[:700] + "..."
        entry = f"[Source {i} — {source}]\n{content}"
        if total + len(entry) > max_chars:
            break
        parts.append(entry)
        total += len(entry)
    return "\n\n".join(parts)


def _filter_duplicates(questions: List[dict], asked: List[str]) -> List[dict]:
    """Remove questions too similar to already-asked ones."""
    if not asked:
        return questions
    asked_lower = [q.lower().strip() for q in asked]
    filtered = []
    for q in questions:
        q_text = q.get("question", "").lower().strip()
        is_dup = any(
            q_text == a
            or (len(q_text) > 15 and (q_text in a or a in q_text))
            or _similarity(q_text, a) > 0.75
            for a in asked_lower
        )
        if not is_dup:
            filtered.append(q)
    # If ALL filtered out, return originals to avoid infinite loops
    return filtered if filtered else questions


def _similarity(a: str, b: str) -> float:
    """Simple word overlap similarity."""
    words_a = set(a.split())
    words_b = set(b.split())
    if not words_a or not words_b:
        return 0.0
    return len(words_a & words_b) / max(len(words_a), len(words_b))


def _strip_html(text: str) -> str:
    """Remove any HTML tags the LLM accidentally injected."""
    import re as _re
    clean = _re.sub(r'<[^>]+>', '', str(text))
    return _re.sub(r'\s+', ' ', clean).strip()


def _normalize_question(q: dict) -> dict:
    if "question" in q:
        q["question"] = _strip_html(q["question"])
    if "correct_answer" in q:
        q["correct_answer"] = _strip_html(q["correct_answer"])
    if "explanation" in q:
        q["explanation"] = _strip_html(q["explanation"])

    if "choices" in q and "options" not in q:
        choices = q["choices"]
        if isinstance(choices, dict):
            q["options"] = [_strip_html(v) for v in choices.values()]
            correct = q.get("correct_answer", "")
            if correct in choices:
                q["correct_answer"] = _strip_html(choices[correct])
        del q["choices"]
    elif "options" in q and isinstance(q["options"], dict):
        choices = q["options"]
        q["options"] = [_strip_html(v) for v in choices.values()]
        correct = q.get("correct_answer", "")
        if correct in choices:
            q["correct_answer"] = _strip_html(choices[correct])
    elif "options" in q and isinstance(q["options"], list):
        q["options"] = [_strip_html(o) for o in q["options"]]

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