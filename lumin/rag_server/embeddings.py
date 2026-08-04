import numpy as np
import ollama

EMBED_MODEL = "nomic-embed-text"
EMBED_DIM = 768  # adjust if your model differs


def embed(text: str) -> np.ndarray:
    """
    Return a float32 numpy vector for the given text.
    """
    resp = ollama.embeddings(model=EMBED_MODEL, prompt=text)
    vec = np.array(resp["embedding"], dtype="float32")
    return vec.reshape(1, -1)  # shape: (1, EMBED_DIM)

