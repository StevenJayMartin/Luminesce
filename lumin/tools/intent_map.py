INTENT_MAP = {
    "search": "web_search",
    "search news": "web_search",
    "web": "web_search",

    "weather": "weather_api",
    "wikipedia": "wikipedia_search",

    "rag": "rag_query",
    "rag ingest": "rag_ingest",

    "list tools": "list_tools",
    "chat tool": "chat_tool",
}

def map_intent(intent: str):
    return INTENT_MAP.get(intent)

