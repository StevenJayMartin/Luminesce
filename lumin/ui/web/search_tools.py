import requests
import logging

log = logging.getLogger("search-tools")

def duckduckgo_search(query: str):
    try:
        resp = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_redirect": 1},
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()

        results = []
        for item in data.get("RelatedTopics", []):
            if "Text" in item:
                results.append({
                    "title": item.get("Text", ""),
                    "snippet": item.get("Text", "")
                })

        return results

    except Exception as e:
        log.error(f"DuckDuckGo search failed: {e}")
        return []
