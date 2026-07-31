# lumin/tools/router.py

def route_intent(intent_json):
    """
    Decide which tool to call based on the LLM's intent JSON.
    Returns: (tool_name, tool_args)
    """

    if not isinstance(intent_json, dict):
        return None, {"error": "Invalid intent JSON"}

    intent = intent_json.get("intent", "").lower()

    if intent == "weather":
        return "weather_api", {
            "location": intent_json.get("location", "")
        }

    if intent == "search":
        return "web_search", {
            "query": intent_json.get("query", "")
        }

    if intent == "knowledge":
        return "wikipedia_search", {
            "topic": intent_json.get("topic", "")
        }

    if intent == "list_tools":
        return "list_tools", {}

    return None, {"error": f"Unknown intent '{intent}'"}
