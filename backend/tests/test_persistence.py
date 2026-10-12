import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, DBSession, DBMessage
from app.services.session_service import session_service
from app.models import SourceCitation, ArtifactPayload

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionTest = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionTest()
    try:
        yield db
    finally:
        db.close()

def test_session_lifecycle(test_db):
    # 1. Create session
    summary = session_service.create_session(test_db, title="PLG Discussion", provider="mock")
    assert summary.id is not None
    assert summary.title == "PLG Discussion"

    # 2. Add message
    citation = SourceCitation(
        id="chunk_1",
        source_title="Elena Verna",
        guest_name="Elena Verna",
        chunk_index=0,
        score=0.95,
        snippet="PLG is an organizational methodology."
    )
    msg = session_service.add_message(
        test_db,
        session_id=summary.id,
        role="user",
        content="What is PLG?",
        citations=[citation]
    )
    assert msg.id is not None

    # 3. Retrieve session with message history
    full_session = session_service.get_session(test_db, summary.id)
    assert full_session is not None
    assert len(full_session.messages) == 1
    assert full_session.messages[0].citations[0].guest_name == "Elena Verna"

    # 4. Delete session
    del_ok = session_service.delete_session(test_db, summary.id)
    assert del_ok
    assert session_service.get_session(test_db, summary.id) is None
