# Public GitHub Repository Preparation Guide

Follow these steps to safely initialize, audit, and push **The Lenny Growth Assistant** repository to public GitHub.

---

### Step 1: Pre-Flight Security & Secret Audit
Run a check to confirm no `.env`, API keys, database credentials, or SQLite/temp databases are tracked:
```bash
# Check git status for untracked sensitive files
git status --ignored

# Verify .gitignore covers .env, data/*.db, data/processed, and node_modules
cat .gitignore
```

---

### Step 2: Initialize Git Repository (if not already initialized)
```bash
git init
git branch -M main
```

---

### Step 3: Verify Folder Structure
Ensure the repository contains the following clean layout:
```text
lenny-growth-assistant/
├── .env.example
├── .gitignore
├── README.md
├── docs/
│   ├── PRD.md
│   ├── design.md
│   ├── architecture.md
│   ├── manual_test_checklist.md
│   ├── demo_script.md
│   └── github_prep.md
├── backend/
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models.py
│   │   ├── database.py
│   │   ├── retrieval/
│   │   ├── providers/
│   │   ├── skills/
│   │   └── services/
│   ├── data/
│   │   └── transcripts/
│   └── tests/
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
└── logs/
    └── agent_execution.log
```

---

### Step 4: Initial Commit & Push
```bash
git add .
git commit -m "feat: initial release of The Lenny Growth Assistant with low-resource retrieval, multi-provider routing, Ship30 skill, and sandboxed artifact viewer"
git remote add origin https://github.com/<your-username>/lenny-growth-assistant.git
git push -u origin main
```
