import requests

def duckduckgo_search(query: str):
    query = " ".join(query.split())
    url = "https://api.duckduckgo.com/"
    params = {"q": query, "format": "json", "no_redirect": 1, "no_html": 1}

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        results = []

        # Main abstract
        if data.get("AbstractText"):
            results.append({
                "title": data.get("Heading", "Result"),
                "snippet": data["AbstractText"]
            })

        # Related topics
        for topic in data.get("RelatedTopics", []):
            if isinstance(topic, dict) and topic.get("Text"):
                results.append({
                    "title": topic.get("FirstURL", "Link"),
                    "snippet": topic["Text"]
                })

        return results if results else [{"title": "No results", "snippet": ""}]

    except Exception as e:
        return [{"title": "Error", "snippet": str(e)}]

