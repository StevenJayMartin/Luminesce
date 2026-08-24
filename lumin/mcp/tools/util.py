import uuid
import hashlib

def tool_uuid(params):
    return {"uuid": str(uuid.uuid4())}

def tool_hash(params):
    text = params.get("text", "")
    return {"sha256": hashlib.sha256(text.encode()).hexdigest()}

TOOL_META = {
    "tool_uuid": {
        "description": "Generates a UUID",
        "params": {},
        "returns": "UUID string",
        "category": "util",
        "examples": ["mcp_uuid"]
    },
    "tool_hash": {
        "description": "SHA256 hash of text",
        "params": {"text": "string"},
        "returns": "Hash string",
        "category": "util",
        "examples": ["mcp_hash text=hello"]
    }
}

