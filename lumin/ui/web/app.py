from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
import uuid
import json
import os

# Load config.json
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../../config.json")
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

# Import your LLM pipeline
from core.ollama_client import OllamaChat

app = FastAPI()

# Serve static files (HTML/JS/CSS)
app.mount("/static", StaticFiles(directory="ui/web/static"), name="static")

# Initialize your LLM once at startup
llm = OllamaChat(config)

# In-memory conversation store (session_id → list of messages)
conversations = {}

# ⭐ Warm the model on startup
@app.on_event("startup")
async def warm_model():
    print("Warming LLM model...")
    try:
        llm.run("warmup")
        print("LLM ready.")
    except Exception as e:
        print("Warmup failed:", e)


@app.websocket("/ws/chat")
async def websocket_chat(ws: WebSocket):
    await ws.accept()

    while True:
        raw = await ws.receive_text()

        # Try to parse JSON from the UI
        try:
            data = json.loads(raw)
        except:
            continue

        # Must include session ID
        session_id = data.get("session")
        if not session_id:
            # Ignore malformed messages
            continue

        # Must include user text
        if "text" not in data:
            continue

        user_text = data["text"]

        # Create session if new
        conversations.setdefault(session_id, [])

        # Add user message to session history
        conversations[session_id].append({"role": "user", "text": user_text})

        # Send "thinking" status to UI
        await ws.send_json({"type": "status", "state": "thinking"})

        # ⭐ Pass full conversation history to the LLM
        history = conversations[session_id]
        response_text = llm.run(history)

        # Add assistant reply to session history
        conversations[session_id].append({"role": "assistant", "text": response_text})

        # Send final structured message
        await ws.send_json({"type": "final", "text": response_text})
