"""
db/database.py
SQLite persistence for student sessions, exam history, and scores.
"""
import os
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "./db/sessions.db")


def _connect() -> sqlite3.Connection:
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = _connect()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            student    TEXT    NOT NULL,
            domain     TEXT    NOT NULL,
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
    """)
    conn.commit()
    conn.close()


def save_session(
    student: str,
    domain: str,
    difficulty: int,
    q_type: str,
    stats: dict,
    results: list,
) -> int:
    """Persist a completed exam session and its individual results."""
    conn = _connect()
    cur  = conn.cursor()

    cur.execute("""
        INSERT INTO sessions (student, domain, difficulty, q_type, total_q, correct, percentage, avg_score, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        student, domain, difficulty, q_type,
        stats["total"], stats["correct"],
        stats["percentage"], stats["avg_score"],
        datetime.now().strftime("%Y-%m-%d %H:%M"),
    ))
    session_id = cur.lastrowid

    for r in results:
        cur.execute("""
            INSERT INTO exam_results (session_id, question, correct_ans, student_ans, score, is_correct, explanation)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            r.get("question", ""),
            r.get("correct_answer", ""),
            r.get("student_answer", ""),
            r.get("score", 0),
            1 if r.get("is_correct") else 0,
            r.get("explanation", ""),
        ))

    conn.commit()
    conn.close()
    return session_id


def get_history(student: str) -> list:
    """Return all past sessions for a student, newest first."""
    conn  = _connect()
    rows  = conn.execute(
        "SELECT * FROM sessions WHERE student=? ORDER BY created_at DESC", (student,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_session_results(session_id: int) -> list:
    """Return all individual question results for a session."""
    conn  = _connect()
    rows  = conn.execute(
        "SELECT * FROM exam_results WHERE session_id=?", (session_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]