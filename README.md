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

Luminesce is built around a simple idea:

> **Intelligence should feel warm, not hot.  
> Helpful, not intrusive.  
> Illuminating, not overwhelming.**

The assistant glows softly, thinks quietly, and responds with clarity —  
a calm presence rather than a noisy gadget.

---

# 🔥 Why Luminesce Is Different

Most “local AI assistants” are:
- a single Python file  
- a wrapper around an LLM  
- a microphone loop  
- a toy

Luminesce is a **platform** with:

- A **full agent architecture**  
- **Tool calling** with JSON routing  
- **MCP integration**  
- **RAG subsystem**  
- **Textual TUI** with animated bulb + filament meter  
- **Web UI** with streaming WebSockets  
- **FastAPI backend**  
- **Config‑driven orchestration**  
- **Session memory**  
- **Wake‑word + silence detection**  
- **Local STT + TTS**  
- **Distributed node support**  
- **Model switching**  
- **GPU‑aware execution**

This is the difference between a *demo* and a *foundation*.

---

# 🚀 Quickstart (60 Seconds)

```bash
git clone https://github.com/StevenJayMartin/Luminesce
cd Luminesce
pip install -r requirements.txt
python -m lumin.main
```

Choose your mode:

- `--ui=tui`  
- `--ui=web`  
- `--llm-mode=chat`  
- `--llm-mode=tools`  
- `--llm-mode=rag`  

Luminesce adapts to your workflow.

---

# 🧩 Architecture Overview

Luminesce is built from clean, isolated subsystems:

### **Core**
- `lumin/core/` — orchestrator, state machine, session logic  
- `lumin/config/` — YAML/JSON configuration  

### **LLM**
- `lumin/llm/` — model drivers, streaming, tool routing  
- Supports Ollama + custom adapters  

### **Voice**
- `lumin/stt/` — offline speech recognition (Vosk)  
- `lumin/tts/` — offline TTS (Piper / Ryan voice)  
- Wake‑word + silence detection  

### **Tools & MCP**
- `lumin/tools/` — built‑in tools  
- MCP integration for external capabilities  

### **RAG**
- `lumin/rag/` — retrieval augmentation, embeddings, indexing  

### **UI**
- `lumin/ui/tui/` — Textual interface with animated bulb  
- `lumin/ui/web/` — Web UI + WebSockets  

### **API**
- `lumin/api/` — FastAPI backend powering both UIs  

Every subsystem can be replaced, extended, or swapped.

---

# 🛠️ Help Wanted (High‑Impact Contributions)

These are areas where contributors can make a *visible* difference:

- 🎨 New bulb animations (breathing, thinking, listening states)  
- 🔧 New Textual widgets (meters, panels, logs, timelines)  
- 🧠 New LLM tools (system control, search, OS integration)  
- 🪟 Web UI enhancements (themes, animations, model selector)  
- 🔌 Plugin architecture (drop‑in capabilities)  
- 🧩 MCP tool registry + discovery  
- 📚 RAG improvements (chunking, embeddings, vector stores)  
- 🎶 TTS voice effects (warmth, pitch, timbre)  
- 🌐 Multi‑language STT/TTS  
- 🧱 Model switching UI  
- 🛰️ Distributed node orchestration  

If you want to help shape a serious local AI platform, this is the place.

---

# 🤝 Contributing

Pull requests are welcome.  
If you want to build a feature, open an issue first so we can coordinate.

---

# 📜 License

MIT License — see `LICENSE`.

---

# 🔥 Official SVG Logo: “Enlightenment Without Heat”

Below is the Luminesce SVG logo you can embed directly in your README or docs.

```svg
<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">

  <defs>
    <radialGradient id="bg" cx="50%" cy="50%" r="75%">
      <stop offset="0%" stop-color="#0A0B10"/>
      <stop offset="60%" stop-color="#05060A"/>
      <stop offset="100%" stop-color="#000000"/>
    </radialGradient>

    <radialGradient id="ambientGlow" cx="50%" cy="38%" r="55%">
      <stop offset="0%" stop-color="#FFF8D6" stop-opacity="0.9"/>
      <stop offset="40%" stop-color="#FFE7A8" stop-opacity="0.55"/>
      <stop offset="75%" stop-color="#F5C46A" stop-opacity="0.22"/>
      <stop offset="100%" stop-color="#F3A94A" stop-opacity="0"/>
    </radialGradient>

    <radialGradient id="bulb" cx="50%" cy="35%" r="50%">
      <stop offset="0%" stop-color="#FFFFFF"/>
      <stop offset="35%" stop-color="#FFF2C9"/>
      <stop offset="70%" stop-color="#F7C46A"/>
      <stop offset="100%" stop-color="#D98A3A"/>
    </radialGradient>

    <linearGradient id="base" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1C1E24"/>
      <stop offset="50%" stop-color="#121318"/>
      <stop offset="100%" stop-color="#08090D"/>
    </linearGradient>

    <filter id="glowText">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <filter id="halo">
      <feGaussianBlur stdDeviation="18" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <rect width="512" height="512" fill="url(#bg)" />
  <circle cx="256" cy="210" r="180" fill="url(#ambientGlow)" />
  <circle cx="256" cy="210" r="95" fill="#FFE7A8" opacity="0.25" filter="url(#halo)" />
  <ellipse cx="256" cy="210" rx="85" ry="115" fill="url(#bulb)" />
  <ellipse cx="256" cy="210" rx="87" ry="117" fill="none" stroke="#FDE7B8" stroke-width="2" opacity="0.55"/>

  <path d="M215 210
           C228 185 240 185 252 210
           C264 235 276 235 288 210
           C300 185 312 185 325 210"
        fill="none"
        stroke="#FFD98A"
        stroke-width="4"
        stroke-linecap="round"
        stroke-linejoin="round"
        opacity="0.95"/>

  <circle cx="256" cy="210" r="14" fill="#FFE9B8" opacity="0.9"/>

  <rect x="230" y="270" width="52" height="42" rx="10" fill="#1A1C22" />
  <rect x="210" y="312" width="92" height="20" rx="6" fill="url(#base)" />
  <rect x="185" y="332" width="142" height="45" rx="12" fill="url(#base)" />

  <ellipse cx="256" cy="380" rx="95" ry="20" fill="#000000" opacity="0.45"/>
  <ellipse cx="256" cy="370" rx="130" ry="28" fill="#F3A94A" opacity="0.12"/>

  <text x="256" y="430"
        text-anchor="middle"
        font-family="system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
        font-size="36"
        fill="#FFE9B8"
        filter="url(#glowText)">
    Luminesce
  </text>

  <text x="256" y="465"
        text-anchor="middle"
        font-family="system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
        font-size="18"
        fill="#F9D47A"
        opacity="0.9">
    Enlightenment without heat
  </text>

</svg>
```

