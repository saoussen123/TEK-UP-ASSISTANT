# 🎓 TEK-UP AI Exam Assistant

AI-powered exam generator and evaluator built with RAG + GROQ + Streamlit.

## Quick Start

```bash
# 1. Clone / enter project
cd tekup_assistant

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your GROQ API key
cp .env.example .env
# Edit .env and paste your GROQ_API_KEY

# 5. Add course PDFs
mkdir -p data/cours/CloudComputing
# Copy your PDFs into data/cours/<DomainName>/

# 6. Index your courses
python scripts/index_courses.py

# 7. Launch the app
streamlit run app.py
```

## Project Structure

```
tekup_assistant/
├── app.py                  Main Streamlit app (4 pages)
├── requirements.txt
├── .env                    API keys (never commit this)
├── rag/
│   ├── ingestion.py        PDF loading + chunking
│   ├── embeddings.py       Vector store (ChromaDB)
│   └── retriever.py        Semantic search
├── llm/
│   ├── groq_client.py      GROQ API connection
│   └── prompts.py          All prompt templates
├── exam/
│   ├── generator.py        Tool 1: question generation
│   └── evaluator.py        Tool 2: answer evaluation
├── db/
│   └── database.py         SQLite session history
├── utils/
│   └── helpers.py          Shared utilities
├── scripts/
│   ├── index_courses.py    Standalone indexer
│   └── test_pipeline.py    CLI smoke test
└── data/
    └── cours/              Your course PDFs go here
```