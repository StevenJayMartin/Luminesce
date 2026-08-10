# Luminesce — Fast But Reliable Install Guide

This guide gets Luminesce running **fast**, with **zero guesswork**, and **no broken steps**.  
It includes sanity checks, real commands, and systemd service files.

---

# 1. Install Python 3.10+

### Windows
Download from: https://www.python.org/downloads/windows/  
Check: “Add Python to PATH”

### macOS
Verify:
```
python3 --version
```

### Linux
Use your package manager or python.org.

### ✔ Sanity Check
```
python --version
```
Should show:
```
Python 3.10.x or 3.11.x
```

---

# 2. Install Ollama

Install from:  
https://ollama.com/download

### ✔ Sanity Check
```
ollama --version
```

---

# 3. Pull an LLM Model

Recommended:
```
ollama pull mistral:7b
```
or
```
ollama pull llama3
```

### ✔ Sanity Check
```
ollama run llama3
```

---

# 4. Install Vosk STT Model

Download:
```
vosk-model-small-en-us-0.15
```

Place it here:
```
lumin/models/vosk/vosk-model-small-en-us-0.15/
```

### ✔ Sanity Check
```
python - <<EOF
from vosk import Model
Model("lumin/models/vosk/vosk-model-small-en-us-0.15")
print("Vosk OK")
EOF
```

---

# 5. Install Piper TTS Voice

Download:
```
en_US-ryan-medium.onnx
```

Place it here:
```
lumin/models/piper/en_US-ryan-medium.onnx
```

### ✔ Sanity Check
```
piper --help
```

---

# 6. Install Luminesce Dependencies

Inside project root:
```
pip install -r requirements.txt
```

### ✔ Sanity Check
```
python - <<EOF
import lumin
print("Luminesce imports OK")
EOF
```

---

# 7. Verify Audio Devices

### Windows
Run:
```
mmsys.cpl
```

### macOS
System Settings → Sound → Input

### Linux
```
pactl list sources | grep Name
```

---

# 8. Run Luminesce (TUI)

From project root:

```
python -m lumin.main --model="mistral:7b" --llm-mode=chat --config="lumin/config.json"
```

You should see:
```
Connected to Lumin
✓ MCP Connected
```

---

# 9. Run Luminesce (Web UI)

```
uvicorn lumin.ui.web.app:app --host 0.0.0.0 --port 8000
```

Open:
```
http://localhost:8000
```

---

# 10. First Commands to Test

### Test LLM
```
hello
```

### Test RAG
```
ingest https://example.com
```

### Test MCP
```
mcp_rpc {"jsonrpc": "2.0", "id": 1, "method": "get_tools"}
```

### Test Voice
Press **Push to Talk**  
Say:
```
how are you
```

---

# 11. Systemd Services (Linux)

Below are **drop‑in ready** systemd units for Web UI, RAG server, and MCP server.

Place these in:
```
/etc/systemd/system/
```

---

## systemd: Luminesce Web UI

```
[Unit]
Description=Luminesce Web UI
After=network.target

[Service]
Type=simple
User=sjm
WorkingDirectory=/home/sjm/Luminesce
ExecStart=/home/sjm/Luminesce/venv/bin/uvicorn lumin.ui.web.app:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## systemd: Luminesce RAG Server

```
[Unit]
Description=Luminesce RAG Server
After=network.target

[Service]
Type=simple
User=sjm
WorkingDirectory=/home/sjm/Luminesce
ExecStart=/home/sjm/Luminesce/venv/bin/python -m lumin.rag.server
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## systemd: Luminesce MCP Server (optional)

```
[Unit]
Description=Luminesce MCP Server
After=network.target

[Service]
Type=simple
User=sjm
WorkingDirectory=/home/sjm/Luminesce/lumin/mcp
ExecStart=/home/sjm/Luminesce/venv/bin/python mcp_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

---

# Enable and Start Services

```
sudo systemctl daemon-reload
sudo systemctl enable luminesce-web
sudo systemctl enable luminesce-rag
sudo systemctl enable luminesce-mcp
sudo systemctl start luminesce-web
sudo systemctl start luminesce-rag
sudo systemctl start luminesce-mcp
```

---

# 12. Troubleshooting (Fast)

### Ollama not responding
```
ollama serve
```

### MCP not starting
Check:
```
lumin/mcp/mcp_server.py
```

### STT not hearing you
Check microphone permissions.

### TTS silent
Check Piper voice path.

---

# ✔ Done

This is the **Fast But Reliable Install Guide** — accurate, complete, and ready for impatient users.


