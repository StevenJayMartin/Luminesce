# TUI (Textual Interface)

Luminesce includes a full terminal UI built with Textual.

---

## Features

- Streaming LLM output  
- Push‑to‑Talk  
- Chat history  
- Tool call visualization  
- MCP integration  
- RAG ingestion/query  

---

## Running

```
python -m lumin.ui.tui
```

---

## Commands

- `ingest <url>`
- `mcp_rpc <json>`
- Natural language queries

```
ui/tui
(venv) PS C:\HOME_Scripts\Luminesce> ...
python -m lumin.main --model="mistral:7b" --llm-mode=chat --config="lumin/config.json"

```
