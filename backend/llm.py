# G.H.O.S.T. - LLM Service
# Sends user messages to Google Gemini and prepares replies to be spoken aloud.

import re

from backend.config import GEMINI_API_KEY, GEMINI_MODEL

SYSTEM_PROMPT = (
    "You are G.H.O.S.T., a friendly and helpful AI voice assistant. "
    "Keep answers short and clear, since they will be spoken out loud."
)

MAX_MESSAGE_LENGTH = 2000
FALLBACK_REPLY = "Sorry, I didn't catch that. Please try again."


class GhostLLM:
    def __init__(self, client=None, model: str = GEMINI_MODEL,
                 max_length: int = MAX_MESSAGE_LENGTH):
        if client is None:
            from google import genai
            client = genai.Client(api_key=GEMINI_API_KEY)
        self.client = client
        self.model = model
        self.max_length = max_length

    def ask(self, message: str) -> str:
        """Validate the user's message, send it to Gemini, and return a clean reply."""

        if not isinstance(message, str):
            raise TypeError("Message must be a string")

        if not message.strip():
            raise ValueError("Message cannot be empty")

        if len(message) > self.max_length:
            raise ValueError(
                f"Message is too long (max {self.max_length} characters)"
            )

        response = self.client.models.generate_content(
            model=self.model,
            contents=message.strip(),
            config={"system_instruction": SYSTEM_PROMPT},
        )
        return self.clean_reply(response.text)

    def clean_reply(self, text) -> str:
        """Strip markdown and extra whitespace so the reply reads well out loud."""

        if text is None:
            return FALLBACK_REPLY

        if not isinstance(text, str):
            raise TypeError("Reply must be a string")

        text = re.sub(r"[*_#`]", "", text)       # markdown symbols
        text = re.sub(r"\s+", " ", text).strip()  # collapse whitespace/newlines

        return text if text else FALLBACK_REPLY


_default_llm = None


def ask(message: str) -> str:
    """Module-level helper used by main.py."""
    global _default_llm
    if _default_llm is None:
        _default_llm = GhostLLM()
    return _default_llm.ask(message)
