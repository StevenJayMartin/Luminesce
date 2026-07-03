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
# GENERATE ENDPOINT (Markdown prompt)
# ------------------------------------------------------------

@app.post("/api/generate")
async def generate(req: dict):
    text = req.get("text", "")
    if not text:
        return {"reply": ""}

    # Tell the LLM to respond in Markdown
    prompt = f"Respond using clean, well-structured Markdown.\n\nUser: {text}\nAssistant:"

    payload = {
        "model": config["ollama"]["model"],
        "prompt": prompt,
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
# CHAT WEBSOCKET (Markdown-aware transcript)
# ------------------------------------------------------------

conversations = {}

@app.websocket("/ws/chat")
async def chat_ws(ws: WebSocket):
    await ws.accept()
    session_id = str(uuid.uuid4())
    conversations[session_id] = []

    try:
        await ws.send_json({"session": session_id, "reply": "Connected. Ask me anything in chat mode."})

        while True:
            data = await ws.receive_text()
            try:
                msg = json.loads(data)
            except json.JSONDecodeError:
                await ws.send_json({"session": session_id, "reply": "Invalid message format."})
                continue

            text = msg.get("text", "").strip()
            if not text:
                await ws.send_json({"session": session_id, "reply": ""})
                continue

            # Store conversation
            conversations[session_id].append({"role": "user", "content": text})

            # Build Markdown-aware transcript
            transcript = "Respond using clean, well-structured Markdown with headings, lists, and code blocks when appropriate.\n\n"
            for m in conversations[session_id]:
                transcript += f"{m['role'].capitalize()}: {m['content']}\n"
            transcript += "Assistant:"

            payload = {
                "model": config["ollama"]["model"],
                "prompt": transcript,
                "stream": False
            }

            try:
                r = requests.post(
                    f"{config['ollama']['url']}/api/generate",
                    json=payload
                )
                print("OLLAMA CHAT RAW RESPONSE:", r.text)
                resp = r.json()
                reply = resp.get("response", "")

                conversations[session_id].append({"role": "assistant", "content": reply})

                await ws.send_json({"session": session_id, "reply": reply})

            except Exception as e:
                print("ERROR in /ws/chat:", e)
                await ws.send_json({"session": session_id, "reply": "Error contacting model."})

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    finally:
        conversations.pop(session_id, None)
