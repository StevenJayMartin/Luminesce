from .registry import register
from .web_search import web_search

# Register all tools here
register("web_search", web_search)
