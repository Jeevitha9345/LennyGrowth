# 🎙️ The Lenny Growth Assistant
> **A fast, source-grounded product leadership and growth intelligence assistant with sandboxed interactive artifact generation, optimized for resource-constrained environments (~1 GB RAM, CPU-only).**

---

## 🌟 Overview & Capabilities

**The Lenny Growth Assistant** indexes high-signal transcripts from *Lenny's Podcast* (featuring operators like Elena Verna, Brian Balfour, Shreyas Doshi, and Rahul Vohra) to provide actionable, verifiable product growth intelligence without hallucination or heavyweight infrastructure.

### Core Features
1. **Grounded Conversational Intelligence**: Multi-session chat grounded in Lenny's Podcast transcripts with traceable, clickable source citations and an honest insufficient-evidence response mechanism.
2. **Ship 30 for 30 Writing Skill**: High-impact, structured 1,000+ word growth essays featuring hooks, 1-sentence takeaways, skimmable core pillars, an explicit *Evidence vs. Inference* table, and 24-hour action checklists.
3. **Sandboxed Interactive Artifact Viewer**: Side-by-side artifact viewer for generated HTML/CSS landing pages, interactive growth calculators, and Markdown strategy documents. Strictly sandboxed with `sandbox="allow-scripts"` (zero parent DOM/cookie breakout).
4. **Multi-Provider AI Routing**: Flexible adapter supporting Local Ollama (`qwen2.5:0.5b`), Cloud OpenAI (`gpt-4o-mini`), Cloud Anthropic Claude (`claude-3-5-haiku`), and a Deterministic Mock Engine for zero-cost testing.
5. **Hybrid Persistence**: Hosted PostgreSQL (Supabase) with an automatic, zero-configuration local SQLite fallback.

---

## ⚡ Strict Hardware Constraint Optimizations
This system was engineered specifically for a standard laptop under **strict ~1 GB available RAM** and CPU-only execution:
- **Zero Heavy ML Frameworks**: No PyTorch, no CUDA, no sentence-transformers, no heavy vector DB daemon.
- **Pure-Python Okapi BM25 Indexing**: Sub-millisecond retrieval on indexed transcripts using sparse document term frequencies and vocabulary caps.
- **Micro Frontend Footprint**: React + Vite bundle of just **158 KB**, rendering directly via vanilla CSS design tokens.
- **Bounded Context Budgets**: Context window capped at 4,000 characters; Top-4 chunks; response limit of 1,024 tokens.

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- **Python**: 3.10+ (Tested on Python 3.12.0)
- **Node.js**: 18+ (Tested on Node.js v22.16.0 & npm 10.9.2)
- **OS**: Windows 11 / macOS / Linux

---

### 2. Environment Setup
Clone the repository and copy the environment template:
```bash
cp .env.example .env
```

Edit `.env` to configure your preferred provider and database:
```ini
# Active Provider: "mock" | "ollama" | "openai" | "anthropic"
ACTIVE_PROVIDER=mock

# Local Ollama (Optional)
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen2.5:0.5b

# Cloud OpenAI (Optional)
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4o-mini

# Cloud Anthropic (Optional)
ANTHROPIC_API_KEY=your-anthropic-key
ANTHROPIC_MODEL=claude-3-5-haiku-latest

# Supabase Hosted PostgreSQL (Optional - falls back to SQLite automatically if empty)
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres
```

---

### 3. Backend Installation & Execution
```bash
# Navigate to backend directory
cd backend

# Install minimal lightweight dependencies
pip install -r requirements.txt

# Ingest and build the transcript index (auto-runs on startup if missing)
python -m app.retrieval.ingest

# Start the FastAPI server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
*The FastAPI backend will be available at `http://127.0.0.1:8000` (Swagger Docs at `/docs`, Health Probe at `/api/health`).*

---

### 4. Frontend Installation & Execution
Open a new terminal window:
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (only React + Vite)
npm install

# Start the Vite development server
npm run dev
```
*Open your browser and navigate to `http://localhost:5173`.*

---

## 🧪 Automated Testing

The backend includes a comprehensive pytest suite covering API validation, retrieval grounding, model routing, persistence, and artifact security:

```bash
cd backend
python -m pytest -v
```

### Test Coverage Summary:
- `test_api.py`: End-to-end FastAPI endpoint integration (Health, Sessions CRUD, Chat, Ship 30).
- `test_retrieval.py`: BM25 tokenization, chunk scoring, relevance thresholding, and insufficient-evidence refusals.
- `test_providers.py`: Provider factory routing, deterministic mock generation, and Ollama offline timeout handling.
- `test_skills.py`: Ship 30 for 30 essay generation and HTML/Markdown artifact extraction.
- `test_persistence.py`: Session and message history lifecycle across SQLite/PostgreSQL.
- `test_artifact_security.py`: Untrusted HTML/JavaScript encapsulation for iframe sandboxing.

