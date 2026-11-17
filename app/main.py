from pathlib import Path
from uuid import uuid4

from app.core.orchestrator import ChuckOrchestrator
from app.memory.executor import commit_memory_action
from app.memory.facts import initialize_facts
from app.models.factory import create_llm
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

app = FastAPI(title="C.H.U.C.K.")
llm = create_llm()
chuck = ChuckOrchestrator(llm)

initialize_facts()


class ChatRequest(BaseModel):
    message: str
    conversation_id: str = Field(
        default_factory=lambda: str(uuid4())
    )


@app.post("/chat")
def chat(request: ChatRequest):
    return chuck.chat(
        conversation_id=request.conversation_id,
        message=request.message,
    )


# Serve frontend last.
FRONTEND_DIR = (
    Path(__file__).resolve().parent.parent / "frontend"
)

app.mount(
    "/",
    StaticFiles(directory=FRONTEND_DIR, html=True),
    name="frontend"
)