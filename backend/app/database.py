import json
import logging
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Generator, Optional

from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session
from sqlalchemy.sql import text

from app.config import settings

logger = logging.getLogger("lenny_growth.database")
Base = declarative_base()

# ==============================================================================
# SQLAlchemy Models
# ==============================================================================

class DBSession(Base):
    __tablename__ = "sessions"

    id = Column(String(64), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    provider_used = Column(String(50), nullable=False, default="mock")

    messages = relationship("DBMessage", back_populates="session", cascade="all, delete-orphan", order_by="DBMessage.created_at")

class DBMessage(Base):
    __tablename__ = "messages"

    id = Column(String(64), primary_key=True, index=True)
    session_id = Column(String(64), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    citations_json = Column(Text, nullable=True)  # JSON string
    artifact_json = Column(Text, nullable=True)   # JSON string
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    session = relationship("DBSession", back_populates="messages")

class DBTranscriptChunk(Base):
    __tablename__ = "transcript_chunks"

    id = Column(String(64), primary_key=True, index=True)
    source_title = Column(String(255), nullable=False)
    guest_name = Column(String(100), nullable=False)
    source_url = Column(String(500), nullable=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    word_count = Column(Integer, nullable=False)

# ==============================================================================
# Database Connection Manager
# ==============================================================================

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.mode = "uninitialized"
        self.healthy = False
        self._init_db()

    def _init_db(self):
        # 1. Try PostgreSQL (Supabase) if configured
        db_url = settings.database_url.strip()
        if db_url and (db_url.startswith("postgresql://") or db_url.startswith("postgresql+psycopg2://") or db_url.startswith("postgres://")):
            # Standardize prefix for SQLAlchemy
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql://", 1)
            try:
                logger.info("Attempting connection to PostgreSQL (Supabase)...")
                engine = create_engine(db_url, pool_pre_ping=True, pool_size=5, max_overflow=5, connect_args={"connect_timeout": 5})
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                self.engine = engine
                self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
                Base.metadata.create_all(bind=self.engine)
                self.mode = "postgresql"
                self.healthy = True
                logger.info("Successfully connected to Supabase PostgreSQL database.")
                return
            except Exception as e:
                logger.warning(f"PostgreSQL connection failed ({e}). Activating SQLite fallback.")

        # 2. SQLite Fallback (Zero-configuration local database)
        fallback_path = Path(settings.sqlite_fallback_path)
        fallback_path.parent.mkdir(parents=True, exist_ok=True)
        sqlite_url = f"sqlite:///{fallback_path.resolve()}"
        
        try:
            self.engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            Base.metadata.create_all(bind=self.engine)
            self.mode = "sqlite_fallback"
            self.healthy = True
            logger.info(f"Initialized SQLite fallback database at: {fallback_path}")
        except Exception as e:
            logger.error(f"Failed to initialize SQLite database: {e}")
            self.healthy = False
            self.mode = "error"

db_manager = DatabaseManager()

def get_db() -> Generator[Session, None, None]:
    if not db_manager.SessionLocal:
        raise RuntimeError("Database not initialized")
    db = db_manager.SessionLocal()
    try:
        yield db
    finally:
        db.close()
