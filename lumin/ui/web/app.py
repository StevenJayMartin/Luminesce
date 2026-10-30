import os
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from lumin.ui.web.models.config import load_config, get_paths
from lumin.ui.web.core.semantic_memory import LuminSemanticMemory
from lumin.ui.web.core.ws_chat import chat_ws

# Import router + dependency placeholders
from lumin.ui.web.routes.system import router as system_router
from lumin.ui.web.routes import system as system_deps

# ------------------------------------------------------------
# Load config + paths
# ------------------------------------------------------------
config = load_config()
paths = get_paths()

# ------------------------------------------------------------
# Initialize semantic memory
# ------------------------------------------------------------
semantic_memory = LuminSemanticMemory(
    file_path=paths["memory"],
    ollama_url=config["ollama"]["url"],
    embedding_model=config["ollama"].get("embedding_model", config["ollama"]["model"]),
)

# ------------------------------------------------------------
# FastAPI app
# ------------------------------------------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------
# Static files
# ------------------------------------------------------------
if os.path.isdir(paths["static"]):
    app.mount("/static", StaticFiles(directory=paths["static"]), name="static")

# ------------------------------------------------------------
# Dependency overrides
# ------------------------------------------------------------
app.dependency_overrides[system_deps.get_config] = lambda: config
app.dependency_overrides[system_deps.get_memory_engine] = lambda: semantic_memory

# ------------------------------------------------------------
# Routes
# ------------------------------------------------------------
current_model = "llama3:latest"

@app.post("/api/set-model")
async def set_model(req: dict):
    global current_model

    new_model = req.get("model")
    if not new_model:
        return {"ok": False, "error": "No model provided"}

    current_model = new_model
    return {"ok": True, "model": current_model}


@app.get("/")
def root():
    return FileResponse(paths["index"])

@app.get("/config")
def get_config_route():
    return {
        "ollama": {
            "url": config["ollama"]["url"],
            "model": config["ollama"]["model"],
            "mode": config["ollama"].get("mode", "chat"),
        },
        "ui": config.get("ui", {}).get("web", {}),
    }

# Register system routes
app.include_router(system_router)

# ------------------------------------------------------------
# WebSocket
# ------------------------------------------------------------
@app.websocket("/ws/chat")
async def ws_chat_endpoint(ws: WebSocket):
    await chat_ws(ws, config=config, paths=paths, semantic_memory=semantic_memory)

# ------------------------------------------------------------
# TTS Endpoint (MeloTTS ONNX)
# ------------------------------------------------------------
import numpy as np
import onnxruntime as ort

# Load ONNX model once at startup
tts_session = ort.InferenceSession(
    os.path.join(paths["static"], "onnx", "model.onnx"),
    providers=["CPUExecutionProvider"]
)

@app.post("/api/tts")
async def tts(req: dict):
    text = req.get("text", "").strip()
    if not text:
        return {"ok": False, "error": "No text provided"}

    # TODO: Replace with real tokenizer
    # For now: dummy single token
    ids = np.array([[1]], dtype=np.int64)

    # Run ONNX model
    out = tts_session.run(None, {"input_ids": ids})[0]

    # Flatten PCM float32 audio
    pcm = out.flatten().tolist()

    return {"ok": True, "pcm": pcm}
