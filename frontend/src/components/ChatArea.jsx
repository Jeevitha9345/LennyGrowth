import React, { useState, useRef, useEffect } from 'react';
import MessageItem from './MessageItem';

const STARTER_PROMPTS = [
  {
    guest: "Elena Verna",
    title: "B2B PLG & Reverse Trials",
    prompt: "What does Elena Verna say about B2B Product-Led Growth, freemium vs. reverse trials, and PQLs?"
  },
  {
    guest: "Brian Balfour",
    title: "Four Fits & Growth Loops",
    prompt: "Explain Brian Balfour's Four Fits framework and why compound growth loops beat traditional linear funnels."
  },
  {
    guest: "Sean Ellis",
    title: "ICE Scoring & 40% PMF Test",
    prompt: "How does Sean Ellis structure the ICE prioritization scoring framework, and what is the 40% PMF benchmark?"
  },
  {
    guest: "April Dunford",
    title: "5-Step Product Positioning",
    prompt: "What are the 5 interlocking components of B2B product positioning according to April Dunford?"
  },
  {
    guest: "Casey Winters",
    title: "Retention Loops & Cold Start",
    prompt: "How does Casey Winters explain solving the marketplace cold start problem and why acquisition is a derivative of retention?"
  },
  {
    guest: "Shreyas Doshi",
    title: "High Agency PM & LNO Framework",
    prompt: "How does Shreyas Doshi define High Agency in product management, and how should PMs use the LNO framework for prioritization?"
  }
];

export default function ChatArea({
  sessionTitle,
  messages,
  isLoading,
  error,
  onSendMessage,
  onOpenArtifact,
  onTriggerShip30,
  onExportSession
}) {
  const [input, setInput] = useState('');
  const threadEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    threadEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (!input.trim() || isLoading) return;
    const msg = input.trim();
    setInput('');
    onSendMessage(msg);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <main className="main-content">
      {/* Active Conversation Subheader */}
      {messages.length > 0 && (
        <div
          style={{
            height: '42px',
            borderBottom: '1px solid #1a273b',
            background: 'rgba(13, 19, 31, 0.7)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0 24px',
            fontSize: '0.8rem',
            color: '#94a3b8'
          }}
        >
          <span style={{ fontWeight: '600', color: '#f8fafc' }}>
            💬 {sessionTitle || 'Growth Conversation'}
          </span>

          <button
            className="btn-icon-action"
            onClick={onExportSession}
            title="Export conversation as Markdown"
            style={{ fontSize: '0.725rem', padding: '3px 8px' }}
          >
            📥 Export Chat (.md)
          </button>
        </div>
      )}

      <div className="chat-thread">
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🎙️</div>
            <h1 className="empty-title">The Lenny Growth Assistant</h1>
            <p className="empty-desc">
              Source-grounded product leadership and growth intelligence indexed from Lenny's Podcast transcripts. Ask frameworks, generate Ship 30 for 30 essays, or synthesize interactive artifacts.
            </p>

            <div className="prompt-grid">
              {STARTER_PROMPTS.map((p, idx) => (
                <div
                  key={idx}
                  className="prompt-card"
                  onClick={() => onSendMessage(p.prompt)}
                >
                  <div className="prompt-card-guest">{p.guest}</div>
                  <div className="prompt-card-text">{p.prompt}</div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg, index) => (
            <MessageItem
              key={msg.id || index}
              message={msg}
              onOpenArtifact={onOpenArtifact}
            />
          ))
        )}

        {isLoading && (
          <div className="message-row assistant">
            <div className="message-bubble" style={{ maxWidth: '200px' }}>
              <div className="loading-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        {error && (
          <div
            style={{
              padding: '12px 16px',
              backgroundColor: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid #ef4444',
              borderRadius: '8px',
              color: '#f87171',
              fontSize: '0.85rem',
              maxWidth: '820px',
              margin: '0 auto',
              width: '100%'
            }}
          >
            ⚠️ {error}
          </div>
        )}

        <div ref={threadEndRef} />
      </div>

      <div className="composer-container">
        {/* Quick Action Pills & Interactive Artifact Launchers */}
        <div className="quick-actions-bar">
          <button
            className="quick-pill"
            onClick={() => onTriggerShip30("Why Growth Loops Beat Funnels in Modern B2B")}
          >
            📝 Ship 30 Essay
          </button>
          <button
            className="quick-pill"
            onClick={() => onSendMessage("Create an interactive Sean Ellis ICE Growth Prioritization Matrix component.")}
          >
            ⚡ ICE Matrix Tool
          </button>
          <button
            className="quick-pill"
            onClick={() => onSendMessage("Create an interactive Superhuman PMF Engine and 40% rule survey dashboard.")}
          >
            🎯 PMF 40% Survey
          </button>
          <button
            className="quick-pill"
            onClick={() => onSendMessage("Create an interactive April Dunford 5-Step Positioning Canvas artifact.")}
          >
            📐 Positioning Canvas
          </button>
          <button
            className="quick-pill"
            onClick={() => onSendMessage("Create an interactive Shreyas Doshi LNO task matrix planner artifact.")}
          >
            ⚡ LNO Task Matrix
          </button>
          <button
            className="quick-pill"
            onClick={() => onSendMessage("Create an interactive HTML/CSS PLG metric and reverse trial calculator component.")}
          >
            🚀 Reverse Trial Modeler
          </button>
        </div>

        <form className="composer-box" onSubmit={handleSubmit}>
          <textarea
            ref={inputRef}
            className="composer-input"
            rows="1"
            placeholder="Ask a growth question, generate an essay, or build an artifact..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
          />
          <button
            type="submit"
            className="btn-send"
            disabled={!input.trim() || isLoading}
            title="Send Message"
          >
            ➔
          </button>
        </form>
      </div>
    </main>
  );
}
