# lumin/mcp/discovery.py

class MCPDiscovery:
    """
    Handles MCP tool + schema discovery.
    """

    def __init__(self, rpc_client):
        self.rpc = rpc_client

    async def get_tools(self) -> list:
        """
        Call MCP get_tools and return the raw list.
        """
        resp = await self.rpc.send_request("get_tools")
        return resp.get("result", {}).get("tools", [])

    async def get_schema(self) -> dict:
        """
        Call MCP get_schema and return the raw schema.
        """
        resp = await self.rpc.send_request("get_schema")
        return resp.get("result", {})
