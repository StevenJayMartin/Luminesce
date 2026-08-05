# lumin/tools/registry.py

from lumin.tools.wikipedia import wikipedia_search
from lumin.tools.weather_api import weather_api
from lumin.tools.web_search import web_search
from lumin.tools.chat_tool import chat_tool
from lumin.tools.list_tools import list_tools_tool
import requests

def rag_ingest(url: str, config=None):
    import requests

    if config is None:
        return {"error": "Config not provided to rag_ingest"}

    rag_url = config["rag"]["url"]
    base = rag_url.rsplit("/", 1)[0]  # strip /rag
    endpoint = f"{base}/ingest_url"

    try:
        resp = requests.post(endpoint, json={"url": url}, timeout=10)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

TOOLS = {
    "weather_api": weather_api,
    "web_search": web_search,
    "wikipedia_search": wikipedia_search,
    "list_tools": list_tools_tool,
    "chat_tool": chat_tool,
    "rag_ingest": rag_ingest,
}


def get(name: str):
    """Return a tool function by name."""
    return TOOLS.get(name)

def list_tools():
    """Return a list of all tools with names and descriptions."""
    return [
        {"name": name, "description": func.__doc__ or ""}
        for name, func in TOOLS.items()
    ]
