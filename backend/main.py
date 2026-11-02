from fastapi import FastAPI
from pydantic import BaseModel

from backend.llm import ask

app = FastAPI(title="G.H.O.S.T.")


class ChatIn(BaseModel):
    message: str


@app.get("/health")
def health():
    return {"status": "Ghost online"}


@app.post("/chat")
def chat(body: ChatIn):
    reply = ask(body.message)
    return {"reply": reply}