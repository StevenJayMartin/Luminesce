# 🌌 Luminesce  
### *Enlightenment without heat — a fully local, multi‑modal AI assistant platform*

## Luminesce is a **local‑first AI system** that listens, speaks, thinks, retrieves, animates, and orchestrates tools — all on your machine.  
It’s built for developers who want a **real**, extensible assistant architecture rather than a toy demo.

## Everything runs locally:  
**LLM, STT, TTS, RAG, Tools, TUI, Web UI, FastAPI, MCP.**

## No cloud. No telemetry.  
Just your hardware, your models, your rules.

---

## 🌟 Vision: Enlightenment Without Heat

The name *Luminesce* reflects the project’s core idea:

> **Illumination without friction.  
> Intelligence without dependency.  
> Light without heat.**

Luminesce aims to feel alive, expressive, and helpful —  
yet cool, quiet, and fully under your control.

---

## ✨ What Luminesce Is

A unified AI assistant platform with:

- **Textual TUI** featuring a glowing bulb + filament meter  
- **Web UI** with streaming responses  
- **FastAPI backend** powering both UIs  
- **Local LLM inference** (Ollama, etc.)  
- **Offline STT** (Vosk)  
- **Offline TTS** (Piper / Ryan voice)  
- **RAG subsystem** (pluggable, optional)  
- **Tool system** (weather, search, OS control, custom tools)  
- **MCP integration**  
- **Config-driven architecture**  
- **Distributed multi-node support**  
- **Wake words, stop words, listen-again words**  
- **Voice command routing**  
- **Session memory**  
- **Model switching**  
- **GPU-aware backend**  

Luminesce is not a script.  
It’s a **platform**.

---

## 🚀 Why Developers Love Luminesce

- **Everything is modular** — STT, TTS, LLM, RAG, Tools, UI, backend  
- **Hackable architecture** — every subsystem is cleanly isolated  
- **Real agent behavior** — tool calls, intents, JSON routing  
- **Voice-native** — wake words, silence detection, push-to-talk  
- **Multi-modal** — text, voice, RAG, tools, UI  
- **Local-first** — privacy, speed, control  
- **Fun to extend** — animations, widgets, plugins, tools, models  

If you want to *build your own Copilot*, Luminesce is your playground.

---

## ⚡ Try It in 60 Seconds

```bash
git clone https://github.com/StevenJayMartin/Luminesce
cd Luminesce
pip install -r requirements.txt
python -m lumin.main
```

🧩 Tech Stack at a Glance
Python — core logic

Textual — TUI

FastAPI — backend

WebSockets — streaming UI

Vosk — STT

Piper — TTS

Ollama — LLM inference

MCP — tool orchestration

NumPy / SciPy — audio processing

SoundDevice — mic input

# 🛠️ Help Wanted (Great First Issues)
🎨 New bulb animations

🔧 New Textual widgets

🧠 New LLM tools (system control, search, OS integration)

🎤 Better wake-word detection

🪟 Web UI enhancements

🔌 Plugin architecture

🧩 MCP tool registry

📚 RAG improvements

🎶 TTS voice effects

🌐 Multi-language STT/TTS

🧱 Model switching UI

## Luminesce is early — your contributions shape the platform.

### 🧭 Architecture Overview
Luminesce is structured into clean, isolated subsystems:

lumin/llm/ — model drivers, streaming, tool routing

lumin/stt/ — offline speech recognition

lumin/tts/ — voice output

lumin/ui/tui/ — Textual interface

lumin/ui/web/ — Web UI + WebSockets

lumin/api/ — FastAPI backend

lumin/tools/ — tool definitions + MCP integration

lumin/rag/ — retrieval augmentation

lumin/config/ — YAML/JSON configuration

lumin/core/ — orchestrator, state machine, sessions

Each subsystem can be replaced, extended, or swapped.

🤝 Contributing
Pull requests are welcome.
If you want to build a feature, open an issue first so we can coordinate.

📜 License
MIT License — see LICENSE.