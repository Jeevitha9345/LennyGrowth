import React, { useState } from 'react';

// Lightweight Markdown Renderer for zero-bloat execution
function renderSimpleMarkdown(content) {
  if (!content) return null;

  const lines = content.split('\n');
  const elements = [];
  let inTable = false;
  let tableRows = [];
  let inList = false;
  let listItems = [];
  let inCodeBlock = false;
  let codeBuffer = [];

  const flushList = () => {
    if (inList && listItems.length > 0) {
      elements.push(
        <ul key={`ul-${elements.length}`} style={{ marginLeft: '20px', marginBottom: '10px' }}>
          {listItems.map((it, idx) => (
            <li key={idx} dangerouslySetInnerHTML={{ __html: formatInline(it) }} />
          ))}
        </ul>
      );
      listItems = [];
      inList = false;
    }
  };

  const flushTable = () => {
    if (inTable && tableRows.length > 0) {
      const header = tableRows[0];
      const body = tableRows.slice(2); // skip header separator
      elements.push(
        <table key={`table-${elements.length}`}>
          <thead>
            <tr>
              {header.map((col, idx) => (
                <th key={idx} dangerouslySetInnerHTML={{ __html: formatInline(col.trim()) }} />
              ))}
            </tr>
          </thead>
          <tbody>
            {body.map((row, rIdx) => (
              <tr key={rIdx}>
                {row.map((col, cIdx) => (
                  <td key={cIdx} dangerouslySetInnerHTML={{ __html: formatInline(col.trim()) }} />
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      );
      tableRows = [];
      inTable = false;
    }
  };

  const formatInline = (text) => {
    if (!text) return '';
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" style="color:#38bdf8;">$1</a>');
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Code blocks
    if (line.startsWith('```')) {
      if (inCodeBlock) {
        elements.push(
          <pre key={`code-${elements.length}`}>
            <code>{codeBuffer.join('\n')}</code>
          </pre>
        );
        codeBuffer = [];
        inCodeBlock = false;
      } else {
        flushList();
        flushTable();
        inCodeBlock = true;
      }
      continue;
    }

    if (inCodeBlock) {
      codeBuffer.push(line);
      continue;
    }

    // Table rows
    if (line.trim().startsWith('|') && line.trim().endsWith('|')) {
      flushList();
      inTable = true;
      const cols = line.trim().split('|').slice(1, -1);
      tableRows.push(cols);
      continue;
    } else if (inTable) {
      flushTable();
    }

    // Headings
    if (line.startsWith('### ')) {
      flushList();
      elements.push(<h3 key={i}>{line.replace('### ', '')}</h3>);
    } else if (line.startsWith('## ')) {
      flushList();
      elements.push(<h2 key={i}>{line.replace('## ', '')}</h2>);
    } else if (line.startsWith('# ')) {
      flushList();
      elements.push(<h1 key={i}>{line.replace('# ', '')}</h1>);
    } else if (line.startsWith('> ')) {
      flushList();
      elements.push(
        <blockquote key={i} dangerouslySetInnerHTML={{ __html: formatInline(line.replace('> ', '')) }} />
      );
    } else if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
      inList = true;
      listItems.push(line.trim().replace(/^[-*]\s+/, ''));
    } else if (line.trim() === '---') {
      flushList();
      elements.push(<hr key={i} style={{ border: 'none', borderTop: '1px solid #223249', margin: '14px 0' }} />);
    } else if (line.trim().length > 0) {
      flushList();
      elements.push(
        <p key={i} dangerouslySetInnerHTML={{ __html: formatInline(line) }} />
      );
    }
  }

  flushList();
  flushTable();

  return <div className="markdown-body">{elements}</div>;
}

export default function MessageItem({ message, onOpenArtifact }) {
  const [showCitations, setShowCitations] = useState(false);
  const isAssistant = message.role === 'assistant';
  const citations = message.citations || [];
  const artifact = message.artifact;

  return (
    <div className={`message-row ${message.role}`}>
      <div className="message-bubble">
        {isAssistant ? (
          renderSimpleMarkdown(message.content)
        ) : (
          <div style={{ whiteSpace: 'pre-wrap' }}>{message.content}</div>
        )}

        {/* Artifact Launch Pill */}
        {artifact && (
          <div className="artifact-pill-banner">
            <div className="artifact-pill-info">
              <span style={{ fontSize: '1.1rem' }}>
                {artifact.type === 'html' ? '🎨' : artifact.type === 'essay' ? '📝' : '📄'}
              </span>
              <div>
                <div className="artifact-pill-title">{artifact.title}</div>
                <div style={{ fontSize: '0.725rem', color: '#94a3b8' }}>
                  {artifact.type.toUpperCase()} • {artifact.summary || 'Click to inspect'}
                </div>
              </div>
            </div>
            <button
              className="btn-open-artifact"
              onClick={() => onOpenArtifact(artifact)}
            >
              <span>Inspect Artifact</span>
              <span>→</span>
            </button>
          </div>
        )}

        {/* Expandable Citations */}
        {isAssistant && citations.length > 0 && (
          <div className="citations-wrapper">
            <button
              className="citations-toggle"
              onClick={() => setShowCitations(!showCitations)}
            >
              <span>{showCitations ? '▼' : '▶'}</span>
              <span>Grounded in {citations.length} Lenny Podcast source{citations.length > 1 ? 's' : ''}</span>
            </button>

            {showCitations && (
              <div className="citations-list">
                {citations.map((c) => (
                  <div key={c.id} className="citation-card">
                    <div className="citation-header">
                      <span className="citation-source">🎙️ {c.source_title}</span>
                      <span className="citation-guest">{c.guest_name}</span>
                    </div>
                    <div className="citation-snippet">"{c.snippet}"</div>
                    {c.source_url && (
                      <a
                        href={c.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="citation-link"
                      >
                        Listen / View Episode ↗
                      </a>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
