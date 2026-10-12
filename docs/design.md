# Design Specification: The Lenny Growth Assistant

## 1. Design Philosophy
The Lenny Growth Assistant interface follows a modern, developer-centric, minimalist design system inspired by Linear and Notion. The UI emphasizes clarity, rapid information scanning, source traceability, and zero unnecessary visual clutter.

---

## 2. Color Palette & Typography

### 2.1 CSS Variables & Design Tokens
```css
:root {
  /* Surface & Background */
  --bg-primary: #0a0d12;
  --bg-secondary: #121820;
  --bg-card: #182230;
  --bg-card-hover: #1f2c3d;
  --bg-composer: #141c28;

  /* Borders & Dividers */
  --border-subtle: #243245;
  --border-focus: #3b82f6;

  /* Typography Colors */
  --text-primary: #f1f5f9;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
  --text-accent: #38bdf8;

  /* Accent & Status Colors */
  --accent-blue: #2563eb;
  --accent-purple: #7c3aed;
  --accent-amber: #d97706;
  --status-online: #10b981;
  --status-warning: #f59e0b;
  --status-error: #ef4444;

  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
}
```

### 2.2 Typography
- **Primary Font**: Inter, system-ui, -apple-system, sans-serif.
- **Monospace Font**: JetBrains Mono, Fira Code, Consolas, monospace.
- **Hierarchy**:
  - Main Title: 1.25rem (700 bold)
  - Section Headings: 1.1rem (600 semi-bold)
  - Body Text: 0.925rem (400 regular, line-height 1.6)
  - Metadata / Citations: 0.8rem (400 regular, line-height 1.4)
  - Code & Badges: 0.775rem (500 medium)

---

## 3. Layout Architecture

The application layout is a 3-column responsive flex grid:
```
+-----------------------------------------------------------------------------------------+
| Top Bar: Logo | Active Model Status Badge | DB Status | Quick Actions (Ship 30 / Artifact)  |
+-------------------+---------------------------------------+-----------------------------+
| Left Sidebar      | Center Chat Area                      | Right Artifact Viewer       |
| - New Chat Button | - Active Conversation Header          | - Artifact Header & Type    |
| - Session History | - Message Stream                      | - Preview / Code Toggle     |
|   (with timestamps) |   - User message bubble             | - Sandboxed iframe or MD    |
| - Ingestion Stats |   - Assistant message (Markdown)      | - Single-click Copy         |
| - Clear All Chats |   - Expandable Source Citations       | - Collapse / Close Button   |
|                   |   - Artifact Launch Pills             |                             |
|                   | - Bottom Composer & Quick Prompts     |                             |
+-------------------+---------------------------------------+-----------------------------+
```

### 3.1 Responsive Breakpoints
- **Desktop (> 1200px)**: 3-column full view (Sidebar: 260px, Chat: 1fr, Artifact Viewer: 480px).
- **Tablet (768px – 1200px)**: 2-column view (Collapsible sidebar or slide-over drawer; Artifact view floats or docks over chat).
- **Mobile (< 768px)**: 1-column view with bottom navigation tab to toggle between Chat and Artifact Viewer.

---

## 4. Component Hierarchy

1. **`App`**: State holder for active session, active provider, artifact drawer open/close, messages list.
   - **`Header`**: Brand identity, active model badge (Ollama / OpenAI / Claude / Mock), persistence indicator (Postgres / SQLite).
   - **`Sidebar`**:
     - `NewChatButton`
     - `SessionList` (Active item indicator, delete button, relative timestamps)
     - `KnowledgeStats` (Total chunks indexed, last sync date)
   - **`ChatArea`**:
     - `EmptyState`: Suggested starter prompts ("PLG metrics from Elena Verna", "Ship 30 essay on product-market fit", "Landing page HTML artifact").
     - `MessageList`:
       - `UserMessageItem`
       - `AssistantMessageItem`:
         - Rendered Markdown (KaTeX / Tables / Bold emphasis)
         - `CitationCard`: Episode title, guest, timestamp, verbatim snippet, and clickable deep-link.
         - `ArtifactPill`: Direct click-to-open artifact in viewer.
     - `LoadingState`: Animated subtle pulse indicator with "Searching Lenny's transcripts..." status.
     - `Composer`: Textarea with Enter-to-send, Shift+Enter for newline, and quick skill action buttons.
   - **`ArtifactViewer`**:
     - `ViewerHeader`: Artifact title, type badge (`HTML/CSS`, `MARKDOWN`, `ESSAY`), and close button.
     - `TabControls`: [Preview] and [Raw Code] tabs.
     - `SandboxedIframe`: Rendered isolated HTML without parent script execution or cookie access.
     - `CodeBlock`: Syntax-highlighted view.
     - `CopyButton`: Clipboard copy with temporary success indicator.

---

## 5. Interaction States & Edge Cases

| State | Visual Feedback | User Action Available |
| :--- | :--- | :--- |
| **Initial / Empty** | Hero greeting + 4 prompt cards | Click card to prefill and submit |
| **Indexing / Cold Start** | Yellow badge "Indexing transcripts..." | System auto-indexes on start; non-blocking |
| **Retrieving Sources** | Pulsing dot + "Searching transcripts..." | Can cancel request |
| **Streaming / Generating** | Fast incremental token stream | Stop generation button |
| **Insufficient Evidence** | Amber notice badge with honest explanation | Prompt user to ask related PM topic |
| **Provider Offline (Ollama)** | Warning pill with explanation & automatic Mock/Cloud switch | Option to retry or toggle provider |
| **Database Disconnected** | SQLite fallback badge displayed | Persistence continues locally |
