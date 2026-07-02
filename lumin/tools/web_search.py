# lumin/tools/web_search.py
import requests

def web_search(query: str) -> str:
    """
    Simple DuckDuckGo Instant Answer search.
    Returns a short summary string for the model to reason over.
    """
    url = "https://api.duckduckgo.com/"
    params = {
        "q": query,
        "format": "json",
        "no_redirect": 1,
        "no_html": 1,
    }

    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return f"Web search error: {e}"

    abstract = data.get("AbstractText")
    if abstract:
        return abstract

    related = data.get("RelatedTopics", [])
    for item in related:
        if isinstance(item, dict) and "Text" in item:
            return item["Text"]

    return "No results found from DuckDuckGo."


# Register this tool with the global registry
from lumin.tools.registry import register
register("web_search", web_search)
