import requests
from bs4 import BeautifulSoup

# ------------------------------------------------------------
# Web operations
# ------------------------------------------------------------

def tool_http_get(params):
    url = params.get("url")
    if not url:
        return {"error": "Missing 'url' parameter"}

    try:
        r = requests.get(url)
        return {
            "status": r.status_code,
            "text": r.text
        }
    except Exception as e:
        return {"error": str(e)}

def tool_fetch_title(params):
    url = params.get("url")
    if not url:
        return {"error": "Missing 'url' parameter"}

    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.title.string if soup.title else None
        return {"title": title}
    except Exception as e:
        return {"error": str(e)}

# ------------------------------------------------------------
# MCP entrypoint
# ------------------------------------------------------------

def run(params):
    command = params.get("command")

    if command == "get":
        return tool_http_get(params)

    if command == "title":
        return tool_fetch_title(params)

    return {"error": f"Unknown web command '{command}'"}

# ------------------------------------------------------------
# Metadata
# ------------------------------------------------------------

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
