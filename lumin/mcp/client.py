import os
import sys
import json
import subprocess
import traceback


class MCPClient:
    """
    JSON‑RPC MCP client compatible with Python 3.14 and Windows.
    Uses text-mode pipes to avoid byte-buffering deadlocks.
    """

    def __init__(self, server_cmd, cwd=None):
        self.server_cmd = server_cmd
        self.cwd = cwd
        self.process = None
        self._next_id = 1

    # ------------------------------------------------------------
    # JSON‑RPC ID generator
    # ------------------------------------------------------------
    def _id(self):
        val = self._next_id
        self._next_id += 1
        return val

    # ------------------------------------------------------------
    # Send JSON‑RPC request and read response
    # ------------------------------------------------------------
    def send_jsonrpc_raw(self, req):
        if not self.process or self.process.poll() is not None:
            return {"error": "MCP server not running"}

        try:
            line = json.dumps(req) + "\n"
            self.process.stdin.write(line)
            self.process.stdin.flush()

            raw = self.process.stdout.readline().strip()
            if not raw:
                return {"error": "Empty response from MCP server"}

            try:
                return json.loads(raw)
            except Exception:
                return {"error": f"Invalid JSON from MCP server: {raw}"}

        except Exception as e:
            return {"error": str(e)}

    # ------------------------------------------------------------
    # Legacy passthrough (non‑JSON‑RPC)
    # ------------------------------------------------------------
    def run_command(self, command: str):
        return self.call_tool(command)

    def call_tool(self, command: str):
        if not self.process or self.process.poll() is not None:
            return {"error": "MCP server not running"}

        try:
            self.process.stdin.write(command + "\n")
            self.process.stdin.flush()

            raw = self.process.stdout.readline().strip()
            if not raw:
                return {"error": "Empty response from MCP server"}

            try:
                return json.loads(raw.replace("'", '"'))
            except Exception:
                return {"result": raw}

        except Exception as e:
            return {"error": str(e)}

    # ------------------------------------------------------------
    # JSON‑RPC tool execution (used by ui_app.py)
    # ------------------------------------------------------------
    def execute(self, name, params):
        if not self.process or self.process.poll() is not None:
            return {"error": "MCP server not running"}

        req = {
            "jsonrpc": "2.0",
            "id": self._id(),
            "method": "call_tool",
            "params": {
                "name": name,
                "params": params
            }
        }

        return self.send_jsonrpc_raw(req)

    # ------------------------------------------------------------
    # Start MCP server process
    # ------------------------------------------------------------
    async def start(self):
        print("\n=== MCP DEBUG START ===")

        # Normalize command
        if isinstance(self.server_cmd, str):
            cmd = self.server_cmd.split()
        else:
            cmd = list(self.server_cmd)

        print("CMD:", cmd)
        print("CWD:", self.cwd)

        try:
            # CRITICAL FIX: text=True + encoding="utf-8"
            self.process = subprocess.Popen(
                cmd,
                cwd=self.cwd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                shell=False
            )
            print("Popen SUCCESS — process started.")

            # Read ready handshake
            ready = self.process.stdout.readline().strip()
            print("SERVER READY LINE:", ready)

            try:
                msg = json.loads(ready)
                if msg.get("method") != "ready":
                    print("WARNING: MCP server did not send ready event")
            except Exception:
                print("WARNING: MCP server sent non‑JSON ready line")

            print("=== MCP DEBUG END ===\n")

        except Exception as e:
            print("Popen FAILED:", e)
            traceback.print_exc()
            print("=== MCP DEBUG END (FAILURE) ===\n")
            raise

    # ------------------------------------------------------------
    # Stop MCP server
    # ------------------------------------------------------------
    def stop(self):
        if self.process:
            try:
                self.process.terminate()
            except Exception:
                pass
            self.process = None


# ------------------------------------------------------------
# GLOBAL INSTANCE — used by ui_app.py
# ------------------------------------------------------------
mcp_client = MCPClient(
    server_cmd=[
        sys.executable,
        os.path.join(os.path.dirname(__file__), "mcp_server.py")
    ],
    cwd=os.path.dirname(__file__)
)
