#!/usr/bin/env python3
import sys
import json
import time

# ------------------------------------------------------------
# Tool Registry
# ------------------------------------------------------------
TOOLS = {}

def register_tool(name, func):
    TOOLS[name] = func

def tool_mcp_time(params):
    return time.time()

def tool_mcp_echo(params):
    return params.get("message", "")

def tool_mcp_add(params):
    return params["a"] + params["b"]

register_tool("mcp_time", tool_mcp_time)
register_tool("mcp_echo", tool_mcp_echo)
register_tool("mcp_add", tool_mcp_add)

# ------------------------------------------------------------
# JSON-RPC helpers
# ------------------------------------------------------------
def send(obj):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()

def read():
    line = sys.stdin.readline()
    if not line:
        return None
    try:
        return json.loads(line)
    except:
        return None

# ------------------------------------------------------------
# JSON-RPC dispatcher
# ------------------------------------------------------------
def handle_request(req):
    if "id" not in req:
        return

    method = req.get("method")
    params = req.get("params", {})

    # Discovery
    if method == "get_tools":
        return {
            "jsonrpc": "2.0",
            "id": req["id"],
            "result": list(TOOLS.keys())
        }

    # Tool execution
    if method == "call_tool":
        tool_name = params.get("name")
        tool_params = params.get("params", {})

        if tool_name not in TOOLS:
            return {
                "jsonrpc": "2.0",
                "id": req["id"],
                "error": f"Unknown tool '{tool_name}'"
            }

        try:
            result = TOOLS[tool_name](tool_params)
            return {
                "jsonrpc": "2.0",
                "id": req["id"],
                "result": result
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req["id"],
                "error": str(e)
            }

    # Unknown method
    return {
        "jsonrpc": "2.0",
        "id": req["id"],
        "error": f"Unknown method '{method}'"
    }

# ------------------------------------------------------------
# Main loop
# ------------------------------------------------------------
def main():
    send({"jsonrpc": "2.0", "method": "ready", "params": {}})

    while True:
        req = read()
        if req is None:
            break

        resp = handle_request(req)
        if resp:
            send(resp)

if __name__ == "__main__":
    main()
