import asyncio
import json
import subprocess

class MCPExecutor:
    def __init__(self, server_cmd):
        self.server_cmd = server_cmd
        self.process = None

    async def start(self):
        # Start MCP server as subprocess
        self.process = await asyncio.create_subprocess_exec(
            *self.server_cmd.split(),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

    async def execute(self, tool_name, args):
        if not self.process:
            return {"error": "MCP server not running"}

        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": tool_name,
            "params": args,
        }

        # Send request
        self.process.stdin.write((json.dumps(request) + "\n").encode())
        await self.process.stdin.drain()

        # Read response
        line = await self.process.stdout.readline()
        if not line:
            return {"error": "No response from MCP server"}

        try:
            return json.loads(line.decode())
        except Exception as e:
            return {"error": f"Invalid MCP response: {e}"}

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process = None
