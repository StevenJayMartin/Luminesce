from fastapi import FastAPI
from pydantic import BaseModel

from .ingest import ingest_url
from .retrieval import build_augmented_prompt

app = FastAPI()


class RAGRequest(BaseModel):
    query: str
    session: str | None = None


class IngestRequest(BaseModel):
    url: str


@app.post("/rag")
def rag_endpoint(req: RAGRequest):
    prompt = build_augmented_prompt(req.query)
    return {"augmented_prompt": prompt}


@app.post("/ingest_url")
def ingest_url_endpoint(req: IngestRequest):
    try:
        ingest_url(req.url)
        return {"status": "ok", "url": req.url}
    except Exception as e:
        return {"error": str(e)}
