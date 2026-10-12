import React, { useState } from 'react';

export default function ArtifactViewer({ artifact, onClose }) {
  const [activeTab, setActiveTab] = useState('preview'); // 'preview' | 'code'
  const [copied, setCopied] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  if (!artifact) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(artifact.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const isHtml = artifact.type === 'html' || artifact.language === 'html';
    const ext = isHtml ? 'html' : 'md';
    const filename = `${artifact.title.replace(/[^a-zA-Z0-9_-]/g, '_').toLowerCase()}.${ext}`;
    const blob = new Blob([artifact.content], { type: isHtml ? 'text/html' : 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const isHtml = artifact.type === 'html' || artifact.language === 'html';

  return (
    <div
      className="artifact-drawer"
      style={{
        width: isExpanded ? 'calc(100vw - 280px)' : '520px',
        transition: 'width 0.25s ease'
      }}
    >
      <div className="artifact-header">
        <div className="artifact-header-left">
          <span className="badge-tag">{artifact.type}</span>
          <div className="artifact-title" title={artifact.title}>
            {artifact.title}
          </div>
        </div>

        <div className="artifact-header-actions">
          <div className="artifact-tabs">
            <button
              className={`artifact-tab ${activeTab === 'preview' ? 'active' : ''}`}
              onClick={() => setActiveTab('preview')}
            >
              Preview
            </button>
            <button
              className={`artifact-tab ${activeTab === 'code' ? 'active' : ''}`}
              onClick={() => setActiveTab('code')}
            >
              Raw Code
            </button>
          </div>

          <button className="btn-icon-action" onClick={handleDownload} title="Download Artifact File">
            📥 Export
          </button>

          <button className="btn-icon-action" onClick={handleCopy} title="Copy Artifact Code">
            {copied ? '✓ Copied' : '📋 Copy'}
          </button>

          <button
            className="btn-icon-action"
            onClick={() => setIsExpanded(!isExpanded)}
            title={isExpanded ? 'Restore Size' : 'Expand Fullscreen'}
          >
            {isExpanded ? '⤢' : '⤡'}
          </button>

          <button className="btn-icon-action" onClick={onClose} title="Close Artifact Viewer">
            ✕
          </button>
        </div>
      </div>

      <div className={`artifact-body ${activeTab === 'code' ? 'code-mode' : ''}`}>
        {activeTab === 'preview' ? (
          isHtml ? (
            <iframe
              title="Artifact Preview Sandbox"
              className="sandboxed-iframe"
              srcDoc={artifact.content}
              sandbox="allow-scripts" // Strict sandbox isolation: NO allow-same-origin
            />
          ) : (
            <div style={{ padding: '24px', overflowY: 'auto', height: '100%', backgroundColor: '#0d131f' }}>
              <div className="markdown-body" style={{ color: '#f1f5f9', whiteSpace: 'pre-wrap' }}>
                {artifact.content}
              </div>
            </div>
          )
        ) : (
          <pre style={{ margin: 0, color: '#38bdf8', fontSize: '0.825rem', fontFamily: 'JetBrains Mono, monospace' }}>
            <code>{artifact.content}</code>
          </pre>
        )}
      </div>
    </div>
  );
}
