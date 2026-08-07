# lumin/mcp/client.py

class MCPClient:
    """
    Manages connection to MCP servers.
    Handles startup, shutdown, reconnection, and discovery.
    """

    def __init__(self, transport):
        self.transport = transport
        self.tools = {}

    async def connect(self):
        """
        Establish connection to MCP server.
        """
        # TODO: open pipes / sockets / stdio
        pass

    async def disconnect(self):
        """
        Close connection.
        """
        pass

    async def discover(self):
        """
        Run MCP discovery (get_tools, get_schema).
        """
        # TODO: call discovery module
        pass

