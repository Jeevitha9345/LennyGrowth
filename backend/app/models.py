from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class SourceCitation(BaseModel):
    id: str
    source_title: str
    guest_name: str
    source_url: Optional[str] = None
    chunk_index: int
    score: float
    snippet: str

class ArtifactPayload(BaseModel):
    id: str
    title: str
    type: str  # "html", "markdown", "essay"
    content: str
    language: Optional[str] = "html"
    summary: Optional[str] = None

class MessageSchema(BaseModel):
    id: str
    session_id: str
    role: str  # "user", "assistant", "system"
    content: str
    citations: Optional[List[SourceCitation]] = []
    artifact: Optional[ArtifactPayload] = None
    created_at: datetime

class SessionSchema(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    provider_used: str
    messages: Optional[List[MessageSchema]] = []

class SessionSummary(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    provider_used: str

class CreateSessionRequest(BaseModel):
    title: Optional[str] = "New Growth Conversation"

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str = Field(..., min_length=1, max_length=2000)
    provider: Optional[str] = None  # Override active provider if specified

class ChatResponse(BaseModel):
    session_id: str
    message_id: str
    reply: str
    citations: List[SourceCitation] = []
    artifact: Optional[ArtifactPayload] = None
    insufficient_evidence: bool = False
    provider_used: str
    latency_ms: float

class Ship30SkillRequest(BaseModel):
    session_id: Optional[str] = None
    topic: str = Field(..., min_length=3, max_length=500)
    target_audience: Optional[str] = "Product Managers and Growth Engineers"
    focus_guest: Optional[str] = None

class ArtifactSkillRequest(BaseModel):
    session_id: Optional[str] = None
    topic: str
    artifact_type: str = "html"  # "html" or "markdown"
    instructions: Optional[str] = ""

class HealthResponse(BaseModel):
    status: str
    active_provider: str
    provider_healthy: bool
    provider_detail: str
    database_mode: str  # "postgresql" or "sqlite_fallback"
    database_healthy: bool
    indexed_chunks: int
    memory_profile: str
