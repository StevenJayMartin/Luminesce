<!-- LUMINESCE BANNER LOGO -->
![Luminesce banner](banner.svg)


# 🌌 Luminesce  
### *Enlightenment without heat — a fully local, multi‑modal AI assistant platform*

Luminesce is a **local‑first AI assistant platform** that blends voice, text, tools, RAG, MCP, and expressive UI into a single cohesive system.  
It’s designed for developers who want a *real* assistant architecture — not a toy demo, not a single‑file script, but a modular, extensible, multi‑modal AI stack.

Everything runs locally:  
**LLM, STT, TTS, RAG, Tools, TUI, Web UI, FastAPI, MCP.**  
No cloud. No telemetry. No hidden magic.

Just your machine. Your models. Your rules.

---

## 🌟 Philosophy: Enlightenment Without Heat

# Luminesce

Luminesce is a fully local AI assistant...
 
## Features

- **Local LLM** via Ollama  
- **RAG engine** for ingesting and querying documents  
- **MCP subsystem** for executing external tools via JSON‑RPC  
- **Voice input** using Vosk  
- **Voice output** using Piper  
- **Textual TUI** for terminal interaction  
- **Web UI** for browser interaction  
- **Unified tool registry** for local, RAG, and MCP tools  
- **Configurable personality, models, and tools**  

Luminesce is designed to be a self‑hosted personal assistant that runs entirely on your machine with no cloud dependencies.

## Quickstart

1. Install Python 3.10+
2. Install Ollama
3. Install Vosk model
4. Install Piper voice
5. Clone Luminesce
6. Run:

```
python -m lumin.ui.tui
```

or

```
python -m lumin.ui.web
```

---

## Documentation

See the `docs/` directory for:

- Getting Started  
- Architecture Overview  
- Tool Registry  
- RAG Tools  
- MCP Tools  
- Voice (STT/TTS)  
- UI (TUI/Web)  
- Performance Tuning  
- Web API  
- Development Guide  

---

## License

MIT


