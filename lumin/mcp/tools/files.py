import os

# ------------------------------------------------------------
# File operations
# ------------------------------------------------------------

def tool_read_file(params):
    """Read the contents of a file."""
    path = params.get("path")
    if not path:
        return {"error": "Missing 'path' parameter"}

    try:
        with open(path, "r") as f:
            return {"content": f.read()}
    except Exception as e:
        return {"error": str(e)}


def tool_search_files(params):
    """Search for files containing a term."""
    root = params.get("root")
    term = params.get("term")

    if not root or not term:
        return {"error": "Missing 'root' or 'term' parameter"}

    matches = []
    try:
        for dirpath, _, filenames in os.walk(root):
            for f in filenames:
                if term in f:
                    matches.append(os.path.join(dirpath, f))
        return {"matches": matches}
    except Exception as e:
        return {"error": str(e)}


def tool_list_dir(params):
    """List files in a directory."""
    path = params.get("path", ".")
    try:
        return {"files": os.listdir(path)}
    except Exception as e:
        return {"error": str(e)}


# ------------------------------------------------------------
# MCP entrypoint
# ------------------------------------------------------------

def run(params):
    """Dispatch MCP commands."""
    command = params.get("command")

    if command == "read":
        return tool_read_file(params)

    if command == "search":
        return tool_search_files(params)

    if command == "list":
        return tool_list_dir(params)

    return {"error": f"Unknown files command '{command}'"}


# ------------------------------------------------------------
# Metadata (optional, used by MCP discovery)
# ------------------------------------------------------------

TOOL_META = {
    "tool_read_file": {
        "description": "Reads a file",
        "params": {"path": "string"},
        "returns": "File contents",
        "category": "files",
        "examples": ["mcp_read_file path=/etc/hosts"]
    },
    "tool_search_files": {
        "description": "Searches for files containing a term",
        "params": {"root": "string", "term": "string"},
        "returns": "List of matching files",
    },
    "tool_list_dir": {
        "description": "Lists files in a directory",
        "params": {"path": "string"},
        "returns": "List of files",
    }
}
