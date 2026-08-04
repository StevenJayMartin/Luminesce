from .embeddings import embed
from .vector_store import add_vector


def ingest_text(text: str) -> None:
    """
    Ingest a single text blob into the RAG store.
    For now: no chunking, just whole-text.
    """
    vec = embed(text)
    add_vector(vec, text)

