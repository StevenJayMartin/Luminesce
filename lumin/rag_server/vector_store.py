import faiss
import numpy as np

# Embedding function
from .embeddings import embed_text

# FAISS index (nomic-embed-text = 768 dims)
DIM = 768
index = faiss.IndexFlatL2(DIM)

# Metadata store
documents = []


def add_vector(doc_id: str, chunk: str):
    """
    Embed a chunk and add it to FAISS + metadata list.
    """
    vec = embed_text(chunk)
    vec = np.array(vec).astype("float32").reshape(1, -1)

    index.add(vec)
    documents.append({
        "id": doc_id,
        "chunk": chunk
    })


def add_document(doc_id: str, text: str):
    """
    Chunk text and add each chunk.
    """
    for chunk in chunk_text(text):
        add_vector(doc_id, chunk)


def search_vectors(query: str, k: int = 5):
    """
    Embed query and search FAISS.
    """
    if index.ntotal == 0:
        return []

    qvec = embed_text(query)
    qvec = np.array(qvec).astype("float32").reshape(1, -1)

    distances, indices = index.search(qvec, k)

    results = []
    for idx in indices[0]:
        if idx < len(documents):
            results.append(documents[idx])

    return results


def chunk_text(text: str, max_len: int = 500):
    """
    Simple chunker: ~500 chars per chunk.
    """
    words = text.split()
    chunks = []
    current = []

    for w in words:
        current.append(w)
        if len(" ".join(current)) > max_len:
            chunks.append(" ".join(current))
            current = []

    if current:
        chunks.append(" ".join(current))

    return chunks
