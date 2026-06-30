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

# /home/sjm/Luminesce/lumin/ui/web
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# /home/sjm/Luminesce/lumin/ui/web/index.html
INDEX_PATH = os.path.join(BASE_DIR, "index.html")

# /home/sjm/Luminesce/lumin/ui/web/static
STATIC_PATH = os.path.join(BASE_DIR, "static")

# /home/sjm/Luminesce/lumin/config.json
#- CONFIG_PATH = os.path.join(os.path.dirname(BASE_DIR), "config.json")
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), "config.json")



# ------------------------------------------------------------
# LOAD CONFIG.JSON
# ------------------------------------------------------------
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)


# ------------------------------------------------------------
# OPTIONAL: WARMUP (SAFE IMPORT)
# ------------------------------------------------------------
try:
    from lumin.main import warm_llm
    warm_llm()
    print("LLM warmup complete.")
except Exception as e:
    print("Warmup skipped or failed:", e)


# ------------------------------------------------------------
# FASTAPI APP
# ------------------------------------------------------------
app = FastAPI()

# Allow browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory
if os.path.isdir(STATIC_PATH):
    app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")


# ------------------------------------------------------------
# ROUTES
# ------------------------------------------------------------

@app.get("/")
def root():
    """
    Serve the main Web UI page.
    """
    return FileResponse(INDEX_PATH)


@app.get("/config")
def get_config():
    """
    Expose config.json to the Web UI.
    """
    return {
        "llm": {
            "url": config["ollama"]["url"],
            "model": config["ollama"]["model"]
        },
        "ui": {
            "mode": config["ui"].get("mode", "auto"),
            "width": config["ui"].get("width", "auto"),
            "theme": config["ui"].get("theme", "dark"),
            "animations": config["ui"].get("animations", True)
        }
    }


# ------------------------------------------------------------
# WEBSOCKET CHAT
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

            # Add user message
            conversations[session_id].append({"role": "user", "content": text})

            # Build transcript
            transcript = ""
            for msg in conversations[session_id]:
                transcript += f"{msg['role'].capitalize()}: {msg['content']}\n"
            transcript += "Assistant:"

            # Call Ollama
            response = requests.post(
                f"{config['ollama']['url']}/api/generate",
                json={
                    "model": config["ollama"]["model"],
                    "prompt": transcript,
                    "stream": False
                }
            ).json()
            reply = response.get("response", "").strip()

            # Add assistant reply
            conversations[session_id].append({"role": "assistant", "content": reply})

            # Send back to browser
            await ws.send_json({
                "session": session_id,
                "reply": reply
            })

    except WebSocketDisconnect:
        print("WebSocket disconnected")
