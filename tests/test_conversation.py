# G.H.O.S.T. - Conversation Manager Unit Tests
# Tests valid and invalid inputs using pytest.

import pytest
from backend.core.conversation import ConversationManager


class TestConversationManager:

    # Method 1: add_message()

    def test_add_valid_message(self):
        conversation = ConversationManager()
        conversation.add_message("user", "Hello")

        assert conversation.get_history() == [
            {"role": "user", "content": "Hello"}
        ]

    def test_add_invalid_role(self):
        conversation = ConversationManager()

        with pytest.raises(ValueError, match="Invalid message role"):
            conversation.add_message("admin", "Hello")

    def test_add_empty_message(self):
        conversation = ConversationManager()

        with pytest.raises(ValueError, match="Message content cannot be empty"):
            conversation.add_message("user", "")

    # Method 2: get_history()

    def test_get_empty_history(self):
        conversation = ConversationManager()

        assert conversation.get_history() == []

    def test_get_multiple_messages(self):
        conversation = ConversationManager()
        conversation.add_message("user", "Hello")
        conversation.add_message("assistant", "Hi!")

        assert conversation.get_history() == [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi!"}
        ]

    def test_history_is_independent_copy(self):
        conversation = ConversationManager()
        conversation.add_message("user", "Original")

        history = conversation.get_history()
        history[0]["content"] = "Changed"

        assert conversation.get_history()[0]["content"] == "Original"

    # Method 3: clear_history()

    def test_clear_history(self):
        conversation = ConversationManager()
        conversation.add_message("user", "Hello")
        conversation.add_message("assistant", "Hi!")

        conversation.clear_history()

        assert conversation.get_history() == []
    
    def test_clear_empty_history_does_not_fail(self):
        conversation = ConversationManager()

        conversation.clear_history()

        assert conversation.get_history() == []
