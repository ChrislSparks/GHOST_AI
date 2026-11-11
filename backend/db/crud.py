# Create, Read, Update, Delete (CRUD) functions for the database

from sqlalchemy.orm import Session
from backend.db.models import Conversation, Message

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