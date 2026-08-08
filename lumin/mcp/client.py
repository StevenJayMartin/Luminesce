# lumin/mcp/client.py

import asyncio
import subprocess
import sys
from pathlib import Path

from lumin.mcp.jsonrpc import JsonRpcClient
from lumin.mcp.discovery import MCPDiscovery
from lumin.mcp.executor import MCPExecutor


class MCPClient:
    """
    MCP Orchestrator:
    - Spawns MCP servers
    - Connects via pipes
    - Wraps JSON‑RPC transport
    - Loads tools via discovery
    - Exposes executor for tool calls
    """

    def __init__(self, server_cmd: str, cwd: str | None = None):
        self.server_cmd = server_cmd
        self.cwd = cwd or str(Path.cwd())

        self.process: subprocess.Popen | None = None
        self.rpc: JsonRpcClient | None = None
        self.discovery: MCPDiscovery | None = None
        self.executor: MCPExecutor | None = None

        self.tools: dict = {}  # tool_name → metadata

    async def start(self):
        """
        Spawn MCP server and connect streams.
        """
        if self.process:
            return  # already running

        # Spawn MCP server
        self.process = subprocess.Popen(
            self.server_cmd.split(),
            cwd=self.cwd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False  # raw bytes
        )

        if not self.process.stdout or not self.process.stdin:
            raise RuntimeError("Failed to open MCP server pipes")

        # Wrap pipes in asyncio streams
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, self.process.stdout)

        writer_transport, writer_protocol = await asyncio.get_event_loop().connect_write_pipe(
            asyncio.streams.FlowControlMixin, self.process.stdin
        )
        writer = asyncio.StreamWriter(writer_transport, writer_protocol, reader, asyncio.get_event_loop())

        # Create JSON‑RPC client
        self.rpc = JsonRpcClient(reader, writer)

        # Create discovery + executor
        self.discovery = MCPDiscovery(self.rpc)
        self.executor = MCPExecutor(self.rpc)

        # Load tools
        await self.load_tools()

    async def load_tools(self):
        """
        Load MCP tools via discovery.
        """
        if not self.discovery:
            raise RuntimeError("MCPDiscovery not initialized")

        raw_tools = await self.discovery.get_tools()
        schema = await self.discovery.get_schema()

        # Convert raw MCP tool definitions into your internal format
        for tool in raw_tools:
            name = tool.get("name")
            desc = tool.get("description", "")
            params = tool.get("parameters", {})

            self.tools[name] = {
                "name": name,
                "description": desc,
                "parameters": params,
                "schema": schema.get(name, {})
            }

    async def execute(self, tool_name: str, args: dict):
        """
        Execute an MCP tool via JSON‑RPC.
        """
        if not self.executor:
            raise RuntimeError("MCPExecutor not initialized")

        return await self.executor.execute(tool_name, args)

    async def stop(self):
        """
        Stop MCP server.
        """
        if self.process:
            self.process.terminate()
            try:
                await asyncio.sleep(0.1)
                self.process.kill()
            except Exception:
                pass

            self.process = None

    def list_tools(self):
        """
        Return MCP tool metadata.
        """
        return self.tools
