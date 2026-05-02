"""
app.py
TEK-UP AI Exam Assistant — Main Streamlit application.
Run with: streamlit run app.py
"""

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TEK-UP AI Exam Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Lazy imports ─────────────────────────────────────────────────────────────
from db.database import init_db, save_session, get_history
from rag.ingestion import ingest
from rag.embeddings import (
    build_vectorstore,
    load_vectorstore,
    vectorstore_exists,
)
from rag.retriever import get_available_domains
from exam.generator import generate_questions, QUESTION_TYPES
from exam.evaluator import evaluate_answer, compute_final_score
from utils.helpers import score_color, score_label, difficulty_label

# ── Init DB ──────────────────────────────────────────────────────────────────
init_db()

# ── Session state defaults ───────────────────────────────────────────────────
defaults = {
    "page": "upload",
    "vectorstore": None,
    "questions": [],
    "answers": {},
    "results": [],
    "stats": {},
    "student_name": "Student",
    "exam_submitted": False,
    "domain": "general",
    "difficulty": 1,
    "q_type": "MCQ",
    "num_questions": 5,
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Helper ───────────────────────────────────────────────────────────────────
def clean_folder(name: str) -> str:
    return name.strip().lower().replace(" ", "_")


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎓 TEK-UP Assistant")
    st.markdown("---")

    st.session_state.student_name = st.text_input(
        "Your name", value=st.session_state.student_name
    )

    st.markdown("---")

    pages = {
        "📂 Upload & Index": "upload",
        "📝 Take Exam": "exam",
        "📊 Results": "results",
        "📈 History": "history",
    }

    for label, key in pages.items():
        if st.button(label, use_container_width=True):
            st.session_state.page = key

    st.markdown("---")

    if st.session_state.vectorstore is not None:
        st.success("✔ Index ready")
    else:
        st.warning("⚠ No index loaded")


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 1 — UPLOAD
# ═════════════════════════════════════════════════════════════════════════════
def page_upload():
    st.title("📂 Upload & Index Course Materials")

    uploaded_files = st.file_uploader(
        "Upload course files",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
    )

    domain_name = st.text_input("Domain name (e.g. AI, Cloud, Cybersecurity)")

    if st.button("⚡ Index Documents", type="primary"):

        if not uploaded_files:
            st.error("Upload at least one file")
            return

        if not domain_name:
            st.error("Enter domain name")
            return

        # clean folder
        domain_clean = clean_folder(domain_name)
        domain_dir = Path("data/cours") / domain_clean
        domain_dir.mkdir(parents=True, exist_ok=True)

        # save files
        for uf in uploaded_files:
            dest = domain_dir / uf.name
            with open(dest, "wb") as f:
                f.write(uf.getbuffer())

        with st.spinner("Processing documents..."):

            chunks = ingest(domain_dir)

            # ✅ IMPORTANT SAFETY CHECK (FIXES YOUR ERROR)
            if not chunks:
                st.error(
                    "❌ No text extracted from PDFs.\n"
                    "👉 Your files may be scanned images or empty."
                )
                return

            vectorstore = build_vectorstore(chunks)

        st.session_state.vectorstore = vectorstore

        st.success(f"✔ Indexed {len(chunks)} chunks from {domain_name}")

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 2 — EXAM
# ═════════════════════════════════════════════════════════════════════════════
def page_exam():
    st.title("📝 Exam")

    if st.session_state.vectorstore is None:
        st.warning("Upload documents first")
        return

    vs = st.session_state.vectorstore
    domains = get_available_domains(vs)

    domain = st.selectbox("Domain", domains)
    q_type = st.selectbox("Type", QUESTION_TYPES)
    num_q = st.slider("Questions", 1, 10, 5)
    diff = st.slider("Difficulty", 1, 3, 1)

    if st.button("Generate"):
        st.session_state.questions = generate_questions(
            vectorstore=vs,
            domain=domain,
            num_questions=num_q,
            difficulty=diff,
            question_type=q_type,
        )
        st.session_state.domain = domain
        st.rerun()

    for i, q in enumerate(st.session_state.questions):
        st.write(f"Q{i+1}: {q['question']}")


# ═════════════════════════════════════════════════════════════════════════════
# PAGE ROUTER
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "upload":
    page_upload()
elif st.session_state.page == "exam":
    page_exam()
elif st.session_state.page == "results":
    st.title("Results")
elif st.session_state.page == "history":
    st.title("History")