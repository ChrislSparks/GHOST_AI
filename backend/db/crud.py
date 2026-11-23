# Create, Read, Update, Delete (CRUD) functions for the database

from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.db.models import Conversation, Message, Reminder

# Retrieve the current UTC time without timezone information
def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

class DatabaseService:
    
    def __init__(self, db: Session):
        self.db = db

    # Creates a conversation and adds it to the database
    def create_conversation(self, title: str = "New conversation") -> Conversation:
        conversation = Conversation(title=title)
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation
    
    # Creates a message and adds it to the database
    def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        input_type: str = "text",
    ) -> Message:
        if role not in ("user", "assistant"):
            raise ValueError("role must be 'user' or 'assistant'")
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            input_type=input_type,
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    # Creates a reminder and adds it to the database
    def create_reminder(self, message: str, remind_at: datetime) -> Reminder:
        message = message.strip()
        if not message:
            raise ValueError("Reminder message cannot be empty.")

        if remind_at.tzinfo is not None:
            remind_at = remind_at.astimezone(timezone.utc).replace(tzinfo=None)

        if remind_at <= _utc_now():
            raise ValueError("Reminder time must be in the future.")

        reminder = Reminder(message=message, remind_at=remind_at)
        self.db.add(reminder)
        self.db.commit()
        self.db.refresh(reminder)
        return reminder

    # Retrieves all active (not triggered) reminders from the database
    def get_active_reminders(self) -> list[Reminder]:
        stmt = (
            select(Reminder)
            .where(Reminder.is_triggered == False)
            .order_by(Reminder.remind_at)
        )
        return list(self.db.scalars(stmt))

    # Retrieves all reminders that are due (remind_at <= now) and not triggered
    def get_due_reminders(self, now: datetime | None = None) -> list[Reminder]:
        now = now or _utc_now()
        stmt = (
            select(Reminder)
            .where(Reminder.is_triggered == False)
            .where(Reminder.remind_at <= now)
            .order_by(Reminder.remind_at)
        )
        return list(self.db.scalars(stmt))

    # Marks a reminder as triggered in the database
    def mark_triggered(self, reminder_id: int) -> Reminder:
        reminder = self.db.get(Reminder, reminder_id)
        if reminder is None:
            raise ValueError(f"Reminder with id {reminder_id} does not exist.")
        reminder.is_triggered = True
        self.db.commit()
        self.db.refresh(reminder)
        return reminder

    def get_pending_alerts(self, now: datetime | None = None) -> list[Reminder]:
        now = now or _utc_now()
        stmt = (
            select(Reminder)
            .where(Reminder.is_triggered == False)
            .where(Reminder.remind_at <= now)
            .order_by(Reminder.remind_at)
        )
        return list(self.db.scalars(stmt))

    def acknowledge_reminder(self, reminder_id: int) -> Reminder:
        reminder = self.db.get(Reminder, reminder_id)
        if reminder is None:
            raise ValueError(f"Reminder with id {reminder_id} does not exist.")
        reminder.is_acknowledged = True
        self.db.commit()
        self.db.refresh(reminder)
        return reminder