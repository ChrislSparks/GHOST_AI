from google import genai
from google.genai import types

from backend.config import GEMINI_API_KEY, GEMINI_MODEL

client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = (
    "You are G.H.O.S.T., a friendly and helpful AI voice assistant. "
    "Keep answers short and clear, since they will be spoken out loud."
)


def ask(message: str) -> str:
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=message,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
    )
    return response.text