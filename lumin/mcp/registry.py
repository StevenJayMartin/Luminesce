# lumin/mcp/registry.py

"""
MCP Tool Registry

This module stores MCP tools discovered at runtime.
It mirrors the structure of the local tool registry, but keeps MCP tools
separate so the TUI can merge them cleanly without circular imports.
"""

# Dictionary of MCP tools:
# key: tool name (str)
# value: metadata dict from MCP discovery
MCP_TOOLS = {}


def register_mcp_tools(tools: dict):
    """
    Register MCP tools discovered from an MCP server.

    tools: dict mapping tool_name → metadata
    """
    global MCP_TOOLS

    for name, meta in tools.items():
        MCP_TOOLS[name] = meta


def get(name: str):
    """
    Retrieve MCP tool metadata by name.
    Returns None if the tool is not an MCP tool.
    """
    return MCP_TOOLS.get(name)


def list_tools():
    """
    Return a list of MCP tools formatted like local tools:
    [
        {"name": "...", "description": "..."},
        ...
    ]
    """
    return [
        {
            "name": name,
            "description": meta.get("description", "")
        }
        for name, meta in MCP_TOOLS.items()
    ]
