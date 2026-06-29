from fastapi import FastAPI, WebSocket
from fastapi.requests import Request
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

# Simple in-memory conversation store
conversations = {}


@app.websocket("/ws/chat")
async def websocket_chat(ws: WebSocket):
    await ws.accept()

    session_id = str(uuid.uuid4())
    conversations[session_id] = []

    while True:
        message = await ws.receive_text()
        conversations[session_id].append({"role": "user", "text": message})

        # Call your actual LLM
        response_text = llm.run(message)

        conversations[session_id].append({"role": "assistant", "text": response_text})

        await ws.send_text(response_text)
