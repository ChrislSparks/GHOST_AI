# Database Unit Tests for G.H.O.S.T.
# Uses pytest.

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, timezone
from backend.db.database import Base
from backend.db import models, crud
from backend.db.crud import DatabaseService

# Helper function to get the current UTC time without timezone information
def utc_in(hours: float = 0) -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=hours)

# Fixture to create a temporary in-memory database for testing
@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()
    engine.dispose()

# Fixture to provide a DatabaseService instance for testing
@pytest.fixture
def service(db):
    return DatabaseService(db)

class TestDatabaseService: 

    # Tests conversation -> database saving function
    def test_create_conversation_saves_to_database(self, db):
        repo = DatabaseService(db)

        conversation = repo.create_conversation(title="G.H.O.S.T. and Gemini")

        assert conversation.id is not None
        assert conversation.title == "G.H.O.S.T. and Gemini"
        assert db.get(models.Conversation, conversation.id) is not None

    # Tests default conversation title
    def test_create_conversation_uses_default_title(self, db):
        repo = DatabaseService(db)

        conversation = repo.create_conversation()

        assert conversation.title == "New conversation"

    # Tests message -> conversation linking function
    def test_add_message_links_to_conversation(self, db):
        repo = DatabaseService(db)
        conversation = repo.create_conversation()

        message = repo.add_message(conversation.id, "user", "Hello", input_type="voice")

        assert message.conversation_id == conversation.id
        assert message.role == "user"
        assert message.input_type == "voice"
        assert len(conversation.messages) == 1

    # Tests invalid role flagging for non-user/assistants
    def test_add_message_rejects_invalid_role(self, db):
        repo = DatabaseService(db)
        conversation = repo.create_conversation()

        with pytest.raises(ValueError):
            repo.add_message(conversation.id, "robot", "Hello")

class TestReminderMethods:

    # Tests reminder creation and saving to the database
    def test_create_reminder_saves_valid_reminder(self, service):
        remind_at = utc_in(hours=1)
        
        reminder = service.create_reminder("Pay bills", remind_at)
            
        assert reminder.id is not None
        assert reminder.message == "Pay bills"
        assert reminder.remind_at == remind_at
        assert reminder.is_triggered is False

    # Tests that whitespace is stripped from the reminder message
    def test_create_reminder_strips_whitespace(self, service):
        reminder = service.create_reminder("   Buy groceries   ", utc_in(hours=1))
        assert reminder.message == "Buy groceries"

    # Tests that an empty reminder message raises a ValueError
    def test_create_reminder_rejects_empty_message(self, service):
        with pytest.raises(ValueError):
            service.create_reminder("   ", utc_in(hours=1))

    # Tests that a reminder cannot be created for a past time
    def test_create_reminder_rejects_past_time(self, service):
        with pytest.raises(ValueError):
            service.create_reminder("Too late", utc_in(hours=-1))

    # Tests that a timezone-aware datetime is converted to UTC without timezone info
    def test_create_reminder_converts_timezone_aware_time_to_utc(self, service):
        aware_time = datetime.now(timezone.utc) + timedelta(hours=1)
        reminder = service.create_reminder("Check email", aware_time)

        assert reminder.remind_at.tzinfo is None
        assert reminder.remind_at == aware_time.replace(tzinfo=None)

    # Tests that active reminders are returned in order of soonest first
    def test_get_active_reminders_returns_soonest_first(self, service):
        service.create_reminder("later", utc_in(hours=3))
        service.create_reminder("sooner", utc_in(hours=1))

        active = service.get_active_reminders()

        assert [r.message for r in active] == ["sooner", "later"]

    # Tests that triggered reminders are excluded from the active reminders list
    def test_get_active_reminders_excludes_triggered(self, service):
        done = service.create_reminder("done", utc_in(hours=1))
        service.create_reminder("pending", utc_in(hours=2))
        service.mark_triggered(done.id)

        active = service.get_active_reminders()

        assert [r.message for r in active] == ["pending"]

    # Tests that due reminders are returned in order of soonest first
    def test_get_due_reminders_returns_due_and_skips_future(self, service):
        service.create_reminder("due", utc_in(hours=1))
        service.create_reminder("future", utc_in(hours=5))

        due = service.get_due_reminders(now=utc_in(hours=2))

        assert [r.message for r in due] == ["due"]

    # Tests that triggered reminders are excluded from the due reminders list
    def test_get_due_reminders_excludes_triggered(self, service):
        reminder = service.create_reminder("already fired", utc_in(hours=1))
        service.mark_triggered(reminder.id)

        due = service.get_due_reminders(now=utc_in(hours=2))

        assert due == []

    # Tests that marking a reminder as triggered sets the is_triggered flag
    def test_mark_triggered_sets_flag(self, service):
        reminder = service.create_reminder("Ping", utc_in(hours=1))
        updated = service.mark_triggered(reminder.id)
        assert updated.is_triggered is True

    # Tests that marking a reminder as triggered with an unknown ID raises a ValueError
    def test_mark_triggered_rejects_unknown_id(self, service):
        with pytest.raises(ValueError):
            service.mark_triggered(999)