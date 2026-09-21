⭐ MCP TEST SUITE (raw JSON‑RPC)
Copy/paste each line into your TUI exactly as‑is.

1. UTIL TOOL
UUID
Code
mcp_rpc {"jsonrpc":"2.0","id":101,"method":"call_tool","params":{"name":"util","params":{"command":"uuid"}}}
Timestamp
Code
mcp_rpc {"jsonrpc":"2.0","id":102,"method":"call_tool","params":{"name":"util","params":{"command":"timestamp"}}}
2. FILES TOOL
List directory
Code
mcp_rpc {"jsonrpc":"2.0","id":201,"method":"call_tool","params":{"name":"files","params":{"command":"list","path":"."}}}
Read a file
Code
mcp_rpc {"jsonrpc":"2.0","id":202,"method":"call_tool","params":{"name":"files","params":{"command":"read","path":"./README.md"}}}
Search for files
Code
mcp_rpc {"jsonrpc":"2.0","id":203,"method":"call_tool","params":{"name":"files","params":{"command":"search","root":".","term":"json"}}}
3. SYSTEM TOOL
System info
Code
mcp_rpc {"jsonrpc":"2.0","id":301,"method":"call_tool","params":{"name":"system","params":{"command":"info"}}}
CPU load
Code
mcp_rpc {"jsonrpc":"2.0","id":302,"method":"call_tool","params":{"name":"system","params":{"command":"cpu"}}}
Disk usage
Code
mcp_rpc {"jsonrpc":"2.0","id":303,"method":"call_tool","params":{"name":"system","params":{"command":"disk"}}}
4. WEB TOOL
HTTP GET
Code
mcp_rpc {"jsonrpc":"2.0","id":401,"method":"call_tool","params":{"name":"web","params":{"command":"get","url":"https://example.com"}}}
Fetch page title
Code
mcp_rpc {"jsonrpc":"2.0","id":402,"method":"call_tool","params":{"name":"web","params":{"command":"title","url":"https://example.com"}}}
5. AI TOOL
Embed text
Code
mcp_rpc {"jsonrpc":"2.0","id":501,"method":"call_tool","params":{"name":"ai","params":{"command":"embed","text":"hello world"}}}
⭐ MCP TEST SUITE (natural‑language routing)
These test your intent model, router, MCP dispatch, and continuation model all at once.

UTIL
Code
Use MCP util to generate a UUID
Code
Ask MCP util for a timestamp
FILES
Code
Use MCP files to list the current directory
Code
Use MCP files to read README.md
Code
Search for files containing 'json' using MCP files
SYSTEM
Code
Use MCP system to show system info
Code
Use MCP system to show CPU load
Code
Use MCP system to show disk usage
WEB
Code
Use MCP web to fetch https://example.com
Code
Use MCP web to get the title of https://example.com
AI
Code
Use MCP ai to embed the text hello world