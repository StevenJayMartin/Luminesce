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
    intent = intent_json.get("intent")

    # Extract args if present
    args = intent_json.get("args") or {k: v for k, v in intent_json.items() if k != "intent"}

    # Custom intent: get_weather
    
    
    if intent == "get_weather":
        cleaned = (
            user_message.lower()
            .replace("what's the weather in", "")
            .replace("whats the weather in", "")
            .replace("what is the weather in", "")
            .replace("weather in", "")
            .replace("right now", "")
            .replace("please", "")
            .strip()
        )
        return "weather_api", {"location": cleaned}
    
    if intent in MCP_TOOLS:
        return intent, args

    if intent in LEGACY_TOOLS:
        return LEGACY_TOOLS[intent], args

    return "chat_tool", {"message": user_message}
