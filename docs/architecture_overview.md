# Architecture Overview

Luminesce is composed of several subsystems working together.

---

## Diagram

```
User → TUI/Web UI → LLM → Intent Router → Tool Registry → (Local Tools / RAG / MCP)
```

---

## Components

### TUI
Terminal interface using Textual.

### Web UI
Browser interface using FastAPI + WebSockets.

### LLM
Local model for intent extraction and conversation.

### Intent Router
Maps LLM JSON output to tool calls.

### Tool Registry
Unified registry for:
- Local tools
- RAG tools
- MCP tools

### RAG Server
Document ingestion + vector search.

### MCP Server
JSON‑RPC subprocess providing external tools.

### STT (Vosk)
Speech‑to‑text engine.

### TTS (Piper)
Text‑to‑speech engine.

---

## Data Flow

1. User sends text or voice.
2. LLM extracts intent.
3. Router selects tool.
4. Tool executes (local, RAG, or MCP).
5. Results returned to LLM.
6. LLM generates final answer.
7. UI displays response.

---

This architecture allows Luminesce to be fully local, modular, and extensible.

