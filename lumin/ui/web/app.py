import os
from fastapi import FastAPI, WebSocket
from fastapi import UploadFile, File
from faster_whisper import WhisperModel
import tempfile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from lumin.ui.web.models.config import load_config, get_paths
from lumin.ui.web.core.semantic_memory import LuminSemanticMemory
from lumin.ui.web.core.ws_chat import chat_ws

# Import router + dependency placeholders
from lumin.ui.web.routes.system import router as system_router
from lumin.ui.web.routes import system as system_deps
from lumin.voice.tts_onnx import OnnxTTS

import lumin.ui.web.models.state as state

tts_engine = OnnxTTS("lumin/models/onnx")
# ------------------------------------------------------------
# Load config + paths
# ------------------------------------------------------------

config = load_config()
paths = get_paths()

state.current_model = config["ollama"]["model"]

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

whisper_model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)

tts_engine = OnnxTTS("lumin/models/onnx")

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
@app.post("/api/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...)
):
    print(f"Received audio: {file.filename}")

    suffix = (
        os.path.splitext(file.filename)[1]
        or ".webm"
    )

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as tmp:

        tmp.write(await file.read())
        temp_path = tmp.name

    try:

        segments, info = whisper_model.transcribe(
            temp_path,
            beam_size=5
        )

        text = " ".join(
            segment.text
            for segment in segments
        ).strip()


        return {
            "success": True,
            "text": text
        }

    finally:

        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.post("/api/set-model")
async def set_model(req: dict):

    new_model = req.get("model")

    if not new_model:
        return {
            "ok": False,
            "error": "No model provided"
        }

    state.current_model = new_model

    print(f"Model changed to: {state.current_model}")

    return {
        "ok": True,
        "model": state.current_model
    }


@app.post("/api/set-personality")
async def set_personality(req: dict):

    new_personality = req.get("personality")

    if not new_personality:
        return {"ok": False}

    state.current_personality = new_personality

    print(f"Personality changed to: {new_personality}")

    return {
        "ok": True,
        "personality": new_personality
    }

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

from fastapi import Body
from fastapi.responses import Response

@app.post("/api/tts")
async def tts(payload: dict = Body(...)):

    text = payload.get("text", "").strip()

    if not text:
        return Response(
            content=b"",
            media_type="audio/wav"
        )

    try:
        wav = tts_engine.synthesize(text)
    except ValueError:
        return Response(
            content=b"",
            media_type="audio/wav"
        )

    return Response(
        content=wav,
        media_type="audio/wav"
    )
    
# ------------------------------------------------------------
# WebSocket
# ------------------------------------------------------------
@app.websocket("/ws/chat")
async def ws_chat_endpoint(ws: WebSocket):
    await chat_ws(ws, config=config, paths=paths, semantic_memory=semantic_memory)
