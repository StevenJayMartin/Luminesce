# lumin/tools/registry.py

from .duckduckgo_search import duckduckgo_search
from .wikipedia import wikipedia_search
from lumin.tools.weather_api import weather_api
from lumin.tools.web_search import web_search

TOOLS = {
    "duckduckgo_search": duckduckgo_search,   # optional legacy
    "wikipedia_search": wikipedia_search,
    "weather_api": weather_api,
    "web_search": web_search,
}

def get(name: str):
    return TOOLS.get(name)

def list_tools():
    return [
        {"name": name, "description": func.__doc__ or ""}
        for name, func in TOOLS.items()
    ]
