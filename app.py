"""
app.py — TEK-UP AI Assistant
Aurora Glass UI + Claude.ai-style sidebar (clean, no div artifacts)
"""

from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="TEK-UP AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: #080812 !important;
    color: #e2e8f0;
}
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

body::before {
    content: '';
    position: fixed; inset: 0;
    background:
        radial-gradient(ellipse 70% 50% at 15% 20%, rgba(99,102,241,0.18) 0%, transparent 65%),
        radial-gradient(ellipse 60% 45% at 85% 75%, rgba(139,92,246,0.14) 0%, transparent 65%),
        radial-gradient(ellipse 50% 60% at 50% 100%, rgba(59,130,246,0.08) 0%, transparent 60%);
    pointer-events: none; z-index: 0;
}

/* ── Sidebar — always visible ── */
section[data-testid="stSidebar"] {
    background: #0c0c18 !important;
    border-right: 0.5px solid rgba(255,255,255,0.06) !important;
    width: 260px !important;
    min-width: 260px !important;
    display: flex !important;
    visibility: visible !important;
    transform: translateX(0) !important;
}
section[data-testid="stSidebar"][aria-expanded="false"] {
    display: flex !important;
    min-width: 260px !important;
    transform: translateX(0) !important;
}
[data-testid="collapsedControl"] { display: none !important; }
section[data-testid="stSidebar"] > div {
    padding: 0 !important;
    display: flex; flex-direction: column; height: 100vh; overflow-y: auto;
}
section[data-testid="stSidebar"] * { color: #94a3b8 !important; }

/* Sidebar buttons — Claude.ai style */
section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    border-radius: 6px !important;
    color: #64748b !important;
    font-size: 13px !important;
    font-weight: 400 !important;
    height: 34px !important;
    width: 100% !important;
    text-align: left !important;
    padding: 0 12px !important;
    transition: all 0.15s !important;
    justify-content: flex-start !important;
    display: flex !important;
    align-items: center !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.06) !important;
    color: #e2e8f0 !important;
}
section[data-testid="stSidebar"] .stTextInput input {
    background: rgba(255,255,255,0.05) !important;
    border: 0.5px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
    font-size: 12px !important;
    height: 32px !important;
}

/* ── Main ── */
.main .block-container { padding: 0 !important; max-width: 100% !important; position: relative; z-index: 1; }

