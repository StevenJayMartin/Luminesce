# lumin/tools/list_tools.py

def list_tools_tool():
    """
    Returns a list of all available tools and their descriptions.
    Used for tool discovery and debugging.
    """
    from lumin.tools.registry import list_tools
    return {"tools": list_tools()}
