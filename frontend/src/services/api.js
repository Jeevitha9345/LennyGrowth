const API_BASE = '/api';

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
  return res.json();
}

export async function switchProvider(providerName) {
  const res = await fetch(`${API_BASE}/config/provider`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ provider: providerName }),
  });
  if (!res.ok) throw new Error(`Failed to switch provider: ${res.statusText}`);
  return res.json();
}

export async function fetchSessions() {
  const res = await fetch(`${API_BASE}/sessions`);
  if (!res.ok) throw new Error(`Failed to fetch sessions: ${res.statusText}`);
  return res.json();
}

export async function createSession(title = "New Growth Conversation") {
  const res = await fetch(`${API_BASE}/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title }),
  });
  if (!res.ok) throw new Error(`Failed to create session: ${res.statusText}`);
  return res.json();
}

export async function fetchSession(sessionId) {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}`);
  if (!res.ok) throw new Error(`Failed to load session: ${res.statusText}`);
  return res.json();
}

export async function deleteSession(sessionId) {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error(`Failed to delete session: ${res.statusText}`);
  return res.json();
}

export async function exportSessionMarkdown(sessionId) {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/export`);
  if (!res.ok) throw new Error(`Failed to export session: ${res.statusText}`);
  return res.json();
}

export async function sendChatMessage(sessionId, message, provider = null) {
  const payload = {
    session_id: sessionId,
    message: message,
    provider: provider,
  };
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Chat request failed: ${res.statusText}`);
  }
  return res.json();
}

export async function generateShip30Essay(topic, targetAudience, sessionId = null) {
  const payload = {
    topic: topic,
    target_audience: targetAudience || "Product Managers and Growth Engineers",
    session_id: sessionId,
  };
  const res = await fetch(`${API_BASE}/skills/ship30`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Failed to generate Ship 30 essay: ${res.statusText}`);
  return res.json();
}
