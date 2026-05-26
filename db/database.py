"""
db/database.py
SQLite persistence — sessions, results, asked questions, uploaded courses by field.
Fixed: WAL mode, context manager, no nested connections.
"""
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "./db/sessions.db")

# ─── Fields / Domains ────────────────────────────────────────────────────────
FIELDS = {
    "cloud":    {"label": "Cloud Administration",       "icon": "☁️",  "certifications": ["AWS SAA", "AWS CLF", "Azure AZ-900", "GCP ACE"]},
    "ai_ml":    {"label": "AI / ML & Data Science",     "icon": "🤖",  "certifications": ["TensorFlow Dev", "AWS ML Specialty", "Azure AI-900", "DP-100"]},
    "network":  {"label": "Réseaux & Infrastructure",   "icon": "🌐",  "certifications": ["CCNA", "CCNP", "CompTIA Network+", "Juniper JNCIA"]},
    "security": {"label": "Cybersécurité",              "icon": "🔐",  "certifications": ["CEH", "CISSP", "CompTIA Security+", "eJPT"]},
}

FIELD_KEYWORDS = {
    "cloud":    ["aws","azure","gcp","cloud","ec2","s3","vpc","lambda","rds","cloudfront","route53","iam","kubernetes","terraform","devops","docker"],
    "ai_ml":    ["machine learning","deep learning","neural","tensorflow","pytorch","pandas","numpy","scikit","data science","nlp","computer vision","llm","ai","ml","model","dataset"],
    "network":  ["cisco","ccna","ccnp","network","router","switch","tcp","ip","ospf","bgp","vlan","firewall","packet","subnet","ethernet","wifi","protocol"],
    "security": ["security","cybersecurity","hacking","penetration","ceh","cissp","malware","vulnerability","exploit","ctf","soc","siem","forensics","encryption","ssl","tls"],
}


def detect_field(filename: str, content_hint: str = "") -> str:
    """Auto-detect field from filename or content keywords."""
    text = (filename + " " + content_hint).lower()
    scores = {field: 0 for field in FIELD_KEYWORDS}
    for field, keywords in FIELD_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                scores[field] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "cloud"


@contextmanager
def _get_conn():
    """Safe WAL-mode connection context manager."""
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Create all tables if they don't exist."""
    with _get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                student    TEXT    NOT NULL,
                domain     TEXT    NOT NULL,
                field      TEXT    NOT NULL DEFAULT 'cloud',
                difficulty INTEGER NOT NULL,
                q_type     TEXT    NOT NULL,
                total_q    INTEGER NOT NULL,
                correct    INTEGER NOT NULL,
                percentage REAL    NOT NULL,
                avg_score  REAL    NOT NULL,
                created_at TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS exam_results (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id  INTEGER NOT NULL,
                question    TEXT    NOT NULL,
                correct_ans TEXT    NOT NULL,
                student_ans TEXT    NOT NULL,
                score       INTEGER NOT NULL,
                is_correct  INTEGER NOT NULL,
                explanation TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            );

            CREATE TABLE IF NOT EXISTS asked_questions (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                student    TEXT    NOT NULL,
                domain     TEXT    NOT NULL,
                question   TEXT    NOT NULL,
                created_at TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS uploaded_courses (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                student    TEXT    NOT NULL,
                filename   TEXT    NOT NULL,
                field      TEXT    NOT NULL,
                filepath   TEXT    NOT NULL,
                size_mb    REAL    NOT NULL DEFAULT 0,
                created_at TEXT    NOT NULL
            );
        """)


# ─── Sessions ─────────────────────────────────────────────────────────────────

def save_session(
    student: str,
    domain: str,
    difficulty: int,
    q_type: str,
    stats: dict,
    results: list,
    field: str = "cloud",
) -> int:
    """Persist a completed exam session. All inserts in ONE connection."""
    with _get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO sessions
                (student, domain, field, difficulty, q_type, total_q, correct, percentage, avg_score, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            student, domain, field, difficulty, q_type,
            stats["total"], stats["correct"],
            stats["percentage"], stats["avg_score"],
            datetime.now().strftime("%Y-%m-%d %H:%M"),
        ))
        session_id = cur.lastrowid
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        for r in results:
            question_text = r.get("question", "")
            cur.execute("""
                INSERT INTO exam_results
                    (session_id, question, correct_ans, student_ans, score, is_correct, explanation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id, question_text,
                r.get("correct_answer", ""), r.get("student_answer", ""),
                r.get("score", 0), 1 if r.get("is_correct") else 0,
                r.get("explanation", ""),
            ))
            cur.execute("""
                INSERT INTO asked_questions (student, domain, question, created_at)
                VALUES (?, ?, ?, ?)
            """, (student, domain, question_text, now))

        return session_id


