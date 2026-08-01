# lumin/tools/registry.py

from lumin.tools.wikipedia import wikipedia_search
from lumin.tools.weather_api import weather_api
from lumin.tools.web_search import web_search
from lumin.tools.chat_tool import chat_tool
from lumin.tools.list_tools import list_tools_tool

TOOLS = {
    "weather_api": weather_api,
    "web_search": web_search,
    "wikipedia_search": wikipedia_search,
    "list_tools": list_tools_tool,
    "chat_tool": chat_tool,
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
