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
    # Weather intent (custom)
    # ------------------------------------------------------------
    if intent == "weather":
        location = intent_json.get("location") or args.get("location") or user_message

        import re
        # Fix merged tokens like "BumpassVirginia" → "Bumpass Virginia"
        location = re.sub(r"([a-z])([A-Z])", r"\1 \2", location)

        # Fix missing spaces after commas
        location = location.replace(",", ", ")

        # Collapse double spaces
        location = re.sub(r"\s{2,}", " ", location).strip()

        return "weather_api", {"location": location}

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
    # Fallback: always provide a valid message
    # ------------------------------------------------------------
    fallback_message = (
        intent_json.get("message")
        or intent_json.get("location")
        or user_message
        or "continue"
    )

    return "chat_tool", {"message": fallback_message}
