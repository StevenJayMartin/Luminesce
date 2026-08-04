import faiss
import numpy as np

from .embeddings import EMBED_DIM

# In-memory FAISS index and doc store
index = faiss.IndexFlatL2(EMBED_DIM)
docs: list[str] = []


def add_vector(vec: np.ndarray, text: str) -> None:
    """
    Add a single vector + its raw text to the store.
    """
    index.add(vec)
    docs.append(text)


def search_vectors(qvec: np.ndarray, k: int = 3) -> list[str]:
    """
    Return top-k document texts for the given query vector.
    """
    if len(docs) == 0:
        return []

    distances, ids = index.search(qvec, k)
    return [docs[i] for i in ids[0] if i >= 0]

