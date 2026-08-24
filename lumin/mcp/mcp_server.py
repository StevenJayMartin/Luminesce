#!/usr/bin/env python3
"""
MCP Server — JSON‑RPC compliant
All debug output goes to stderr.
Only JSON‑RPC messages go to stdout.
"""

import sys
import os
import json
import pkgutil
import importlib
import traceback

# ------------------------------------------------------------
# Helper: debug printing to stderr
# ------------------------------------------------------------
def debug(msg):
    sys.stderr.write(str(msg) + "\n")
    sys.stderr.flush()

# ------------------------------------------------------------
# Startup diagnostics
# ------------------------------------------------------------
debug("=== MCP SERVER START ===")
debug(f"Executable: {sys.executable}")
debug(f"File: {__file__}")
debug(f"CWD: {os.getcwd()}")
debug(f"Initial sys.path: {sys.path}")

# ------------------------------------------------------------
# Add project root to sys.path
# ------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

debug(f"Patched sys.path: {sys.path}")
debug(f"Project root: {PROJECT_ROOT}")

# ------------------------------------------------------------
# Load MCP tools package
# ------------------------------------------------------------
try:
    import lumin.mcp.tools as tools_pkg
    debug("Imported lumin.mcp.tools successfully.")
except Exception as e:
    debug(f"ERROR: Failed to import lumin.mcp.tools: {e}")
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

# ------------------------------------------------------------
# Discover tool modules
# ------------------------------------------------------------
TOOLS = {}

debug("Discovering MCP tools...")

for loader, module_name, is_pkg in pkgutil.iter_modules(tools_pkg.__path__):
    debug(f"Loading tool module: {module_name}")
    try:
        module = importlib.import_module(f"lumin.mcp.tools.{module_name}")
        TOOLS[module_name] = module
        debug(f"✓ Loaded: {module_name}")
    except Exception as e:
        debug(f"✗ ERROR loading {module_name}: {e}")
        traceback.print_exc(file=sys.stderr)

debug(f"Tool discovery complete. Tools loaded: {list(TOOLS.keys())}")

# ------------------------------------------------------------
# JSON‑RPC send helper (stdout ONLY)
# ------------------------------------------------------------
def send(obj):
    try:
        line = json.dumps(obj)
        sys.stdout.write(line + "\n")
        sys.stdout.flush()
    except Exception as e:
        debug(f"ERROR sending JSON: {e}")
        traceback.print_exc(file=sys.stderr)

# ------------------------------------------------------------
# Tool execution
# ------------------------------------------------------------
def call_tool(name, params):
    debug(f"call_tool invoked: {name} with params: {params}")

    if name not in TOOLS:
        return {"error": f"Unknown MCP tool '{name}'"}

    tool_module = TOOLS[name]

    try:
        if hasattr(tool_module, "run"):
            debug(f"Running tool '{name}' via run()")
            return tool_module.run(params)
        else:
            debug(f"Tool '{name}' has no run() function")
            return {"error": f"Tool '{name}' has no run() function"}
    except Exception as e:
        debug(f"ERROR executing tool '{name}': {e}")
        traceback.print_exc(file=sys.stderr)
        return {"error": str(e)}

# ------------------------------------------------------------
# READY HANDSHAKE (stdout)
# ------------------------------------------------------------
debug("Sending ready handshake...")
send({"jsonrpc": "2.0", "method": "ready", "params": {}})
debug("Ready handshake sent.")

# ------------------------------------------------------------
# MAIN JSON‑RPC LOOP
# ------------------------------------------------------------
debug("Entering JSON‑RPC loop...")

while True:
    try:
        raw = sys.stdin.readline()
        if not raw:
            debug("stdin closed — exiting MCP server.")
            break

        raw = raw.strip()
        debug(f"Received raw: {raw}")

        try:
            req = json.loads(raw)
        except Exception as e:
            debug(f"Invalid JSON received: {e}")
            traceback.print_exc(file=sys.stderr)
            continue

        method = req.get("method")
        rpc_id = req.get("id")

        debug(f"RPC method: {method}, id: {rpc_id}")

        if method == "get_tools":
            debug("Handling get_tools")
            send({"jsonrpc": "2.0", "id": rpc_id, "result": list(TOOLS.keys())})
            continue

        if method == "call_tool":
            params = req.get("params", {})
            name = params.get("name")
            tool_params = params.get("params", {})

            result = call_tool(name, tool_params)
            send({"jsonrpc": "2.0", "id": rpc_id, "result": result})
            continue

        debug(f"Unknown method: {method}")
        send({"jsonrpc": "2.0", "id": rpc_id, "error": "Unknown method"})

    except Exception as e:
        debug(f"FATAL MCP LOOP ERROR: {e}")
        traceback.print_exc(file=sys.stderr)

debug("=== MCP SERVER EXIT ===")
