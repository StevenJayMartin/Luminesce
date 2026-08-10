# Getting Started

Luminesce is a fully local AI assistant. This guide walks you through installation and first use.

---

## Requirements

- Python 3.10+
- Ollama installed
- Vosk STT model
- Piper TTS voice
- Textual (Python)
- FastAPI (for Web UI)

---

## Installation

Clone the repository:

```
git clone https://github.com/yourname/luminesce
cd luminesce
```

Install dependencies:

```
pip install -r requirements.txt
```

---

## Install Ollama Models

See `docs/models/ollama_models.md`.

---

## Install Vosk STT Model

See `docs/models/vosk_models.md`.

---

## Install Piper TTS Voice

See `docs/voice/tts.md`.

---

## Run the TUI

```
python -m lumin.ui.tui
```

---

## Run the Web UI

```
python -m lumin.ui.web
```

---

## First Commands

Try:

```
how are you
list tools
ingest https://example.com
mcp_time
```

---

## Voice Mode

Press **Push to Talk** or enable always‑listen mode in config:

```
voice:
  listen_mode: always
```

---

You’re ready to use Luminesce.

