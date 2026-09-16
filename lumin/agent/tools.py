# lumin/agent/tools.py

import asyncio
import json
from lumin.tools.registry import get as get_tool, list_tools
from lumin.mcp.registry import MCP_TOOLS

async def execute_tool(tool_name, tool_args, config=None, mcp_client=None):
    # MCP tool
    if tool_name in MCP_TOOLS and mcp_client:
        req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "call_tool",
            "params": {"name": tool_name, "params": tool_args},
        }
        return mcp_client.send_jsonrpc_raw(req)

    # Local tool
    tool = get_tool(tool_name)
    if not tool:
        return {"error": f"Unknown tool '{tool_name}'"}

    try:
        if asyncio.iscoroutinefunction(tool.__call__):
            return await tool(**tool_args)
        return tool(config=config, **tool_args)
    except Exception as e:
        return {"error": str(e)}


def format_tool_results(tool_name, results):
    return f"[{tool_name} returned]\n{json.dumps(results, indent=2)}\n"

