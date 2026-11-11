from fastapi import FastAPI
from pydantic import BaseModel

from contextlib import asynccontextmanager
from backend.db.database import init_db
from backend.llm import ask

# Initialize the database if it does not exist yet
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="G.H.O.S.T.", lifespan=lifespan)


class ChatIn(BaseModel):
    message: str


@app.get("/health")
def health():
    return {"status": "Ghost online"}


@app.post("/chat")
def chat(body: ChatIn):
    reply = ask(body.message)
    return {"reply": reply}