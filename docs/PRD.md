# Product Requirements Document (PRD)
## The Lenny Growth Assistant

### 1. Executive Summary & Problem Statement
Product Managers, Growth Leads, and Founders often struggle to extract actionable, verifiable insights from hundreds of hours of high-signal podcast interviews and essays (such as Lenny Rachitsky's podcast and newsletter). Generic LLM outputs hallucinate methodologies or lack concrete context. 

**The Lenny Growth Assistant** is a lightweight, source-grounded conversational AI assistant and synthesis engine designed to run efficiently even on resource-constrained environments (e.g., 1 GB RAM, CPU-only). It indexes Lenny's podcast transcripts, provides verifiable citations, synthesizes long-form essays using the Ship 30 for 30 framework, and generates live interactive artifacts (Markdown documents, wireframes, HTML/CSS landing components) in a secure, sandboxed viewer.

---

### 2. Target Users & Personas
1. **Product Managers & Growth Engineers**: Seeking proven retention, PLG (Product-Led Growth), activation, and monetization frameworks grounded in real-world operator transcripts (e.g., Brian Balfour, Elena Verna, Shreyas Doshi).
2. **Founders & Operators**: Seeking quick, actionable syntheses, growth strategy essays, and landing page wireframes without reading hours of transcripts.
3. **Engineers / Technical Interviewers**: Evaluating how a modern, resource-constrained AI agent architecture can deliver production-grade retrieval, isolation, multi-provider routing, and persistence without heavyweight overhead.

---

### 3. Core Goals & Measurable Success Metrics
| Metric | Target | Measurement Method |
| :--- | :--- | :--- |
| **Grounded Retrieval Precision** | >= 90% relevance | Citation verification test suite & BM25/TF-IDF relevance thresholding |
| **Insufficient-Evidence Handling** | 100% honesty | Refusal to invent advice when transcripts lack coverage |
| **Memory Footprint** | < 450 MB RAM backend + frontend | Windows Task Manager / Process memory checks |
| **End-to-End Latency** | < 2.5s (Mock/Fast Cloud), < 5s (Local CPU) | Server-side execution timers in response payload |
| **Artifact Security** | Zero XSS / Zero parent DOM breakout | Sandboxed `iframe` test with `sandbox="allow-scripts"` (no `allow-same-origin`) |
| **Database Resilience** | 100% graceful fallback | Auto-switch from Supabase PostgreSQL to SQLite if unconfigured/offline |

---

### 4. System Assumptions & Hardware Constraints
- **Hardware Profile**: Windows 11, strictly bounded available RAM (~1 GB free), CPU-only execution.
- **Dependency Philosophy**: No heavyweight frameworks (no PyTorch, no CUDA, no LangChain bloat, no multi-GB vector databases). Pure, high-speed Python TF-IDF / BM25 search.
- **Provider Agnostic**: Seamless switching between Local Ollama (`qwen2.5:0.5b`), Cloud OpenAI (`gpt-4o-mini`), Cloud Anthropic (`claude-3-5-haiku`), or Deterministic Mock Mode.

---

### 5. Functional Requirements & Scope

#### Feature A — Grounded Conversational Assistant
- **FR-A1**: Multi-session management with create, list, select, and clear operations.
- **FR-A2**: Grounded Q&A against curated Lenny's Podcast transcripts.
- **FR-A3**: Structured citations (Episode title, Guest name, Timestamp/Chunk ID, Transcript excerpt, and URL).
- **FR-A4**: Explicit "Insufficient Evidence" gatekeeper when query similarity is below the relevance cutoff.
- **FR-A5**: Conversation memory across follow-up turns within the active session.

#### Feature B — Ship 30 for 30 Writing Skill
- **FR-B1**: Structured long-form essay synthesis engine following Ship 30 for 30 methodology:
  - Strong hook & 1-sentence takeaway.
  - Clear narrative progression with skimmable headings.
  - Bulleted takeaways with bold emphasis.
  - Clear delineation between *Transcript Evidence* and *Actionable Inference*.
  - Word count target ~800–1,250 words.

#### Feature C — Multi-Format Artifact Generation & Isolation
- **FR-C1**: Detection of artifact generation requests (e.g., Growth Strategy Doc, Launch Checklist, HTML/CSS Landing Page Wireframe, Interactive Calculator).
- **FR-C2**: Inline chat reference with automatic sync to the right-side Artifact Viewer.
- **FR-C3**: Live toggle between Sandboxed HTML Preview and Raw Code View.
- **FR-C4**: Restrictive `iframe` sandboxing (`sandbox="allow-scripts"` without `allow-same-origin`, `allow-top-navigation`, or secret leakage).
- **FR-C5**: Single-click "Copy Artifact" action with user feedback.

#### Feature D — Persistence & Hybrid Storage
- **FR-D1**: Primary persistence to hosted PostgreSQL (Supabase) via SQLAlchemy.
- **FR-D2**: Zero-configuration fallback to local SQLite when `DATABASE_URL` is omitted or unverified.
- **FR-D3**: Schema migrations and table auto-creation on application startup.

---

### 6. Non-Functional Requirements
- **NFR-1 (Performance)**: Minimal cold start (< 1.5s), sub-millisecond retrieval on indexed transcripts.
- **NFR-2 (Reliability)**: Explicit timeout budgets (15s Ollama, 20s Cloud) with structured error envelopes.
- **NFR-3 (UX)**: Clean, distraction-free aesthetic with visual provider status badge, empty states, and loading spinners.
- **NFR-4 (Maintainability)**: Modular, clean code separation (retrieval, providers, skills, services, api).

---

### 7. Risk Analysis & Mitigation Plan
| Risk | Severity | Mitigation Strategy |
| :--- | :--- | :--- |
| Ollama not installed or out of RAM | High | Built-in provider health check; fallback to deterministic mock / cloud with clear UI banner |
| Supabase connection timeout / missing credentials | Medium | Auto-detection with seamless fallback to SQLite + banner indicator |
| High RAM consumption during TF-IDF indexing | High | Chunking streaming parser with vocabulary caps (`max_features=5000`) |
| Untrusted HTML code injection from model output | Critical | Strict iframe sandbox (`sandbox="allow-scripts"`, CSP headers, no `allow-same-origin`) |
