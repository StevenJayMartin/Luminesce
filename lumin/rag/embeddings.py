import requests

def embed_text(text: str):
    """
    Call Ollama embedding model.
    """
    resp = requests.post(
        "http://localhost:11434/api/embed",
        json={"model": "nomic-embed-text", "input": text},
        timeout=10
    )
    return resp.json()["embeddings"][0]
