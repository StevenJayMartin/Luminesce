README.md (raw Markdown)
markdown
<p align="center">
  <img src="banner.svg" alt="Lumin – Local Light‑Bulb Assistant" />
</p>

<h1 align="center">Lumin · Local Light‑Bulb Assistant</h1>

<p align="center">
  <strong>A fully local, voice‑driven AI assistant with a glowing bulb personality.</strong><br/>
  No cloud. No telemetry. Just your machine, your models, your rules.
</p>

<p align="center">
  <a href="#-features">Features</a> ·
  <a href="#-architecture">Architecture</a> ·
  <a href="#-configuration">Configuration</a> ·
  <a href="#-running-lumin">Running Lumin</a> ·
  <a href="#-contributing">Contributing</a>
</p>

---

## 🌟 Why Lumin?

Lumin is a local AI assistant designed to feel alive — a glowing bulb that listens, thinks, and speaks entirely on your machine.

- **Local‑first:** Everything runs on your hardware.  
- **Voice‑native:** Wake‑word, speech recognition, and text‑to‑speech built in.  
- **Hackable:** Modular Python components you can extend, replace, or remix.  
- **Fun:** Animated UI, personality, and room to play.

If you’ve ever wanted a **personal Copilot** that lives on your desktop instead of in the cloud, Lumin is for you.

---

## 🚀 Features

### 🎤 Speech Recognition (STT)

- Offline STT powered by **Vosk**  
- High‑pass filtering for clarity  
- Silence detection  
- Volume metering (for the filament meter)  
- Wake‑words:
  - `Lumin`
  - `Hey Lumin`  
- Control words:
  - `stop`, `cancel`
  - `clear that`, `reset`
  - `listen again`, `start over`

### 🧠 Local LLM Integration

- Uses **Ollama** for fully local inference  
- Streaming, token‑by‑token responses  
- Works with any installed Ollama model  
- Simple client API:
  - `stream_chat(messages, on_token)`
  - `ask(messages)`

### 🔊 Text‑to‑Speech (TTS)

- Powered by **pyttsx3**  
- Non‑blocking threaded engine  
- Queue‑based speech  
- Wake‑word does not interrupt TTS  
- Clean shutdown, no overlapping messages

### 💡 Textual UI

- Animated bulb widget (idle, listening, thinking, speaking)  
- Filament volume meter  
- Push‑to‑talk (`Ctrl+M`)  
- Always‑listen mode  
- Thread‑safe UI updates  
- Simple state machine:
  - idle → listening → thinking → speaking

### 🔐 Privacy‑First

- No cloud calls  
- No telemetry  
- Your voice and data never leave your machine  

---

## 🧱 Architecture

Lumin is intentionally modular — each component lives in its own file for clarity and easy hacking.

```text
lumin/
│
├── main.py              # Entry point, config loading, CLI overrides
├── stt.py               # Speech recognition + wake-word engine
├── tts.py               # Threaded text-to-speech engine
├── ollama_client.py     # Streaming LLM client for Ollama
└── ui_app.py            # Textual UI + assistant orchestration
main.py — The Conductor
Parses CLI arguments

Loads config.json

Applies overrides

Launches the Textual UI (LuminApp)

stt.py — The Ears
Vosk STT pipeline

Wake‑word detection ("Lumin", "Hey Lumin")

Stop / Clear / Listen‑Again detection

Silence detection

High‑pass filtering

Volume metering callback

Returns structured results like:

python
{
  "text": "...",
  "stop": False,
  "clear": False,
  "listen_again": False
}
tts.py — The Voice
Threaded text‑to‑speech engine

Internal queue

is_busy() flag (used by wake‑word logic)

Clean shutdown

No overlapping messages

ollama_client.py — The Brain
Talks to the local Ollama server

stream_chat(messages, on_token) for streaming

ask(messages) for synchronous responses

Basic error handling and retries

ui_app.py — The Body
Textual UI

Bulb widget

Filament meter widget

Always‑listen loop

Push‑to‑talk (Ctrl+M)

Wake‑word acknowledgment (“I’m listening.”)

STT → LLM → TTS pipeline

State machine: idle / listening / thinking / speaking

⚙️ Configuration
Create a config.json in the project root:

json
{
  "model": "llama3.1",
  "ollama_url": "http://localhost:11434",
  "mic_device": 0,
  "listen_mode": "push_to_talk",

  "wake_words": ["hey lumin", "lumin"],
  "stop_words": ["stop", "cancel"],
  "clear_words": ["clear that", "reset"],
  "listen_again_words": ["listen again", "start over"],

  "vosk_model_path": "models/vosk",
  "silence_threshold": 3000,
  "silence_duration": 0.6
}
▶️ Running Lumin
From inside the lumin/ directory:

bash
python3 main.py
Optional CLI overrides:

bash
python3 main.py --model llama3.2
python3 main.py --mic 1
python3 main.py --listen-mode always
python3 main.py --ollama http://localhost:11435
🧪 Requirements
Install dependencies:

bash
pip install sounddevice scipy vosk pyttsx3 textual requests numpy
You also need:

Vosk model  
Download any English model and place it in models/vosk/.

Ollama  
Install from their site, then pull a model:

bash
ollama pull llama3.1
🤝 Contributing
Lumin is intentionally modular — adding new features should feel fun, not painful.

You can:

Add new widgets

Add new wake‑words

Add new control words

Add new animations

Add new LLM tools

Add new commands ("turn on the lights", "play music", etc.)

PRs are welcome.
Ideas are welcome.
Experiments are encouraged.

💡 Vision
Lumin is more than a script — it’s a platform for building a local, expressive, voice‑driven AI companion.

If you want:

A logo and banner (see banner.svg)

A CONTRIBUTING.md

A ROADMAP.md

A wiki layout

A “Getting Started” video script

A feature showcase GIF

You’re in the right place.

Lumin is early, but he’s already:

Listening

Thinking

Speaking

Animating

And making people smile

If you want to help shape a local, open, creative AI assistant —

welcome aboard.