# Database Unit Tests for G.H.O.S.T.
# Uses pytest.

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.db.database import Base
from backend.db import models, crud
from backend.db.crud import DatabaseService

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()
    engine.dispose()

class TestDatabaseService: 
    
    # Tests conversation -> database saving function
    def test_create_conversation_saves_to_database(self, db):
        repo = DatabaseService(db)

        conversation = repo.create_conversation(title="G.H.O.S.T. and Gemini")

        assert conversation.id is not None
        assert conversation.title == "G.H.O.S.T. and Gemini"
        assert db.get(models.Conversation, conversation.id) is not None

    # Tests message -> conversation linking function
    def test_add_message_links_to_conversation(self, db):
        repo = DatabaseService(db)
        conversation = repo.create_conversation()

        message = repo.add_message(conversation.id, "user", "Hello", input_type="voice")

        assert message.conversation_id == conversation.id
        assert message.role == "user"
        assert message.input_type == "voice"
        assert len(conversation.messages) == 1