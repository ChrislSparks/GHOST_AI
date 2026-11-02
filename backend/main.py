from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="G.H.O.S.T.")


class ChatIn(BaseModel):
    message: str


@app.get("/health")
def health():
    return {"status": "Ghost online"}


@app.post("/chat")
def chat(body: ChatIn):
    # For now G.H.O.S.T. just repeats you. Later this calls the LLM.
    return {"reply": f"Echo: {body.message}"}