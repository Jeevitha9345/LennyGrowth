import React, { useState } from 'react';

export default function Sidebar({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewChat,
  onDeleteSession,
  indexedChunks = 0
}) {
  const [searchFilter, setSearchFilter] = useState('');

  const filteredSessions = sessions.filter(s =>
    s.title.toLowerCase().includes(searchFilter.toLowerCase())
  );

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <button className="btn-new-chat" onClick={onNewChat}>
          <span style={{ fontSize: '1.1rem' }}>+</span>
          <span>New Chat</span>
        </button>

        {/* Conversation Search Filter */}
        <div style={{ marginTop: '10px' }}>
          <input
            type="text"
            placeholder="Search conversations..."
            value={searchFilter}
            onChange={(e) => setSearchFilter(e.target.value)}
            style={{
              width: '100%',
              background: '#151e2e',
              border: '1px solid #223249',
              borderRadius: '6px',
              padding: '6px 10px',
              color: '#f8fafc',
              fontSize: '0.775rem',
              outline: 'none'
            }}
          />
        </div>
      </div>

      <div className="sidebar-content">
        <div className="session-section-title">
          <span>Conversations ({filteredSessions.length})</span>
        </div>
        {filteredSessions.length === 0 ? (
          <div style={{ padding: '12px', fontSize: '0.8rem', color: '#64748b' }}>
            {searchFilter ? 'No matching conversations.' : 'No chats yet. Start a new growth session above!'}
          </div>
        ) : (
          filteredSessions.map((session) => (
            <div
              key={session.id}
              className={`session-item ${session.id === activeSessionId ? 'active' : ''}`}
              onClick={() => onSelectSession(session.id)}
            >
              <span className="session-title-text" title={session.title}>
                💬 {session.title}
              </span>
              <button
                className="btn-delete-session"
                title="Delete Chat"
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteSession(session.id);
                }}
              >
                ✕
              </button>
            </div>
          ))
        )}
      </div>

      <div className="sidebar-footer">
        <div className="knowledge-badge">
          <span className="pulse-dot"></span>
          <span>{indexedChunks} Lenny transcript chunks indexed</span>
        </div>
      </div>
    </aside>
  );
}
