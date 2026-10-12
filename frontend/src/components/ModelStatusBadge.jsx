import React, { useState } from 'react';

export default function ModelStatusBadge({ health, onProviderChange }) {
  const [isSwitching, setIsSwitching] = useState(false);

  if (!health) {
    return (
      <div className="status-badge warning">
        <span className="pulse-dot" style={{ backgroundColor: '#f59e0b' }}></span>
        <span>Connecting...</span>
      </div>
    );
  }

  const handleSelect = async (e) => {
    const newProv = e.target.value;
    setIsSwitching(true);
    try {
      await onProviderChange(newProv);
    } finally {
      setIsSwitching(false);
    }
  };

  const isHealthy = health.provider_healthy;

  return (
    <div className="header-status-group">
      {/* Dynamic Model Switcher Dropdown */}
      <div
        className={`status-badge ${isHealthy ? 'online' : 'warning'}`}
        style={{ padding: '2px 8px', display: 'flex', alignItems: 'center', gap: '6px' }}
      >
        <span
          className="pulse-dot"
          style={{
            backgroundColor: isHealthy ? '#10b981' : '#f59e0b',
            boxShadow: `0 0 8px ${isHealthy ? '#10b981' : '#f59e0b'}`
          }}
        ></span>
        <select
          value={health.active_provider}
          onChange={handleSelect}
          disabled={isSwitching}
          style={{
            background: 'transparent',
            border: 'none',
            color: 'inherit',
            fontSize: '0.775rem',
            fontWeight: '600',
            fontFamily: 'inherit',
            cursor: 'pointer',
            outline: 'none',
            padding: '4px 0'
          }}
          title={health.provider_detail}
        >
          <option value="mock" style={{ background: '#111827', color: '#f8fafc' }}>
            ⚡ Deterministic Mock Engine (Fast / Zero-Cost)
          </option>
          <option value="ollama" style={{ background: '#111827', color: '#f8fafc' }}>
            🖥️ Local Ollama (qwen2.5:0.5b)
          </option>
          <option value="openai" style={{ background: '#111827', color: '#f8fafc' }}>
            ☁️ Cloud OpenAI (gpt-4o-mini)
          </option>
          <option value="anthropic" style={{ background: '#111827', color: '#f8fafc' }}>
            ☁️ Cloud Anthropic (claude-3-5-haiku)
          </option>
        </select>
      </div>

      {/* Database Mode Badge */}
      <div
        className="status-badge"
        style={{ fontSize: '0.7rem', color: '#94a3b8' }}
        title={`Storage Engine: ${health.database_mode}`}
      >
        <span>{health.database_mode === 'postgresql' ? '🐘 Supabase PG' : '💾 Local SQLite'}</span>
      </div>
    </div>
  );
}
