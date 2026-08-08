import sys
import subprocess
import os
import traceback

class MCPClient:
    def __init__(self, server_cmd, cwd=None):
        self.server_cmd = server_cmd
        self.cwd = cwd
        self.process = None
        
    async def start(self):
        print("\n=== MCP DEBUG START ===")

        # 1. Show raw server_cmd
        print("RAW server_cmd:", repr(self.server_cmd), "TYPE:", type(self.server_cmd))

        # 2. Normalize command
        if isinstance(self.server_cmd, str):
            cmd = self.server_cmd.split()
        else:
            cmd = list(self.server_cmd)

        print("NORMALIZED CMD LIST:", cmd)
        for i, part in enumerate(cmd):
            print(f"  CMD[{i}] =", repr(part))

        # 3. Show cwd
        print("CWD:", repr(self.cwd))
        print("CWD exists:", os.path.isdir(self.cwd) if self.cwd else "(None)")

        # 4. Show PATH and python resolution
        print("sys.executable:", sys.executable)
        print("PATH:", os.environ.get("PATH"))

        # 5. Show environment differences
        print("Working directory (os.getcwd()):", os.getcwd())

        # 6. Try a dry-run resolution
        try:
            resolved = shutil.which(cmd[0])
            print("shutil.which(cmd[0]):", resolved)
        except Exception as e:
            print("shutil.which ERROR:", e)

        print("Attempting subprocess.Popen...\n")

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
            print("=== MCP DEBUG END ===\n")

        except Exception as e:
            print("Popen FAILED:", e)
            print("TYPE:", type(e))
            print("TRACEBACK:")
            traceback.print_exc()
            print("=== MCP DEBUG END (FAILURE) ===\n")
            raise
