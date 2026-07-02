import requests

def duckduckgo_search(query: str):
    url = "https://api.duckduckgo.com/"
    params = {
        "q": query,
        "format": "json",
        "no_redirect": 1,
        "no_html": 1,
    }

    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()

    results = []

    if data.get("AbstractText"):
        results.append({
            "title": data.get("Heading", ""),
            "snippet": data.get("AbstractText", ""),
            "url": data.get("AbstractURL", ""),
        })

    for item in data.get("RelatedTopics", []):
        if isinstance(item, dict) and "Text" in item:
            results.append({
                "title": item.get("Text", ""),
                "snippet": item.get("Text", ""),
                "url": item.get("FirstURL", ""),
            })

    return results[:3]
