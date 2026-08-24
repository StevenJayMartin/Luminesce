from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def tool_embed_text(params):
    text = params.get("text")
    emb = model.encode(text).tolist()
    return {"embedding": emb}

TOOL_META = {
    "tool_embed_text": {
        "description": "Generates an embedding for text",
        "params": {"text": "string"},
        "returns": "Embedding vector",
        "category": "ai",
        "examples": ["mcp_embed_text text='hello world'"]
    }
}
