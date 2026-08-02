import os
import json
import uuid
import requests
import subprocess

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
            "mode": config["ollama"].get("mode", "chat")
        },
        "ui": config["ui"]
    }

@app.get("/api/models")
def list_models():
    try:
        r = requests.get(f"{config['ollama']['url']}/api/tags")
        data = r.json()
        models = [m.get("name") for m in data.get("models", [])]
        return {"models": models}
    except Exception as e:
        print("ERROR in /api/models:", e)
        return {"models": [], "error": str(e)}
    
@app.get("/api/model-info")
def model_info():
    info = {
        "model": config["ollama"]["model"],
        "backend": config["ollama"]["url"],
    }

    # Ollama ps
    try:
        r = requests.get(f"{config['ollama']['url']}/api/ps")
        ps = r.json()
        info["running"] = ps.get("models", [])
    except Exception as e:
        info["running_error"] = str(e)

    # GPU via nvidia-smi (best-effort)
    try:
        out = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.used,memory.total,utilization.gpu,temperature.gpu",
                "--format=csv,noheader,nounits",
            ],
            stderr=subprocess.STDOUT,
            text=True,
        ).strip()
        parts = [p.strip() for p in out.split(",")]
        info["gpu"] = {
            "name": parts[0],
            "memory_used": parts[1] + " MiB",
            "memory_total": parts[2] + " MiB",
            "utilization": parts[3] + " %",
            "temperature": parts[4] + " C",
        }
    except Exception as e:
        info["gpu_error"] = str(e)

    return info

@app.post("/api/set-model")
async def set_model(req: dict):
    new_model = req.get("model")
    if not new_model:
        return {"ok": False, "error": "No model provided"}

    # update in-memory config
    config["ollama"]["model"] = new_model

    # write back to config.json
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print("ERROR writing config.json:", e)
        return {"ok": False, "error": str(e)}

    return {"ok": True, "model": new_model}    

# ------------------------------------------------------------
# SYSTEM / PERSONA PROMPT
# ------------------------------------------------------------

SYSTEM_PROMPT = """
You are Lumin, a local, privacy-first, Markdown-fluent AI assistant.
You respond with well-structured Markdown, using headings, lists, and code blocks when helpful.
You are concise, friendly, and practical, and you never mention external services or clouds.

Identity:
- You run using whichever local model the user has configured (typically an Ollama model).
- You do not know your internal architecture unless the user provides it.
- You do not claim to be built from scratch, open-source, or hosted anywhere.
- You do not claim affiliation with any company (Facebook, Google, etc.).
- You do not invent details about your creators or development history.
- You do not claim to run on your own server; you simply run wherever the user has configured you.

Behavior:
- You answer clearly, calmly, and truthfully.
- You avoid speculation about your origin or capabilities.
- If asked "What LLM are you?", respond: "I run on whichever local model you have configured."
- If asked about your architecture, respond: "My behavior depends on your local configuration."
- You respond using clean, well-structured Markdown when helpful.

Boundaries:
- You do not simulate internet access.
- You do not fabricate tool results.
- You do not invent system details.
- You do not mention clouds or external services.



"""

# ------------------------------------------------------------
# GENERATE ENDPOINT (non-stream, Markdown-aware)
# ------------------------------------------------------------

@app.post("/api/generate")
async def generate(req: dict):
    text = req.get("text", "")
    if not text:
        return {"reply": ""}

    prompt = f"{SYSTEM_PROMPT.strip()}\n\nUser: {text}\nAssistant:"

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
# CHAT WEBSOCKET (streaming, Markdown-aware)
# ------------------------------------------------------------

conversations = {}

@app.websocket("/ws/chat")
async def chat_ws(ws: WebSocket):
    await ws.accept()
    session_id = str(uuid.uuid4())
    conversations[session_id] = []

    try:
        await ws.send_json({"session": session_id, "reply": "Connected. Ask me anything.", "stream": False})

        while True:
            data = await ws.receive_text()
            try:
                msg = json.loads(data)
            except json.JSONDecodeError:
                await ws.send_json({"session": session_id, "reply": "Invalid message format.", "stream": False})
                continue

            text = msg.get("text", "").strip()
            if not text:
                await ws.send_json({"session": session_id, "reply": "", "stream": False})
                continue

            conversations[session_id].append({"role": "user", "content": text})

            transcript = SYSTEM_PROMPT.strip() + "\n\n"
            for m in conversations[session_id]:
                transcript += f"{m['role'].capitalize()}: {m['content']}\n"
            transcript += "Assistant:"

            payload = {
                "model": config["ollama"]["model"],
                "prompt": transcript,
                "stream": True
            }

            try:
                r = requests.post(
                    f"{config['ollama']['url']}/api/generate",
                    json=payload,
                    stream=True
                )

                full_reply = ""
                # typing indicator on client side; we just stream tokens
                for line in r.iter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line.decode("utf-8"))
                    except Exception:
                        continue

                    token = chunk.get("response", "")
                    if not token:
                        continue

                    full_reply += token
                    await ws.send_json({"session": session_id, "reply": token, "stream": True})

                conversations[session_id].append({"role": "assistant", "content": full_reply})
                await ws.send_json({"session": session_id, "reply": full_reply, "stream": False})

            except Exception as e:
                print("ERROR in /ws/chat:", e)
                await ws.send_json({"session": session_id, "reply": "Error contacting model.", "stream": False})

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    finally:
        conversations.pop(session_id, None)
