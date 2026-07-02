import os
import json
import uuid
import requests

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# ------------------------------------------------------------
# PATHS
# ------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE_DIR, "index.html")
STATIC_PATH = os.path.join(BASE_DIR, "static")
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), "config.json")

# ------------------------------------------------------------
# LOAD CONFIG.JSON
# ------------------------------------------------------------
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

# ------------------------------------------------------------
# FASTAPI APP
# ------------------------------------------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.isdir(STATIC_PATH):
    app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")

# ------------------------------------------------------------
# ROUTES
# ------------------------------------------------------------

@app.get("/")
def root():
    return FileResponse(INDEX_PATH)

@app.get("/config")
def get_config():
    return {
        "ollama": {
            "url": config["ollama"]["url"],
            "model": config["ollama"]["model"],
            "mode": config["ollama"].get("mode", "generate")
        },
        "ui": config["ui"]
    }

# ------------------------------------------------------------
# GENERATE ENDPOINT
# ------------------------------------------------------------

@app.post("/api/generate")
async def generate(req: dict):
    text = req.get("text", "")
    if not text:
        return {"reply": ""}

    payload = {
        "model": config["ollama"]["model"],
        "prompt": text,
        "stream": False
    }

    try:
        r = requests.post(
            f"{config['ollama']['url']}/api/generate",
            json=payload
        )

        print("OLLAMA RAW RESPONSE:", r.text)

        resp = r.json()
        return {"reply": resp.get("response", "")}

    except Exception as e:
        print("ERROR in /api/generate:", e)
        return {"reply": "Error contacting model."}

# ------------------------------------------------------------
# CHAT WEBSOCKET
# ------------------------------------------------------------

conversations = {}

@app.websocket("/ws/chat")
async def websocket_chat(ws: WebSocket):
    await ws.accept()

    try:
        while True:
            data = await ws.receive_json()
            session_id = data.get("session")
            text = data.get("text", "").strip()

            if not session_id:
                session_id = str(uuid.uuid4())

            if session_id not in conversations:
                conversations[session_id] = []

            conversations[session_id].append({"role": "user", "content": text})

            transcript = ""
            for msg in conversations[session_id]:
                transcript += f"{msg['role'].capitalize()}: {msg['content']}\n"
            transcript += "Assistant:"

            response = requests.post(
                f"{config['ollama']['url']}/api/generate",
                json={
                    "model": config["ollama"]["model"],
                    "prompt": transcript,
                    "stream": False
                }
            ).json()

            reply = response.get("response", "").strip()

            conversations[session_id].append({"role": "assistant", "content": reply})

            await ws.send_json({
                "session": session_id,
                "reply": reply
            })

    except WebSocketDisconnect:
        print("WebSocket disconnected")
