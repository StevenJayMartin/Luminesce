import json
from lumin.mcp.registry import MCP_TOOLS

# Legacy tool names
LEGACY_TOOLS = {
    "weather": "weather_api",
    "web": "web_search",
    "wiki": "wikipedia_search",
    "rag_ingest": "rag_ingest",
    "rag_query": "rag_query",
    "chat": "chat_tool",
    "list": "list_tools",
    "list_tools": "list_tools",   # ⭐ FIXED
}

def route_intent(intent_json, user_message):
    """
    Hybrid-mode intent router.
    Supports both legacy tools and MCP tools.
    """

    intent = intent_json.get("intent")
    args = intent_json.get("args", {})

    # ------------------------------------------------------------
    # MCP tool routing
    # ------------------------------------------------------------
    if intent in MCP_TOOLS:
        return intent, args

    # ------------------------------------------------------------
    # Legacy tool routing
    # ------------------------------------------------------------
    if intent in LEGACY_TOOLS:
        return LEGACY_TOOLS[intent], args

    # ------------------------------------------------------------
    # Fallback: no tool
    # ------------------------------------------------------------
    return "chat_tool", {"message": user_message}
