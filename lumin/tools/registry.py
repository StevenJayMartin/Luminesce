# lumin/tools/registry.py

from lumin.tools.wikipedia import wikipedia_search
from lumin.tools.weather_api import weather_api
from lumin.tools.web_search import web_search

TOOLS = {
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
