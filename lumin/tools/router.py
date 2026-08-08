# lumin/tools/router.py

def route_intent(intent_json, user_message: str, config=None`):
    """
    Decide which tool to call based on the LLM's intent JSON.
    Returns: (tool_name, tool_args)
    """

    if not isinstance(intent_json, dict):
        return None, {"error": "Invalid intent JSON"}

    intent = intent_json.get("intent", "").lower()

    message = user_message.lower()

    # Explicit override: rag_query
    if "rag_query" in message:
        return "rag_query", {
            "query": intent_json.get("query", ""),
            "session": intent_json.get("session", "default")
        }

    # Explicit override: rag_ingest
    if "rag_ingest" in message:
        return "rag_ingest", {
            "url": intent_json.get("url", ""),
            "config": intent_json.get("config", None)
        }

    # WEATHER
    if intent == "weather":
        return "weather_api", {
            "location": intent_json.get("location", "")
        }

    # SEARCH
    if intent == "search":
        return "web_search", {
            "query": intent_json.get("query", "")
        }

    # KNOWLEDGE / WIKIPEDIA
    if intent == "knowledge":
        return "wikipedia_search", {
            "topic": intent_json.get("topic", "")
        }

    # LIST TOOLS
    if intent == "list_tools":
        return "list_tools", {}

    # CHAT / SMALL TALK
    if intent == "chat":
        return "chat_tool", {
            "message": intent_json.get("message", "")
        }

    return None, {"error": f"Unknown intent '{intent}'"}
