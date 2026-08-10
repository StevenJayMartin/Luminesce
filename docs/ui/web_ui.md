# Web UI

Luminesce includes a browser‑based UI.

---

## Running

```
python -m lumin.ui.web
```

---

## Features

- Chat interface  
- Tool results  
- RAG integration  
- MCP integration  

```
ui/web
(venv) sjm@pop-os:~/Luminesce$ ...
uvicorn lumin.ui.web.app:app --host 0.0.0.0 --port 8000
```