---

## 📂 Project Architecture

```text
lenny-growth-assistant/
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore for secrets, node_modules, caches
├── README.md                 # Project documentation & runbook
├── docs/
│   ├── PRD.md                # Product Requirements Document
│   ├── design.md             # UI/UX design tokens & responsive specifications
│   ├── architecture.md       # Full system architecture & data flow diagrams
│   ├── manual_test_checklist.md # Comprehensive UI verification checklist
│   ├── demo_script.md        # 2–3 minute video presentation walkthrough
│   └── github_prep.md        # Public release & secret audit guide
├── backend/
│   ├── requirements.txt      # Minimal Python dependencies
│   ├── app/
│   │   ├── main.py           # FastAPI application & routes
│   │   ├── config.py         # App settings & bounded resource limits
│   │   ├── models.py         # Pydantic data schemas
│   │   ├── database.py       # SQLAlchemy Supabase PostgreSQL + SQLite fallback
│   │   ├── retrieval/
│   │   │   ├── indexer.py    # Okapi BM25 retrieval engine
│   │   │   └── ingest.py     # Reproducible transcript chunker
│   │   ├── providers/
│   │   │   ├── base.py       # BaseModelProvider interface
│   │   │   ├── factory.py    # Provider factory & fallback router
│   │   │   ├── mock_provider.py     # Deterministic high-signal mock engine
│   │   │   ├── ollama_provider.py   # Local Ollama adapter
│   │   │   ├── openai_provider.py   # OpenAI Cloud adapter
│   │   │   └── anthropic_provider.py# Anthropic Claude adapter
│   │   ├── skills/
│   │   │   ├── ship30_skill.py      # Ship 30 for 30 essay generator
│   │   │   └── artifact_skill.py    # Artifact extraction & parser
│   │   └── services/
│   │       ├── chat_service.py      # Chat turn orchestration & grounding
│   │       └── session_service.py   # Session CRUD & persistence
│   ├── data/
│   │   ├── transcripts/      # Curated transcripts (Elena Verna, Brian Balfour, Shreyas Doshi, Rahul Vohra)
│   │   └── processed/        # Ingested chunk JSON cache
│   └── tests/                # Automated pytest suite (16 tests)
├── frontend/
│   ├── package.json          # React & Vite dependencies
│   ├── vite.config.js        # Vite config with backend proxy
│   ├── index.html            # HTML shell with Google Fonts
│   └── src/
│       ├── main.jsx          # Root mount
│       ├── App.jsx           # Main application state orchestrator
│       ├── App.css           # Modern dark-mode styling system
│       ├── services/
│       │   └── api.js        # Backend API fetch client
│       └── components/
│           ├── Sidebar.jsx           # Session list & new chat
│           ├── ChatArea.jsx          # Message thread & composer
│           ├── MessageItem.jsx       # Markdown & expandable citations
│           ├── ArtifactViewer.jsx    # Sandboxed iframe & code viewer
│           └── ModelStatusBadge.jsx  # Active model & DB badge
└── logs/
    └── agent_execution.log   # Detailed development & verification logs
```

---

## 🔒 Security & Sandboxing

All HTML/CSS snippets generated by models are rendered in the client using a strictly sandboxed `iframe`:
```html
<iframe
  title="Artifact Preview Sandbox"
  className="sandboxed-iframe"
  srcDoc={artifact.content}
  sandbox="allow-scripts"
/>
```
- **No `allow-same-origin`**: Ensures the iframe runs on an opaque `null` origin, making it impossible for untrusted code to read cookies, access `localStorage`, or reach into parent window DOM.
- **No `allow-top-navigation` / `allow-popups`**: Prevents redirection or clickjacking.

---

## 🛠️ Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| `Ollama connection unreachable` | Ollama service is not running locally | Start Ollama (`ollama serve`) or switch `ACTIVE_PROVIDER=mock` in `.env`. |
| `PostgreSQL connection failed` | Supabase credentials missing or invalid | The backend will automatically switch to `sqlite_fallback`. Verify `DATABASE_URL` in `.env` if Postgres is desired. |
| `Frontend fails to load data` | Backend is not running on port 8000 | Start the backend with `python -m uvicorn app.main:app --port 8000`. |
| `Port 8000 already in use` | Another process is occupying port 8000 | Run with `--port 8001` and update proxy in `frontend/vite.config.js`. |
