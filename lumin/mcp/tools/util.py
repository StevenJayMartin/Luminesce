import uuid
import hashlib

def tool_uuid(params):
    return {"uuid": str(uuid.uuid4())}

def tool_hash(params):
    text = params.get("text", "")
    return {"sha256": hashlib.sha256(text.encode()).hexdigest()}

def run(params):
    """
    MCP entrypoint for the 'util' tool.
    Dispatches commands to the correct helper.
    """

    command = params.get("command")

    if command == "uuid":
        return tool_uuid(params)

    if command == "hash":
        return tool_hash(params)

    return {"error": f"Unknown util command '{command}'"}

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
