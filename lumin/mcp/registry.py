# lumin/mcp/registry.py

class MCPRegistry:
    """
    Stores MCP tool metadata and exposes them to the tool router.
    """

    def __init__(self):
        self.tools = {}

    def register_tools(self, tool_list):
        """
        Add MCP tools discovered from the server.
        """
        for tool in tool_list:
            self.tools[tool["name"]] = tool

    def get_tool(self, name):
        return self.tools.get(name)

