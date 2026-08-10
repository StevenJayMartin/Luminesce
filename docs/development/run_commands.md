# Run Commands

Useful commands for development.

---

## Run TUI

```
python -m lumin.ui.tui
```

## Run Web UI

```
python -m lumin.ui.web
```

## Run RAG Server

```
python -m lumin.rag.server
```

## Run MCP Server Manually

```
python lumin/mcp/mcp_server.py
```
### Example
```
ui/tui
(venv) PS C:\HOME_Scripts\Luminesce> ...
python -m lumin.main --model="mistral:7b" --llm-mode=chat --config="lumin/config.json"

ui/web
(venv) sjm@pop-os:~/Luminesce$ ...
uvicorn lumin.ui.web.app:app --host 0.0.0.0 --port 8000
```
