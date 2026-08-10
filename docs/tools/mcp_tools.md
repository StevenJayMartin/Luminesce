# MCP Tools

MCP tools are executed via a JSON‑RPC subprocess.

---

## How MCP Works

- Luminesce launches `mcp_server.py` as a subprocess.
- Communication uses JSON‑RPC over stdin/stdout.
- Tools are registered inside the MCP server.

---

## Built‑in MCP Tools

### mcp_time
Returns system time.

### mcp_echo
Echoes a message.

### mcp_add
Adds two numbers.

---

## JSON‑RPC Methods

### get_tools

Returns list of available MCP tools.

### call_tool

Executes a tool:

```
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "call_tool",
  "params": {
    "name": "mcp_time",
    "params": {}
  }
}
```

---

## Adding New MCP Tools

Edit `mcp_server.py`:

```python
def tool_new(params):
    return "Hello"

register_tool("new_tool", tool_new)
```

