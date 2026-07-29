def route_intent(intent_json):
    """
    Decide which tool to call based on the LLM's intent JSON.
    Returns: (tool_name, tool_args)
    """

    if not isinstance(intent_json, dict):
        return None, {"error": "Invalid intent JSON"}

    intent = intent_json.get("intent", "").lower()

    # WEATHER
    if intent == "weather":
        return "weather_api", {
            "location": intent_json.get("location", "")
        }

    # SEARCH
    if intent == "search":
        return "duckduckgo_search", {
            "query": intent_json.get("query", "")
        }

    # KNOWLEDGE / WIKIPEDIA
    if intent == "knowledge":
        return "wikipedia_search", {
            "topic": intent_json.get("topic", "")
        }

    # FALLBACK
    return None, {"error": f"Unknown intent '{intent}'"}

