import logging
import os
from typing import List, Dict, Any
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import settings
from app.models import (
    HealthResponse, SessionSummary, SessionSchema, CreateSessionRequest,
    ChatRequest, ChatResponse, Ship30SkillRequest
)
from app.database import get_db, db_manager
from app.retrieval.indexer import retriever
from app.providers.factory import provider_factory
from app.services.session_service import session_service
from app.services.chat_service import chat_service
from app.skills.ship30_skill import ship30_skill

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
)
logger = logging.getLogger("lenny_growth.main")

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing The Lenny Growth Assistant API...")
    logger.info(f"Database Mode: {db_manager.mode} (Healthy: {db_manager.healthy})")
    logger.info(f"Active Model Provider: {settings.active_provider}")
    logger.info(f"Total Chunks in BM25 Index: {len(retriever.chunks)}")
    yield

app = FastAPI(
    title="The Lenny Growth Assistant API",
    description="Resource-constrained, grounded growth intelligence assistant and artifact generator.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================================
# Health & Status Endpoints
# ==============================================================================

@app.get("/api/health", response_model=HealthResponse)
async def get_health():
    active_prov = provider_factory.get_provider()
    health_info = await active_prov.health_check()
    
    return HealthResponse(
        status="healthy" if db_manager.healthy else "degraded",
        active_provider=settings.active_provider,
        provider_healthy=health_info.healthy,
        provider_detail=health_info.detail,
        database_mode=db_manager.mode,
        database_healthy=db_manager.healthy,
        indexed_chunks=len(retriever.chunks),
        memory_profile="Strict ~1GB RAM (CPU-only, zero heavy embeddings)"
    )

# ==============================================================================
# Session Management Endpoints
# ==============================================================================

@app.get("/api/sessions", response_model=List[SessionSummary])
def list_sessions(db: Session = Depends(get_db)):
    return session_service.list_sessions(db)

@app.post("/api/sessions", response_model=SessionSummary)
def create_session(req: CreateSessionRequest, db: Session = Depends(get_db)):
    return session_service.create_session(
        db,
        title=req.title or "New Growth Conversation",
        provider=settings.active_provider
    )

@app.get("/api/sessions/{session_id}", response_model=SessionSchema)
def get_session(session_id: str, db: Session = Depends(get_db)):
    session = session_service.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db)):
    success = session_service.delete_session(db, session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "deleted", "session_id": session_id}

# ==============================================================================
# Chat & Skill Endpoints
# ==============================================================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat_turn(req: ChatRequest, db: Session = Depends(get_db)):
    try:
        response = await chat_service.process_chat(
            db=db,
            message=req.message,
            session_id=req.session_id,
            provider_name=req.provider
        )
        return response
    except Exception as e:
        logger.error(f"Error processing chat turn: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal chat error: {str(e)}")

@app.post("/api/skills/ship30")
async def generate_ship30_essay(req: Ship30SkillRequest, db: Session = Depends(get_db)):
    try:
        res = await ship30_skill.generate_essay(
            topic=req.topic,
            target_audience=req.target_audience or "Product Managers and Growth Engineers",
            focus_guest=req.focus_guest
        )
        
        # If session_id is provided, persist it as a conversation turn
        if req.session_id:
            session_service.add_message(
                db=db,
                session_id=req.session_id,
                role="user",
                content=f"Generate a Ship 30 for 30 essay on: {req.topic}"
            )
            session_service.add_message(
                db=db,
                session_id=req.session_id,
                role="assistant",
                content=res["essay"],
                citations=res["citations"],
                artifact=res["artifact"]
            )

        return res
    except Exception as e:
        logger.error(f"Error executing Ship 30 skill: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ship 30 skill execution error: {str(e)}")

@app.post("/api/config/provider")
async def set_active_provider(req: Dict[str, str]):
    new_provider = req.get("provider", "mock").lower().strip()
    if new_provider in ["mock", "ollama", "openai", "anthropic"]:
        settings.active_provider = new_provider
        prov = provider_factory.get_provider(new_provider)
        health = await prov.health_check()
        return {
            "status": "updated",
            "active_provider": new_provider,
            "healthy": health.healthy,
            "detail": health.detail
        }
    raise HTTPException(status_code=400, detail=f"Invalid provider: {new_provider}")

@app.get("/api/sessions/{session_id}/export")
def export_session_markdown(session_id: str, db: Session = Depends(get_db)):
    session = session_service.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    md_lines = [
        f"# {session.title}",
        f"**Session ID**: `{session.id}` | **Date**: {session.created_at} | **Provider**: {session.provider_used}\n",
        "---\n"
    ]
    for msg in session.messages or []:
        role_title = "👤 User" if msg.role == "user" else "🎙️ Lenny Growth Assistant"
        md_lines.append(f"### {role_title}\n{msg.content}\n")
        if msg.citations:
            md_lines.append("**Sources Grounded:**")
            for c in msg.citations:
                md_lines.append(f"- 🎙️ *{c.source_title}* ({c.guest_name}): \"{c.snippet}\"")
            md_lines.append("")
        md_lines.append("---\n")

    return {
        "session_id": session.id,
        "title": session.title,
        "markdown": "\n".join(md_lines)
    }

@app.post("/api/retrieval/reindex")
def reindex_transcripts():
    from app.retrieval.ingest import ingest_transcripts
    chunks = ingest_transcripts()
    retriever.chunks = chunks
    retriever._build_index()
    return {
        "status": "reindexed",
        "total_chunks": len(retriever.chunks),
        "vocab_terms": len(retriever.idf)
    }

# ==============================================================================
# Retrieval Diagnostic Endpoints
# ==============================================================================

@app.get("/api/retrieval/stats")
def get_retrieval_stats():
    return {
        "total_chunks": len(retriever.chunks),
        "unique_vocab_terms": len(retriever.idf),
        "avg_doc_len_words": round(retriever.avg_doc_len, 2),
        "cache_file": settings.chunks_cache_file
    }

@app.post("/api/retrieval/search")
def search_diagnostics(query: str = Query(..., min_length=2)):
    chunks, insufficient = retriever.search(query, top_k=4)
    return {
        "query": query,
        "insufficient_evidence": insufficient,
        "results_count": len(chunks),
        "results": chunks
    }
