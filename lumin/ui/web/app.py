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

PERSONALITY_DIR = os.path.join(os.path.dirname(CONFIG_PATH), "prompts")

def load_personality_prompt(model_name: str) -> str:
    personalities = config.get("personalities", {})
    model_map = config.get("model_personality_map", {})

    personality_name = model_map.get(model_name, "default")
    personality_path = personalities.get(personality_name)

    if not personality_path:
        return SYSTEM_PROMPT  # fallback

    full_path = os.path.join(os.path.dirname(CONFIG_PATH), personality_path)
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"ERROR loading personality '{personality_name}':", e)
        return SYSTEM_PROMPT

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

@app.get("/api/personalities")
def list_personalities():
    personalities = config.get("personalities", {})
    model_map = config.get("model_personality_map", {})
    current_model = config["ollama"]["model"]
    current_personality = model_map.get(current_model, "default")

    return {
        "personalities": list(personalities.keys()),
        "current_model": current_model,
        "current_personality": current_personality,
        "model_personality_map": model_map
    }

@app.post("/api/set-personality")
async def set_personality(req: dict):
    model_name = req.get("model") or config["ollama"]["model"]
    personality_name = req.get("personality")

    if not personality_name:
        return {"ok": False, "error": "No personality provided"}

    if "personalities" not in config or personality_name not in config["personalities"]:
        return {"ok": False, "error": "Unknown personality"}

    model_map = config.get("model_personality_map", {})
    model_map[model_name] = personality_name
    config["model_personality_map"] = model_map

    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print("ERROR writing config.json:", e)
        return {"ok": False, "error": str(e)}

    return {"ok": True, "model": model_name, "personality": personality_name}

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

from fastapi import UploadFile, File


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    # Read raw bytes
    raw = await file.read()

    # Try to decode as UTF‑8 text
    try:
        text = raw.decode("utf-8")
        decoded = True
    except:
        decoded = False
        text = None

    # Determine active session
    # If your chat system uses a session ID, retrieve it here.
    # If not, fall back to a single global session.
    session_id = "default"
    if session_id not in conversations:
        conversations[session_id] = []

    # Store file content in conversation history
    if decoded:
        conversations[session_id].append({
            "role": "user",
            "content": f"[Uploaded file: {file.filename}]\n{text}"
        })
    else:
        conversations[session_id].append({
            "role": "user",
            "content": (
                f"[Uploaded file: {file.filename} — binary data, {len(raw)} bytes]"
            )
        })

    # Build assistant reply
    if decoded:
        preview = text[:500]  # prevent flooding the chat
        return {
            "reply": (
                f"I received **{file.filename}** and successfully read it.\n\n"
                f"Here is a preview:\n\n"
                f"{preview}\n\n"
                f"(The full content is now part of the conversation, "
                f"so you can ask me questions about it.)"
            )
        }
    else:
        return {
            "reply": (
                f"I received **{file.filename}**, but it isn't a text file I can decode.\n"
                f"I stored its metadata in the conversation so you can still ask me about it."
            )
        }


@app.post("/api/generate")
async def generate(req: dict):
    text = req.get("text", "")
    if not text:
        return {"reply": ""}

    model_name = config["ollama"]["model"]
    personality_prompt = load_personality_prompt(model_name)

    prompt = f"{personality_prompt.strip()}\n\nUser: {text}\nAssistant:"

    payload = {
        "model": model_name,
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

    model_name = config["ollama"]["model"]
    personality_prompt = load_personality_prompt(model_name)

    try:
        await ws.send_json({"session": session_id, "reply": "Connected. Ask me anything.", "stream": False})

        while True:
            # Receive JSON message from the client
            data = await ws.receive_json()
            text = data.get("text", "")

            # Store user message
            conversations[session_id].append({"role": "user", "content": text})

            # Build transcript with personality prompt
            transcript = personality_prompt.strip() + "\n\n"
            for m in conversations[session_id]:
                transcript += f"{m['role'].capitalize()}: {m['content']}\n"
            transcript += "Assistant:"

            payload = {
                "model": model_name,
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
