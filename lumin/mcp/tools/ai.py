from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

# ------------------------------------------------------------
# AI operations
# ------------------------------------------------------------

def tool_embed_text(params):
    text = params.get("text")
    if not text:
        return {"error": "Missing 'text' parameter"}

    try:
        emb = model.encode(text).tolist()
        return {"embedding": emb}
    except Exception as e:
        return {"error": str(e)}

# ------------------------------------------------------------
# MCP entrypoint
# ------------------------------------------------------------

def run(params):
    command = params.get("command")

    if command == "embed":
        return tool_embed_text(params)

    return {"error": f"Unknown ai command '{command}'"}

# ------------------------------------------------------------
# Metadata
# ------------------------------------------------------------

TOOL_META = {
    "tool_embed_text": {
        "description": "Generates an embedding for text",
        "params": {"text": "string"},
        "returns": "Embedding vector",
        "category": "ai",
        "examples": ["mcp_embed_text text='hello world'"]
    }
}
