# Database models for G.H.O.S.T.

from datetime import datetime, timezone
from sqlalchemy import ForeignKey, String, Text, DateTime, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.db.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), default="New conversation")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.id",
    )

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"))
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    input_type: Mapped[str] = mapped_column(String(10), default="text")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")

class Reminder(Base): 
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(primary_key=True)
    message: Mapped[str] = mapped_column(String(500))
    remind_at: Mapped[datetime] = mapped_column(DateTime)
    is_triggered: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

class UserSettings(Base):
    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    display_name: Mapped[str] = mapped_column(String(100), default="User")
    wake_phrase: Mapped[str] = mapped_column(String(50), default="Hey Ghost")
    voice_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    speaking_rate: Mapped[float] = mapped_column(Float, default=1.0)
    response_style: Mapped[str] = mapped_column(String(30), default="balanced")
    response_length: Mapped[str] = mapped_column(String(30), default="medium")
    save_history: Mapped[bool] = mapped_column(Boolean, default=True)

# class UploadedFiles(Base):
    # __tablename__ ="uploaded_files"
    # Add later when file upload tasks are completed