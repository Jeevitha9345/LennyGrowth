# Manual UI/UX Test Checklist: The Lenny Growth Assistant

Use this step-by-step checklist to verify end-to-end functionality across frontend, backend, retrieval, skills, and sandboxed rendering.

---

### Test Suite 1: Application Boot & Health
- [ ] **1.1 Backend Health Check**: Navigate to `http://localhost:8000/api/health`. Verify JSON contains `status: "healthy"`, active provider, and DB mode (`postgresql` or `sqlite_fallback`).
- [ ] **1.2 Frontend Boot**: Navigate to `http://localhost:5173`. Verify the interface loads with dark-mode theme, Top Bar, Left Sidebar, Main Chat Area, and Knowledge Base status.
- [ ] **1.3 Active Model Badge**: Check the top-right model indicator. It should show the currently configured active provider (e.g. `Ollama (qwen2.5:0.5b)`, `Cloud OpenAI`, `Claude`, or `Mock (Test Engine)`).

---

### Test Suite 2: Session Management
- [ ] **2.1 New Session Creation**: Click the **"+ New Chat"** button in the sidebar. Verify a clean chat area is displayed with default starter prompt suggestions.
- [ ] **2.2 Session Persistence across reload**: Send a message, refresh the browser window (`F5`), and verify the conversation messages remain intact.
- [ ] **2.3 Multi-Session Switching**: Create 2 separate sessions with different questions. Switch between them in the sidebar and verify each session retains its respective history.
- [ ] **2.4 Session Deletion**: Click the trash icon next to a session in the sidebar. Verify the session is removed and the UI resets gracefully.

---

### Test Suite 3: Grounded Conversational Q&A & Insufficient Evidence
- [ ] **3.1 High-Signal PM Question**: Ask: *"What does Elena Verna say about B2B Product-Led Growth and freemium conversion loops?"*
  - Verify the response is directly grounded in Elena Verna's episode.
  - Verify expandable Source Citations appear beneath the response with Episode Title, Guest Name, and deep link.
- [ ] **3.2 Follow-Up Question**: In the same chat, ask: *"How should early-stage startups measure the North Star metric for this?"*
  - Verify conversational context is retained.
- [ ] **3.3 Insufficient-Evidence Check**: Ask an out-of-domain question: *"How do I bake sourdough bread with whole wheat flour?"*
  - Verify the assistant gives an honest, explicit refusal explaining that Lenny's podcast knowledge base does not contain sourdough baking recipes.

---

### Test Suite 4: Ship 30 for 30 Writing Skill
- [ ] **4.1 Quick Skill Pill**: Click the **"📝 Ship 30 Essay"** quick-action button in the composer or type: *"Generate a Ship 30 for 30 essay on finding Product-Market Fit based on Brian Balfour and Superhuman's PMF engine."*
- [ ] **4.2 Structure Verification**: Verify the generated output adheres to:
  - Strong hook & 1-sentence takeaway.
  - Narrative progression with bold headers and bullet points.
  - Clear distinction section for *[Evidence from Transcripts]* vs *[Actionable Inference]*.
  - Word count target ~800–1,250 words.

---

### Test Suite 5: Artifact Generation & Sandboxed Preview
- [ ] **5.1 HTML/CSS Artifact Generation**: Ask: *"Create an interactive HTML/CSS PLG metric calculator landing page component."*
- [ ] **5.2 Artifact Drawer Auto-Open**: Verify the right-side Artifact Viewer opens automatically displaying the title, type badge (`HTML/CSS`), and sandboxed preview.
- [ ] **5.3 Preview vs. Code Toggle**: Click the **[Raw Code]** tab. Verify the HTML source code is displayed. Click **[Preview]** to toggle back to the rendered interactive view.
- [ ] **5.4 Copy Action**: Click **"Copy Code"** button. Verify temporary "Copied!" feedback and clipboard contains valid code.
- [ ] **5.5 Sandbox Security Verification**: Attempt to inspect iframe inside developer tools. Verify iframe has `sandbox="allow-scripts"` and cannot access `parent.window` or parent `localStorage`.

---

### Test Suite 6: Provider Switching & Error Recovery
- [ ] **6.1 Offline / Unreachable Provider Handling**: If Ollama or cloud key is invalid/offline, verify the UI displays a clean error card with actionable advice rather than a white-screen crash.
- [ ] **6.2 Database Fallback**: Unset `DATABASE_URL` in `.env` and restart backend. Verify SQLite auto-initializes without server crash.
