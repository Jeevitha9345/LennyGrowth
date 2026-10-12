import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database_mode" in data
    assert data["indexed_chunks"] > 0

def test_sessions_api():
    # 1. Create session
    create_resp = client.post("/api/sessions", json={"title": "API Test Session"})
    assert create_resp.status_code == 200
    session_data = create_resp.json()
    session_id = session_data["id"]

    # 2. List sessions
    list_resp = client.get("/api/sessions")
    assert list_resp.status_code == 200
    sessions = list_resp.json()
    assert any(s["id"] == session_id for s in sessions)

    # 3. Chat in session
    chat_resp = client.post("/api/chat", json={
        "session_id": session_id,
        "message": "What is the reverse trial from Elena Verna?"
    })
    assert chat_resp.status_code == 200
    chat_data = chat_resp.json()
    assert "Elena Verna" in chat_data["reply"] or "Reverse Trial" in chat_data["reply"]
    assert len(chat_data["citations"]) > 0

    # 4. Delete session
    del_resp = client.delete(f"/api/sessions/{session_id}")
    assert del_resp.status_code == 200

def test_ship30_skill_api():
    resp = client.post("/api/skills/ship30", json={
        "topic": "Four Fits Framework and Growth Loops",
        "target_audience": "Founders"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "essay" in data
    assert data["artifact"] is not None
