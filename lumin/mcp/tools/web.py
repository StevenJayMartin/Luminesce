
import requests
from bs4 import BeautifulSoup

def tool_http_get(params):
    url = params.get("url")
    r = requests.get(url)
    return {
        "status": r.status_code,
        "text": r.text
    }

def tool_fetch_title(params):
    url = params.get("url")
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    title = soup.title.string if soup.title else None
    return {"title": title}

TOOL_META = {
    "tool_http_get": {
        "description": "Fetches a URL via HTTP GET",
        "params": {"url": "string"},
        "returns": "HTTP status + body",
        "category": "web",
        "examples": []
    },
    "tool_fetch_title": {
        "description": "Extracts the <title> from a webpage",
        "params": {"url": "string"},
        "returns": "Page title",
        "category": "web",
        "examples": []
    }
}