/* ── Top header ── */
.top-header {
    background: rgba(8,8,20,0.8); border-bottom: 0.5px solid rgba(99,102,241,0.15);
    padding: 11px 28px; display: flex; align-items: center; justify-content: space-between;
    backdrop-filter: blur(20px); position: sticky; top: 0; z-index: 100;
}
.top-header-title {
    font-family: 'Syne', sans-serif; font-size: 14px; font-weight: 700;
    background: linear-gradient(90deg,#c7d2fe,#a78bfa);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.model-badge {
    background: rgba(99,102,241,0.1); border: 0.5px solid rgba(99,102,241,0.25);
    border-radius: 20px; padding: 3px 11px; color: #818cf8; font-size: 11px; font-weight: 500;
}

/* ── Chat ── */
.chat-area { padding: 28px 24px; max-width: 780px; margin: 0 auto; }
.msg-user-wrap { display: flex; justify-content: flex-end; margin: 14px 0; }
.msg-user {
    background: linear-gradient(135deg,#6366f1,#8b5cf6);
    border-radius: 18px 18px 4px 18px; padding: 11px 16px; max-width: 72%;
    color: #fff; font-size: 13.5px; line-height: 1.65;
    box-shadow: 0 4px 20px rgba(99,102,241,0.3);
}
.ai-avatar {
    width: 30px; height: 30px; border-radius: 50%;
    background: linear-gradient(135deg,#6366f1,#8b5cf6);
    border: 1px solid rgba(99,102,241,0.4);
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 700; color: #fff !important;
    flex-shrink: 0; margin-top: 2px;
}
.file-bubble-wrap { display: flex; justify-content: flex-end; margin: 8px 0; }
.file-bubble {
    background: rgba(255,255,255,0.05); border: 0.5px solid rgba(255,255,255,0.1);
    border-radius: 12px; padding: 9px 14px;
    display: flex; align-items: center; gap: 10px; max-width: 260px;
}
.file-icon-box {
    width: 34px; height: 34px; background: rgba(99,102,241,0.2);
    border: 0.5px solid rgba(99,102,241,0.3); border-radius: 8px;
    display: flex; align-items: center; justify-content: center; font-size: 16px; flex-shrink: 0;
}

/* ── Main buttons ── */
.stButton > button {
    background: rgba(255,255,255,0.05) !important;
    border: 0.5px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important; color: #cbd5e1 !important;
    font-size: 12.5px !important; height: auto !important;
    padding: 9px 14px !important; transition: all 0.2s !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: rgba(99,102,241,0.12) !important;
    border-color: rgba(99,102,241,0.4) !important; color: #c7d2fe !important;
}
div[data-testid="stButton"] button[kind="primary"] {
    background: linear-gradient(135deg,#6366f1,#8b5cf6) !important;
    border-color: transparent !important; color: #fff !important;
    font-weight: 600 !important; box-shadow: 0 4px 18px rgba(99,102,241,0.35) !important;
}
div[data-testid="stButton"] button[kind="primary"]:hover {
    background: linear-gradient(135deg,#4f46e5,#7c3aed) !important;
    box-shadow: 0 6px 24px rgba(99,102,241,0.45) !important;
    transform: translateY(-1px) !important;
}

/* ── Progress ── */
.stProgress > div > div { background: linear-gradient(90deg,#6366f1,#8b5cf6) !important; border-radius: 4px !important; }
.stProgress > div { background: rgba(255,255,255,0.06) !important; border-radius: 4px !important; height: 3px !important; }

/* ── Quiz card ── */
.quiz-card {
    background: rgba(255,255,255,0.04); border: 0.5px solid rgba(99,102,241,0.18);
    border-radius: 4px 16px 16px 16px; padding: 16px 18px;
    margin-left: 42px; margin-bottom: 12px;
}

/* ── Welcome ── */
.welcome-wrap { text-align: center; padding: 80px 20px 32px; position: relative; }
.welcome-glow {
    position: absolute; width: 280px; height: 280px; border-radius: 50%;
    background: radial-gradient(circle,rgba(99,102,241,0.12) 0%,transparent 70%);
    top: 50%; left: 50%; transform: translate(-50%,-60%); pointer-events: none;
}
.welcome-title {
    font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 800;
    background: linear-gradient(135deg,#f1f5f9,#c7d2fe,#a78bfa);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 8px; position: relative;
}
.welcome-sub { color: rgba(148,163,184,0.7); font-size: 13px; margin-bottom: 36px; position: relative; }

/* ── Input ── */
.stChatInput > div {
    background: rgba(255,255,255,0.05) !important;
    border: 0.5px solid rgba(99,102,241,0.2) !important;
    border-radius: 14px !important;
    box-shadow: 0 0 24px rgba(99,102,241,0.08) !important;
}
.stChatInput > div:focus-within {
    border-color: rgba(99,102,241,0.45) !important;
    box-shadow: 0 0 28px rgba(99,102,241,0.18) !important;
}
.stChatInput textarea { background: transparent !important; color: #e2e8f0 !important; font-size: 13.5px !important; }
.stFileUploader > label { display: none !important; }
.stFileUploader section { background: transparent !important; border: none !important; padding: 0 !important; }
.stFileUploader section > div {
    background: rgba(255,255,255,0.04) !important;
    border: 0.5px dashed rgba(99,102,241,0.25) !important;
    border-radius: 8px !important; padding: 5px 10px !important; min-height: 34px !important;
}

::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.25); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Imports ───────────────────────────────────────────────────────────────────
from db.database import (
    init_db, save_session, get_history, get_asked_questions,
    reset_asked_questions, get_all_courses, get_courses_by_field,
    save_course, get_student_stats, FIELDS, detect_field
)
from rag.ingestion   import ingest
from rag.embeddings  import build_vectorstore
from rag.retriever   import retrieve_context, format_context, get_available_domains
from exam.generator  import generate_questions
from exam.evaluator  import evaluate_answer, compute_final_score
from llm.groq_client import get_llm

init_db()

defaults = {
    "messages":         [],
    "vectorstore":      None,
    "course_name":      None,
    "course_field":     "cloud",
    "student_name":     "Student",
    "quiz_active":      False,
    "quiz_questions":   [],
    "quiz_index":       0,
    "quiz_answers":     {},
    "quiz_topic":       "",
    "quiz_field":       "cloud",
    "quiz_correct":     0,
    "quiz_wrong":       0,
    "sidebar_view":     "home",
    "active_field":     None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ═════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════════════════════════════════════
with st.sidebar:

    # ── Logo ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="padding:18px 16px 10px; display:flex; align-items:center; gap:10px;">
        <div style="width:32px;height:32px;border-radius:9px;
            background:linear-gradient(135deg,rgba(99,102,241,0.35),rgba(139,92,246,0.35));
            border:0.5px solid rgba(99,102,241,0.4);
            display:flex;align-items:center;justify-content:center;font-size:16px;">🎓</div>
        <div>
            <div style="font-family:'Syne',sans-serif;font-size:14px;font-weight:800;
                background:linear-gradient(90deg,#c7d2fe,#a78bfa);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;">TEK-UP AI</div>
            <div style="font-size:10px;color:rgba(148,163,184,0.45)!important;">Certification Platform</div>
        </div>
    </div>
    <div style="height:0.5px;background:rgba(255,255,255,0.06);margin:0 16px 8px;"></div>
    """, unsafe_allow_html=True)

    # ── New conversation ───────────────────────────────────────────────────────
    if st.button("＋  New conversation", key="btn_new", use_container_width=True):
        st.session_state.messages       = []
        st.session_state.quiz_active    = False
        st.session_state.quiz_questions = []
        st.session_state.quiz_index     = 0
        st.session_state.quiz_answers   = {}
        st.session_state.sidebar_view   = "home"
        st.rerun()

    st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)

    # ── Student profile ────────────────────────────────────────────────────────
    name     = st.session_state.student_name or "Student"
    initials = "".join(w[0].upper() for w in name.split()[:2]) or "S"
    st.markdown(f"""
    <div style="padding:2px 16px 6px;display:flex;align-items:center;gap:9px;">
        <div style="width:24px;height:24px;background:linear-gradient(135deg,#6366f1,#8b5cf6);
            border-radius:50%;display:flex;align-items:center;justify-content:center;
            font-size:10px;color:#fff!important;font-weight:700;flex-shrink:0;">{initials}</div>
        <span style="font-size:12.5px;color:#64748b!important;overflow:hidden;
            text-overflow:ellipsis;white-space:nowrap;">{name}</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Navigation ────────────────────────────────────────────────────────────
    if st.button("📊  My Results", key="nav_results", use_container_width=True):
        st.session_state.sidebar_view = "results"
        st.rerun()
    if st.button("📋  Certification Rules", key="nav_rules", use_container_width=True):
        st.session_state.sidebar_view = "rules"
        st.rerun()

    # ── Fields ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="padding:12px 16px 4px;font-size:10px;font-weight:600;
        color:rgba(148,163,184,0.35)!important;text-transform:uppercase;letter-spacing:0.8px;">
        Certification Fields
    </div>
    """, unsafe_allow_html=True)

    for field_key, field_info in FIELDS.items():
        courses = get_courses_by_field(st.session_state.student_name, field_key)
        count   = len(courses)
        lbl     = f"{field_info['icon']}  {field_info['label']}"
        if count:
            lbl += f"  · {count}"
        if st.button(lbl, key=f"field_btn_{field_key}", use_container_width=True):
            st.session_state.sidebar_view = f"field_{field_key}"
            st.session_state.active_field = field_key
            st.rerun()

    # ── Recent exams ──────────────────────────────────────────────────────────
    hist = get_history(st.session_state.student_name)
    if hist:
        st.markdown("""
        <div style="padding:12px 16px 4px;font-size:10px;font-weight:600;
            color:rgba(148,163,184,0.35)!important;text-transform:uppercase;letter-spacing:0.8px;">
            Recent Exams
        </div>
        """, unsafe_allow_html=True)
        for s in hist[:4]:
            pct   = s["percentage"]
            color = "#34d399" if pct >= 70 else "#fbbf24" if pct >= 50 else "#f87171"
            fi    = FIELDS.get(s.get("field","cloud"), FIELDS["cloud"])
            st.markdown(f"""
            <div style="padding:3px 16px;display:flex;align-items:center;gap:8px;">
                <span style="font-size:12px;">{fi['icon']}</span>
                <div style="flex:1;min-width:0;">
                    <div style="font-size:11px;color:#475569!important;white-space:nowrap;
                        overflow:hidden;text-overflow:ellipsis;">{s['domain'][:20]}</div>
                    <div style="font-size:10px;color:#2d3748!important;">{s['created_at']}</div>
                </div>
                <span style="font-size:11px;font-weight:600;color:{color}!important;flex-shrink:0;">{pct}%</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div style="flex:1;"></div>', unsafe_allow_html=True)

    # ── Bottom: name input + remove course ────────────────────────────────────
    st.markdown('<div style="border-top:0.5px solid rgba(255,255,255,0.05);padding:10px 12px 14px;">', unsafe_allow_html=True)
    st.session_state.student_name = st.text_input(
        "Your name", value=st.session_state.student_name,
        placeholder="Enter your name...", label_visibility="visible"
    )
    if st.button("🗑️  Remove loaded course", key="btn_remove", use_container_width=True):
        st.session_state.vectorstore = None
        st.session_state.course_name = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═════════════════════════════════════════════════════════════════════════════
def _detect_lang(text: str) -> str:
    fr = ["sur","le","la","les","des","une","moi","mon","je","tu","nous","vous",
          "est","sont","avec","pour","dans","que","qui","génère","donne","fais",
          "explique","cours","quiz","comment","pourquoi","c'est","quoi","quel"]
    words = text.lower().split()
    return "french" if sum(1 for w in words if w in fr) >= 2 else "english"


def _extract_num_questions(msg: str) -> int:
    import re
    for pattern in [r'(\d+)\s*questions?', r'(\d+)\s*q\b', r'(\d+)\s*mcq', r'(\d+)\s*qcm']:
        m = re.search(pattern, msg, re.IGNORECASE)
        if m: return int(m.group(1))
    return 5


def detect_intent(msg: str) -> str:
    m = msg.lower()
    course_kw = [
        "quiz sur le cours","quiz on the course","white test","test sur le cours",
        "questions sur le cours","questions from the course","generate a test",
        "based on the course","basé sur le cours","from my course","from the course",
        "le fichier","the file","ce cours","this course","le document","the document",
        "i provided","that i provided","course material","course materials","course content",
        "mock exam","practice test","from the pdf","my course","provided you",
        "certification exam","aws exam","based on my","from my pdf","from my document",
    ]
    if any(k in m for k in course_kw): return "quiz_course"
    quiz_kw = ["quiz","qcm","mcq","questions sur","questions about","generate questions",
               "génère des questions","donne moi des questions","give me questions",
               "teste moi","test me","quiz moi","quiz me","fais moi un quiz","make a quiz",
               "génère un quiz","generate a quiz","donne moi un test","give me a test","interroge moi"]
    if any(k in m for k in quiz_kw): return "quiz_general"
    return "chat"


def get_rag_context(query: str, top_k: int = 4) -> str:
    if not st.session_state.vectorstore: return ""
    try:
        docs = retrieve_context(query, st.session_state.vectorstore, top_k=top_k)
        return format_context(docs) if docs else ""
    except Exception: return ""


def get_history_prompt() -> str:
    recent = [m for m in st.session_state.messages if m.get("type") == "text"][-6:]
    if not recent: return ""
    return "\n".join(
        f"{'User' if m['role']=='user' else 'Assistant'}: {m['content']}"
        for m in recent[:-1]
    )

# ═════════════════════════════════════════════════════════════════════════════
# AI BRAIN
# ═════════════════════════════════════════════════════════════════════════════
def ai_response(user_message: str) -> None:
    intent = detect_intent(user_message)
    if intent == "quiz_course":    _quiz_course(user_message)
    elif intent == "quiz_general": _quiz_general(user_message)
    else:                          _chat(user_message)


def _chat(user_message: str) -> None:
    llm  = get_llm(temperature=0.5)
    ctx  = get_rag_context(user_message)
    hist = get_history_prompt()
    lang = _detect_lang(user_message)
    course_info = f"A course '{st.session_state.course_name}' is loaded." if st.session_state.course_name else ""
    ctx_block  = f"\n\n--- COURSE MATERIAL ---\n{ctx}\n---\n" if ctx else ""
    hist_block = f"\nCONVERSATION:\n{hist}\n" if hist else ""
    prompt = f"""You are TEK-UP AI, an intelligent certification assistant for university students.
{course_info}
RULES: Answer EXACTLY what asked. Use course material when relevant. Format with markdown. Be warm and pedagogical. Respond in {lang}. NEVER generate a quiz unless explicitly asked.
{ctx_block}{hist_block}
User: {user_message}
Assistant:"""
    resp = llm.invoke(prompt)
    st.session_state.messages.append({
        "role": "assistant",
        "content": resp.content if hasattr(resp, "content") else str(resp),
        "type": "text"
    })


def _quiz_general(user_message: str) -> None:
    lang  = _detect_lang(user_message)
    llm   = get_llm(temperature=0.75)
    num_q = _extract_num_questions(user_message)
    topic = user_message
    for p in ["génère un quiz sur","generate a quiz on","quiz moi sur","quiz me on",
              "donne moi des questions sur","give me questions about","make a quiz on",
              "questions sur","questions about","quiz sur","quiz on","quiz","qcm","mcq"]:
        topic = topic.lower().replace(p, "").strip()
    topic = topic.strip() or user_message
    ctx = get_rag_context(topic, top_k=3)
    ctx_block = f"\nCourse context:\n{ctx}\n" if ctx else ""
    prompt = f"""Generate exactly {num_q} MCQ questions about: {topic}
{ctx_block}
FORMAT:
**Q1. [Question]**
A. Option 1  B. Option 2  C. Option 3  D. Option 4
✅ **Correct: B. [Option]**
💡 *Explanation*
---
Respond in {lang}"""
    resp = llm.invoke(prompt)
    content = resp.content if hasattr(resp, "content") else str(resp)
    intro = (f"Voici **{num_q} questions** sur **{topic}** :" if lang == "french"
             else f"Here are **{num_q} questions** about **{topic}**:")
    st.session_state.messages.append({
        "role": "assistant", "content": f"{intro}\n\n{content}", "type": "text"
    })


def _quiz_course(user_message: str) -> None:
    lang = _detect_lang(user_message)
    if not st.session_state.vectorstore:
        msg = ("❌ Aucun cours chargé. Uploadez votre PDF ci-dessous." if lang == "french"
               else "❌ No course loaded. Upload your PDF below.")
        st.session_state.messages.append({"role": "assistant", "content": msg, "type": "text"})
        return
    num_q   = _extract_num_questions(user_message)
    domains = get_available_domains(st.session_state.vectorstore)
    domain  = domains[0] if domains else "general"
    asked   = get_asked_questions(st.session_state.student_name, domain)
    with st.spinner(f"✨ Generating {num_q} questions..."):
        questions = generate_questions(
            vectorstore=st.session_state.vectorstore,
            domain=domain, num_questions=num_q,
            difficulty=1, question_type="MCQ", asked_questions=asked,
        )
        if not questions:
            reset_asked_questions(st.session_state.student_name, domain)
            questions = generate_questions(
                vectorstore=st.session_state.vectorstore,
                domain=domain, num_questions=num_q, difficulty=1, question_type="MCQ",
            )
    if questions:
        st.session_state.quiz_active    = True
        st.session_state.quiz_questions = questions
        st.session_state.quiz_index     = 0
        st.session_state.quiz_answers   = {}
        st.session_state.quiz_topic     = st.session_state.course_name or domain
        st.session_state.quiz_field     = st.session_state.course_field
        st.session_state.quiz_correct   = 0
        st.session_state.quiz_wrong     = 0
        start = (f"✅ **{len(questions)} questions** prêtes depuis **{st.session_state.course_name}**. C'est parti !"
                 if lang == "french" else
                 f"✅ **{len(questions)} questions** ready from **{st.session_state.course_name}**. Let's go!")
        st.session_state.messages.append({"role": "assistant", "content": start, "type": "text"})
    else:
        st.session_state.messages.append({
            "role": "assistant", "content": "❌ Could not generate questions. Please try again.", "type": "text"
        })


def _submit_quiz() -> None:
    questions = st.session_state.quiz_questions
    results   = []
    correct = wrong = 0
    for i, question in enumerate(questions):
        ans = st.session_state.quiz_answers.get(f"q_{i}", "")
        if st.session_state.vectorstore:
            res = evaluate_answer(question, ans, st.session_state.vectorstore)
        else:
            ca  = question.get("correct_answer", "")
            ok  = ans.strip().lower() == ca.strip().lower()
            res = {"score": 10 if ok else 0, "is_correct": ok,
                   "feedback": "Correct!" if ok else f"Correct: {ca}",
                   "explanation": question.get("explanation", "")}
        res.update({"question": question.get("question",""),
                    "correct_answer": question.get("correct_answer",""),
                    "student_answer": ans})
        results.append(res)
        if res.get("is_correct"): correct += 1
        else: wrong += 1

    stats = compute_final_score(results)
    if st.session_state.vectorstore:
        save_session(
            st.session_state.student_name, st.session_state.quiz_topic,
            1, "MCQ", stats, results,
            field=st.session_state.get("quiz_field", "cloud")
        )

    pct   = stats["percentage"]
    emoji = "🏆" if pct >= 80 else "👍" if pct >= 60 else "📚"
    if pct >= 90:   verdict = "🟢 **Exam Ready** — You're ready for the real certification!"
    elif pct >= 75: verdict = "🟡 **Nearly Ready** — A bit more practice and you'll ace it."
    elif pct >= 60: verdict = "🟠 **Needs More Practice** — Review the weak areas below."
    else:           verdict = "🔴 **Review Course Again** — Go back to the fundamentals."

    md = f"""## {emoji} Results — {st.session_state.quiz_topic.upper()}

| | |
|---|---|
| **Score** | **{pct}%** |
| ✅ Correct | {correct} / {stats['total']} |
| ❌ Wrong | {wrong} / {stats['total']} |
| ⭐ Avg | {stats['avg_score']} / 10 |

{verdict}

---
### Corrections\n\n"""

    for i, r in enumerate(results):
        ok = r.get("is_correct", False)
        md += f"{'✅' if ok else '❌'} **Q{i+1}.** {r['question']}\n\n"
        md += f"> Your answer: `{r['student_answer'] or '(no answer)'}`\n\n"
        if not ok: md += f"> ✅ Correct: **{r['correct_answer']}**\n\n"
        if r.get("explanation"): md += f"> 💡 {r['explanation']}\n\n"
        md += "---\n\n"

    md += "_Ask me anything to continue preparing!_"
    st.session_state.messages.append({"role": "assistant", "content": md, "type": "text"})
    st.session_state.quiz_active    = False
    st.session_state.quiz_questions = []
    st.session_state.quiz_index     = 0
    st.session_state.quiz_answers   = {}
    st.session_state.quiz_correct   = correct
    st.session_state.quiz_wrong     = wrong

# ═════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="top-header">
    <div class="top-header-title">✦ TEK-UP AI Assistant</div>
    <div class="model-badge">⚡ llama-3.3-70b-versatile</div>
</div>
""", unsafe_allow_html=True)

view = st.session_state.sidebar_view

# ── VIEW: Field detail ────────────────────────────────────────────────────────
if view.startswith("field_"):
    field_key  = view.replace("field_", "")
    field_info = FIELDS.get(field_key, FIELDS["cloud"])
    courses    = get_courses_by_field(st.session_state.student_name, field_key)
    hist_field = get_history(st.session_state.student_name, field=field_key)

    st.markdown(f"""
    <div style="padding:32px 40px 0;">
        <div style="font-size:26px;margin-bottom:6px;">{field_info['icon']}</div>
        <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;
            background:linear-gradient(90deg,#f1f5f9,#c7d2fe);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:4px;">
            {field_info['label']}
        </div>
        <div style="color:#475569;font-size:13px;margin-bottom:24px;">
            {len(courses)} course(s) · {len(hist_field)} exam(s)
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns([1.2, 1], gap="large")
    with col_a:
        st.markdown('<div style="padding:0 0 0 40px;">', unsafe_allow_html=True)
        st.markdown("#### 📚 Uploaded Courses")
        if courses:
            for c in courses:
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.04);border:0.5px solid rgba(255,255,255,0.08);
                    border-radius:10px;padding:10px 14px;margin-bottom:8px;
                    display:flex;align-items:center;gap:10px;">
                    <div style="font-size:20px;">📄</div>
                    <div style="flex:1;min-width:0;">
                        <div style="color:#e2e8f0;font-size:12.5px;font-weight:500;
                            white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{c['filename']}</div>
                        <div style="color:#475569;font-size:10px;">{c['size_mb']:.1f} MB · {c['created_at']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:rgba(255,255,255,0.02);border:0.5px dashed rgba(255,255,255,0.08);
                border-radius:10px;padding:20px;text-align:center;color:#334155;font-size:13px;">
                No courses yet — upload a PDF from the chat.
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### 🏆 Target Certifications")
        certs_html = "".join(f'<span style="display:inline-block;background:rgba(99,102,241,0.1);border:0.5px solid rgba(99,102,241,0.25);border-radius:20px;padding:4px 12px;margin:3px 4px 3px 0;font-size:12px;color:#818cf8;">{cert}</span>' for cert in field_info["certifications"])
        st.markdown(f'<div style="margin-bottom:16px;">{certs_html}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown("#### 📊 Exam History")
        if hist_field:
            for s in hist_field[:8]:
                pct   = s["percentage"]
                color = "#34d399" if pct >= 70 else "#fbbf24" if pct >= 50 else "#f87171"
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.03);border:0.5px solid rgba(255,255,255,0.06);
                    border-radius:8px;padding:9px 12px;margin-bottom:6px;
                    display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <div style="font-size:12px;color:#94a3b8;">{s['domain'][:28]}</div>
                        <div style="font-size:10px;color:#334155;">{s['created_at']} · {s['total_q']}q</div>
                    </div>
                    <div style="font-size:15px;font-weight:700;color:{color};">{pct}%</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#334155;font-size:13px;">No exams yet.</div>', unsafe_allow_html=True)

# ── VIEW: Certification Rules ─────────────────────────────────────────────────
elif view == "rules":
    st.markdown("""
    <div style="padding:32px 40px 16px;max-width:760px;">
        <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;
            background:linear-gradient(90deg,#f1f5f9,#c7d2fe);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:4px;">
            📋 Certification Rules
        </div>
        <div style="color:#475569;font-size:13px;margin-bottom:24px;">TEK-UP University — Official requirements</div>
    </div>
    """, unsafe_allow_html=True)

    for icon, title, desc in [
        ("🎯", "Minimum Pass Score",    "75% or above to earn certification credit"),
        ("🔁", "Retake Policy",         "Up to 3 attempts per domain per semester"),
        ("⏱️", "Exam Duration",         "45 min standard · 90 min advanced"),
        ("📊", "Score Progression",     "Best score out of all attempts counts"),
        ("📚", "Course Requirement",    "Must upload at least 1 official course PDF before exam"),
        ("🏆", "Distinction Threshold", "90%+ earns a distinction badge on your transcript"),
        ("📅", "Validity",              "Scores valid for the current academic year"),
        ("🔐", "Academic Integrity",    "Each exam generates unique questions — no two exams identical"),
    ]:
        st.markdown(f"""
        <div style="padding:0 40px;margin-bottom:8px;">
            <div style="background:rgba(255,255,255,0.03);border:0.5px solid rgba(255,255,255,0.07);
                border-radius:12px;padding:13px 18px;display:flex;gap:14px;align-items:flex-start;">
                <div style="font-size:19px;flex-shrink:0;">{icon}</div>
                <div>
                    <div style="color:#e2e8f0;font-size:13px;font-weight:600;margin-bottom:2px;">{title}</div>
                    <div style="color:#64748b;font-size:12px;">{desc}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="padding:20px 40px 0;">
        <div style="background:rgba(99,102,241,0.07);border:0.5px solid rgba(99,102,241,0.18);
            border-radius:12px;padding:16px 20px;">
            <div style="color:#818cf8;font-size:11px;font-weight:600;text-transform:uppercase;
                letter-spacing:0.6px;margin-bottom:10px;">Scoring Guide</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">
                <div style="color:#34d399;font-size:12.5px;">🟢 90%+  Exam Ready</div>
                <div style="color:#60a5fa;font-size:12.5px;">🔵 75–89%  Nearly Ready</div>
                <div style="color:#fbbf24;font-size:12.5px;">🟡 60–74%  Needs Practice</div>
                <div style="color:#f87171;font-size:12.5px;">🔴 &lt;60%  Review Course</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── VIEW: Results ─────────────────────────────────────────────────────────────
elif view == "results":
    hist_all = get_history(st.session_state.student_name)
    stats    = get_student_stats(st.session_state.student_name)

    st.markdown("""
    <div style="padding:32px 40px 16px;">
        <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;
            background:linear-gradient(90deg,#f1f5f9,#c7d2fe);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            📊 My Results
        </div>
    </div>
    """, unsafe_allow_html=True)

    if stats:
        cols = st.columns(len(stats))
        for i, (fk, s) in enumerate(stats.items()):
            fi    = FIELDS.get(fk, FIELDS["cloud"])
            color = "#34d399" if s["avg_pct"] >= 70 else "#fbbf24" if s["avg_pct"] >= 50 else "#f87171"
            with cols[i]:
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.04);border:0.5px solid rgba(255,255,255,0.08);
                    border-radius:12px;padding:16px;text-align:center;">
                    <div style="font-size:20px;margin-bottom:4px;">{fi['icon']}</div>
                    <div style="font-size:11px;color:#475569;margin-bottom:4px;">{fi['label']}</div>
                    <div style="font-size:22px;font-weight:700;color:{color};">{s['avg_pct']}%</div>
                    <div style="font-size:10px;color:#334155;">{s['exams']} exams · best {s['best']}%</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown('<div style="padding:20px 40px 0;">', unsafe_allow_html=True)
    st.markdown("#### All Exams")
    if hist_all:
        for s in hist_all[:20]:
            pct   = s["percentage"]
            color = "#34d399" if pct >= 70 else "#fbbf24" if pct >= 50 else "#f87171"
            fi    = FIELDS.get(s.get("field","cloud"), FIELDS["cloud"])
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.03);border:0.5px solid rgba(255,255,255,0.06);
                border-radius:10px;padding:10px 16px;margin-bottom:6px;
                display:flex;align-items:center;gap:12px;">
                <span style="font-size:18px;">{fi['icon']}</span>
                <div style="flex:1;">
                    <div style="color:#94a3b8;font-size:13px;font-weight:500;">{s['domain']}</div>
                    <div style="color:#334155;font-size:11px;">{s['created_at']} · {s['total_q']} questions</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:16px;font-weight:700;color:{color};">{pct}%</div>
                    <div style="font-size:10px;color:#334155;">{s['correct']}/{s['total_q']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#334155;font-size:13px;">No exams yet.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── VIEW: Chat (home) ─────────────────────────────────────────────────────────
else:
    st.markdown('<div class="chat-area">', unsafe_allow_html=True)

    if not st.session_state.messages and not st.session_state.quiz_active:
        if st.session_state.course_name:
            fi = FIELDS.get(st.session_state.course_field, FIELDS["cloud"])
            st.markdown(f"""
            <div style="background:rgba(16,185,129,0.07);border:0.5px solid rgba(16,185,129,0.18);
                border-radius:10px;padding:8px 14px;margin-bottom:16px;
                display:flex;align-items:center;gap:8px;">
                <span style="font-size:16px;">{fi['icon']}</span>
                <div style="flex:1;">
                    <div style="color:#34d399;font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">Course loaded</div>
                    <div style="color:#6ee7b7;font-size:12px;">{st.session_state.course_name}</div>
                </div>
                <div style="color:#475569;font-size:11px;">{fi['label']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div class="welcome-wrap">
            <div class="welcome-glow"></div>
            <div style="position:relative;margin-bottom:18px;">
                <div style="width:58px;height:58px;margin:0 auto;border-radius:16px;
                    background:linear-gradient(135deg,rgba(99,102,241,0.25),rgba(139,92,246,0.25));
                    border:0.5px solid rgba(99,102,241,0.35);
                    display:flex;align-items:center;justify-content:center;font-size:26px;
                    box-shadow:0 0 34px rgba(99,102,241,0.25);">🎓</div>
            </div>
            <div class="welcome-title">TEK-UP AI Assistant</div>
            <div class="welcome-sub">Ask anything · Upload your course · Generate certification quizzes</div>
        </div>
        """, unsafe_allow_html=True)

        suggestions = [
            ("⚡", "Explain what EC2 is"),
            ("🌐", "Explique moi le cloud computing"),
            ("📝", "Quiz me on AWS S3 — 10 questions"),
            ("🤖", "What is a neural network?"),
            ("📖", "Make a quiz from my course"),
            ("🔐", "What is IAM in AWS?"),
        ]
        c1, c2, c3 = st.columns(3)
        for i, (emoji, sug) in enumerate(suggestions):
            with [c1, c2, c3][i % 3]:
                if st.button(f"{emoji}  {sug}", key=f"sug_{i}", use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": sug, "type": "text"})
                    with st.spinner(""):
                        ai_response(sug)
                    st.rerun()
    else:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                if msg.get("file_name"):
                    st.markdown(f"""
                    <div class="file-bubble-wrap">
                        <div class="file-bubble">
                            <div class="file-icon-box">📄</div>
                            <div>
                                <div style="color:#e2e8f0;font-size:11.5px;font-weight:500;">{msg["file_name"]}</div>
                                <div style="color:#475569;font-size:10px;margin-top:2px;">{msg.get("file_size_mb","")}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                if msg.get("content"):
                    st.markdown(f'<div class="msg-user-wrap"><div class="msg-user">{msg["content"]}</div></div>',
                                unsafe_allow_html=True)
            else:
                c_av, c_msg = st.columns([0.055, 0.945])
                with c_av:
                    st.markdown('<div class="ai-avatar">AI</div>', unsafe_allow_html=True)
                with c_msg:
                    st.markdown(msg["content"])

        if st.session_state.quiz_active:
            questions = st.session_state.quiz_questions
            idx       = st.session_state.quiz_index
            total     = len(questions)
            q         = questions[idx]
            ans_key   = f"q_{idx}"
            pct_done  = int((idx / total) * 100)

            st.markdown(f"""
            <div style="margin-left:42px;margin-top:12px;margin-bottom:6px;">
                <div style="display:flex;align-items:center;gap:10px;">
                    <div style="flex:1;height:3px;background:rgba(255,255,255,0.06);border-radius:3px;overflow:hidden;">
                        <div style="width:{pct_done}%;height:100%;
                            background:linear-gradient(90deg,#6366f1,#8b5cf6);border-radius:3px;"></div>
                    </div>
                    <span style="color:#64748b;font-size:11px;">{idx+1} / {total}</span>
                    <span style="color:#34d399;font-size:11px;font-weight:600;">✓ {st.session_state.quiz_correct}</span>
                    <span style="color:#f87171;font-size:11px;font-weight:600;">✕ {st.session_state.quiz_wrong}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="quiz-card">
                <div style="color:rgba(99,102,241,0.65);font-size:10px;text-transform:uppercase;
                    letter-spacing:0.8px;margin-bottom:8px;font-weight:600;">Question {idx+1}</div>
                <div style="color:#f1f5f9;font-size:13.5px;font-weight:500;line-height:1.7;">{q.get("question","")}</div>
            </div>
            """, unsafe_allow_html=True)

            current = st.session_state.quiz_answers.get(ans_key, None)
            st.markdown('<div style="margin-left:42px;">', unsafe_allow_html=True)

            if "options" in q and q["options"]:
                for i, opt in enumerate(q["options"]):
                    letter = ["A","B","C","D","E"][i] if i < 5 else str(i+1)
                    if st.button(f"{letter}.   {opt}", key=f"qo_{idx}_{i}",
                                 use_container_width=True,
                                 type="primary" if current == opt else "secondary"):
                        st.session_state.quiz_answers[ans_key] = opt; st.rerun()
            else:
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✅  True", key=f"qt_{idx}", use_container_width=True,
                                 type="primary" if current == "True" else "secondary"):
                        st.session_state.quiz_answers[ans_key] = "True"; st.rerun()
                with c2:
                    if st.button("❌  False", key=f"qf_{idx}", use_container_width=True,
                                 type="primary" if current == "False" else "secondary"):
                        st.session_state.quiz_answers[ans_key] = "False"; st.rerun()

            if current:
                st.markdown(f'<div style="color:rgba(99,102,241,0.65);font-size:11px;margin-top:5px;">Selected: <b style="color:#818cf8;">{current}</b></div>',
                            unsafe_allow_html=True)

            cp, cn = st.columns([1, 2])
            with cp:
                if idx > 0 and st.button("← Back", use_container_width=True):
                    st.session_state.quiz_index -= 1; st.rerun()
            with cn:
                if idx < total - 1:
                    if st.button("Next →", type="primary", use_container_width=True):
                        st.session_state.quiz_index += 1; st.rerun()
                else:
                    if st.button("🏁 Submit & See Results", type="primary", use_container_width=True):
                        with st.spinner("✨ Evaluating..."):
                            _submit_quiz()
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Input bar ─────────────────────────────────────────────────────────────
    uploaded_file = st.file_uploader(
        "attach", type=["pdf","docx","txt"],
        label_visibility="collapsed", key="chat_upload"
    )
    user_input = st.chat_input("Ask anything — explain, quiz me, or attach your course PDF...")

    if uploaded_file is not None:
        file_key = f"done_{uploaded_file.name}_{uploaded_file.size}"
        if file_key not in st.session_state:
            st.session_state[file_key] = True
            with st.spinner(f"✨ Reading {uploaded_file.name}..."):
                tmp = Path("data/cours/uploaded")
                tmp.mkdir(parents=True, exist_ok=True)
                fp  = tmp / uploaded_file.name
                with open(fp, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                chunks = ingest(tmp)
                if chunks:
                    st.session_state.vectorstore = build_vectorstore(chunks)
                    course_name  = uploaded_file.name.rsplit(".", 1)[0]
                    size_mb      = uploaded_file.size / 1_000_000
                    course_field = detect_field(uploaded_file.name)
                    st.session_state.course_name  = course_name
                    st.session_state.course_field = course_field
                    save_course(
                        student=st.session_state.student_name,
                        filename=uploaded_file.name,
                        field=course_field,
                        filepath=str(fp),
                        size_mb=round(size_mb, 2)
                    )
                    fi = FIELDS[course_field]
                    st.session_state.messages.append({
                        "role": "user", "content": "",
                        "file_name": uploaded_file.name,
                        "file_size_mb": f"{size_mb:.1f} MB", "type": "file"
                    })
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"""✅ I've read **{uploaded_file.name}**.

{fi['icon']} Saved in **{fi['label']}** field.

I can now:
- 💬 Answer questions about the course content
- 📝 Generate a quiz — say *"make a quiz from my course"*
- 📖 Explain or summarize any topic from it

What would you like to do?""",
                        "type": "text"
                    })
                    st.rerun()
                else:
                    st.error("Could not extract text from the file.")

    if user_input and user_input.strip():
        msg = user_input.strip()
        if st.session_state.quiz_active:
            st.session_state.quiz_active    = False
            st.session_state.quiz_questions = []
        st.session_state.messages.append({"role": "user", "content": msg, "type": "text"})
        with st.spinner(""):
            ai_response(msg)
        st.rerun()