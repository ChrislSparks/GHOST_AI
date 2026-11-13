# G.H.O.S.T. - Conversation Manager
# Manages messages within an active conversation.
# GitHub Issue #16: Conversation Context

class ConversationManager:
    def __init__(self):
        self.messages = []

    def add_message(self, role: str, content: str):
        """Validate and add a message to the conversation."""

        if role not in ("user", "assistant"):
            raise ValueError("Invalid message role")

        if not isinstance(content, str) or not content.strip():
            raise ValueError("Message content cannot be empty")

        message = {
            "role": role,
            "content": content
        }

        self.messages.append(message)

    def get_history(self):
        """Return a copy of the conversation history."""
        return [message.copy() for message in self.messages]

    def clear_history(self):
        """Remove all messages from the active conversation."""
        self.messages.clear()
