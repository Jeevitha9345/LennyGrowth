import json
import uuid
import logging
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session
from app.database import DBSession, DBMessage
from app.models import SessionSummary, SessionSchema, MessageSchema, SourceCitation, ArtifactPayload

logger = logging.getLogger("lenny_growth.services.session")

class SessionService:
    def create_session(self, db: Session, title: str = "New Growth Conversation", provider: str = "mock") -> SessionSummary:
        session_id = str(uuid.uuid4())[:8]
        now = datetime.now(timezone.utc)
        new_session = DBSession(
            id=session_id,
            title=title,
            created_at=now,
            updated_at=now,
            provider_used=provider
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        return SessionSummary(
            id=new_session.id,
            title=new_session.title,
            created_at=new_session.created_at,
            updated_at=new_session.updated_at,
            message_count=0,
            provider_used=new_session.provider_used
        )

    def list_sessions(self, db: Session) -> List[SessionSummary]:
        sessions = db.query(DBSession).order_by(DBSession.updated_at.desc()).all()
        summaries = []
        for s in sessions:
            msg_count = db.query(DBMessage).filter(DBMessage.session_id == s.id).count()
            summaries.append(SessionSummary(
                id=s.id,
                title=s.title,
                created_at=s.created_at,
                updated_at=s.updated_at,
                message_count=msg_count,
                provider_used=s.provider_used
            ))
        return summaries

    def get_session(self, db: Session, session_id: str) -> Optional[SessionSchema]:
        session = db.query(DBSession).filter(DBSession.id == session_id).first()
        if not session:
            return None

        messages = db.query(DBMessage).filter(DBMessage.session_id == session_id).order_by(DBMessage.created_at.asc()).all()
        msg_schemas = []
        for m in messages:
            citations = []
            if m.citations_json:
                try:
                    c_data = json.loads(m.citations_json)
                    citations = [SourceCitation(**item) for item in c_data]
                except Exception:
                    pass

            artifact = None
            if m.artifact_json:
                try:
                    a_data = json.loads(m.artifact_json)
                    artifact = ArtifactPayload(**a_data)
                except Exception:
                    pass

            msg_schemas.append(MessageSchema(
                id=m.id,
                session_id=m.session_id,
                role=m.role,
                content=m.content,
                citations=citations,
                artifact=artifact,
                created_at=m.created_at
            ))

        return SessionSchema(
            id=session.id,
            title=session.title,
            created_at=session.created_at,
            updated_at=session.updated_at,
            provider_used=session.provider_used,
            messages=msg_schemas
        )

    def add_message(
        self,
        db: Session,
        session_id: str,
        role: str,
        content: str,
        citations: List[SourceCitation] = None,
        artifact: Optional[ArtifactPayload] = None
    ) -> DBMessage:
        msg_id = str(uuid.uuid4())[:8]
        now = datetime.now(timezone.utc)
        
        c_json = json.dumps([c.model_dump() for c in (citations or [])]) if citations else None
        a_json = json.dumps(artifact.model_dump()) if artifact else None

        msg = DBMessage(
            id=msg_id,
            session_id=session_id,
            role=role,
            content=content,
            citations_json=c_json,
            artifact_json=a_json,
            created_at=now
        )
        db.add(msg)

        # Update session timestamp
        session = db.query(DBSession).filter(DBSession.id == session_id).first()
        if session:
            session.updated_at = now
            # Auto-title first session message
            if session.title in ["New Growth Conversation", "New Chat"] and role == "user":
                clean_title = content.strip().replace("\n", " ")
                session.title = clean_title[:45] + ("..." if len(clean_title) > 45 else "")

        db.commit()
        db.refresh(msg)
        return msg

    def delete_session(self, db: Session, session_id: str) -> bool:
        session = db.query(DBSession).filter(DBSession.id == session_id).first()
        if not session:
            return False
        db.delete(session)
        db.commit()
        return True

session_service = SessionService()
