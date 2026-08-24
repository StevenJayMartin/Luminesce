import os

def tool_read_file(params):
    path = params.get("path")
    with open(path, "r") as f:
        return {"content": f.read()}

def tool_search_files(params):
    root = params.get("root")
    term = params.get("term")
    matches = []
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if term in f:
                matches.append(os.path.join(dirpath, f))
    return {"matches": matches}

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
    }
}