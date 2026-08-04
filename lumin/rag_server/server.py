from fastapi import FastAPI
from pydantic import BaseModel

from .retrieval import build_augmented_prompt

app = FastAPI()


class RagRequest(BaseModel):
    query: str
    session: str | None = None  # reserved for future per-session logic


class RagResponse(BaseModel):
    augmented_prompt: str


@app.post("/rag", response_model=RagResponse)
def rag_endpoint(req: RagRequest):
    """
    RAG microservice:
    - takes a query
    - builds an augmented prompt using stored docs
    - returns that prompt to the chat server
    """
    augmented = build_augmented_prompt(req.query)
    return RagResponse(augmented_prompt=augmented)

