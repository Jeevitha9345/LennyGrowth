import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import ArtifactViewer from './components/ArtifactViewer';
import ModelStatusBadge from './components/ModelStatusBadge';
import {
  fetchHealth,
  fetchSessions,
  createSession,
  fetchSession,
  deleteSession,
  sendChatMessage,
  generateShip30Essay,
  switchProvider,
  exportSessionMarkdown
} from './services/api';
import './App.css';

export default function App() {
  const [health, setHealth] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeArtifact, setActiveArtifact] = useState(null);

  useEffect(() => {
    loadHealthAndSessions();
  }, []);

  const loadHealthAndSessions = async () => {
    try {
      const hData = await fetchHealth();
      setHealth(hData);

      const sData = await fetchSessions();
      setSessions(sData);

      if (sData.length > 0) {
        loadSessionMessages(sData[0].id);
      }
    } catch (err) {
      console.error('Failed to load initial data:', err);
      setError('Could not connect to backend server. Ensure FastAPI is running on port 8000.');
    }
  };

  const loadSessionMessages = async (sessionId) => {
    try {
      setIsLoading(true);
      setError(null);
      setActiveSessionId(sessionId);
      const sessionData = await fetchSession(sessionId);
      setMessages(sessionData.messages || []);

      const lastWithArtifact = (sessionData.messages || []).slice().reverse().find(m => m.artifact);
      if (lastWithArtifact) {
        setActiveArtifact(lastWithArtifact.artifact);
      }
    } catch (err) {
      setError(`Failed to load chat history: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleProviderChange = async (newProvider) => {
    try {
      const updated = await switchProvider(newProvider);
      setHealth(prev => ({
        ...prev,
        active_provider: updated.active_provider,
        provider_healthy: updated.healthy,
        provider_detail: updated.detail
      }));
    } catch (err) {
      setError(`Failed to switch provider: ${err.message}`);
    }
  };

  const handleNewChat = async () => {
    try {
      setError(null);
      const newSess = await createSession('New Growth Conversation');
      setSessions([newSess, ...sessions]);
      setActiveSessionId(newSess.id);
      setMessages([]);
      setActiveArtifact(null);
    } catch (err) {
      setError(`Failed to create new chat: ${err.message}`);
    }
  };

  const handleDeleteSession = async (sessionId) => {
    try {
      await deleteSession(sessionId);
      const updated = sessions.filter(s => s.id !== sessionId);
      setSessions(updated);
      if (activeSessionId === sessionId) {
        if (updated.length > 0) {
          loadSessionMessages(updated[0].id);
        } else {
          setActiveSessionId(null);
          setMessages([]);
          setActiveArtifact(null);
        }
      }
    } catch (err) {
      setError(`Failed to delete session: ${err.message}`);
    }
  };

  const handleExportSession = async () => {
    if (!activeSessionId) return;
    try {
      const expData = await exportSessionMarkdown(activeSessionId);
      const filename = `${expData.title.replace(/[^a-zA-Z0-9_-]/g, '_').toLowerCase()}_export.md`;
      const blob = new Blob([expData.markdown], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(`Failed to export chat: ${err.message}`);
    }
  };

  const handleSendMessage = async (text) => {
    if (!text.trim()) return;

    const tempUserMsg = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: text,
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempUserMsg]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await sendChatMessage(activeSessionId, text);
      
      if (response.session_id !== activeSessionId) {
        setActiveSessionId(response.session_id);
        const freshSessions = await fetchSessions();
        setSessions(freshSessions);
      }

      const assistantMsg = {
        id: response.message_id,
        session_id: response.session_id,
        role: 'assistant',
        content: response.reply,
        citations: response.citations,
        artifact: response.artifact,
        created_at: new Date().toISOString()
      };

      setMessages(prev => [...prev.filter(m => m.id !== tempUserMsg.id), tempUserMsg, assistantMsg]);

      if (response.artifact) {
        setActiveArtifact(response.artifact);
      }

      const freshSessions = await fetchSessions();
      setSessions(freshSessions);
    } catch (err) {
      setError(`Error sending message: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTriggerShip30 = async (topic) => {
    setIsLoading(true);
    setError(null);

    const tempUserMsg = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: `Generate a Ship 30 for 30 essay on: ${topic}`,
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempUserMsg]);

    try {
      const res = await generateShip30Essay(topic, "Product Managers and Growth Engineers", activeSessionId);
      
      const assistantMsg = {
        id: `ship30-${Date.now()}`,
        role: 'assistant',
        content: res.essay,
        citations: res.citations,
        artifact: res.artifact,
        created_at: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMsg]);
      if (res.artifact) {
        setActiveArtifact(res.artifact);
      }
      const freshSessions = await fetchSessions();
      setSessions(freshSessions);
    } catch (err) {
      setError(`Failed to generate Ship 30 essay: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const currentSession = sessions.find(s => s.id === activeSessionId);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <header className="app-header">
        <div className="brand-section">
          <span className="brand-logo">🎙️</span>
          <span className="brand-title">The Lenny Growth Assistant</span>
          <span className="brand-subtitle">PM & Growth Intelligence</span>
        </div>

        <ModelStatusBadge
          health={health}
          onProviderChange={handleProviderChange}
        />
      </header>

      <div className="app-container">
        <Sidebar
          sessions={sessions}
          activeSessionId={activeSessionId}
          onSelectSession={loadSessionMessages}
          onNewChat={handleNewChat}
          onDeleteSession={handleDeleteSession}
          indexedChunks={health?.indexed_chunks || 0}
        />

        <ChatArea
          sessionTitle={currentSession?.title}
          messages={messages}
          isLoading={isLoading}
          error={error}
          onSendMessage={handleSendMessage}
          onOpenArtifact={(art) => setActiveArtifact(art)}
          onTriggerShip30={handleTriggerShip30}
          onExportSession={handleExportSession}
        />

        {activeArtifact && (
          <ArtifactViewer
            artifact={activeArtifact}
            onClose={() => setActiveArtifact(null)}
          />
        )}
      </div>
    </div>
  );
}
