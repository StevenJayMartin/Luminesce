# lumin/tools/wikipedia.py

import requests
import urllib.parse

def wikipedia_search(topic: str, config=None) -> dict:
    """
    Fetch a summary for a topic from Wikipedia REST API.
    Returns a dict with title, description, extract, url or an error.
    """
    base = "https://en.wikipedia.org/api/rest_v1/page/summary/"
    encoded = urllib.parse.quote(topic, safe="")
    url = base + encoded

    headers = {
        "User-Agent": "LuminApp/1.0 (https://example.com; contact@example.com)"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=5)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return {"error": f"Wikipedia error: {e}"}

    if resp.status_code == 404 or "title" not in data:
        return {"error": f"Topic '{topic}' not found on Wikipedia."}

    return {
        "title": data.get("title", ""),
        "description": data.get("description", ""),
        "extract": data.get("extract", ""),
        "url": data.get("content_urls", {})
                 .get("desktop", {})
                 .get("page", ""),
    }
