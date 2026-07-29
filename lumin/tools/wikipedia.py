import requests
import urllib.parse

def wikipedia_search(topic: str):
    formatted = topic.replace(" ", "_")
    encoded = urllib.parse.quote(formatted)

    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"

    headers = {
        "User-Agent": "LuminAI/1.0 (https://localhost)"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=5)

        # Try to parse JSON
        try:
            data = resp.json()
        except ValueError:
            # Wikipedia returned HTML or text instead of JSON
            return {
                "error": "Non-JSON response from Wikipedia",
                "raw": resp.text,
                "title": "",
                "description": "",
                "extract": "",
                "url": ""
            }

        # If JSON is not a dict, also fail gracefully
        if not isinstance(data, dict):
            return {
                "error": "Wikipedia returned unexpected JSON format",
                "raw": data,
                "title": "",
                "description": "",
                "extract": "",
                "url": ""
            }

        # Now it's safe to use .get()
        return {
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "extract": data.get("extract", ""),
            "url": data.get("content_urls", {}).get("desktop", {}).get("page", "")
        }

    except Exception as e:
        return {
            "error": str(e),
            "title": "",
            "description": "",
            "extract": "",
            "url": ""
        }
