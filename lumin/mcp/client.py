import os
import sys
import json
import shutil
import subprocess
import traceback

class MCPClient:
    def __init__(self, server_cmd, cwd=None):
        self.server_cmd = server_cmd
        self.cwd = cwd
        self.process = None

    def send_jsonrpc_raw(self, req):
        if not self.process or self.process.poll() is not None:
            return {"error": "MCP server not running"}

        self.process.stdin.write((json.dumps(req) + "\n").encode())
        self.process.stdin.flush()

        raw = self.process.stdout.readline().decode().strip()
        return json.loads(raw)

    def run_command(self, command: str):
        return self.call_tool(command)

    def call_tool(self, command: str):
        if not self.process or self.process.poll() is not None:
            return {"error": "MCP server not running"}

        try:
            self.process.stdin.write((command + "\n").encode())
            self.process.stdin.flush()

            raw = self.process.stdout.readline().decode().strip()
            if not raw:
                return {"error": "Empty response from MCP server"}

            try:
                return json.loads(raw.replace("'", '"'))
            except Exception:
                return {"result": raw}

        except Exception as e:
            return {"error": str(e)}

    async def start(self):
        print("\n=== MCP DEBUG START ===")

        if isinstance(self.server_cmd, str):
            cmd = self.server_cmd.split()
        else:
            cmd = list(self.server_cmd)

        print("CMD:", cmd)
        print("CWD:", self.cwd)

        try:
            self.process = subprocess.Popen(
                cmd,
                cwd=self.cwd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False,
                shell=True if sys.platform == "win32" else False
            )
            print("Popen SUCCESS — process started.")

            ready = self.process.stdout.readline().decode().strip()
            print("SERVER READY LINE:", ready)

            print("=== MCP DEBUG END ===\n")

        except Exception as e:
            print("Popen FAILED:", e)
            traceback.print_exc()
            print("=== MCP DEBUG END (FAILURE) ===\n")
            raise

    def stop(self):
        if self.process:
            try:
                self.process.terminate()
            except Exception:
                pass
            self.process = None


# ------------------------------------------------------------
# GLOBAL INSTANCE — THIS IS THE ONE YOU SHOULD USE
# ------------------------------------------------------------
mcp_client = MCPClient(
    server_cmd=[
        sys.executable,
        os.path.join(os.path.dirname(__file__), "mcp_server.py")
    ],
    cwd=os.path.dirname(__file__)
)