def get_history(student: str, field: str = None) -> list:
    """Return past sessions for a student, optionally filtered by field."""
    with _get_conn() as conn:
        if field:
            rows = conn.execute(
                "SELECT * FROM sessions WHERE student=? AND field=? ORDER BY created_at DESC",
                (student, field)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM sessions WHERE student=? ORDER BY created_at DESC",
                (student,)
            ).fetchall()
    return [dict(r) for r in rows]


def get_session_results(session_id: int) -> list:
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM exam_results WHERE session_id=?", (session_id,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_student_stats(student: str) -> dict:
    """Return global stats for a student."""
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT field, COUNT(*) as exams, AVG(percentage) as avg_pct, MAX(percentage) as best "
            "FROM sessions WHERE student=? GROUP BY field",
            (student,)
        ).fetchall()
    stats = {}
    for r in rows:
        stats[r["field"]] = {
            "exams": r["exams"],
            "avg_pct": round(r["avg_pct"] or 0, 1),
            "best": round(r["best"] or 0, 1),
        }
    return stats


# ─── Asked questions ──────────────────────────────────────────────────────────

def save_asked_question(student: str, domain: str, question: str):
    with _get_conn() as conn:
        conn.execute("""
            INSERT INTO asked_questions (student, domain, question, created_at)
            VALUES (?, ?, ?, ?)
        """, (student, domain, question, datetime.now().strftime("%Y-%m-%d %H:%M")))


def get_asked_questions(student: str, domain: str) -> list:
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT question FROM asked_questions WHERE student=? AND domain=?",
            (student, domain)
        ).fetchall()
    return [r["question"] for r in rows]


def reset_asked_questions(student: str, domain: str):
    with _get_conn() as conn:
        conn.execute(
            "DELETE FROM asked_questions WHERE student=? AND domain=?",
            (student, domain)
        )


# ─── Uploaded courses ─────────────────────────────────────────────────────────

def save_course(student: str, filename: str, field: str, filepath: str, size_mb: float = 0):
    """Register an uploaded course under a field."""
    with _get_conn() as conn:
        # Avoid duplicates
        exists = conn.execute(
            "SELECT id FROM uploaded_courses WHERE student=? AND filename=?",
            (student, filename)
        ).fetchone()
        if not exists:
            conn.execute("""
                INSERT INTO uploaded_courses (student, filename, field, filepath, size_mb, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (student, filename, field, filepath, size_mb,
                  datetime.now().strftime("%Y-%m-%d %H:%M")))


def get_courses_by_field(student: str, field: str) -> list:
    """Return all uploaded courses for a student in a given field."""
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM uploaded_courses WHERE student=? AND field=? ORDER BY created_at DESC",
            (student, field)
        ).fetchall()
    return [dict(r) for r in rows]


def get_all_courses(student: str) -> list:
    """Return all uploaded courses for a student."""
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM uploaded_courses WHERE student=? ORDER BY field, created_at DESC",
            (student,)
        ).fetchall()
    return [dict(r) for r in rows]


def delete_course(course_id: int):
    with _get_conn() as conn:
        conn.execute("DELETE FROM uploaded_courses WHERE id=?", (course_id,))