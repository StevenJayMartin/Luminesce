# lumin/mcp/discovery.py

class MCPDiscovery:
    """
    Handles MCP tool + schema discovery.
    """

    def __init__(self, transport):
        self.transport = transport

    async def get_tools(self):
        """
        Call MCP get_tools.
        """
        # TODO: JSON-RPC call
        return []

    async def get_schema(self):
        """
        Call MCP get_schema.
        """
        # TODO: JSON-RPC call
        return {}

