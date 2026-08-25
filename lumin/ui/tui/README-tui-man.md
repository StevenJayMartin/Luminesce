# LUMIN(1) — Lumin Text User Interface Manual

## NAME
**lumin** — interactive text‑user‑interface for chat, tools, RAG, and MCP integration.

---

## SYNOPSIS

```
python -m lumin.main --llm-mode=chat --config="lumin/config.json" --model="phi3:medium"
```

Launches the Lumin TUI, providing chat interaction, tool execution, RAG operations, and MCP tool access.

---

## DESCRIPTION

The **Lumin TUI** is a text‑based interface for interacting with the Lumin assistant.  
It supports:

- Natural language chat  
- Local tool execution  
- RAG ingestion and querying  
- MCP (Model Context Protocol) tools  
- Voice input (Push‑to‑Talk or wake‑word mode)  
- Raw JSON‑RPC commands  

The interface displays:

- MCP status line  
- Scrollable chat history  
- Input box  
- Push‑to‑Talk button  

---

## STARTUP

On launch, Lumin displays:

```
🔄 Loading MCP server…
🔌 MCP Connected
🔧 MCP Tools Loaded: N
Connected to Lumin
```

If MCP is disabled in `config.json`, the status line shows:

```
⚠ MCP client missing
```

---

## CONFIGURATION

### MCP
Enabled only if `config.json` contains:

```json
"mcp": {
  "server_cmd": "python lumin/mcp/test_server.py"
}
```

If `"server_cmd"` is missing or empty, MCP is disabled.

### RAG
Configured separately:

```json
"rag": {
  "enabled": true,
  "url": "http://<host>:8001/rag"
}
```

---

## INTERACTION

### Basic Chat
Type any message:

```
hello lumin
tell me a joke
explain quantum tunneling
```

If no tool is triggered, Lumin responds via `chat_tool`.

---

## TOOL INVOCATION

Tools are triggered automatically via intent detection or manually via commands.

### Local Tools

| Tool | Trigger | Example |
|------|---------|---------|
| `weather_api` | “weather”, “forecast”, “weather in X” | `weather in Richmond` |
| `web_search` | “search X”, “lookup X” | `search python decorators` |
| `wikipedia_search` | “wiki X”, “wikipedia X” | `wiki Heisenberg uncertainty` |
| `rag_ingest` | `ingest <url>` | `ingest https://example.com/doc.pdf` |
| `rag_query` | “ask rag”, “query rag” | `query rag about quantum computing` |
| `chat_tool` | fallback small talk | `tell me a joke` |
| `list_tools` | “list tools”, “what tools exist” | `list_tools` |

---

## LISTING TOOLS

```
list_tools
```

Displays both local and MCP tools:

```
🧰 Available Tools:
• weather_api
• wikipedia_search
• rag_ingest
• rag_query
• ai
• files
• system
• util
• web
```

---

## MCP INTERACTION

### List MCP tools

```
mcp_rpc {"jsonrpc": "2.0", "id": 1, "method": "get_tools"}
```

### Call an MCP tool

```
mcp_rpc {
  "jsonrpc": "2.0",
  "id": 2,
  "method": "call_tool",
  "params": {
    "name": "files",
    "params": {"path": "."}
  }
}
```

### Notes
- MCP tools are discovered at startup.
- MCP routing is automatic if intent matches an MCP tool name.

---

## VOICE MODE

### Push‑to‑Talk
Click:

```
Push to Talk
```

### Wake‑Word Mode
Enabled via config:

```json
"voice": { "listen_mode": "always" }
```

Flow:

1. Wake word detected  
2. Lumin says “I’m listening.”  
3. STT captures speech  
4. Intent → tool → response  

---

## RAW JSON‑RPC MODE

Send any JSON‑RPC payload:

```
mcp_rpc { ... }
```

Errors are displayed inline.

---

## DEBUGGING

### Inspect routing
Send:

```
{"intent": "weather"}
```

### Inspect MCP
```
mcp_rpc {"jsonrpc": "2.0", "id": 1, "method": "get_tools"}
```

### Inspect RAG
```
ingest <url>
```

---

## EXIT

Press:

```
Ctrl+C
Ctrl+Q
```

Or type:

```
quit
```

---

## FILES

```
lumin/state/chat.json     Chat history
lumin/tools/              Local tool implementations
lumin/mcp/                MCP client + registry
lumin/ui/tui/ui_app.py    TUI implementation
```

---

## AUTHOR

Lumin — local‑first AI assistant with TUI, Web UI, RAG, and MCP support.

---

## COPYRIGHT

© You — this is your project.
