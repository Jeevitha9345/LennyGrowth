# Demo Video Script: The Lenny Growth Assistant (2–3 Minutes)

**Presenter**: Senior Forward Deployed Engineer / AI Lead  
**Setting**: Screen recording with camera enabled in top-right corner.

---

### [0:00 – 0:30] Introduction & Problem Setup
- **Presenter (On Camera)**:  
  *"Hi everyone! Today I'm excited to demonstrate **The Lenny Growth Assistant**—a fast, source-grounded conversational agent and artifact synthesis engine tailored for Product Managers and Growth Engineers.*
- **Screen**: Show the clean, dark-mode Lenny Growth Assistant UI loaded on `http://localhost:5173`. Point to the top status bar.
- **Presenter**:  
  *"Notice our system is running under strict hardware constraints: under 1 GB of RAM on a standard laptop with zero GPU requirements, powered by a pure-Python TF-IDF/BM25 retrieval engine, Supabase PostgreSQL persistence with local SQLite fallback, and a flexible model adapter."*

---

### [0:30 – 1:15] Feature 1: Grounded Q&A & Source Citations
- **Action**: Click a suggested prompt or type:  
  `"What does Elena Verna say about B2B Product-Led Growth and monetization loops?"`
- **Screen**: The assistant generates a fast, structured answer.
- **Presenter**:  
  *"Notice the response is strictly grounded in Lenny's podcast transcript with Elena Verna. Look below the answer: we have expandable citations showing the exact episode title, guest, timestamp, and verbatim quotes. If I ask something completely outside the knowledge base—like 'How do I bake sourdough bread?'—the assistant explicitly and honestly declines rather than hallucinating."*
- **Action**: Quickly submit the sourdough bread question to demonstrate the honest insufficient-evidence response.

---

### [1:15 – 1:55] Feature 2: Ship 30 for 30 Long-Form Essay Skill
- **Action**: Click the **"📝 Ship 30 Essay"** quick pill or submit:  
  `"Generate a Ship 30 for 30 essay on finding Product-Market Fit based on Brian Balfour and Superhuman's PMF engine."`
- **Screen**: The assistant crafts an approximately 1,000-word structured essay.
- **Presenter**:  
  *"Here is our Ship 30 for 30 writing skill in action. It structures the advice with a high-impact hook, clear narrative progression, skimmable bold headers, and an explicit section distinguishing verbatim transcript evidence from strategic inference."*

---

### [1:55 – 2:35] Feature 3: Sandboxed Artifact Generation & HTML Preview
- **Action**: Ask:  
  `"Generate an interactive HTML/CSS PLG metric calculator component for our team."`
- **Screen**: The response finishes, and the right-side **Artifact Viewer** smoothly opens.
- **Presenter**:  
  *"The assistant doesn't just return code; it mounts an isolated, sandboxed artifact viewer right next to our chat. Here we have a live interactive calculator rendered in a strictly sandboxed iframe (`sandbox='allow-scripts'`, no same-origin DOM breakout). We can test inputs live, toggle to Raw Code mode, and click 'Copy Code' with a single click."*

---

### [2:35 – 3:00] Wrap-up & Engineering Architecture
- **Presenter (Camera focus)**:  
  *"To summarize: The Lenny Growth Assistant delivers production-grade, source-grounded intelligence and interactive artifacts while respecting low-resource constraints. The full codebase, automated test suite, and documentation are available in the repository. Thank you!"*
