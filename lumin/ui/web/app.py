from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
import json
import os

from core.ollama_client import OllamaChat

app = FastAPI()

app.mount("/static", StaticFiles(directory="ui/web/static"), name="static")

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../../config.json")
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

llm = OllamaChat(config)

conversations = {}

@app.on_event("startup")
async def warm_model():
    print("Warming LLM model...")
    try:
        llm.run([{"role": "user", "content": "warmup"}])
        print("LLM ready.")
    except Exception as e:
        print("Warmup failed:", e)


@app.websocket("/ws/chat")
async def websocket_chat(ws: WebSocket):
    await ws.accept()
    print("WebSocket connected")

    while True:
        try:
            raw = await ws.receive_text()
        except Exception as e:
            print("WebSocket closed:", e)
            break

        try:
            data = json.loads(raw)
        except:
            print("Invalid JSON:", raw)
            continue

        session_id = data.get("session")
        user_text = data.get("text")

        if not session_id or not user_text:
            print("Missing session or text")
            continue

        conversations.setdefault(session_id, [])

        conversations[session_id].append({
            "role": "user",
            "content": user_text
        })

        await ws.send_json({"type": "status", "state": "thinking"})

        history = conversations[session_id]

        try:
            response_text = llm.run(history)
        except Exception as e:
            print("LLM error:", e)
            await ws.send_json({"type": "error", "message": str(e)})
            continue

        conversations[session_id].append({
            "role": "assistant",
            "content": response_text
        })

        await ws.send_json({"type": "final", "text": response_text})
