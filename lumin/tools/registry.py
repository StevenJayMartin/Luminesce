from .duckduckgo_search import duckduckgo_search
from .wikipedia import wikipedia_search
from lumin.tools.weather_api import weather_api
from lumin.tools.router import route_intent


TOOLS = {
    "duckduckgo_search": duckduckgo_search,
    "wikipedia_search": wikipedia_search,
    "weather_api": weather_api,
}

def get(name: str):
    return TOOLS.get(name)

