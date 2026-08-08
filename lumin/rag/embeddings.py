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
    
    data = resp.json()

    embs = data.get("embeddings", [])
    if not embs:
        raise ValueError(f"Embedding model returned no embeddings: {data}")

    return embs[0]
